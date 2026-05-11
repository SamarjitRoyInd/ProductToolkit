"""
Release History Tracker
-----------------------
Scans a Slack release channel for the last N days, uses Claude to filter out
noise and summarise the actual releases, then publishes a release-notes page
to Confluence and posts a digest link back to Slack.

Usage:
    python src/main.py --dry-run     # print only, no publish
    python src/main.py               # publish to Confluence + Slack digest
"""

import argparse
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone

from anthropic import Anthropic
from atlassian import Confluence
from dotenv import load_dotenv
from slack_sdk import WebClient

load_dotenv()


# ---------- Slack ----------

def fetch_slack_messages(lookback_days: int) -> list[dict]:
    """Fetch top-level (non-thread-reply) messages from the release channel."""
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    channel = os.environ["SLACK_RELEASE_CHANNEL_ID"]
    oldest = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).timestamp()

    messages: list[dict] = []
    cursor = None
    while True:
        resp = client.conversations_history(
            channel=channel,
            oldest=str(oldest),
            limit=200,
            cursor=cursor,
        )
        for m in resp["messages"]:
            # Skip bot messages, thread-broadcasts-only, joins/leaves, empty text
            if m.get("subtype") in {"channel_join", "channel_leave", "bot_message"}:
                continue
            if not m.get("text", "").strip():
                continue
            messages.append({
                "ts": m["ts"],
                "user": m.get("user", "unknown"),
                "text": m["text"],
            })
        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
    return messages


# ---------- Claude: classify & summarise ----------

def _claude_client() -> Anthropic:
    return Anthropic()


def _model() -> str:
    return os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")


def classify_release_messages(messages: list[dict]) -> list[dict]:
    """Ask Claude which messages are actual release announcements.

    Returns the subset of messages tagged as releases, with an added
    'area' field (e.g., 'recommendation-engine', 'microsoft-integration').
    """
    if not messages:
        return []

    client = _claude_client()
    numbered = "\n".join(
        f"[{i}] {m['text']}" for i, m in enumerate(messages)
    )

    prompt = f"""You are reviewing the last week of messages from a B2B gaming
platform's #releases Slack channel. Identify which messages announce an actual
release, hotfix, deployment, or partner-facing change. Ignore banter, questions,
deploy bot pings without context, and reactions.

For each message you keep, assign a short 'area' tag like:
recommendation-engine, microsoft-integration, youtube-integration,
samsung-integration, amazon-integration, genai-bug-agent, marketing-automation,
catalogue, analytics, infra, other.

Return ONLY a JSON array. No prose, no markdown fences. Example:
[{{"index": 3, "area": "recommendation-engine"}}, {{"index": 7, "area": "microsoft-integration"}}]

Messages:
{numbered}
"""

    message = client.messages.create(
        model=_model(),
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    # Be defensive: strip code fences if Claude added them
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw).strip()
    try:
        decisions = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[warn] could not parse classifier output, got: {raw[:200]}")
        return []

    kept = []
    for d in decisions:
        idx = d.get("index")
        if isinstance(idx, int) and 0 <= idx < len(messages):
            kept.append({**messages[idx], "area": d.get("area", "other")})
    return kept


def group_by_area(items: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for item in items:
        groups.setdefault(item["area"], []).append(item)
    return groups


def summarise_group(area: str, items: list[dict]) -> str:
    client = _claude_client()
    bullets = "\n".join(f"- {it['text']}" for it in items)
    prompt = f"""Write one section of a weekly release-notes document for a
B2B gaming platform's enterprise partners.

Area: {area}
Raw Slack messages from engineers this week:
{bullets}

Output format:
- One short intro line setting context for this area
- A bulleted list, one line per release item, in plain partner-readable English
- No marketing fluff, no hyperbole
- Strip internal-only details (engineer names, internal tool names, joke phrasing)
- If two messages clearly describe the same shipment, merge them into one bullet
"""
    message = client.messages.create(
        model=_model(),
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ---------- Publish ----------

def publish_to_confluence(title: str, body_html: str) -> str:
    """Publish a new child page under the configured parent. Returns page URL."""
    confluence = Confluence(
        url=os.environ["CONFLUENCE_BASE_URL"].rstrip("/"),
        username=os.environ["CONFLUENCE_EMAIL"],
        password=os.environ["CONFLUENCE_API_TOKEN"],
        cloud=True,
    )
    page = confluence.create_page(
        space=os.environ["CONFLUENCE_SPACE_KEY"],
        title=title,
        body=body_html,
        parent_id=os.environ["CONFLUENCE_PARENT_PAGE_ID"],
        representation="storage",
    )
    page_id = page["id"]
    base = os.environ["CONFLUENCE_BASE_URL"].rstrip("/")
    return f"{base}/spaces/{os.environ['CONFLUENCE_SPACE_KEY']}/pages/{page_id}"


def post_slack_digest(page_title: str, page_url: str) -> None:
    digest_channel = os.environ.get("SLACK_DIGEST_CHANNEL_ID")
    if not digest_channel:
        return
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    client.chat_postMessage(
        channel=digest_channel,
        text=f":rocket: *{page_title}* is up — <{page_url}|read on Confluence>",
    )


# ---------- Rendering ----------

def render_markdown(sections: list[tuple[str, str]], week_label: str) -> str:
    body = [f"# Release Notes — {week_label}\n"]
    for area, content in sections:
        body.append(f"## {area}\n\n{content}\n")
    return "\n".join(body)


def markdown_to_confluence_storage(md: str) -> str:
    """Very light markdown -> Confluence storage HTML.
    For anything fancier, swap in a real converter."""
    html = md
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    # Convert bullets
    lines = []
    in_list = False
    for line in html.split("\n"):
        if line.startswith("- "):
            if not in_list:
                lines.append("<ul>")
                in_list = True
            lines.append(f"<li>{line[2:]}</li>")
        else:
            if in_list:
                lines.append("</ul>")
                in_list = False
            if line.strip():
                lines.append(f"<p>{line}</p>")
            else:
                lines.append("")
    if in_list:
        lines.append("</ul>")
    return "\n".join(lines)


# ---------- Entry point ----------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print only, no publish")
    args = parser.parse_args()

    lookback = int(os.environ.get("LOOKBACK_DAYS", "7"))
    print(f"[1/4] Fetching Slack messages from last {lookback} days...")
    raw_messages = fetch_slack_messages(lookback)
    print(f"      Got {len(raw_messages)} non-bot, non-empty messages.")

    print("[2/4] Classifying release-relevant messages with Claude...")
    releases = classify_release_messages(raw_messages)
    print(f"      Kept {len(releases)} as releases.")

    print("[3/4] Grouping & summarising by area...")
    groups = group_by_area(releases)
    sections: list[tuple[str, str]] = []
    for area, items in groups.items():
        print(f"      - {area} ({len(items)} items)")
        sections.append((area, summarise_group(area, items)))
        time.sleep(0.5)  # gentle on rate limits

    week_label = datetime.now(timezone.utc).strftime("Week of %d %b %Y")
    title = f"Release Notes — {week_label}"
    md = render_markdown(sections, week_label)

    if args.dry_run:
        print("\n----- DRY RUN OUTPUT -----\n")
        print(md)
        return

    print("[4/4] Publishing to Confluence...")
    html = markdown_to_confluence_storage(md)
    page_url = publish_to_confluence(title, html)
    post_slack_digest(title, page_url)
    print(f"Done. Page: {page_url}")


if __name__ == "__main__":
    main()
