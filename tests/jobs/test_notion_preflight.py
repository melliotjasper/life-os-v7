"""The daily run's Notion pre-check: a connection that cannot read the Job Ledger stops publishing with a clear message instead of a silent no-op."""
import io
import os
import tempfile
import unittest

from lifeos.jobs import ledger
from lifeos.jobs import notion_preflight
from lifeos.platform.notion_client import NotionError

LEDGER_PROPS = {name: {"type": kind} for name, kind in ledger.REQUIRED.items()}
ENV = {"NOTION_API_TOKEN": "t", "NOTION_JOB_LEDGER_DATA_SOURCE_ID": "783ede0c-615c-466f-971a-d6936d5ac7c6",
       "NETWORK_HANDOFF_PAGE_ID": "40f0fdd9acb68172838cc9de8c0fdbd9"}


class Fake:
    def __init__(self, ledger_ok=True, page_ok=True, props=None):
        self.ledger_ok, self.page_ok, self.props = ledger_ok, page_ok, props or LEDGER_PROPS
        self.source = ENV["NOTION_JOB_LEDGER_DATA_SOURCE_ID"]

    def call(self, method, path, body=None):
        if path.startswith("/data_sources/"):
            if not self.ledger_ok:
                raise NotionError("NOTION_HTTP_404")
            return {"properties": self.props}
        if path.startswith("/blocks/"):
            if not self.page_ok:
                raise NotionError("NOTION_HTTP_404")
            return {"results": [], "has_more": False}
        raise AssertionError(path)


def run(fake, env=ENV):
    out = io.StringIO()
    with tempfile.NamedTemporaryFile("r+", delete=False) as handle:
        path = handle.name
    try:
        code = notion_preflight.main({**env, "GITHUB_ENV": path}, fake, out)
        written = open(path).read()
    finally:
        os.unlink(path)
    return code, out.getvalue(), written


class Preflight(unittest.TestCase):
    def test_both_readable(self):
        code, text, env = run(Fake())
        self.assertEqual(code, 0)
        self.assertIn("job_ledger=ok linkedin_page=ok", text)
        self.assertIn("NETWORK_OK=true", env)

    def test_an_unconnected_ledger_fails_with_the_fix(self):
        code, text, env = run(Fake(ledger_ok=False, page_ok=False))
        self.assertEqual(code, 1)
        self.assertIn("job_ledger=target_unreadable", text)
        self.assertIn("::error::", text)
        self.assertIn("Connections", text)
        self.assertIn("NETWORK_OK=false", env)

    def test_a_wrong_database_is_a_mismatch(self):
        props = dict(LEDGER_PROPS)
        props.pop("My Decision")
        code, text, _ = run(Fake(props=props))
        self.assertEqual(code, 1)
        self.assertIn("job_ledger=target_mismatch", text)

    def test_an_unreadable_linkedin_page_only_warns(self):
        code, text, env = run(Fake(page_ok=False))
        self.assertEqual(code, 0)
        self.assertIn("linkedin_page=NOTION_HTTP_404", text)
        self.assertIn("::warning::", text)
        self.assertIn("NETWORK_OK=false", env)

    def test_no_handoff_page_configured(self):
        env = {k: v for k, v in ENV.items() if k != "NETWORK_HANDOFF_PAGE_ID"}
        code, text, written = run(Fake(), env)
        self.assertEqual(code, 0)
        self.assertNotIn("linkedin_page", text)
        self.assertIn("NETWORK_OK=false", written)


if __name__ == "__main__":
    unittest.main()
