# LIFE OS Jobs (Matt's fork) — Claude Code entrypoint

This repository is **Matt Jasper's** copy of Jim Markunas's LIFE OS V7 job-search system, retargeted to Matt (Jira MEJ-215). It does one thing: find jobs, score them against Matt's career profile, publish the good ones to Matt's Notion Job Ledger, and show LinkedIn referral paths.

Start here:
- [docs/MATT_SETUP.md](docs/MATT_SETUP.md): how it runs, the one-time setup (secrets, Notion, Gmail), and how to tune it.
- `.github/workflows/matt-daily.yml`: the only scheduled workflow (daily, 6:13 AM Pacific in winter, 7:13 AM in summer). `.github/workflows/tests.yml` runs the unit tests on every push.
- Matt's tuning lives in a few places: `lifeos/jobs/lanes.py` (`POLICIES["US Remote"]`: remote or Seattle-area hybrid, $150K floor, 30 days), the private fit profile (GitHub secret `FIT_PROFILE_JSON`; never commit it), `lifeos/sources/web/boards.json` `extras` (target employers read every day), and `lifeos/sources/linkedin_search.py` `QUERIES`.

Rules for agents working here:
- **Matt is the owner.** Show times in Pacific Time (Seattle). Jim's LIFE/LOS Jira process, Buzz, OpenClaw, Oracle, Hostinger and Bitwarden do not apply to this fork; `AGENTS.md` and `docs/life-os-development-policy.md` are Jim's upstream governance, kept as reference only.
- Jim's other domains (bills, Amazon, mail, calendar, interview OS, recruiters, MegIBOW, Jira cards) are still in the code but are **not run**: their workflows are parked in `.github/jim-workflows/`, which GitHub never executes. Don't move a file back into `.github/workflows/` unless Matt asks.
- **Never commit personal data**: the fit profile, LinkedIn connections, job-store dumps (they live on the `state` branch only, encrypted with the STATE_KEY secret; this repo is a public fork), tokens. `private/` is git-ignored for local copies.
- Run `python -m unittest discover -s tests -t .` before pushing. Tests that exercise Jim's lane rules use `tests/kit/jim_lanes.py`; Matt's own rules are in `tests/jobs/test_matt_lanes.py` and `tests/jobs/fit/test_matt_profile.py` (the latter runs only when the private profile is present).
- Develop on a branch and open a pull request; don't push to `main` directly unless Matt says so.
