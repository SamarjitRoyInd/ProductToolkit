# Setup Guide

Step-by-step setup for the two integrations that aren't obvious: the Slack app and the Confluence parent page.

---

## 1. Create the Slack app

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Name it something like `Release Notes Bot`, pick your workspace, **Create App**
3. In the left sidebar → **OAuth & Permissions** → scroll to **Scopes** → **Bot Token Scopes** → add:
   - `channels:history` (read messages from public channels)
   - `groups:history` (read messages from private channels — needed if your release channel is private)
   - `chat:write` (post the digest message)
4. Scroll back up → **Install to Workspace** → authorise
5. Copy the **Bot User OAuth Token** (starts with `xoxb-`) → that's your `SLACK_BOT_TOKEN`
6. In Slack, invite the bot to your release channel: `/invite @Release Notes Bot`
7. Get the channel ID: right-click the channel → **Copy link** → the ID is the last path segment (starts with `C`)

## 2. Set up Confluence

1. Generate an API token: [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens) → **Create API token**
2. Create a parent page where weekly notes will be nested — e.g., `Release History / 2026`
3. Get the parent page ID: open the page, look at the URL: `/wiki/spaces/REL/pages/123456789/2026` → the ID is `123456789`
4. Note the space key from the URL too (the bit after `/spaces/`) — e.g., `REL`

## 3. Anthropic API key

Get one from [console.anthropic.com](https://console.anthropic.com/) → that's `ANTHROPIC_API_KEY`.

## 4. Local dry-run

```bash
cd projects/01-release-history-tracker
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with all the values above
python src/main.py --dry-run
```

If the dry-run prints sensible output, you're good. Then drop `--dry-run` for the real publish.

## 5. Schedule it on GitHub Actions

1. Push the repo to GitHub
2. In the repo → **Settings → Secrets and variables → Actions** → add every variable from `.env.example` as a secret with the same name
3. The workflow at `.github/workflows/weekly-release.yml` will run automatically every Monday at 09:00 IST
4. You can also trigger it manually from the **Actions** tab while testing

---

## Troubleshooting

- **`not_in_channel` from Slack:** the bot isn't in the release channel. `/invite @your-bot` in that channel.
- **`channel_not_found`:** you used the channel name instead of the ID. Need the `C0...` ID.
- **Classifier returns nothing useful:** check your `--dry-run` raw output. If the channel is very noisy, tighten the prompt in `classify_release_messages()` with concrete examples of what counts as a release at your company.
- **Confluence 403:** the API token needs to belong to a user with edit access to the parent page's space.
