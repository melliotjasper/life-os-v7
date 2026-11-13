"""Jim's lane policy as it stood before the Matt fork (MEJ-215), for the tests that still exercise those mechanisms (the UK lanes, the US remote-only
rule, the D115 keep list). `setUpModule = install` / `tearDownModule = uninstall` in a test module swaps them into lifeos.jobs.lanes for that module only."""
from dataclasses import replace

from lifeos.jobs import lanes

_MATT = dict(lanes.POLICIES)
JIM = {**_MATT,
       "US Remote": replace(_MATT["US Remote"], work_mode="remote_only", metro=None, pay_floor=75_000, max_age_days=14),
       "Scale-Up": replace(_MATT["Scale-Up"], enabled=True),
       "Skilled Worker": replace(_MATT["Skilled Worker"], enabled=True)}
KEEP_LIST = (
    ("revolut", r"^product designer \(platform\)$"),
    ("revolut", r"^partnerships manager \(lifestyle\)$"),
    ("revolut", r"^operations manager \(revenue\)$"),
    ("revolut", r"^product owner\s*[(\-–,:]*\s*technical\b"),
    ("revolut", r"^product owner\s*[(\-–,:]*\s*(?:ux|user experience)\b"),
    ("revolut", r"^credit manager\b.*\bproduct\b"),
)
KEEP_OVERRIDES_EXCLUSION = (("revolut", r"^credit manager\b.*\bproduct\b"),)
_saved = {}


def install():
    _saved.update(policies=dict(lanes.POLICIES), keep=lanes.KEEP_LIST, overrides=lanes.KEEP_OVERRIDES_EXCLUSION)
    lanes.POLICIES.clear()
    lanes.POLICIES.update(JIM)
    lanes.KEEP_LIST, lanes.KEEP_OVERRIDES_EXCLUSION = KEEP_LIST, KEEP_OVERRIDES_EXCLUSION


def uninstall():
    lanes.POLICIES.clear()
    lanes.POLICIES.update(_saved["policies"])
    lanes.KEEP_LIST, lanes.KEEP_OVERRIDES_EXCLUSION = _saved["keep"], _saved["overrides"]
