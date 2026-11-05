"""Matt's profile sorts his own love and reject examples (MEJ-247 interview guide, section 7). The profile is private (never committed): this test runs when
private/fit_profile.json or FIT_PROFILE_JSON is present and is skipped otherwise. The postings below are synthetic."""
from datetime import date
import json
import os
from pathlib import Path
import unittest

from lifeos.jobs import lanes
from lifeos.jobs.fit import score
from lifeos.jobs.fit.profile import Profile

TODAY = date(2026, 11, 5)
PRIVATE = Path(__file__).resolve().parents[3] / "private" / "fit_profile.json"
BOILER = "Join a creator-friendly team that ships products customers love. " * 6

LOVE = {
    "Head of Product, Marketplace": ("Faire", """About the role
We're hiring a Head of Product to own our two-sided marketplace and lead product strategy for brands and retailers.

What you'll do
- Own the product roadmap and prioritization across checkout, search and browse, and seller onboarding
- Lead discovery with customers and partners, and turn insights into product requirements
- Drive experimentation and A/B testing to improve conversion across the funnel
- Partner cross-functionally with engineering, design, marketing and sales leadership
- Own pricing and monetization for marketplace fees and advertising

Requirements
- 10+ years of product management experience in ecommerce or marketplaces
- Experience owning a P&L or revenue targets
- Track record of launching 0 to 1 products and scaling them
- Experience hiring and managing a team
- Strong executive communication
""" + BOILER),
    "Principal Product Manager, Checkout": ("Everlane", """About the role
We are seeking a Principal Product Manager to own checkout and the product detail page for our DTC ecommerce site.

Responsibilities
- Own the checkout roadmap on Shopify Plus and our headless commerce stack
- Run A/B tests with Optimizely and analyze results in GA4 and Looker
- Lead the replatforming of the PDP and cart to a headless build
- Work with payments partners (Stripe, PayPal, Klarna, Affirm)

Qualifications
- 8+ years of experience in ecommerce product management
- Experience with conversion rate optimization and experimentation
- Experience with Shopify Plus or Salesforce Commerce Cloud
- Cross-functional leadership with engineering and design
""" + BOILER),
    "Director of Product, Partnerships & Retail Media": ("Babylist", """About the role
Lead product for our partnerships and retail media business, serving brand partners and millions of parents building a registry.

What you'll do
- Own the roadmap for sponsored products, sampling and partner placements
- Set pricing, packaging and the rate card for retail media
- Build partner reporting and QBR tooling with ad operations
- Drive revenue growth and own revenue targets for the business unit

Requirements
- 8+ years in product management, partnerships or retail media
- Experience with ad operations tools such as Koddi
- Experience in ecommerce, baby or kids, or consumer goods
- Ability to influence without authority across cross-functional teams
""" + BOILER),
}

REJECT = {
    "Senior Software Engineer, Payments": ("Stripe", """About the role
We're hiring a Senior Software Engineer to build payments infrastructure.

Requirements
- 6+ years of hands-on software development in Java or Go
- Experience designing distributed systems and writing production code
- Experience with Kubernetes, Kafka and AWS
- Strong computer science fundamentals
""" + BOILER),
    "Senior Program Manager, Operations": ("Acme Retail", """About the role
We need a Senior Program Manager to run operational programs.

Requirements
- 8+ years of program management experience
- Experience managing schedules, risks and dependencies
- PMP certification required
""" + BOILER),
    "Head of Product, Exchange": ("CoinVault", """About the role
CoinVault is a cryptocurrency exchange. Lead product for our crypto trading app and blockchain wallet.

Requirements
- 10+ years of product management experience
- Experience with blockchain, DeFi and crypto trading
- Own the product roadmap
""" + BOILER),
}


def _profile():
    raw = os.environ.get("FIT_PROFILE_JSON") or (PRIVATE.read_text() if PRIVATE.exists() else "")
    return Profile(json.loads(raw)) if raw else None


@unittest.skipUnless(_profile(), "Matt's private profile is not present")
class MattSortsHisExamples(unittest.TestCase):
    def setUp(self):
        self.profile = _profile()

    def test_every_love_example_is_a_go(self):
        for title, (company, text) in LOVE.items():
            result = score.evaluate(title, company, text, self.profile, TODAY)
            self.assertEqual(result.decision, "Go", f"{title}: {result.score} {result.line} / {result.why}")
            self.assertGreaterEqual(result.score, lanes.FIT_FLOOR, title)

    def test_every_reject_example_is_a_no_go(self):
        for title, (company, text) in REJECT.items():
            result = score.evaluate(title, company, text, self.profile, TODAY)
            self.assertEqual(result.decision, "No-Go", f"{title}: {result.score} {result.line} / {result.why}")


if __name__ == "__main__":
    unittest.main()
