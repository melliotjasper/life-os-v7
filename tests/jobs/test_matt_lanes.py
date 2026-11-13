"""Matt's lane policy (MEJ-215): US remote anywhere, or hybrid in the Seattle area; a $150K floor on posted pay; Jim's UK lanes and keep list are off;
a profile `flag` rule (Walmart, Disney) labels the Fit line and never excludes."""
from datetime import date, timedelta
import unittest

from lifeos.jobs import lanes
from lifeos.jobs.fit import exclusions
from lifeos.jobs.fit.profile import Profile

TODAY = date(2026, 11, 5)


def facts(location, text="", salary="", fit=80, posted=TODAY - timedelta(days=2), first_party=True):
    return lanes.facts_for(fit, "Head of Product", location, text, salary, posted, posted, first_party=first_party)


def decide(location, text="", salary="", **kw):
    decision, lane = lanes.decide("US Remote", facts(location, text, salary, **kw), TODAY)
    return decision.status, decision.reason, lane


class MattLane(unittest.TestCase):
    def test_policy(self):
        us = lanes.POLICIES["US Remote"]
        self.assertEqual((us.work_mode, us.pay_floor, us.max_age_days, us.enabled), ("remote_or_metro", 150_000, 30, True))
        self.assertFalse(lanes.POLICIES["Scale-Up"].enabled)
        self.assertFalse(lanes.POLICIES["Skilled Worker"].enabled)
        self.assertEqual((lanes.KEEP_LIST, lanes.KEEP_OVERRIDES_EXCLUSION), ((), ()))
        self.assertEqual(lanes.FIT_FLOOR, 72)

    def test_remote_us_is_admitted(self):
        self.assertEqual(decide("Remote - United States"), ("ADMIT", None, "US Remote"))
        self.assertEqual(decide("United States", "We are a remote-first company."), ("ADMIT", None, "US Remote"))

    def test_seattle_area_hybrid_is_admitted(self):
        for place in ("Seattle, WA", "Bellevue, WA", "Redmond, Washington", "Kirkland, WA (Hybrid)"):
            self.assertEqual(decide(place, "This is a hybrid role: three days a week in the office."), ("ADMIT", "Seattle-area hybrid", "US Remote"), place)

    def test_hybrid_or_onsite_elsewhere_is_excluded(self):
        status, reason, _ = decide("New York, NY", "This is a hybrid role: three days a week in the office.")
        self.assertEqual(status, "EXCLUDE")
        self.assertTrue(reason.startswith("not remote: hybrid required outside the Seattle area"), reason)
        self.assertEqual(lanes.public_reason(reason), "not_remote_hybrid_outside_metro")
        status, reason, _ = decide("Austin, TX", "This is an onsite role.")
        self.assertEqual((status, lanes.public_reason(reason)), ("EXCLUDE", "not_remote_onsite_outside_metro"))

    def test_fully_onsite_in_seattle_is_review(self):
        status, reason, _ = decide("Seattle, WA", "This is an onsite role.")
        self.assertEqual((status, reason, lanes.public_reason(reason)), ("REVIEW", "onsite in the Seattle area", "onsite_in_metro"))

    def test_pay_floor_is_150k_on_posted_pay_only(self):
        self.assertEqual(decide("Remote - US", salary="$120,000 - $140,000")[0], "EXCLUDE")
        self.assertEqual(decide("Remote - US", salary="$160,000 - $210,000")[0], "ADMIT")
        self.assertEqual(decide("Remote - US", salary="")[0], "ADMIT")

    def test_fit_floor_and_age(self):
        self.assertEqual(decide("Remote - US", fit=70)[0], "REVIEW")
        self.assertEqual(decide("Remote - US", fit=55)[0], "EXCLUDE")
        self.assertEqual(decide("Remote - US", posted=TODAY - timedelta(days=31))[0], "EXCLUDE")
        self.assertEqual(decide("Remote - US", posted=TODAY - timedelta(days=25))[0], "ADMIT")

    def test_uk_jobs_are_never_admitted(self):
        self.assertEqual(decide("London, UK", first_party=False)[0], "EXCLUDE")
        self.assertEqual(decide("Remote - United Kingdom", first_party=False)[0], "EXCLUDE")


class CultureFlag(unittest.TestCase):
    PROFILE = Profile({"capabilities": [{"id": "x", "class": "direct", "terms": ["roadmap"]}],
                       "exclusions": [{"id": "culture_walmart_disney", "reason": "Walmart/Disney culture", "flag": True, "where": "company",
                                       "patterns": [r"\bwalmart\b", r"\bdisney\b"]},
                                      {"id": "crypto", "reason": "crypto", "where": "any", "strict": True, "terms": ["cryptocurrency"]}]})

    def test_a_flag_rule_labels_and_never_excludes(self):
        self.assertEqual(exclusions.check("Head of Product", "Walmart Global Tech", "Own the roadmap. " * 40, self.PROFILE), (None, []))
        self.assertEqual(exclusions.flags("Head of Product", "The Walt Disney Company", self.PROFILE), ["Walmart/Disney culture"])
        self.assertEqual(exclusions.flags("Head of Product", "Chewy", self.PROFILE), [])

    def test_a_hard_rule_in_the_same_profile_still_excludes(self):
        hard, _ = exclusions.check("Head of Product", "Coinbase", "We build cryptocurrency products.", self.PROFILE)
        self.assertEqual(hard["id"], "crypto")

    def test_the_flag_reaches_the_fit_line(self):
        from lifeos.jobs.fit import score
        text = "Requirements\n" + "".join(f"- 5+ years of experience owning the product roadmap for item {i}\n" for i in range(10)) + "Own the roadmap. " * 30
        result = score.evaluate("Head of Product", "Walmart", text, self.PROFILE, TODAY)
        self.assertIn("Culture flag: Walmart/Disney culture", result.line)
        self.assertIsNone(result.exclusion)


if __name__ == "__main__":
    unittest.main()
