# DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
# Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
"""A private 10-marla house in Lahore. English, rupees, Punjab marla factor.

Rates on the bill are indicative build-ups for the walkthrough. Each line names
the Market Rate System chapter it sits against. The official Lahore file for
January-June 2025 stays on the Finance Department portal and is not copied here.
"""

from __future__ import annotations

from app.core.demo_projects import DemoTemplate

_MRS = "https://finance.punjab.gov.pk/input-rates"

SECTIONS = [
    (
        "01",
        "01 - Preliminaries",
        {"masterformat": "01"},
        [
            ("01.01", "Setting out the 10-marla plot", "lsum", 1, 85000.0, {"masterformat": "01 71 23"}),
        ],
    ),
    (
        "03",
        "03 - Earthwork (MRS chapter 3)",
        {"masterformat": "31"},
        [
            (
                "03.01",
                "Excavation in ordinary soil. MRS chapter 3, Lahore, January-June 2025. Indicative rate; the official figure is the Finance Department file.",
                "m3",
                48,
                420.0,
                {"masterformat": "31 23 16", "mrs_chapter": 3, "mrs_district": "Lahore", "mrs_source": _MRS},
            ),
        ],
    ),
    (
        "06",
        "06 - Concrete (MRS chapter 6)",
        {"masterformat": "03"},
        [
            (
                "06.01",
                "Plain cement concrete in foundations. MRS chapter 6, Lahore, January-June 2025. Indicative rate.",
                "m3",
                14,
                12500.0,
                {"masterformat": "03 30 00", "mrs_chapter": 6, "mrs_district": "Lahore", "mrs_source": _MRS},
            ),
            (
                "06.02",
                "Reinforced concrete in the roof slab. MRS chapter 6, Lahore, January-June 2025. Indicative rate.",
                "m3",
                18,
                18500.0,
                {"masterformat": "03 30 00", "mrs_chapter": 6, "mrs_district": "Lahore", "mrs_source": _MRS},
            ),
        ],
    ),
    (
        "07",
        "07 - Brickwork (MRS chapter 7)",
        {"masterformat": "04"},
        [
            (
                "07.01",
                "Brick masonry in the walls. MRS chapter 7, Lahore, January-June 2025. Indicative rate.",
                "m3",
                42,
                9800.0,
                {"masterformat": "04 21 13", "mrs_chapter": 7, "mrs_district": "Lahore", "mrs_source": _MRS},
            ),
        ],
    ),
    (
        "10",
        "10 - Flooring (MRS chapter 10)",
        {"masterformat": "09"},
        [
            (
                "10.01",
                "Floor finish in the rooms. MRS chapter 10, Lahore, January-June 2025. Indicative rate.",
                "m2",
                210,
                2800.0,
                {"masterformat": "09 30 00", "mrs_chapter": 10, "mrs_district": "Lahore", "mrs_source": _MRS},
            ),
        ],
    ),
    (
        "19",
        "19 - Plumbing (MRS chapter 19)",
        {"masterformat": "22"},
        [
            (
                "19.01",
                "Sanitary fittings and water supply. MRS chapter 19, Lahore, January-June 2025. Indicative rate.",
                "lsum",
                1,
                650000.0,
                {"masterformat": "22 40 00", "mrs_chapter": 19, "mrs_district": "Lahore", "mrs_source": _MRS},
            ),
        ],
    ),
]

TEMPLATE = DemoTemplate(
    demo_id="lahore-house",
    project_name="House on a 10-marla plot, Lahore",
    project_description=(
        "A single-storey house for a private owner on a 10-marla plot in Lahore. "
        "The marla is the Punjab revenue count of 225 square feet. A kanal in the "
        "Lahore Development Authority regulations is 20 marlas. Setbacks follow the "
        "LDA table for a plot of this size; the distances are not copied into the bill."
    ),
    region="PK",
    classification_standard="masterformat",
    currency="PKR",
    locale="en",
    address={
        "street": "Street 12, Allama Iqbal Town",
        "city": "Lahore",
        "postcode": "54570",
        "country": "Pakistan",
        "lat": 31.5121,
        "lng": 74.2846,
    },
    validation_rule_sets=["pakistan", "boq_quality", "project_completeness"],
    boq_name="Bill of Quantities - 10-marla house, Lahore",
    boq_description=(
        "Item rate bill at direct cost, then overhead, profit, and Punjab sales tax on services. "
        "Rates are indicative. Each trade names its Market Rate System chapter and the Finance Department link."
    ),
    boq_metadata={
        "standard": "Item rate bill of quantities",
        "phase": "Private builder walkthrough",
        "price_level": "Indicative PKR, without sales tax. Official MRS file is linked, not copied.",
    },
    sections=SECTIONS,
    markups=[
        ("Contractor's overhead", 5.0, "overhead", "direct_cost"),
        ("Contractor's profit", 10.0, "profit", "direct_cost"),
        ("Punjab sales tax on services (16 %)", 16.0, "tax", "cumulative"),
    ],
    total_months=8,
    tender_name="Private building contract - Lahore house",
    tender_companies=[
        ("Ravi Homes", "tenders@ravi-homes.example", 0.98),
        ("Lahore Masonry Works", "tenders@lahore-masonry.example", 1.02),
    ],
    progress_claims=(0.20, 0.55, 0.90),
    claim_retention=0.10,
    project_metadata={
        "address": "Street 12, Allama Iqbal Town, Lahore 54570, Punjab, Pakistan",
        "client": "Private owner (fictitious)",
        "works": "private",
        "plot_marla": 10,
        "marla_sqft": 225,
        "kanal_marlas": 20,
        "storeys": 1,
        "covered_area_sqft": 1650,
        "setback_note": (
            "Setbacks follow the LDA Building and Zoning Regulations 2019 row for a plot of this size. "
            "The distances are not copied here, and no coverage percentage is invented."
        ),
        "setback_source": "https://lda.gop.pk/downloads/file/09-02-2026-amended-building-regulations-2019-with-amendment.pdf",
        "mrs_district": "Lahore",
        "mrs_period": "1 January 2025 to 30 June 2025",
        "mrs_source": _MRS,
        "contract_form": "pec_civil_works",
        "contract_price_pkr": 2262760,
        "tax_note": "Punjab sales tax on services at the standard 16 percent, as its own line. Federal GST is the goods line.",
    },
)
