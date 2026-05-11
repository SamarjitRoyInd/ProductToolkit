# Release History Tracker

> A Claude-powered automation that turns a noisy Slack release channel into a clean, partner-ready release history doc on Confluence — every Monday morning, with no manual copy-paste.

## Quick Stats

| Metric | Before | After |
|---|---|---|
| Time to compile weekly release notes | ~2 hours | ~15 minutes |
| Coverage of shipped items | ~60% (manual recall) | ~95% (channel-scanned) |
| Format consistency across weeks | Low | High (templated) |
| Frequency | Ad-hoc, often skipped | Every Monday 9:00 AM IST |

## The Problem

Our release channel on Slack is where things actually get announced — engineers drop messages when a feature ships, when a hotfix goes out, when a partner-facing change goes live. It's fast, low-friction, and exactly where the source of truth lives day-to-day.

The problem is what happens *after*. Every Monday I used to:

1. Scroll back through the channel for the last 7 days
2. Pick out the actual release announcements from the noise (banter, deploy bot pings, threads)
3. Group them by squad / partner
4. Rewrite each one in partner-readable language
5. Paste it into a Confluence page nested under our release history space

Two hours. Every week. Zero net-new thinking.

Worse — the partner-facing release summaries (the ones shared with enterprise clients) were derived from that same Confluence page. Any miss compounded.

## The Solution

A Python script that:

1. **Pulls** all messages from the configured Slack release channel for the last 7 days using `conversations.history`
2. **Filters** out noise — bot pings, threads-only replies, non-release banter — using a Claude-powered classifier
3. **Groups** the surviving messages by squad / partner / area (using author, channel hints, and Claude classification)
4. **Summarises** each group with Claude into clean, human-readable release notes
5. **Publishes** the output as a new child page under a Confluence parent (e.g., "Release History → 2026 → May")
6. **Posts** a one-line "release notes are up" digest back to Slack with a link to the Confluence page
7. **Runs automatically** via GitHub Actions every Monday at 9 AM IST

The whole thing is ~300 lines of Python. The interesting design choices live in the classifier prompt and the grouping logic, not the plumbing.

## Architecture

```
┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐
│  Slack API   │ -> │ Claude          │ -> │ Claude          │ -> │ Confluence API │
│ (channel     │    │ (classify:      │    │ (summarise per  │    │ (publish page) │
│  history 7d) │    │  release? noise)│    │  group)         │    │                │
└──────────────┘    └─────────────────┘    └─────────────────┘    └────────────────┘
                                                                          │
                                                                          v
                                                                 ┌────────────────┐
                                                                 │ Slack webhook  │
                                                                 │ (link digest)  │
                                                                 └────────────────┘
```

## Tech Stack

- **Python 3.10+**
- **Slack Web API** — `conversations.history` for channel scan, `chat.postMessage` for digest
- **Claude API** (`claude-sonnet-4-6`) — for noise filtering + summarisation
- **Confluence REST API v2** — for publishing
- **GitHub Actions** — for scheduling

## Setup

### Prerequisites
- Python 3.10+
- A Slack app with `channels:history` and `chat:write` scopes installed in your workspace
- Confluence Cloud account with API token
- Anthropic API key

### Install
```bash
git clone https://github.com/<your-username>/automation-projects.git
cd automation-projects/projects/01-release-history-tracker
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configure
```bash
cp .env.example .env
# Fill in your tokens — never commit this file
```

### Run locally
```bash
python src/main.py --dry-run     # prints output without publishing
python src/main.py               # publishes to Confluence + posts Slack digest
```

### Automate
Push to your fork. The included GitHub Actions workflow (`.github/workflows/weekly-release.yml`) runs every Monday at 09:00 IST. Add your secrets under repo Settings → Secrets and variables → Actions.

## Sample Output

See [`examples/sample-release-notes.md`](./examples/sample-release-notes.md) for a redacted real-world output.

## Learnings

A few things I'd flag if you're building something similar:

- **Classify first, summarise second.** Asking Claude to "summarise the release-relevant messages" in one shot was unreliable — banter slipped through, real releases got dropped. Splitting into a classification pass (`release? yes/no`) followed by a summarisation pass on the survivors made the output stable.
- **Slack channel scrollback is messier than it looks.** Reactions, threaded replies, bot messages, edits — `conversations.history` returns all of it. Filter by `subtype is None` and skip messages with empty text before anything else.
- **Group deterministically when you can.** I tried having Claude both group and summarise. Inconsistent. Now: I group by Slack thread + author hint in Python, then summarise per group. Stable.
- **Dry-run mode is non-negotiable** when the destination is a partner-visible doc. The first time I skipped the dry-run, a half-rendered placeholder went out in the page title.
- **Cache the Slack response while iterating.** Saves API calls and makes the dev loop fast.

## What's Next

- Add a "blast radius" tag to each release item (internal / partner-affecting / customer-facing) so the partner-facing digest can be derived from the same source
- Pipe the output into the GenAI bug-reporting agent's context so it can correlate new bugs against recent releases
- Multi-locale summaries for partners who request English + regional language briefs

---

*Built and maintained by [Samarjit Roy](https://linkedin.com/in/samarjitroy).*
