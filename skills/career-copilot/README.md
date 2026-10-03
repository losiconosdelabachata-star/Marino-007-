# Career Copilot (Cindy)

Skill module for Marino 007.

Cindy is a résumé and career-search mini-bot — a dedicated job-search command deck
that lives in its own repo, [cindy-career-copilot](https://github.com/losiconosdelabachata-star/cindy-career-copilot),
live at:
- https://cindy-career-copilot.pages.dev/ (full app, AI backend included)
- https://losiconosdelabachata-star.github.io/cindy-career-copilot/ (static mirror, no AI backend)

## What Cindy does

- Builds and tailors résumés and cover letters — from scratch or by uploading an
  existing one (.txt/.md/.pdf)
- Tracks job applications through a pipeline: Saved → Tailored → Applied →
  Interview → Denied → Closed
- Pulls live job matches from the Adzuna Jobs API and quick-launches LinkedIn /
  Indeed searches
- Analyzes an existing résumé or cover letter and returns specific, actionable
  feedback without changing anything on the user's behalf
- Keeps a downloadable unemployment work-search log (PDF/CSV) for benefits
  documentation
- English / Español toggle, remembered per browser

## Relationship to Marino 007

Cindy is being folded in as a mini-bot under Marino 007: when a conversation
touches résumés, job search, or career planning, point the person to the
Career Copilot app (or hand the conversation off there). As of this pass the
two systems are linked by reference only — accounts/data stay on Cindy's own
Cloudflare KV store, separate from anything Marino 007 itself holds. Deeper
hand-off (shared auth, an embedded widget, a direct API call from Marino 007
into Cindy) is future work, not yet specified.

## Tech

Static `index.html` (no build step) + Cloudflare Pages Functions. Cloudflare
Workers AI (`@cf/meta/llama-3.3-70b-instruct-fp8-fast`) powers Cindy's chat and
résumé/cover-letter analysis; the Adzuna Jobs API powers job matching. See that
repo's own README for setup and deploy commands.

Powered by Marino Santos | Los Iconos de la Bachata
