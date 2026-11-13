# LIFE OS Jobs — Matt's setup and operating guide

Jira: MEJ-215 (fork Jim's job-search system), MEJ-247 (career profile), MEJ-244 (LinkedIn connections).

## What runs

One GitHub Actions workflow, `.github/workflows/matt-daily.yml`, once a day (6:13 AM Pacific in winter, 7:13 AM in summer) and on demand:

1. **Find jobs.**
   - **Employer job boards:** about 10,700 public Greenhouse, Lever and Ashby boards. Your 30 target employers (`extras` in `lifeos/sources/web/boards.json`) are read every day. Boards never read before are read 1,350 a day until all have been read once (about 8 days); after that, a board is re-read daily if it lists a role that fits.
   - **LinkedIn's public job search:** your titles (`QUERIES` in `lifeos/sources/linkedin_search.py`), US, last 24 hours. Optional.
   - **Gmail alert emails:** LinkedIn and Jobright alerts, once Gmail is connected (step 6).
2. **Screen cheaply.** Titles that are clearly another profession, non-US places, and hybrid/onsite roles outside the Seattle area are dropped before any reading.
3. **Read** each remaining job's full description from the employer's own page.
4. **Score Fit (0-100)** against your profile: requirements are matched against your evidence, not just the title. **72 or higher is a Go.**
5. **Apply your lane rules** (`POLICIES["US Remote"]` in `lifeos/jobs/lanes.py`):
   - US remote anywhere, or hybrid in the Seattle area (Seattle, Bellevue, Redmond, Kirkland, Bothell, Renton, Issaquah, Tacoma and nearby).
   - A fully onsite Seattle role goes to **Review**; hybrid or onsite anywhere else is excluded.
   - A posted base salary under **$150K** is excluded. No posted pay is not a reason.
   - Posted within **30 days**.
   - Fit 72+ is **Admitted**, 60-71 is **Passed / Review**, under 60 is excluded.
6. **Hard rejects** (your profile): crypto, blockchain, NFT and web3; gambling and betting; cannabis and CBD; liquor and spirits brands. Also Program/Project Manager titles (a late-search fallback only), design roles, and any title that isn't a product role. The generic rules still reject security clearance, federal/DoD, clinical professions and hospital employers. Healthcare and digital-health product roles are **in scope**.
7. **Culture flag:** Walmart and Disney roles are not rejected. Their "Why It Fits" line ends with "Culture flag: Walmart/Disney culture", so you decide.
8. **Publish** Admitted and Review jobs to the Notion **Job Ledger**, with the score, strengths and gaps ("Why It Fits"), and the full description on the page.
9. **Referral paths:** once your LinkedIn export is on the "LinkedIn Connections" page, each admitted job's page gets a "Network Leads" block listing the people you know who currently or previously list that employer.

The job store is a MariaDB database that lives only inside the run. At the end of each run it is saved to the repository's `state` branch, compressed and **encrypted** (AES-256) with your `STATE_KEY` secret, and restored at the start of the next run.

**This repository is public.** It's a fork, and GitHub doesn't let a fork be made private. So:
- The saved store is unreadable without `STATE_KEY`.
- Your fit profile and all tokens live only in GitHub secrets.
- The run logs (public) print counts only, never job titles, companies or names.
- What anyone *can* see is the code and docs: your lane rules ($150K floor, remote or Seattle hybrid), your target-company list in `boards.json`, and the Notion page IDs below (useless without your Notion token).

To keep even that private, create a new **private** repository (not a fork, e.g. `melliotjasper/life-os-jobs`), push this branch to it, and add the same secrets there. Private repos get 2,000 free Actions minutes a month; a daily run takes about 25-45 minutes.

## Notion (already created)

All three pages are in your "Stride" workspace:
- **LIFE OS Jobs** (page): https://app.notion.com/p/40f0fdd9acb6818494addb06a32e01df
- **Job Ledger** (database): https://app.notion.com/p/92f4ead8c9294527818eabd39810e0d3 (data source id `783ede0c-615c-466f-971a-d6936d5ac7c6`)
- **LinkedIn Connections** (page, id `40f0fdd9acb68172838cc9de8c0fdbd9`): drop Connections.csv here

The run writes only the machine columns. **Applied**, **Applied On** and **My Decision** are yours: a page with any of them set is never trashed or changed.

## One-time setup

1. **Make up a store passphrase.** Use a password manager to generate a random passphrase of 30+ characters, and keep a copy there. If it's lost, the next run can't read the saved store: delete the `state` branch and the system starts over with an empty store (your Notion pages are kept).
2. **Create the Notion integration.**
   - Go to https://www.notion.so/profile/integrations and choose New integration: name "LIFE OS Jobs", workspace Stride, type Internal.
   - Capabilities: Read content, Update content, Insert content. Save, then copy the **Internal Integration Secret**.
   - In Notion, open the **LIFE OS Jobs** page, then ••• > Connections > add "LIFE OS Jobs". Its two child pages inherit access.
3. **Add the GitHub secrets:** Settings > Secrets and variables > Actions > New repository secret.

   | Secret | Value |
   |---|---|
   | `FIT_PROFILE_JSON` | the whole JSON from the Notion page "Fit Profile (private)" under LIFE OS Jobs |
   | `STATE_KEY` | the passphrase from step 1 |
   | `NOTION_API_TOKEN` | the integration secret from step 2 |
   | `NOTION_JOB_LEDGER_DATA_SOURCE_ID` | `783ede0c-615c-466f-971a-d6936d5ac7c6` |
   | `NETWORK_HANDOFF_PAGE_ID` | `40f0fdd9acb68172838cc9de8c0fdbd9` |
4. **Merge the pull request into `main`.** GitHub runs schedules only from the default branch.
5. **First run:** Actions > matt-daily > Run workflow (Live ticked). The run summary shows the counts. Jobs appear in the Job Ledger.
6. **Gmail alerts (optional).**
   - In Google Cloud Console: create a project, enable the Gmail API, and set up the OAuth consent screen (External, add yourself as a test user).
   - Create an OAuth client ID (type Desktop app).
   - Get a refresh token with the `https://www.googleapis.com/auth/gmail.modify` scope. For example, in the OAuth 2.0 Playground, use your own client ID and secret.
   - Add secrets `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET` and `GMAIL_OAUTH_REFRESH_TOKEN`.
   - Set up LinkedIn job alerts for your titles, delivered by email. The run moves those emails out of the inbox into a "J Newsletters" label, then reads the jobs in them.
7. **LinkedIn connections (MEJ-244):** LinkedIn > Settings > Data privacy > Get a copy of your data > Connections. When the email arrives, download Connections.csv and drop it onto the "LinkedIn Connections" Notion page. Only names, companies and titles are read; email addresses never are. To refresh, attach a newer export.

## Tuning

| To change | Edit |
|---|---|
| Profile evidence, titles, rejects, culture flags | the profile JSON: update the Notion copy, then the `FIT_PROFILE_JSON` secret. A changed profile re-scores every job automatically. |
| Pay floor, posting age, Seattle-area towns | `POLICIES["US Remote"]` and `SEATTLE_METRO` in `lifeos/jobs/lanes.py` (bump `POLICY_VERSION` so stored jobs are re-judged) |
| Target employers read every day | `extras` in `lifeos/sources/web/boards.json` (`{"kind": "greenhouse" or "lever" or "ashby", "slug": ..., "company": ...}`) |
| LinkedIn search titles | `QUERIES` in `lifeos/sources/linkedin_search.py` |
| Run time | the `cron` line in `.github/workflows/matt-daily.yml` (UTC) |

Profile shape: `lifeos/jobs/fit/profile.py`. Scoring model: `docs/FIT_MODEL.md`. A profile exclusion with `"flag": true` labels a job instead of rejecting it.

## Known limits

- Recall depends on the profile's term lists: a requirement your profile does not name counts as a gap. Review a week of Ledger results and adjust the terms.
- Pay is judged only when the posting states it.
- Indeed alerts are not parsed (Jim's system never read them). LinkedIn, Jobright and the employer boards are.
- LinkedIn's public search may refuse GitHub's servers on some days. That step then fails alone; the rest of the run continues.
