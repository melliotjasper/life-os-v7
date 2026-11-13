"""Matt's daily run, before any work: can the Notion connection read the Job Ledger (and the LinkedIn Connections page, when configured)?

    python -m lifeos.jobs.notion_preflight

Prints one line per target with a fixed code and, when something is wrong, what to do. Exit 1 when the Job Ledger is not usable (nothing could be
published), 0 otherwise; an unreadable LinkedIn page is reported and leaves the network steps off for the run (the workflow reads NETWORK_OK)."""
import os
import sys

from lifeos.jobs import ledger
from lifeos.platform.notion_client import Client, NotionError

FIX = ("In Notion, open the LIFE OS Jobs page, click ••• (top right) > Connections, and add the LIFE OS Jobs connection "
       "(docs/MATT_SETUP.md step 2). Then run the workflow again.")


def identity(client):
    """Who the token is (no secret): 'bot "LIFE OS Jobs" in workspace "Stride"', 'person', or the fixed error code."""
    try:
        me = client.call("GET", "/users/me")
    except NotionError as error:
        return str(error)
    if not isinstance(me, dict):
        return "unknown"
    if me.get("type") == "bot":
        bot = me.get("bot") or {}
        owner = (bot.get("owner") or {}).get("type") or "unknown"
        return f'bot "{me.get("name") or "?"}" in workspace "{bot.get("workspace_name") or "?"}" (owner: {owner})'
    return str(me.get("type") or "unknown")


def ledger_code(client):
    """The Job Ledger check with the HTTP code when the read itself fails (ledger.verify only says 'unreadable')."""
    try:
        client.call("GET", f"/data_sources/{client.source}")
    except NotionError as error:
        return f"{ledger.UNREADABLE} ({error})"
    return ledger.verify(client)


def check(environ=os.environ, client=None):
    """-> (ledger_code, network_code); each is 'ok' or a fixed failure code. network_code is None when no handoff page is configured."""
    try:
        client = client or Client(environ)
    except NotionError as error:
        return str(error), None
    target = ledger_code(client)
    page = (environ.get("NETWORK_HANDOFF_PAGE_ID") or "").strip().replace("-", "")
    if not page:
        return target, None
    try:
        client.call("GET", f"/blocks/{page}/children?page_size=1")
        network = "ok"
    except NotionError as error:
        network = str(error)
    return target, network


def main(environ=os.environ, client=None, out=sys.stdout):
    try:
        client = client or Client(environ)
    except NotionError:
        client = None
    target, network = check(environ, client) if client else ("NOTION_CONFIG_MISSING", None)
    lines = [f"notion-preflight: job_ledger={target}" + ("" if network is None else f" linkedin_page={network}"),
             f"notion-preflight: token is {identity(client) if client else 'not set'}"]
    if target.startswith(ledger.UNREADABLE) or target.startswith("NOTION_"):
        lines.append("::error::The Notion connection cannot read the Job Ledger. " + FIX)
    elif target == ledger.MISMATCH:
        lines.append("::error::NOTION_JOB_LEDGER_DATA_SOURCE_ID points at a database that is not the Job Ledger (a required column is missing or renamed).")
    if network not in (None, "ok"):
        lines.append("::warning::The Notion connection cannot read the LinkedIn Connections page, so referral matching is skipped this run. " + FIX)
    print("\n".join(lines), file=out)
    if environ.get("GITHUB_ENV"):
        with open(environ["GITHUB_ENV"], "a") as handle:
            handle.write(f"NETWORK_OK={'true' if network == 'ok' else 'false'}\n")
    return 0 if target == ledger.OK else 1          # an unreadable ledger reads "target_unreadable (NOTION_HTTP_404)"


if __name__ == "__main__":
    sys.exit(main())
