## No-Code Path: Run It via Claude in Chrome

Don't want to set up Python, tokens, or cron? You can run the same release-history workflow manually using the **Claude extension for Chrome** — no install, no scripts, no scheduler.

This guide gives you a single prompt to paste into Claude in Chrome. Claude will then drive the browser: search Slack, walk through every result, extract Jira links, and hand you back a clean table you can paste into Confluence.

---

## When to Use This vs. the Python Script

| | Python script | Claude in Chrome |
|---|---|---|
| **Setup time** | One-time setup with tokens, cron, env vars | Zero — just install the extension |
| **Recurring use** | Runs itself every week | You run it on demand |
| **Best for** | Long-term, hands-off automation | One-off pulls, ad-hoc audits, "show me last week" |
| **Where output lands** | Directly on the Confluence page | A table in chat — you paste it where you want |

If you only need the release history once a quarter or want to spot-check before a stakeholder review, the Chrome path is faster than getting the script running.

---

## Prerequisites

1. **Chrome browser** — desktop, signed in
2. **Claude extension for Chrome** — installed and signed in
3. **Slack open in a tab** — logged into the Gamezop workspace, with access to `#proj-gamezop-enterprise`
4. **A scratchpad** for the final table — Confluence draft, Google Doc, or Notion page

---

## How to Run It

1. Open Slack in a Chrome tab and make sure you're on the workspace home (not a DM, not buried in a thread).
2. Open the Claude side panel from the extension icon.
3. Paste the prompt below into Claude.
4. Watch it work — Claude will narrate each step. Don't click around in the Slack tab while it's running; you'll throw off the automation.
5. When Claude returns the final table, copy it into your Confluence release history page.

---

## The Prompt

Paste this exactly into Claude in Chrome:

```
Search the #channel-name Slack channel for messages containing
"This is merged" or "pushed to Prod" posted after DATE. For each
search result found:

1. Execute search in Slack using the query:
   "This is merged in:#channel-name after:date"
2. Set sort order to "Newest".
3. Apply filter: "date" using the Filters panel
   (do NOT press Enter in filter fields — wait for autocomplete
   and click the suggestion).
4. For each search result displayed:
   - Click on the result to open its thread in the right panel.
   - Scroll UP in the thread panel to find the parent message.
   - Look for Jira ticket links
     (format: jira link/GAMEZ-XXXX).
   - Record: Poster name, Date/time of message, Slack thread link,
     and all Jira links found.
   - If clicking on @username tags opens a profile popup, press
     Escape and click on non-tagged message text instead.
5. Navigate through all pages of results
   (typically 5+ pages with ~127 results).
6. After completing "This is merged" search, repeat the entire
   process with query:
   "pushed to Prod in:#proj-gamezop-enterprise after:2026-04-01"
7. Compile all results into a table with columns:
   # | Poster | Date | Jira Link(s)
8. Include entries with "No Jira found" if applicable.

Key notes (from previous runs):
- Do NOT type search in DM field — use the main search bar at top.
- Use autocomplete dropdown to confirm search scope; don't just press Enter.
- Click message text area, not user avatars or @mentions, to open threads.
- Close any profile popups with Escape key before proceeding.
- Pagination buttons appear at bottom of results — use to navigate
  between pages.
```

Tweak the date ranges before pasting if you're running for a different window.

---

## What You Get Back

A markdown table like:

| # | Poster | Date | Jira Link(s) |
|---|---|---|---|
| 1 | Aman | 2026-05-08 | jira link/GAMEZ-2341 |
| 2 | Priya | 2026-05-07 | GAMEZ-2338, GAMEZ-2340 |
| 3 | Rohit | 2026-05-06 | No Jira found |

Copy it directly into the Confluence release history page. You'll still need to add the `Item Released` and `Notes` columns from context, but the date / author / Jira link spine is done.

---

## Tips for Smooth Runs

- **Don't touch Slack while it's working.** Clicks, scrolls, or tab switches will derail the automation.
- **Sessions can be long.** ~127 results across two searches means 250+ clicks. Expect 10–20 minutes. Leave the tab alone.
- **If Claude gets stuck on a profile popup,** tell it "press Escape and continue" — that's the most common snag.
- **Pause and resume.** If you need to stop mid-run, ask Claude to "give me the partial table so far" before closing the panel.
- **Verify a few rows.** Spot-check 2–3 entries against Slack manually before pasting into Confluence. The automation is reliable, not infallible.

---

## Known Limitations

- **Manual trigger only.** No scheduling — you run it when you need it.
- **One workspace, one run.** Can't run two queries in parallel.
- **Slack UI changes can break it.** If Slack ships a redesign, the click targets in the prompt (Filters panel, sort dropdown, pagination buttons) may need tweaking. Update the prompt and re-run.
- **Long sessions can hit Slack rate limits** on rapid clicks. If results stop loading, wait 30s and ask Claude to resume.

---

## When to Graduate to the Python Script

If you find yourself running this prompt more than once a month, switch to the Python version. The setup is a one-evening investment and you stop spending 15 minutes a week babysitting a browser.
