"""Build the ``PartnerPackManifest`` instance for the pakistan-pk pack."""

from __future__ import annotations

from app.core.partner_pack.manifest import PartnerBranding, PartnerPackManifest

MANIFEST = PartnerPackManifest(
    slug="pakistan-pk",
    partner_name="Pakistan Construction Pack",
    partner_url=None,  # None marks a first-party pack (a URL names an outside rights holder)
    pack_version="0.2.0",
    pack_type="country",
    description=(
        "The home-market pack of PrimeCrest Construction Management, by Spyder Solutions. Pre-configured for "
        "contractors working in Pakistan, private and public: Pakistani rupee, the bill with the sales tax "
        "(federal GST on goods, provincial sales tax on services by province: PRA, SRB, KPRA) carried as a "
        "line of its own, income tax withheld from contractor payments by payee class, interim payment "
        "certificates with the 10 percent retention and the mobilization advance of the PEC standard bidding "
        "documents, PEC contractor categories, the PPRA public works defaults and the Clause 70 price "
        "adjustment, the Punjab Market Rate System and provincial Composite Schedule of Rates layout, marla, "
        "kanal, sft, cft and rft as units, the Pakistani public holidays, and Urdu."
    ),
    default_locale="en-GB",
    additional_locales={"ur": "locales/ur.json"},
    # No CWICR region: Pakistani rates come from the provincial MRS / CSR files through the importer
    # described in rates.json, never from a bundled cost base.
    cwicr_regions=[],
    default_currency="PKR",
    default_tax_template=None,
    default_methodology="pakistan",
    validation_rule_packs=[
        "pakistan_tax",
        "pec_ppra",
    ],
    validation_rule_sets=["pakistan", "masterformat"],
    default_modules=[
        "oe_projects",
        "oe_boq",
        "oe_costs",
        "oe_assemblies",
        "oe_takeoff",
        "oe_tendering",
        "oe_contracts",
        "oe_measurement_book",
        "oe_variations",
        "oe_tax_withholding",
        "oe_preliminaries",
        "oe_schedule",
        "oe_daily_diary",
        "oe_subcontractors",
        "oe_procurement",
        "oe_rfq_bidding",
        "oe_punchlist",
        "oe_qms",
        "oe_safety",
        "oe_cvr",
        "oe_project_controls",
        "oe_reporting",
        "oe_documents",
        "oe_contacts",
        "oe_users",
    ],
    hidden_modules=[],
    demo_template_ids=["bhu-punjab", "lahore-house", "faisalabad-road", "school-karachi"],
    branding=PartnerBranding(
        primary_color="#01411C",  # Pakistan green (flag)
        accent_color="#FFFFFF",
        logo_path=None,
        favicon_path=None,
        powered_by_text=None,
    ),
    onboarding_script_path="onboarding.yaml",
    metadata={
        "country": "PK",
        "country_name_en": "Pakistan",
        "country_name_ur": "پاکستان",
        "classification_standard": "masterformat",
        "regulator_refs": [
            "Sales Tax Act, 1990 (federal, goods) and the provincial services tax laws: Punjab Sales Tax on Services Act 2012, Sindh Sales Tax on Services Act 2011, Khyber Pakhtunkhwa Sales Tax on Services Act 2022",
            "Income Tax Ordinance, 2001, section 153 (withholding on payments under a contract)",
            "Public Procurement Rules 2004 (PPRA) and the provincial procurement rules",
            "Pakistan Engineering Council Standard Bidding Documents for Procurement of Works",
        ],
        "vat_standard_rate": 18,
        "currency_decimals": 2,
        "retention_percent": 10,
        "review_status": (
            "Drawn from the published forms and the Federal Board of Revenue rate card. Every figure is "
            "flagged unconfirmed or provisional in the data tables. Pending review by a Pakistani quantity "
            "surveyor and a Pakistani tax adviser: do not rely on it for a tender or a tax filing before that review."
        ),
        "publisher": "Spyder Solutions",
        "support_email": "support@primecrest.pk",
        "support_name": "Spyder Solutions",
        "support_url": "https://primecrest.pk",
        "docs_url": "https://docs.primecrest.pk",
        "sales_tax_authorities": {
            "PK": "FBR (federal GST on goods)",
            "PK-PB": "PRA (Punjab Revenue Authority)",
            "PK-SD": "SRB (Sindh Revenue Board)",
            "PK-KP": "KPRA (Khyber Pakhtunkhwa Revenue Authority)",
            "PK-BA": "BRA (Balochistan Revenue Authority, rate not shipped)",
        },
        # PEC contractor licence categories and the single-contract limit in PKR million (None = no limit).
        # Unconfirmed: PEC revises the limits by bye-law; advisory only, never blocks a bid.
        "pec_contractor_categories": {
            "C-A": None,
            "C-B": 4000,
            "C-1": 2500,
            "C-2": 1000,
            "C-3": 500,
            "C-4": 200,
            "C-5": 65,
            "C-6": 25,
        },
        "pec_contractor_categories_status": "unconfirmed",
        "rate_books": ["Punjab Market Rate System (MRS)", "Composite Schedule of Rates (CSR), provincial", "NHA composite rates"],
        "code_library_path": "codes.json",
        "rate_book_path": "rates.json",
        # The phase model the demo projects are told on. Pinned by the demo file only: no
        # default_for_* flag, so a new project still gets the platform's default model.
        "catalogues": [
            {
                "kind": "phase_model",
                "id": "pakistan_pk",
                "version": 1,
                "path": "catalogues/phase_model/pakistan_pk.json",
            },
        ],
        # Story of the four Pakistan demo projects for the module seeders (governance,
        # engineering brief, economics, site logistics), read by catalogue_packs.active_pack_demo.
        "demo": {"path": "demo/demo_project.json"},
    },
)
