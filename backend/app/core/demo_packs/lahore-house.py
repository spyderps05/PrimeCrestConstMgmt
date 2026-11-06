# DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
# Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
"""A private 10-marla house in Lahore. English, rupees, Punjab marla factor.

Rates on the bill are indicative 2026 build-ups for the walkthrough, without
sales tax. Lines that sit against a Market Rate System chapter name it. The
official Lahore file stays on the Finance Department portal and is not copied
here. Quantities are taken off a typical double-storey 10-marla plan of about
3,400 square feet covered area; the parties are invented.
"""

from __future__ import annotations

from app.core.demo_packs._pakistan_demo_data import module_data_for
from app.core.demo_projects import DemoTemplate

_MRS = "https://finance.punjab.gov.pk/input-rates"


def _c(masterformat: str, chapter: int | None = None) -> dict:
    """Classification for one line: MasterFormat code, plus the MRS chapter when the line sits on one."""
    out: dict = {"masterformat": masterformat}
    if chapter is not None:
        out.update({"mrs_chapter": chapter, "mrs_district": "Lahore", "mrs_source": _MRS})
    return out


SECTIONS = [
    (
        "01",
        "01 - Preliminaries (Site setup)",
        {"masterformat": "01"},
        [
            ("01.01", "Setting out and layout of the 10-marla plot (Setting out)", "lsum", 1, 85000.0, _c("01 71 23")),
            ("01.02", "Soil investigation, two boreholes to 6 m (Soil test)", "lsum", 1, 85000.0, _c("01 32 00")),
            ("01.03", "Temporary LESCO connection and site water (Temporary utilities)", "lsum", 1, 120000.0, _c("01 51 00")),
            ("01.04", "Chowkidar room and cement store (Temporary buildings)", "lsum", 1, 150000.0, _c("01 52 00")),
            ("01.05", "Steel scaffolding hire and safety netting (Scaffolding)", "lsum", 1, 240000.0, _c("01 54 00")),
            ("01.06", "Curing water by tanker during structure works (Curing water)", "lsum", 1, 90000.0, _c("01 51 00")),
        ],
    ),
    (
        "03",
        "03 - Earthwork (MRS chapter 3)",
        {"masterformat": "31"},
        [
            ("03.01", "Excavation for foundations in ordinary soil, lift up to 1.5 m (Foundation excavation)", "m3", 165, 520.0, _c("31 23 16", 3)),
            ("03.02", "Backfilling with excavated earth, watered and rammed (Backfill)", "m3", 70, 380.0, _c("31 23 23", 3)),
            ("03.03", "Earth filling under floors from approved borrow, compacted (Earth filling)", "m3", 110, 1450.0, _c("31 23 23", 3)),
            ("03.04", "Sand filling under floors, watered and compacted (Sand filling)", "m3", 38, 2400.0, _c("31 23 23", 3)),
            ("03.05", "Disposal of surplus earth within 1 km (Spoil disposal)", "m3", 60, 650.0, _c("31 23 23", 3)),
            ("03.06", "Anti-termite treatment to foundations and floors (Anti-termite)", "m2", 260, 160.0, _c("31 31 16", 3)),
        ],
    ),
    (
        "06",
        "06 - Concrete (MRS chapter 6)",
        {"masterformat": "03"},
        [
            ("06.01", "Plain cement concrete 1:4:8 under foundations (PCC 1:4:8)", "m3", 18, 15500.0, _c("03 30 00", 6)),
            ("06.02", "Plain cement concrete 1:2:4 in floors, 75 mm (PCC 1:2:4 floors)", "m3", 22, 19500.0, _c("03 30 00", 6)),
            ("06.03", "Reinforced cement concrete 1:2:4 in footings and plinth beams (RCC foundations)", "m3", 38, 27000.0, _c("03 30 00", 6)),
            ("06.04", "Reinforced cement concrete 1:2:4 in columns (RCC columns)", "m3", 12, 34000.0, _c("03 30 00", 6)),
            ("06.05", "Reinforced cement concrete 1:2:4 in beams and lintels (RCC beams)", "m3", 16, 32000.0, _c("03 30 00", 6)),
            ("06.06", "Reinforced cement concrete 1:2:4 in roof slabs, ground and first floor (RCC slabs)", "m3", 58, 30500.0, _c("03 30 00", 6)),
            ("06.07", "Reinforced cement concrete in staircase waist slab and steps (RCC stair)", "m3", 6, 34000.0, _c("03 30 00", 6)),
            ("06.08", "Reinforced cement concrete in underground water tank (RCC water tank)", "m3", 5, 31000.0, _c("03 30 00", 6)),
            ("06.09", "Reinforced cement concrete in chajjas and sunshades (RCC chajjas)", "m3", 3, 33000.0, _c("03 30 00", 6)),
            ("06.10", "Steel shuttering to RCC members, including props (Shuttering)", "m2", 820, 1150.0, _c("03 11 00", 6)),
            ("06.11", "Steel reinforcement Grade 60 deformed bars, cut, bent and fixed (Steel Grade 60)", "t", 15, 305000.0, _c("03 21 00", 6)),
            ("06.12", "Binding wire for reinforcement (Binding wire)", "kg", 180, 420.0, _c("03 21 00", 6)),
        ],
    ),
    (
        "07",
        "07 - Brickwork (MRS chapter 7)",
        {"masterformat": "04"},
        [
            ("07.01", "First class brick masonry in cement sand mortar 1:6 in foundations and plinth (Brickwork in foundations)", "m3", 48, 19800.0, _c("04 21 13", 7)),
            ("07.02", "First class brick masonry in cement sand mortar 1:6 in superstructure (Brickwork 9 inch walls)", "m3", 135, 20500.0, _c("04 21 13", 7)),
            ("07.03", "Half-brick partition walls in cement sand mortar 1:4 (Brickwork 4.5 inch)", "m2", 180, 1650.0, _c("04 21 13", 7)),
            ("07.04", "Damp proof course 40 mm PCC 1:2:4 with two coats of hot bitumen (DPC)", "m2", 32, 1050.0, _c("07 11 00", 7)),
            ("07.05", "Brick masonry in parapet walls, cement sand mortar 1:6 (Parapet brickwork)", "m3", 9, 20500.0, _c("04 21 13", 7)),
            ("07.06", "Brick-on-edge coping to parapet (Parapet coping)", "m", 75, 650.0, _c("04 21 13", 7)),
        ],
    ),
    (
        "08",
        "08 - Roof insulation and waterproofing (Roof)",
        {"masterformat": "07"},
        [
            ("08.01", "Bitumen waterproofing, two coats with polythene sheet (Roof waterproofing)", "m2", 170, 650.0, _c("07 11 00")),
            ("08.02", "Expanded polystyrene roof insulation, 40 mm (Thermopore insulation)", "m2", 170, 750.0, _c("07 22 00")),
            ("08.03", "Mud phuska 100 mm with gobri leeping (Mud phuska)", "m2", 170, 380.0, _c("07 22 00")),
            ("08.04", "Burnt brick tile roof finish laid in cement mortar (Roof tiles)", "m2", 170, 1350.0, _c("07 31 00")),
            ("08.05", "uPVC rainwater down pipes 100 mm with spouts (Rainwater pipes)", "m", 36, 1250.0, _c("22 14 00")),
        ],
    ),
    (
        "09",
        "09 - Plaster and paint (Finishes)",
        {"masterformat": "09"},
        [
            ("09.01", "Cement sand plaster 1:4, 13 mm, internal walls (Internal plaster)", "m2", 1450, 720.0, _c("09 24 00")),
            ("09.02", "Cement sand plaster 1:4, 20 mm, external walls (External plaster)", "m2", 420, 880.0, _c("09 24 00")),
            ("09.03", "Cement sand plaster 1:3, 10 mm, to ceilings (Ceiling plaster)", "m2", 330, 650.0, _c("09 24 00")),
            ("09.04", "Wall putty two coats and primer (Putty and primer)", "m2", 1780, 260.0, _c("09 91 00")),
            ("09.05", "Plastic emulsion paint, three coats (Emulsion paint)", "m2", 1780, 420.0, _c("09 91 00")),
            ("09.06", "Weather-shield paint to external walls (Weather-shield paint)", "m2", 420, 560.0, _c("09 91 00")),
            ("09.07", "Enamel paint to doors, grills and railing (Enamel paint)", "m2", 160, 520.0, _c("09 91 00")),
        ],
    ),
    (
        "10",
        "10 - Flooring and tiling (MRS chapter 10)",
        {"masterformat": "09"},
        [
            ("10.01", "Porcelain floor tiles 600 x 600 mm on cement mortar bed (Porcelain floor tiles)", "m2", 230, 4800.0, _c("09 30 00", 10)),
            ("10.02", "Ceramic glazed wall tiles to bathrooms and kitchen dado (Wall tiles)", "m2", 160, 3900.0, _c("09 30 00", 10)),
            ("10.03", "Marble flooring 20 mm in lounge and stair treads (Marble flooring)", "m2", 65, 7500.0, _c("09 63 40", 10)),
            ("10.04", "Marble skirting 100 mm high (Marble skirting)", "m", 260, 650.0, _c("09 63 40", 10)),
            ("10.05", "Tuff tiles 60 mm on sand bed in car porch and driveway (Tuff tiles)", "m2", 45, 2200.0, _c("32 14 00", 10)),
            ("10.06", "Granite kitchen counter top 20 mm with edge polish (Granite counter)", "m", 9, 12500.0, _c("12 36 00", 10)),
        ],
    ),
    (
        "11",
        "11 - Doors, windows and woodwork (Openings)",
        {"masterformat": "08"},
        [
            ("11.01", "Deodar wood door frames (chokhats) 7 x 3 inch (Door frames)", "m", 110, 3800.0, _c("08 14 00")),
            ("11.02", "Solid wood panelled doors, 40 mm, with polish (Wooden doors)", "m2", 42, 22000.0, _c("08 14 00")),
            ("11.03", "Aluminium sliding windows with 5 mm tinted glass (Aluminium windows)", "m2", 48, 13500.0, _c("08 51 13")),
            ("11.04", "Mild steel window grills, painted (Window grills)", "m2", 48, 4200.0, _c("05 50 00")),
            ("11.05", "Main gate in mild steel sheet with fittings (Main gate)", "pcs", 1, 285000.0, _c("05 50 00")),
            ("11.06", "Stainless steel staircase railing (Stair railing)", "m", 22, 9500.0, _c("05 52 00")),
            ("11.07", "Kitchen cabinets, lamination sheet on MDF (Kitchen cabinets)", "m", 9, 38000.0, _c("12 35 30")),
            ("11.08", "Built-in wardrobes in bedrooms (Wardrobes)", "m2", 18, 24000.0, _c("06 41 00")),
            ("11.09", "Door locks, hinges and stoppers, per door set (Ironmongery)", "pcs", 16, 7500.0, _c("08 71 00")),
        ],
    ),
    (
        "19",
        "19 - Plumbing and sanitary (MRS chapter 19)",
        {"masterformat": "22"},
        [
            ("19.01", "PPR water supply pipes concealed in walls (PPR pipes)", "m", 220, 1250.0, _c("22 11 16", 19)),
            ("19.02", "uPVC soil and waste pipes with fittings (uPVC drainage)", "m", 120, 1650.0, _c("22 13 16", 19)),
            ("19.03", "Wall-hung WC with concealed cistern (WC sets)", "pcs", 5, 38000.0, _c("22 42 13", 19)),
            ("19.04", "Wash basin with vanity and mirror (Wash basins)", "pcs", 5, 32000.0, _c("22 42 16", 19)),
            ("19.05", "Shower and basin mixers, per bathroom set (Mixers)", "pcs", 5, 28000.0, _c("22 41 00", 19)),
            ("19.06", "Stainless steel kitchen sink with mixer (Kitchen sink)", "pcs", 1, 32000.0, _c("22 42 16", 19)),
            ("19.07", "Polyethylene overhead water tank 1,000 gallon (Overhead tank)", "pcs", 1, 85000.0, _c("22 11 23", 19)),
            ("19.08", "Water lifting pump 1 hp with float switch (Water pump)", "pcs", 2, 38000.0, _c("22 11 23", 19)),
            ("19.09", "Gas water heater 35 gallon with connections (Geyser)", "pcs", 1, 95000.0, _c("22 33 00", 19)),
            ("19.10", "Brick manholes and connection to society sewer (Manholes)", "pcs", 4, 38000.0, _c("33 31 00", 19)),
            ("19.11", "Internal Sui gas piping with valves (Gas piping)", "m", 45, 1600.0, _c("23 11 23", 19)),
        ],
    ),
    (
        "24",
        "24 - Electrical installation (MRS chapter 24)",
        {"masterformat": "26"},
        [
            ("24.01", "Light points, concealed PVC conduit and copper wiring (Light points)", "pcs", 85, 4800.0, _c("26 05 19", 24)),
            ("24.02", "15 A power plug points for AC and kitchen (Power points)", "pcs", 30, 6500.0, _c("26 27 26", 24)),
            ("24.03", "Main and floor distribution boards with MCBs (Distribution boards)", "pcs", 3, 48000.0, _c("26 24 16", 24)),
            ("24.04", "Main incoming cable 4-core 16 mm2 from meter (Main cable)", "m", 30, 3800.0, _c("26 05 13", 24)),
            ("24.05", "LED panel and downlight fittings (LED fittings)", "pcs", 70, 3200.0, _c("26 51 00", 24)),
            ("24.06", "Ceiling fans 56 inch, energy saver (Ceiling fans)", "pcs", 9, 14500.0, _c("26 28 00", 24)),
            ("24.07", "Earthing pits with copper plate (Earthing)", "pcs", 2, 28000.0, _c("26 05 26", 24)),
            ("24.08", "UPS and solar-ready circuit wiring (UPS circuit)", "lsum", 1, 85000.0, _c("26 33 53", 24)),
            ("24.09", "Split AC copper piping and power points (AC points)", "pcs", 5, 18000.0, _c("23 81 26", 24)),
            ("24.10", "Exhaust fans in kitchen and bathrooms (Exhaust fans)", "pcs", 6, 6500.0, _c("23 34 00", 24)),
        ],
    ),
    (
        "32",
        "32 - External works (Front elevation and lawn)",
        {"masterformat": "32"},
        [
            ("32.01", "Front boundary wall with RCC posts and steel grill (Front wall)", "m", 12, 28000.0, _c("32 31 00")),
            ("32.02", "Front lawn preparation and grass plantation (Lawn)", "lsum", 1, 75000.0, _c("32 92 00")),
            ("32.03", "Final cleaning and handing over (Cleaning and handover)", "lsum", 1, 45000.0, _c("01 74 00")),
        ],
    ),
]

TEMPLATE = DemoTemplate(
    demo_id="lahore-house",
    project_name="House on a 10-marla plot, Lahore",
    project_description=(
        "A double-storey house for a private owner on a 10-marla plot in Allama Iqbal Town, Lahore: "
        "four bedrooms with attached bathrooms, drawing and dining, lounge, kitchen, car porch and a roof "
        "terrace, about 3,400 square feet covered. The marla is the Punjab revenue count of 225 square feet. "
        "A kanal in the Lahore Development Authority regulations is 20 marlas. Setbacks follow the LDA table "
        "for a plot of this size; the distances are not copied into the bill. Grey structure is complete and "
        "finishes are under way."
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
        "Rates are indicative 2026 build-ups. Trades that sit on a Market Rate System chapter name it "
        "and link the Finance Department file."
    ),
    boq_metadata={
        "standard": "Item rate bill of quantities",
        "phase": "Construction - finishes stage",
        "base_date": "2026-Q1",
        "price_level": "Indicative PKR 2026, without sales tax. Official MRS file is linked, not copied.",
    },
    sections=SECTIONS,
    markups=[
        ("Contractor's overhead", 5.0, "overhead", "direct_cost"),
        ("Contractor's profit", 10.0, "profit", "direct_cost"),
        ("Punjab sales tax on services (16 %)", 16.0, "tax", "cumulative"),
    ],
    total_months=10,
    tender_name="Private building contract - Lahore house",
    tender_companies=[
        ("Ravi Homes", "tenders@ravi-homes.example", 0.98),
        ("Lahore Masonry Works", "tenders@lahore-masonry.example", 1.02),
        ("Shalimar Electric and Sanitary", "quotes@shalimar-es.example", 1.0),
    ],
    tender_packages=[
        (
            "Grey structure - main building contract",
            "Main building contract: earthwork, concrete, steel, brickwork, roof waterproofing and every item not tendered separately.",
            "awarded",
            [
                ("Ravi Homes", "tenders@ravi-homes.example", 0.98),
                ("Lahore Masonry Works", "tenders@lahore-masonry.example", 1.02),
            ],
        ),
        (
            "Finishes - flooring, doors, windows and paint",
            "Plaster, floor and wall tiles, marble, doors, windows, kitchen cabinets and painting.",
            "evaluating",
            [
                ("Lahore Masonry Works", "tenders@lahore-masonry.example", 1.01),
                ("Ravi Homes", "tenders@ravi-homes.example", 0.99),
            ],
        ),
        (
            "Plumbing, gas and electrical services",
            "Water supply, soil and waste pipes, sanitary fittings, Sui gas piping, wiring, lighting and fans.",
            "issued",
            [
                ("Shalimar Electric and Sanitary", "quotes@shalimar-es.example", 0.97),
                ("Ravi Homes", "tenders@ravi-homes.example", 1.04),
            ],
        ),
    ],
    seed_requisitions=True,
    progress_claims=(0.20, 0.45, 0.65),
    claim_retention=0.10,
    project_metadata={
        "address": "Street 12, Allama Iqbal Town, Lahore 54570, Punjab, Pakistan",
        "client": "Mr. Kashif Mehmood",
        "parties_note": "The owner, consultants and firms are invented for the walkthrough.",
        "architect": "Shahzad Iqbal Associates",
        "structural_engineer": "Engr. Bilal Hussain Consulting",
        "main_contractor": "Ravi Homes",
        "works": "private",
        "plot_marla": 10,
        "marla_sqft": 225,
        "kanal_marlas": 20,
        "storeys": 2,
        "covered_area_sqft": 3400,
        "setback_note": (
            "Setbacks follow the LDA Building and Zoning Regulations 2019 row for a plot of this size. "
            "The distances are not copied here, and no coverage percentage is invented."
        ),
        "setback_source": "https://lda.gop.pk/downloads/file/09-02-2026-amended-building-regulations-2019-with-amendment.pdf",
        "mrs_district": "Lahore",
        "mrs_period": "1 January 2025 to 30 June 2025",
        "mrs_source": _MRS,
        "contract_form": "pec_civil_works",
        "contract_price_pkr": 29296150,
        "bill_total_pkr": 39081064.10,
        "contract_price_note": (
            "The contract price is the bill amount at item rates. The bill then adds overhead, profit and the "
            "provincial sales tax on services, and closes at bill_total_pkr. The cost plan, budget lines and "
            "cash-flow plan are on the contract price."
        ),
        "tax_note": "Punjab sales tax on services at the standard 16 percent, as its own line. Federal GST is the goods line.",
    },
    module_data=module_data_for("lahore-house"),
)
