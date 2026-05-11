# Release Notes — Week of 04 May 2026

## recommendation-engine

This week's changes focused on improving cold-start behaviour and reducing the model's bias toward over-served titles.

- Tuned exploration rate in the contextual bandit to surface long-tail games more often
- Added a fallback ranker for users with fewer than 5 sessions
- Fixed a logging regression that was under-reporting click-through events

## microsoft-integration

Partner-facing changes for the Microsoft surface.

- Resolved a layout shift on the Microsoft Edge new-tab embed
- Added partner-attribution headers to outgoing analytics events

## genai-bug-agent

- Added structured severity classification (P0 → P3) to natural-language reports
- Reduced false-positive duplicate detection by tightening the embedding similarity threshold

## catalogue

- Added 8 new HTML5 games to the catalogue
- Deprecated 3 underperforming titles flagged by the engagement dashboard
