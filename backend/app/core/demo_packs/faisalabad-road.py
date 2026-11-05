# DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
# Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
"""A Punjab public road in Faisalabad, estimated above Rs 100 million.

The December 2023 PEC form is the one offered: 10 percent performance security
and a 5 percent retention-money limit. The older form's 10 percent deduction
on each certificate is not rewritten into those two figures. The government
civil-works sales-tax option is named. The reduced rate is not invented; the
standard 16 percent stays on the line until a tax adviser confirms the option.
"""

from __future__ import annotations

from app.core.demo_projects import DemoTemplate

_MRS = "https://finance.punjab.gov.pk/input-rates"

SECTIONS = [
    (
        "01",
        "01 - Carriage (MRS chapter 1)",
        {"masterformat": "31"},
        [
            (
                "01.01",
                "Carriage of aggregates. MRS chapter 1, Faisalabad, January-June 2025. Kacha-road, hilly-area and long-article allowances sit on this chapter. Indicative rate.",
                "m3",
                2400,
                950.0,
                {"masterformat": "31 05 16", "mrs_chapter": 1, "mrs_district": "Faisalabad", "mrs_source": _MRS},
            ),
        ],
    ),
    (
        "03",
        "03 - Earthwork (MRS chapter 3)",
        {"masterformat": "31"},
        [
            (
                "03.01",
                "Formation in ordinary soil. MRS chapter 3, Faisalabad, January-June 2025. Indicative rate.",
                "m3",
                6000,
                380.0,
                {"masterformat": "31 23 16", "mrs_chapter": 3, "mrs_district": "Faisalabad", "mrs_source": _MRS},
            ),
        ],
    ),
    (
        "18",
        "18 - Road and road structure (MRS chapter 18)",
        {"masterformat": "32"},
        [
            (
                "18.01",
                "Sub-base. MRS chapter 18, Faisalabad, January-June 2025. Indicative rate.",
                "m3",
                1800,
                4200.0,
                {"masterformat": "32 11 23", "mrs_chapter": 18, "mrs_district": "Faisalabad", "mrs_source": _MRS},
            ),
            (
                "18.02",
                "Water-bound macadam. MRS chapter 18, Faisalabad, January-June 2025. Indicative rate.",
                "m2",
                14000,
                1450.0,
                {"masterformat": "32 12 16", "mrs_chapter": 18, "mrs_district": "Faisalabad", "mrs_source": _MRS},
            ),
            (
                "18.03",
                "Asphalt wearing course. Indicative rate for this walkthrough, not an official MRS item. The Finance Department file is linked and not copied.",
                "m2",
                14000,
                2000.0,
                {"masterformat": "32 12 16", "mrs_chapter": 18, "mrs_district": "Faisalabad", "mrs_source": _MRS},
            ),
        ],
    ),
    (
        "20",
        "20 - Surface drainage (MRS chapter 20)",
        {"masterformat": "33"},
        [
            (
                "20.01",
                "Road drainage and culverts. Indicative rate for this walkthrough, not an official MRS item.",
                "lsum",
                1,
                39580000.0,
                {"masterformat": "33 40 00", "mrs_chapter": 20, "mrs_district": "Faisalabad", "mrs_source": _MRS},
            ),
        ],
    ),
    (
        "24",
        "24 - Electric installation (MRS chapter 24)",
        {"masterformat": "26"},
        [
            (
                "24.01",
                "Street lighting along the carriageway. Indicative rate for this walkthrough, not an official MRS item.",
                "nr",
                80,
                250000.0,
                {"masterformat": "26 56 00", "mrs_chapter": 24, "mrs_district": "Faisalabad", "mrs_source": _MRS},
            ),
        ],
    ),
]

TEMPLATE = DemoTemplate(
    demo_id="faisalabad-road",
    project_name="City road, Faisalabad",
    project_description=(
        "About two kilometres of city road for a Punjab public client in Faisalabad. "
        "The engineer's estimate is above Rs 100 million, so the December 2023 Pakistan "
        "Standard Bidding Documents are the form offered. Punjab Procurement Rules 2014 apply."
    ),
    region="PK",
    classification_standard="masterformat",
    currency="PKR",
    locale="en",
    address={
        "street": "Jhang Road",
        "city": "Faisalabad",
        "postcode": "38000",
        "country": "Pakistan",
        "lat": 31.4187,
        "lng": 73.0791,
    },
    validation_rule_sets=["pakistan", "boq_quality", "project_completeness"],
    boq_name="Bill of Quantities - Faisalabad city road",
    boq_description=(
        "Direct cost, overhead, profit, then Punjab sales tax on services. "
        "The government civil-works option is recorded. The reduced rate is not stored."
    ),
    boq_metadata={
        "standard": "Item rate bill of quantities",
        "phase": "Tender - engineer's estimate",
        "price_level": "Indicative PKR. Official MRS file is linked, not copied.",
    },
    sections=SECTIONS,
    markups=[
        ("Contractor's overhead", 5.0, "overhead", "direct_cost"),
        ("Contractor's profit", 10.0, "profit", "direct_cost"),
        (
            "Punjab sales tax on services, government civil works (standard 16 % until the reduced option is confirmed)",
            16.0,
            "tax",
            "cumulative",
        ),
    ],
    total_months=14,
    tender_name="Contract for works - Faisalabad city road",
    tender_companies=[
        ("Chenab Roads", "tenders@chenab-roads.example", 0.99),
        ("Faisalabad Civil Company", "tenders@faisalabad-civil.example", 1.04),
    ],
    progress_claims=(0.12, 0.40, 0.70),
    claim_retention=0.10,
    project_metadata={
        "address": "Jhang Road, Faisalabad 38000, Punjab, Pakistan",
        "client": "Punjab public works client (fictitious)",
        "works": "public",
        "procurement_rules": "Punjab Procurement Rules 2014",
        "contract_form": "pec_sbd_2023_12",
        "contract_price_pkr": 120000000,
        "performance_security_percent": "10",
        "retention_money_limit_percent": "5",
        "length_km": 2,
        "mrs_district": "Faisalabad",
        "mrs_period": "1 January 2025 to 30 June 2025",
        "mrs_source": _MRS,
        "tax_note": (
            "Government civil works have a reduced Punjab sales-tax option. "
            "The pack does not invent that rate. The line shows the standard 16 percent until a tax adviser confirms the option."
        ),
        "payment_note": (
            "December 2023 form: performance security 10 percent of the accepted contract amount, "
            "retention-money limit 5 percent of the contract price. "
            "The older form's 10 percent deduction on each certificate is a different figure and is not replaced by these two."
        ),
    },
)
