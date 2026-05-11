# Release Histroy Update

A growing collection of automation scripts and AI-powered tools I've built as a Product Manager to reduce manual work, improve consistency, and reclaim time for high-leverage thinking.

Each project lives in its own folder under `ProductToolkit/` with a self-contained README, code, setup instructions, and impact metrics.

A Python script that listens to release-confirmation messages in Slack and posts a structured weekly release log to a Confluence page.
The goal: stop hand-maintaining the release history. Devs and QA already confirm releases in Slack this tool treats those messages as the source of truth and writes the weekly summary to Confluence in a consistent format.

---

## Why this repo exists

Most PMs talk about leverage. I try to ship it.

These tools are built around the same operating principle: identify the recurring, low-cognitive, high-tax tasks in a PM's week release notes, status digests, partner follow-ups, backlog hygiene and replace them with scripts that run reliably while I focus on roadmap, partner conversations, and product strategy.

This tool help to update Confluence docs for the release done

---
## How It Works

┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│  Slack channel   │        │  Release History │        │  Confluence page │
│  (#releases)     │  ───►  │  Updater (Python)│  ───►  │  (weekly log)    │
│                  │        │                  │        │                  │
│  Dev + QA        │        │  Weekly cron     │        │  Date │ By │ ... │
│  confirmations   │        │                  │        │                  │
└──────────────────┘        └──────────────────┘        └──────────────────┘
   
## Flow

Slack as the source of truth. Devs post when a feature is pushed; QA replies confirming verification. The script reads the configured Slack channel and looks for messages matching the release-confirmation pattern (dev push + QA verified).
Weekly trigger. A scheduled job runs once a week and pulls all confirmed releases from the past 7 days.
Parse & normalise. Each confirmed release is parsed into a row with four fields:

Date — date the item was pushed
Pushed By — name of the person who shipped it
Item Released — feature / fix / ticket
Notes — context, QA sign-off, caveats


Write to Confluence. The script appends rows to the release history table on the configured Confluence page, preserving existing history and keeping the format consistent.

## Projects

| # | Project | Status | Time Saved | Stack |
|---|---|---|---|---|
| 01 | [Release History Tracker](./projects/01-release-history-tracker) | 🟢 Live | ~2 hrs/week | Python, Slack API, Claude API, Confluence API |

More coming soon.

---

## About me

I'm Samarjit Roy — Product Manager (AI & Platform) at Gamezop, a B2B gaming platform powering partners like Microsoft, YouTube, Samsung, and Amazon. I focus on AI/ML product work, platform integrations, and revenue analytics.

- LinkedIn: [linkedin.com/in/samarjitroy](https://linkedin.com/in/samarjitroy)
- Email: samarjitroy30@gmail.com

---

## License

[MIT](./LICENSE) — feel free to fork, learn from, or adapt any of these for your own workflows.
