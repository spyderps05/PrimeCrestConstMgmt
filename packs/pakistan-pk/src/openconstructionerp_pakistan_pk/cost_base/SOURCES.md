# Pakistan cost base — sources

One section per rate book (`<book_id>.json` in this folder).

## MES Schedule of Rates (`mes_sr.json`)

**Edition shipped:** MES Schedule of Rates 2014, First Edition (August 2014). It was compiled under the orders of
the Engineer-in-Chief, GHQ Rawalpindi (Ministry of Defence, Military Engineer Services, Pakistan), and the foreword is
dated September 2014. It superseded MES SR 2009 and its 2010, 2012 and 2013 reprints.

**Where it came from:** the complete 736-page PDF, published as an attachment to a UNDP Pakistan procurement
notice: <https://procurement-notices.undp.org/view_file.cfm?doc_id=289774> (retrieved 2026-11-06).

**What is in the file:** 6,588 rated items:

| Sections | Content | `kind` | Items |
|---|---|---|---|
| 1–27 | Composite work items: earthwork, roads, concrete, brick and stone masonry, woodwork, doors and windows, mongery, steel, roofing, flooring, plaster, ceilings, finishes, glazing, sanitary, water supply, SWV, drainage, pre-engineered, demolition, internal and external electrification, natural gas, HVAC | `item` | 4,908 |
| 28–29 | "Material Supply Only" rates | `material` | 1,645 |
| 31 | Labour rates, per day | `labour` | 35 |

Section 30 (the cement-consumption sheet) carries no rates and is not included.

**How it was extracted:**
- Text was extracted with pdfplumber, with the red watermark filtered out.
- Every rate was cross-checked against a second, independent text extraction of the same page, with 0 mismatches.
- 20 random rows were checked by hand against the raw PDF text, and all 20 matched.
- Codes are kept as printed (`1-1`, `24-303.1`, …).
- Units are normalised as follows:
  - Cum → m3, Sqm → m2, Metre → m, Lit → l, Tonne → t.
  - Each, Point, Set, Pair and Per set → pcs, with the rate unchanged.
  - "C.No" and "C Rifles" are per 100, "M.Nos" is per 1000 and a Dozen is per 12.
  - A "90 M coil" is converted to a rate per m.
  - A cement "Bag" is converted to a rate per kg, using the bag weight printed in the description.
- `unit_as_printed` and `rate_as_printed` keep the original values.
- Rates include GST (General Rule 25).

**What is missing:**
- 81 items that are printed without a rate, marked "Deleted being obsolete" or "shifted to Section 27".
- 28-149 and 29-538, which have no rate printed.
- Two rows printed without an item number (after 29-388 and after 29-551).
- Two codes misprinted in the source were corrected from the surrounding numbering: "2-5" in Section 22 became `22-5`, and the second "29-62" became `29-622`.
- `29-612` (Rs 1,336,125.65) is kept as printed even though it looks like a misprint.

**This is not the current edition.** Current MES tenders (2021–2026) are quoted against *"MES Schedule of Rates –
2021 amended up-to-date (including Ruling Percentage issued by MES)"*. One example is the NUTECH tender TC-EM-24-25:
<https://nutech.edu.pk/wp-content/uploads/2021/09/Bidding-Document-TC-EM-24-25.pdf>. The 2021 book, its amendments and
the E-in-C "ruling percentage" letters are sold or issued by E-in-C's Branch and are not published openly. The only
online copies found are login-gated Scribd uploads, which were not used:
- "MES Schedule of Rates 2021": scribd 681770472, 820027039 and 626132000
- A "2025" upload: scribd 974740858

No rate in this file comes from those copies. **2014 rates are therefore well below 2026 market prices.** Treat
`mes_sr` as a structural and relative-price reference until the 2021 book (plus its ruling percentage) is keyed in from a
licensed copy.

### How MES SR rates are applied ("SR + premium")

MES contracts do not usually price items afresh. They take the **Schedule rate** and apply a single **contractor's
percentage**:

- **Measurement & Term contracts** (works orders priced from the book): the bidder quotes one uniform percentage
  **above / at par / below** the MES Schedule. Under PAFW-2249 General Conditions, condition 1(o)(2), the "Contract
  Rates" are *"the rates in the MES Schedule of Rates as adjusted by the said Contractor's Percentage"*. The tender form
  reads "...at the uniform percentage of ___ on / off the rates contained in the MES Schedule".
- **Lump-sum contracts with Bills of Quantities:** the contractor's percentage is the percentage by which the priced
  BOQ total differs from the BOQ valued at MES Schedule rates (PAFW-2249 condition 1(o)(1)). Errors and variations
  are then valued at Schedule rates adjusted by that same percentage.
- **Ruling percentage:** when the book has aged, MES/E-in-C issues a "ruling percentage" (a general escalation over
  the printed SR). Tenders state that the rates are "MES SR 2021 including Ruling Percentage issued by MES", and the
  bidder's own above or below percentage is applied on top of that.
- **Material Supply Only** rates (sections 28 and 29) and **Labour Rates** (section 31) are the build-up rates. Under
  General Rules 17–18, they also price star rates and contractor-supplied materials, again subject to the contractor's percentage.
- Items not in the book are "star rates". They are priced from analogous items, or from Section-31 labour plus
  materials at market cost +25%, and the contract percentage applies unless the item is marked "Net".

**In the app:** load the book rates at par, then put the tender premium on the BOQ as a single markup with
`category="tender_adjustment"` (positive for "x % above SR", negative for "below SR"). Show the result as
**"SR rate + premium %"**, e.g. `1-1 Excavation, ordinary soil — SR Rs 181.15/m3 + 34% = Rs 242.74/m3`. If you are
pricing with the 2014 book, add the published ruling percentage, or your own escalation allowance, as a separate line
from the bidder's premium so the two can be audited independently.

Sources for the mechanism:
- PAFW-2249 MES General Conditions of Contract, on the PPRA EPMS:
  <https://epms.ppra.gov.pk/pdf?file=dGVuZGVyX2F0dGFjaG1lbnRzLzE3NzM2NTk4NjJfNjliN2U2ZDY0YWFiMS5wZGY%3D>
- MES SR 2014, General Rules 17–18 and 25.
- The NUTECH tender above, for "Ruling Percentage" and "Percent Above / At Par / Below MES Schedule – (2021)".
- The GE (Army) Tarbela 2026 term-contract form PAFW-1821:
  <https://epms.ppra.gov.pk/pdf?file=dGVuZGVyX2F0dGFjaG1lbnRzLzE3NzI3Nzg5NzlfNjlhYTc1ZTNlNjA1MS5wZGY%3D>

## Punjab Market Rate System (`punjab_mrs.json`)

**Edition shipped:** MRS 2nd Bi-Annual 2026 (01.07.2026 to 31.12.2026), District Lahore. Published by the Finance
Department, Government of the Punjab. This is the latest period listed on the Finance Department site at retrieval.

**Where it came from** (all retrieved 2026-11-06):
- Index page for district rate books: <https://finance.punjab.gov.pk/details/market-rates-bi-annual-period>
- Lahore rate book (222 pages): <https://finance.punjab.gov.pk/system/files/416_20260716141808.pdf>
- Index page for input rates: <https://finance.punjab.gov.pk/details/market-rates-input-rates>
- Input rates for the same period, Lahore column only:
  - Materials: <https://finance.punjab.gov.pk/system/files/96_20260717114253.pdf>
  - Labour: <https://finance.punjab.gov.pk/system/files/94_20260717114145.pdf>
  - Equipment: <https://finance.punjab.gov.pk/system/files/93_20260717114127.pdf>

**What is in the file:** 7,255 rows.

| Part | Codes | `kind` | Rows |
|---|---|---|---|
| Schedule items, chapters 3–27: earthwork, demolition, mortar, concrete, brickwork, stone, roofing, flooring, rendering, woodwork, painting, canals, protection, outlets, roads, plumbing, drainage, sewerage, wells, tubewell and water supply, electrical, iron work, miscellaneous, HVAC | `MRS-<ch>-<Sr>-<sub-items>` | `item`, or `labour` where the book prints only a labour rate | 3,943 |
| Input rates: materials | `MAT-<book code>` | `material` | 3,164 |
| Input rates: labour | `LB-…` | `labour` | 74 |
| Input rates: equipment | `EQ-…` | `plant` | 74 |

**How it was extracted:**
- Text was extracted from the official PDFs with pdfplumber, using word positions mapped to the printed columns. The
  PDFs have a text layer, so no OCR was used.
- The book prints a British-system and a metric-system rate for each item:
  - `unit_as_printed` and `rate_as_printed` keep the British unit and the composite rate, e.g. `100 Cft.`.
  - `rate_pkr` is the book's own printed metric composite rate, e.g. per Cum or per Sqm. Where the metric unit
    carries a count, such as "100 Nos.", the rate is divided by that count.
- Every row with both systems printed (about 3,700) was cross-checked: the British rate was converted with 1 cft =
  0.0283168 m3, 1 sft = 0.092903 m2 and 1 rft = 0.3048 m, then compared with the printed metric rate.
  - All accepted rows agree to within 1%.
  - About 20 rows disagree by more than 5% and were dropped. These are misprinted metric rates in the book, for
    example a "Per Meter" rate computed with the sft factor.
- Input-rate units: maund (Md) was converted at 37.3242 kg.

**What is left out:**
- Chapter 1, Carriage. Its rates are per km or per chain for a given load, which does not fit the unit set.
- Chapter 2, Loading/Unloading. Its table layout did not extract reliably.
- Rows whose unit is outside the allowed set: per km, acre, bag, sq inch, letter, cut and similar.
- About 90 rate rows printed without their own sub-item number under an already-priced line. Their rates were read
  correctly, but their descriptions could not be attributed reliably.

**Known caveats:**
- **"Per Ton":** this appears on 7 rows and is mapped to `t`. The book does not say whether it means the long or the
  metric ton.
- **Codes:** they follow the book's own numbering. A `#n` suffix marks printed numbering that repeats within an item.
- **Other districts:** Lahore only. The other districts are separate PDFs listed on the same index page, and
  Faisalabad uses the same layout, so the parser can be re-run on any of them.

**Spot check:** 32 schedule rows, 10 material rows and the equipment and labour samples were compared by eye against
the PDF text lines, and all rates matched.

## Khyber Pakhtunkhwa (`kp_csr.json`)

**Edition shipped:** Market Rate System MRS-2025 (1st Bi-Annual), published by the MRS Cell, Finance Department,
Government of Khyber Pakhtunkhwa.

KP replaced its Composite Schedule of Rates with the MRS in 2021. The last KP CSR seen online is the 2014 edition, and
only as an unofficial SlideShare copy. This file therefore carries the current official KP schedule under the `kp_csr`
id.

**Where it came from** (retrieved 2026-11-06):
- Index page: <https://finance.gkp.pk/articles/info-desk/market-rate-system>
- Edition page: <https://finance.gkp.pk/article/market-rate-system-mrs-2025-ist-bi-annual>
- PDF (393 pages): <https://finance.gkp.pk/attachments/af7b9330a42411f0bcd755dcc852530a/download>

**What is in the file:** 4,148 items in 27 chapters, including Repair & Maintenance and Photovoltaic. All are `kind`
`item`.

**How to read the rates:**
- Rates are Peshawar market rates. Other districts and the merged areas apply the published area factors.
- Per the preface, composite rates include 23.5% in total: 4% KP sales tax, 2% overheads, 7.5% income tax and 10%
  contractor's profit.
- Codes are the book's own, e.g. `06-05-d`, prefixed `KP-`.
- `unit_as_printed` and `rate_as_printed` are the British unit and composite rate. `rate_pkr` is the printed metric
  composite rate.

**How it was extracted:** pdfplumber, using word positions. The British and metric rates were cross-checked to within
5%. Only 2 rows failed the check, both misprints in the book, and both were dropped.

**What is left out:**
- Rows marked "Deleted" (printed with 0.00 rates).
- Chapter 1, Carriage.
- Rows with units outside the allowed set: km/mile, acre, HP, joint, point, cut and similar.

**Spot check:** 20 random rows were compared by eye against the PDF text, and all 20 matched.

## Balochistan Composite Schedule of Rates (`balochistan_csr.json`)

**Edition shipped:** BCSR 2026, Volume-I, "updated till 23-04-2026". Published by the Planning & Development
Department, Government of Balochistan.

**Where it came from** (retrieved 2026-11-06):
<https://cdn.pnd.balochistan.gov.pk/downloads/CSR/bcsr-2026-bcsr-2026-updated-160426-pdf/BCSR-2026-updated-till-230426.pdf>
(285 pages). The previous edition, CSR 2023, is at
<https://cdn.pnd.balochistan.gov.pk/downloads/CSR/bcsr-2023-bcsr-2023/CSR-2023.pdf> but was not used.

**What is in the file:** 4,279 rows from 30 sections (2–31): 3,782 composite items and 497 labour-only items.

**How to read the rates:**
- The book prints metric first, so `unit_as_printed` and `rate_as_printed` are the metric unit and rate (R.M, Sq.m,
  Cu.m, Each, …). `rate_pkr` is that rate per normalised unit.
- Codes are `BCSR-<item no.>-<sub-item markers>`:
  - `hN` is an unnumbered sub-heading, such as "Ordinary soil".
  - `#n` marks repeated printed numbering.

**How it was extracted:** pdfplumber, using word positions. Where the British rate is printed, about 2,700 rows were
cross-checked against it, with a 5% tolerance; mismatches were dropped.

**What is left out:**
- Section 1, Carriage (per-km rates).
- Percentage-addition rows (e.g. "+25% for wet conditions").
- Rows with units outside the allowed set: point, watt, AH, cm/inch and similar.
- About 150 rate rows printed without their own sub-item marker under an already-priced line, as for Punjab above.

**Spot check:** 20 random rows were compared by eye against the PDF text, and all 20 rates matched.

## Not shipped

### Sindh CSR (`sindh_csr`)

The Standing Rates Committee (SRC) Sindh publishes the Composite Schedule of Rates 2024, enforced from 30 May 2024
and revising the 2022 schedule. Its PDF was linked at
<https://pnd.sindh.gov.pk/storage/tenders/psV0LaryJAW7R9NKhxHAbMgibO6PgsZKBikThdYE.pdf>, from
<https://pnd.sindh.gov.pk/Schedule>.

The P&D site has since moved to pnd.gos.pk. The old storage links now return 404, and the new site's Schedule page
loads its documents client-side. An archived copy exists in the Wayback Machine (snapshot 2024-08-09), but the
archive refused downloads from this network (HTTP 429). No Sindh file is shipped. To add it, download the PDF in a
browser and run the same extraction.

### Pak PWD CSR (`pwd_csr`)

Pak PWD was wound up in 2021. The pwd.gov.pk domain no longer resolves, and no official copy of the PWD CSR, last
issued in 2012, was found online. Only unofficial Scribd and SlideShare uploads exist. No file is shipped.

### Punjab CSR

Punjab costs public works with the Finance Department's MRS (`punjab_mrs` above). The old Punjab CSR (2009/2012) is
obsolete for estimates, so it was not pursued.
