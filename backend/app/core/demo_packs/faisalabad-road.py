# DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
# Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
"""A Punjab public road in Faisalabad, estimated above Rs 100 million.

The December 2023 PEC form is the one offered: 10 percent performance security
and a 5 percent retention-money limit. The older form's 10 percent deduction
on each certificate is not rewritten into those two figures. The government
civil-works sales-tax option is named. The reduced rate is not invented; the
standard 16 percent stays on the line until a tax adviser confirms the option.

Rates are indicative 2026 build-ups without sales tax. Lines that sit against a
Market Rate System chapter name it; the official file is linked, not copied.
Quantities are for about two kilometres of 7.3 m dual-lane carriageway with
shoulders, footpaths, a storm drain and street lighting. The parties are invented.
"""

from __future__ import annotations

from app.core.demo_packs._pakistan_demo_data import module_data_for
from app.core.demo_projects import DemoTemplate

_MRS = "https://finance.punjab.gov.pk/input-rates"


def _c(masterformat: str, chapter: int | None = None) -> dict:
    """Classification for one line: MasterFormat code, plus the MRS chapter when the line sits on one."""
    out: dict = {"masterformat": masterformat}
    if chapter is not None:
        out.update({"mrs_chapter": chapter, "mrs_district": "Faisalabad", "mrs_source": _MRS})
    return out


SECTIONS = [
    (
        "00",
        "00 - General items (Mobilisation and site facilities)",
        {"masterformat": "01"},
        [
            ("00.01", "Mobilisation and demobilisation of plant and crew (Mobilisation)", "lsum", 1, 3500000.0, _c("01 54 00")),
            ("00.02", "Topographic survey, setting out and benchmarks (Survey)", "lsum", 1, 950000.0, _c("01 71 23")),
            ("00.03", "Field laboratory with soil, aggregate and asphalt testing (Site laboratory)", "lsum", 1, 1800000.0, _c("01 45 00")),
            ("00.04", "Engineer's site office, furnished, with utilities (Engineer's office)", "lsum", 1, 1400000.0, _c("01 52 00")),
            ("00.05", "Traffic management and diversions during construction (Traffic management)", "lsum", 1, 2600000.0, _c("01 55 26")),
            ("00.06", "Project sign boards at both ends (Sign boards)", "pcs", 4, 65000.0, _c("01 58 00")),
            ("00.07", "Environmental monitoring and dust control (Environmental management)", "lsum", 1, 750000.0, _c("01 57 00")),
            ("00.08", "As-built drawings and completion documents (As-built drawings)", "lsum", 1, 450000.0, _c("01 78 00")),
        ],
    ),
    (
        "01",
        "01 - Carriage (MRS chapter 1)",
        {"masterformat": "31"},
        [
            (
                "01.01",
                "Carriage of crushed stone aggregates from Sargodha quarry, beyond the free lead (Carriage of aggregates)",
                "m3",
                2400,
                950.0,
                _c("31 05 16", 1),
            ),
            ("01.02", "Carriage of bitumen and asphalt plant material (Carriage of bitumen)", "t", 280, 1800.0, _c("31 05 16", 1)),
        ],
    ),
    (
        "03",
        "03 - Earthwork (MRS chapter 3)",
        {"masterformat": "31"},
        [
            ("03.01", "Clearing and grubbing of the right of way (Clearing and grubbing)", "m2", 22000, 35.0, _c("31 11 00", 3)),
            ("03.02", "Dismantling of existing asphalt pavement and disposal (Dismantling asphalt)", "m2", 9000, 180.0, _c("02 41 13", 3)),
            ("03.03", "Excavation of unsuitable material below formation (Unsuitable excavation)", "m3", 3500, 520.0, _c("31 23 16", 3)),
            ("03.04", "Formation in ordinary soil to line and level (Formation)", "m3", 6000, 380.0, _c("31 23 16", 3)),
            ("03.05", "Embankment from borrow, compacted to 95 percent modified AASHTO (Embankment)", "m3", 5200, 950.0, _c("31 23 23", 3)),
            ("03.06", "Compaction of natural ground under embankment (Ground compaction)", "m2", 18000, 85.0, _c("31 23 23", 3)),
            ("03.07", "Subgrade preparation, scarify, water and compact (Subgrade preparation)", "m2", 16000, 120.0, _c("31 23 23", 3)),
            ("03.08", "Excavation for storm drain and culvert trenches (Drain excavation)", "m3", 4500, 520.0, _c("31 23 16", 3)),
        ],
    ),
    (
        "18",
        "18 - Road and road structure (MRS chapter 18)",
        {"masterformat": "32"},
        [
            ("18.01", "Granular sub-base, 200 mm compacted (Sub-base)", "m3", 1800, 4200.0, _c("32 11 23", 18)),
            ("18.02", "Water-bound macadam to shoulders (Water-bound macadam)", "m2", 4000, 1450.0, _c("32 11 23", 18)),
            ("18.03", "Aggregate base course, 150 mm crushed stone (Aggregate base course)", "m3", 2100, 5600.0, _c("32 11 23", 18)),
            ("18.04", "Bituminous prime coat MC-70 (Prime coat)", "m2", 14600, 120.0, _c("32 12 13", 18)),
            ("18.05", "Bituminous tack coat (Tack coat)", "m2", 14600, 65.0, _c("32 12 13", 18)),
            ("18.06", "Asphaltic base course, plant mix, 75 mm (Asphalt base course)", "m3", 1100, 28000.0, _c("32 12 16", 18)),
            (
                "18.07",
                "Asphaltic wearing course, 50 mm. Indicative rate for this walkthrough, not an official MRS item (Asphalt wearing course)",
                "m2",
                14000,
                2000.0,
                _c("32 12 16", 18),
            ),
            ("18.08", "Precast concrete kerb stones on PCC bed (Kerb stones)", "m", 4000, 1450.0, _c("32 16 13", 18)),
            ("18.09", "Median kerb and earth fill to central median (Median)", "m", 2000, 3200.0, _c("32 16 13", 18)),
            ("18.10", "Footpath in PCC tiles on sand bed (Footpath tiles)", "m2", 3000, 2100.0, _c("32 14 00", 18)),
            ("18.11", "Shoulder dressing and turfing (Shoulder treatment)", "m2", 4000, 650.0, _c("32 92 00", 18)),
            ("18.12", "Pedestrian crossings at junctions, tactile tiles (Pedestrian crossings)", "m2", 240, 4800.0, _c("32 14 00", 18)),
        ],
    ),
    (
        "19",
        "19 - Road furniture and marking (Signs and safety)",
        {"masterformat": "32"},
        [
            ("19.01", "Thermoplastic road marking, lines and arrows (Road marking)", "m2", 1200, 2800.0, _c("32 17 23")),
            ("19.02", "Reflective road studs, cat's eyes (Road studs)", "pcs", 400, 1500.0, _c("32 17 26")),
            ("19.03", "Retro-reflective traffic signs on galvanised posts (Traffic signs)", "pcs", 40, 28000.0, _c("10 14 53")),
            ("19.04", "W-beam steel guard rail at culvert approaches (Guard rail)", "m", 300, 9500.0, _c("34 71 13")),
            ("19.05", "Kilometre posts and hectometre stones (Kilometre posts)", "pcs", 22, 6500.0, _c("10 14 53")),
            ("19.06", "Speed humps with marking near school frontage (Speed humps)", "pcs", 6, 45000.0, _c("32 17 13")),
        ],
    ),
    (
        "20",
        "20 - Surface drainage (MRS chapter 20)",
        {"masterformat": "33"},
        [
            ("20.01", "RCC pipe 600 mm diameter, ASTM C76 class III, laid and jointed (RCC pipe 600 mm)", "m", 1800, 9500.0, _c("33 41 13", 20)),
            ("20.02", "RCC pipe 900 mm diameter, laid and jointed (RCC pipe 900 mm)", "m", 600, 16500.0, _c("33 41 13", 20)),
            ("20.03", "Brick masonry manholes with cast iron covers (Manholes)", "pcs", 60, 95000.0, _c("33 05 61", 20)),
            ("20.04", "Catch pits with ductile iron gully gratings (Catch pits)", "pcs", 120, 28000.0, _c("33 44 13", 20)),
            ("20.05", "Reinforced concrete 1:1.5:3 in box culverts (RCC box culvert)", "m3", 180, 32000.0, _c("03 30 00", 20)),
            ("20.06", "Steel reinforcement Grade 60 in culverts (Steel Grade 60)", "t", 25, 305000.0, _c("03 21 00", 20)),
            ("20.07", "Brick masonry in cement sand mortar 1:6 in side drains (Side drain brickwork)", "m3", 450, 20000.0, _c("04 21 13", 20)),
            ("20.08", "Cement plaster 1:3 to drain inner faces (Drain plaster)", "m2", 2600, 780.0, _c("09 24 00", 20)),
            ("20.09", "PCC 1:2:4 bed and haunch to pipes (Pipe bedding)", "m3", 420, 19500.0, _c("03 30 00", 20)),
            ("20.10", "Outfall structure into the WASA disposal channel (Outfall)", "lsum", 1, 3800000.0, _c("33 42 00", 20)),
        ],
    ),
    (
        "24",
        "24 - Electric installation (MRS chapter 24)",
        {"masterformat": "26"},
        [
            (
                "24.01",
                "Street light pole 9 m, galvanised, with 120 W LED luminaire and foundation (Street lights)",
                "pcs",
                80,
                250000.0,
                _c("26 56 19", 24),
            ),
            ("24.02", "Underground armoured cable 4-core 25 mm2 (Street light cable)", "m", 2200, 2800.0, _c("26 05 13", 24)),
            ("24.03", "Feeder pillars with timers and protection (Feeder pillars)", "pcs", 4, 380000.0, _c("26 24 13", 24)),
            ("24.04", "Earthing to each pole (Pole earthing)", "pcs", 80, 12000.0, _c("26 05 26", 24)),
            ("24.05", "Traffic signal installation at Jhang Road junction (Traffic signals)", "lsum", 1, 4500000.0, _c("34 41 13", 24)),
        ],
    ),
    (
        "25",
        "25 - Utility shifting (Relocation of services)",
        {"masterformat": "33"},
        [
            ("25.01", "Relocation of WASA water main, 300 mm (Water main shifting)", "lsum", 1, 6500000.0, _c("33 14 00")),
            ("25.02", "Relocation of SNGPL gas line, by the utility at contractor's cost (Gas line shifting)", "lsum", 1, 4800000.0, _c("33 51 00")),
            ("25.03", "Shifting of FESCO electricity poles (FESCO pole shifting)", "pcs", 18, 185000.0, _c("33 71 00")),
            ("25.04", "Protection and shifting of PTCL telecom ducts (Telecom shifting)", "lsum", 1, 1600000.0, _c("33 81 00")),
        ],
    ),
    (
        "32",
        "32 - Landscaping (Green belt)",
        {"masterformat": "32"},
        [
            ("32.01", "Tree plantation in median and green belt, with guards (Tree plantation)", "pcs", 400, 2500.0, _c("32 93 43")),
            ("32.02", "Grassing of median and verges (Grassing)", "m2", 6000, 180.0, _c("32 92 00")),
            ("32.03", "Watering and maintenance during the defects period (Maintenance)", "lsum", 1, 600000.0, _c("32 01 90")),
        ],
    ),
]

TEMPLATE = DemoTemplate(
    demo_id="faisalabad-road",
    project_name="City road, Faisalabad",
    project_description=(
        "Rehabilitation and widening of about two kilometres of city road off Jhang Road, Faisalabad, "
        "for a Punjab public client: 7.3 m dual-lane carriageway with a central median, shoulders, "
        "footpaths, a piped storm drain with box culverts, street lighting and utility shifting. "
        "The engineer's estimate is above Rs 100 million, so the December 2023 Pakistan Standard "
        "Bidding Documents are the form offered. Punjab Procurement Rules 2014 apply."
    ),
    region="PK",
    # Punjab: the PRA sales tax on services and the Punjab MRS rate book apply.
    subdivision_code="PK-PB",
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
        "phase": "Construction - base course and drainage",
        "base_date": "2026-Q1",
        "price_level": "Indicative PKR 2026. Official MRS file is linked, not copied.",
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
        ("Lyallpur Electro Works", "bids@lyallpur-electro.example", 1.01),
    ],
    tender_packages=[
        (
            "Road works - main contract",
            "Main works contract: earthwork, pavement, storm drain, culverts, road furniture and utility shifting.",
            "awarded",
            [
                ("Chenab Roads", "tenders@chenab-roads.example", 0.99),
                ("Faisalabad Civil Company", "tenders@faisalabad-civil.example", 1.04),
            ],
        ),
        (
            "Street lighting and traffic signals",
            "Street light poles, cabling, feeder pillars and the junction signals.",
            "evaluating",
            [
                ("Lyallpur Electro Works", "bids@lyallpur-electro.example", 0.98),
                ("Faisalabad Civil Company", "tenders@faisalabad-civil.example", 1.03),
            ],
        ),
    ],
    seed_requisitions=True,
    progress_claims=(0.12, 0.30, 0.48),
    claim_retention=0.10,
    project_metadata={
        "address": "Jhang Road, Faisalabad 38000, Punjab, Pakistan",
        "client": "Highways Division Faisalabad, Government of the Punjab",
        "consultant": "Indus Highway Consultants",
        "structural_engineer": "Indus Highway Consultants",
        "quantity_surveyor": "Saleem Cost Consultants",
        "main_contractor": "Chenab Roads",
        "parties_note": "The client office, consultants and firms are invented for the walkthrough.",
        "works": "public",
        "procurement_rules": "Punjab Procurement Rules 2014",
        "contract_form": "pec_sbd_2023_12",
        "contract_price_pkr": 273443000,
        "bill_total_pkr": 364772962.00,
        "contract_price_note": (
            "The contract price is the bill amount at item rates. The bill then adds overhead, profit and the "
            "provincial sales tax on services, and closes at bill_total_pkr. The cost plan, budget lines and "
            "cash-flow plan are on the contract price."
        ),
        "performance_security_percent": "10",
        "retention_money_limit_percent": "5",
        "length_km": 2,
        "carriageway_width_m": 7.3,
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
    module_data=module_data_for("faisalabad-road"),
)
