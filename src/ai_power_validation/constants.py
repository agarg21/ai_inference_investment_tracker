from __future__ import annotations

from dataclasses import dataclass

EVENT_TYPES = (
    "signed_large_load_contract",
    "tariff_or_special_rate_approval",
    "pipeline_mw_increase",
    "transmission_or_interconnection_approval",
    "behind_the_meter_or_self_generation",
    "regulatory_delay_or_pushback",
)

SIGNAL_VARIANTS = (
    "approved_tariff_with_minimums",
    "approved_infrastructure_incentive",
    "company_load_forecast",
    "contracted_load_backlog",
    "customer_savings_framework",
    "early_pipeline_signal",
    "named_large_load_contract",
    "pipeline_capacity_expansion",
    "proposed_rate_design",
    "regional_grid_readthrough",
    "transmission_capex_growth",
)

SIGNAL_TIER_BY_VARIANT = {
    "approved_tariff_with_minimums": "high",
    "approved_infrastructure_incentive": "medium",
    "company_load_forecast": "medium",
    "contracted_load_backlog": "high",
    "customer_savings_framework": "medium",
    "early_pipeline_signal": "medium",
    "named_large_load_contract": "high",
    "pipeline_capacity_expansion": "high",
    "proposed_rate_design": "low",
    "regional_grid_readthrough": "low",
    "transmission_capex_growth": "high",
}

PRIMARY_TICKERS = ("AEP", "FE", "ETR", "BKH", "PNW", "POR", "IDA")
BENCHMARK_TICKERS = ("XLU", "SPY")
FORWARD_HORIZONS = (1, 5, 20, 60)


@dataclass(frozen=True)
class Issuer:
    ticker: str
    name: str
    cik: str
    region: str


ISSUERS = (
    Issuer("AEP", "American Electric Power Company, Inc.", "0000004904", "PJM"),
    Issuer("FE", "FirstEnergy Corp.", "0001031296", "PJM"),
    Issuer("ETR", "Entergy Corporation", "0000065984", "MISO"),
    Issuer("BKH", "Black Hills Corporation", "0001130464", "SPP"),
    Issuer("PNW", "Pinnacle West Capital Corporation", "0000764622", "AZ"),
    Issuer("POR", "Portland General Electric Company", "0000784977", "OR"),
    Issuer("IDA", "IDACORP, Inc.", "0001057877", "ID"),
)

ISSUER_BY_TICKER = {issuer.ticker: issuer for issuer in ISSUERS}
ISSUER_BY_CIK = {issuer.cik: issuer for issuer in ISSUERS}

SOURCE_KEYWORDS = (
    "data center",
    "ai load",
    "large load",
    "megawatt",
    "mw",
    "load growth",
    "hyperscale",
    "special contract",
    "tariff",
    "take-or-pay",
    "cost recovery",
    "interconnection",
    "transmission",
    "behind-the-meter",
)

SEC_FORMS = {"10-K", "10-Q", "8-K"}
SEC_FORM_LIMITS = {"10-K": 2, "10-Q": 4, "8-K": 6}

SEED_DOCUMENTS = (
    {
        "source_type": "pjm",
        "issuer_or_region": "PJM",
        "title": "PJM 2025 Year in Review: Planning Prepares for Burgeoning Electricity Demand",
        "url": "https://insidelines.pjm.com/2025-year-in-review-planning-prepares-for-burgeoning-electricity-demand/",
        "publish_timestamp": "2026-01-08T00:00:00-05:00",
    },
    {
        "source_type": "ercot",
        "issuer_or_region": "ERCOT",
        "title": "ERCOT Announces Strategic Progress in Planning and Managing Large Loads",
        "url": "https://www.ercot.com/news/release/12122025-ercot-announces-strategic",
        "publish_timestamp": "2025-12-12T00:00:00-06:00",
    },
    {
        "source_type": "ercot",
        "issuer_or_region": "ERCOT",
        "title": "Large Load Interconnection Process Q&A",
        "url": "https://www.ercot.com/files/docs/2025/12/24/Large-Load-Interconnection-Process-Q-A.pdf",
        "publish_timestamp": "2025-12-24T00:00:00-06:00",
    },
    {
        "source_type": "eia",
        "issuer_or_region": "US",
        "title": "EIA Forecasts U.S. Power Consumption Will Reach Record Highs in 2025 and 2026",
        "url": "https://www.eia.gov/pressroom/releases/press582.php",
        "publish_timestamp": "2026-01-13T00:00:00-05:00",
    },
    {
        "source_type": "ferc",
        "issuer_or_region": "FERC",
        "title": "FERC Company Identifier Listing",
        "url": "https://data.ferc.gov/company-registration/ferc-company-identifier-listing/",
        "publish_timestamp": "2026-03-01T16:11:00-05:00",
    },
)

ISSUER_SEED_DOCUMENTS = (
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "AEP",
        "title": "AEP Ohio Proposal on Data Centers to Protect Ohio Consumers Adopted by PUCO",
        "url": "https://www.aep.com/news/stories/view/10327/",
        "publish_timestamp": "2025-07-31T00:00:00-04:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "AEP",
        "title": "AEP 1Q25 Earnings Release Presentation",
        "url": "https://docs.aep.com/docs/newsroom/resources/earnings/2025-05/1Q25EarningsReleasePresentation.pdf",
        "publish_timestamp": "2025-05-06T00:00:00-04:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "AEP",
        "title": "AEP 3Q25 Earnings Release Presentation",
        "url": "https://docs.aep.com/docs/newsroom/resources/earnings/2025-10/3Q25EarningsReleasePresentation.pdf",
        "publish_timestamp": "2025-10-30T00:00:00-04:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "AEP",
        "title": "AEP 4Q25 Earnings Release Presentation",
        "url": "https://docs.aep.com/docs/newsroom/resources/earnings/2026-02/4Q25EarningsReleasePresentation.pdf",
        "publish_timestamp": "2026-02-13T00:00:00-05:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "FE",
        "title": "FirstEnergy 3Q24 Highlights",
        "url": "https://investors.firstenergycorp.com/files/doc_financials/2024/q3/3Q24_FE-Highlights.pdf",
        "publish_timestamp": "2024-10-30T00:00:00-04:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "FE",
        "title": "FirstEnergy Transmission and Transource Energy Joint Venture Receive Approval for Major Electric Transmission Project in Central Ohio",
        "url": "https://investors.firstenergycorp.com/investor-materials/news-releases/news-details/2026/FirstEnergy-Transmission-and-Transource-Energy-Joint-Venture-Receive-Approval-for-Major-Electric-Transmission-Project-in-Central-Ohio/default.aspx",
        "publish_timestamp": "2026-02-16T09:00:00-05:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "FE",
        "title": "FirstEnergy Transmission Awarded Projects by PJM Interconnection to Enhance Reliability and Address Rising Customer Demand",
        "url": "https://investors.firstenergycorp.com/investor-materials/news-releases/news-details/2026/FirstEnergy-Transmission-Awarded-Projects-by-PJM-Interconnection-to-Enhance-Reliability-and-Address-Rising-Customer-Demand/default.aspx",
        "publish_timestamp": "2026-03-02T11:22:00-05:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "FE",
        "title": "FirstEnergy Announces Third Quarter 2025 Financial Results",
        "url": "https://investors.firstenergycorp.com/investor-materials/news-releases/news-details/2025/FirstEnergy-Announces-Third-Quarter-2025-Financial-Results/default.aspx",
        "publish_timestamp": "2025-10-29T00:00:00-04:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "ETR",
        "title": "Meta Selects Entergy, Northeast Louisiana as Site of $10B Data Center",
        "url": "https://www.entergy.com/news/meta-selects-northeast-louisiana-as-site-10-billion-data-center",
        "publish_timestamp": "2024-12-05T00:00:00-06:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "ETR",
        "title": "Entergy Arkansas Powers Google's $4B Investment in the State",
        "url": "https://www.entergy.com/news/entergy-arkansas-powers-googles-4b-investment-in-the-state",
        "publish_timestamp": "2025-10-02T00:00:00-05:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "ETR",
        "title": "Regulatory Approval Gives Entergy Louisiana Green Light for Major Infrastructure Investments to Support Meta Data Center in Richland Parish",
        "url": "https://www.entergy.com/news/regulatory-approval-gives-entergy-louisiana-green-light-major-infrastructure-investments-support-meta-data-center-richland-parish",
        "publish_timestamp": "2025-08-20T00:00:00-05:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "ETR",
        "title": "Entergy 3Q25 Earnings Call Presentation",
        "url": "https://s201.q4cdn.com/714390239/files/doc_financials/2025/q3/3Q25-Presentation.pdf",
        "publish_timestamp": "2025-10-29T00:00:00-05:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "ETR",
        "title": "Hut 8 Selects Entergy Southeast Louisiana for $10 Billion AI Data Center",
        "url": "https://www.entergy.com/news/hut-8-selects-entergy-southeast-louisiana-for-10-billion-artificial-intelligence-data-center",
        "publish_timestamp": "2025-12-17T00:00:00-06:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "ETR",
        "title": "Entergy Announces $5B in Customer Savings Delivered by Data Center Agreements",
        "url": "https://www.entergy.com/news/5b-in-customer-savings-delivered-by-data-center-agreements-issues-fair-share-plus-pledge",
        "publish_timestamp": "2026-03-05T00:00:00-06:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "BKH",
        "title": "Black Hills Corp. to Power Meta's New Data Center in Wyoming with Innovative Energy Solution",
        "url": "https://ir.blackhillscorp.com/news-releases/news-release-details/black-hills-corp-power-metas-new-data-center-wyoming-innovative/",
        "publish_timestamp": "2024-07-11T16:15:00-04:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "BKH",
        "title": "Black Hills Corp. Energizes First Phase of its Ready Wyoming Transmission Expansion",
        "url": "https://ir.blackhillscorp.com/news-releases/news-release-details/black-hills-corp-energizes-first-phase-its-ready-wyoming/",
        "publish_timestamp": "2025-01-15T16:42:00-05:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "BKH",
        "title": "Black Hills Corp. Reports 2024 Fourth-Quarter and Full-Year Results and Initiates 2025 Earnings Guidance",
        "url": "https://ir.blackhillscorp.com/news-releases/news-release-details/black-hills-corp-reports-2024-fourth-quarter-and-full-year",
        "publish_timestamp": "2025-02-05T16:16:00-05:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "PNW",
        "title": "Pinnacle West Reports 2024 Full-Year and Fourth-Quarter Results",
        "url": "https://www.pinnaclewest.com/newsroom/company-news/news-release-details/2025/Pinnacle-West-Reports-2024-Full-Year-and-Fourth-Quarter-Results/default.aspx",
        "publish_timestamp": "2025-02-25T00:00:00-07:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "PNW",
        "title": "APS Requests Rate Adjustment to Support Reliable Service for Customers",
        "url": "https://www.pinnaclewest.com/newsroom/company-news/news-release-details/2025/APS-Requests-Rate-Adjustment-to-Support-Reliable-Service-for-Customers/default.aspx",
        "publish_timestamp": "2025-06-13T00:00:00-07:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "PNW",
        "title": "Pinnacle West 3Q25 Earnings Presentation",
        "url": "https://s22.q4cdn.com/464697698/files/doc_financials/2025/q3/Q3_2025_Earnings_Final.pdf",
        "publish_timestamp": "2025-11-03T00:00:00-07:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "POR",
        "title": "Portland General Electric Announces Third Quarter 2024 Results",
        "url": "https://investors.portlandgeneral.com/news-releases/news-release-details/portland-general-electric-announces-third-quarter-2024-results",
        "publish_timestamp": "2024-10-25T05:00:00-04:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "POR",
        "title": "Portland General Electric Announces 2024 Financial Results and Initiates 2025 Earnings Guidance",
        "url": "https://investors.portlandgeneral.com/node/20016/pdf",
        "publish_timestamp": "2025-02-14T00:00:00-08:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "POR",
        "title": "Portland General Electric Announces First Quarter 2025 Results",
        "url": "https://investors.portlandgeneral.com/news-releases/news-release-details/portland-general-electric-announces-first-quarter-2025-results",
        "publish_timestamp": "2025-04-25T05:00:00-04:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "POR",
        "title": "Portland General Electric Announces Second Quarter 2025 Results",
        "url": "https://investors.portlandgeneral.com/node/20406/pdf",
        "publish_timestamp": "2025-07-25T05:00:00-07:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "IDA",
        "title": "IDACORP Fourth Quarter and Year End 2024 Earnings Presentation",
        "url": "https://s26.q4cdn.com/720254477/files/doc_financials/2024/q4/2024-Q4-IDACORP-Conference-Call-Slides-FINAL.pdf",
        "publish_timestamp": "2025-02-20T16:30:00-05:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "IDA",
        "title": "IDACORP Investor Outreach Late Spring 2024",
        "url": "https://www.idacorpinc.com/files/doc_presentations/IDACORP-Investor-Outreach-Late-Spring-2024.pdf",
        "publish_timestamp": "2024-05-31T00:00:00-06:00",
    },
    {
        "source_type": "issuer_ir",
        "issuer_or_region": "IDA",
        "title": "Idaho Power Substation Allowance",
        "url": "https://www.idahopower.com/about-us/economic-development/substation-allowance/",
        "publish_timestamp": "2025-01-15T00:00:00-07:00",
    },
)

TARGETED_READABLE_EXCLUDED_URLS = {
    "https://www.pinnaclewest.com/files/doc_financials/2024/q4/PNW-2024-12-31-10-K.pdf",
    "https://www.idacorpinc.com/files/doc_presentations/IDACORP-Investor-Outreach-Late-Spring-2024.pdf",
}

TARGETED_READABLE_SEEDS = tuple(seed for seed in SEED_DOCUMENTS if seed["source_type"] != "ferc") + tuple(
    seed for seed in ISSUER_SEED_DOCUMENTS if seed["url"] not in TARGETED_READABLE_EXCLUDED_URLS
)

ANNOTATION_FIELDS = (
    "annotation_id",
    "canonical_event_key",
    "source_url",
    "issuer",
    "event_type",
    "signal_variant",
    "event_timestamp",
    "trade_date_override",
    "region",
    "mw_value",
    "contract_term_years",
    "take_or_pay_pct",
    "tariff_type",
    "cost_recovery",
    "capex_mention",
    "directional_label",
    "source_confidence",
    "analyst_confidence",
    "evidence_snippet",
    "notes",
)
