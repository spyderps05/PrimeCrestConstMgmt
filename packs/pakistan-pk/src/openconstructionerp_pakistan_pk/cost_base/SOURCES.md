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
