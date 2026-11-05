# PrimeCrest Pakistan Pack (`pakistan-pk`)

The home-market country pack of **PrimeCrest Construction Management**, published by **Spyder Solutions**.
It pre-configures a PrimeCrest workspace for contractors, consultants and public bodies building in Pakistan,
private and public. It carries no engine code of its own: it composes neutral platform modules with Pakistani
data rows, rule packs, reference libraries and an Urdu overlay.

- Publisher: Spyder Solutions, <support@primecrest.pk>
- Website: <https://primecrest.pk>, documentation: <https://docs.primecrest.pk>
- Source: <https://github.com/spyderps05/PrimeCrestConstMgmt>

## What the pack sets up

### Currency: Pakistani rupee (PKR)

- Default currency `PKR`, shown as `Rs` at two decimals. A contract priced in US dollars can still be chosen
  at onboarding.
- Bills, interim payment certificates and invoices carry the rupee amount, the sales tax line and the income
  tax withheld separately, so the net payable is traceable.

### Sales tax: federal GST on goods, provincial sales tax on services

Goods are taxed by the federation and services by the province, so a construction bill has no single national
rate. The pack carries the sales tax as a line of its own (rule set `pakistan`, markup template PK) and the
person confirming the bill picks the rate for the province of the site and the payer.

| Code | Authority | Applies to | Rate | Status |
| --- | --- | --- | --- | --- |
| `GST` | FBR (federal) | goods | 18 % | seeded |
| `PRA_ST` | Punjab Revenue Authority | construction services in Punjab | 16 % | provisional, seeded |
| `PRA_ST_GOVT_CIVIL_WORKS` | Punjab Revenue Authority | government civil works in Punjab | 5 % | provisional, not seeded |
| `SRB_ST` | Sindh Revenue Board | construction services in Sindh | 15 % | provisional, seeded |
| `SRB_ST_REDUCED` | Sindh Revenue Board | reduced construction rate in Sindh | 5 % | provisional, not seeded |
| `KPRA_ST` | Khyber Pakhtunkhwa Revenue Authority | construction services in KP | 15 % | provisional, seeded |
| `KPRA_ST_GOVT_WORKS` | Khyber Pakhtunkhwa Revenue Authority | government funded works in KP | 4 % | from the authority's notification, not seeded |

The province of the site is asked at onboarding and stored on the project, so a new job picks the right
provincial row. Balochistan (BRA) is not shipped yet.

### Income tax withheld from contractor payments

Section 153(1)(c) of the Income Tax Ordinance, 2001, as four selectable payee classes (company or other
payee, on or off the Active Taxpayer List of the FBR), payment taxes table `data_pk`. A payee off the list
has tax withheld at twice the rate.

### PEC standard bidding documents and PPRA procurement

- Interim payment certificates paid within 28 days, 10 percent retention on each certificate up to 5 percent
  of the Contract Price (contract defaults row PK, payment clock `pk_pec_sbd_clause_60`).
- Public works defaults of the Pakistan Engineering Council Standard Bidding Documents for Works:
  mobilization advance up to 15 percent against a guarantee, performance security 10 percent, delay damages
  capped at 10 percent, and the Clause 70 price adjustment `pk_pec_sbd_clause_70`.
- PPRA (Public Procurement Rules 2004) and the provincial procurement rules as the frame for public tenders.
  All figures are shown for review, never enforced, and no price index values are shipped.

### PEC contractor categories

Contractors and operators registered with the Pakistan Engineering Council are licensed in categories that
cap the value of a single contract they may bid for. The pack records the firm's category at onboarding so
tenders can be checked against it:

| Category | Contract value limit (PKR) |
| --- | --- |
| C-A | no limit |
| C-B | up to 4,000 million |
| C-1 | up to 2,500 million |
| C-2 | up to 1,000 million |
| C-3 | up to 500 million |
| C-4 | up to 200 million |
| C-5 | up to 65 million |
| C-6 | up to 25 million |

The limits are **unconfirmed**: PEC revises them through its bye-laws, so check the current schedule on
<https://www.pec.org.pk> before relying on a limit in a tender. The category is advisory and never blocks a bid.

### Rate books: Punjab MRS and provincial CSR

- **Market Rate System (MRS), Punjab.** `rates.json` describes the bi-annual MRS published by the Finance
  Department of Punjab: the 27 chapters (carriage, earthwork, concrete, brickwork, roofing, plumbing, electric
  installation, HVAC and the rest), the labour, composite, material and equipment rate kinds, the carriage
  allowances (kacha road, hilly area, long articles) and the bill split into direct cost, overhead, profit and
  Punjab sales tax on services as its own line. The latest period listed on the portal is 1 January 2025 to
  30 June 2025.
- **Composite Schedule of Rates (CSR).** The provincial CSRs of Punjab, Sindh, Khyber Pakhtunkhwa and
  Balochistan, and the NHA composite rates for road works, use the same item layout and load through the same
  importer.
- The government rate files themselves are **not** copied into the pack. The importer accepts a period only
  from the official source (`finance.punjab.gov.pk` or `nha.gov.pk`) and refuses third-party reprints; every
  imported item keeps its district, period and source address.

### Code library

`codes.json` lists the instruments a Pakistani project names: Building Code of Pakistan 2021 and the 2007
seismic provisions, the PEC fire safety and energy provisions, the PEC standard bidding documents and Clause 70,
PPRA 2004 and Punjab PPRA 2014, the LDA building regulations, the Punjab Sales Tax on Services Act 2012 and
the FBR withholding rate card.

### Units

`sft`, `cft`, `rft` and "running ft" are aliases of ft2, ft3 and ft. `marla` and `kanal` are units of their
own with no fixed m2 factor, because a marla is 272.25 sq ft in the federal survey and 225 sq ft in Punjab
revenue practice. The firm picks the factor it uses at onboarding and it is stored on the project; a kanal is
20 marlas.

### Calendar

Monday to Friday working week, national holidays, Eid and Ashura spans with the moon-sighting observances of
2025 recorded.

### Urdu (اردو)

The pack ships `locales/ur.json`, a right-to-left Urdu overlay for the screens it adds (the Pakistan library,
onboarding, codes and rates) on top of the core Urdu bundle; missing keys fall back to English. Rule pack names
carry an Urdu title (`name_ur`), and the country name is stored as پاکستان.

### Demo projects

RCC Basic Health Unit in Punjab (`bhu-punjab`), a 10-marla house in Lahore (`lahore-house`), a road in
Faisalabad (`faisalabad-road`) and a government primary school in Karachi (`school-karachi`, sales tax of Sindh).

## Activate

The pack ships inside PrimeCrest. Activate it from Modules, then Partner Packs: click Rescan, find
"Pakistan Construction Pack", then Activate. To boot a workspace straight into it:

```bash
OE_PACK=pakistan-pk primecrest serve
```

## Sources and status

Every figure is flagged `unconfirmed` or provisional and needs review by a Pakistani quantity surveyor and tax
adviser before it is relied on for a tender or a tax filing.

- Income tax rates: Federal Board of Revenue withholding rate card updated up to 30 June 2026.
- Contract defaults, public works figures, price adjustment: Standard Bidding Documents for Procurement of
  Works (large contracts), harmonized with the Pakistan Engineering Council.
- Provisional: the provincial rates for Punjab (16 percent), Sindh and Khyber Pakhtunkhwa (15 percent) and the
  reduced government works rates (Punjab 5, Sindh 5) come from secondary sources. The Khyber Pakhtunkhwa
  government works rate (4 percent) was read on the authority's own notification.
- Holidays: Cabinet Division yearly circular and the 2025 Eid press releases. Islamic dates follow the
  Umm al-Qura calendar, which can differ from the Pakistani moon sighting by one to two days.

## Not shipped yet

- The rate values of the MRS and CSR periods (loaded through the importer from the official files).
- Balochistan Revenue Authority sales tax rate.
- Sales tax withheld by the paying body, income tax on services under section 153(1)(b), minimum tax,
  exemption certificates, stamp duty.
- The FBR electronic invoice profile.

## License

AGPL-3.0-or-later. © 2026 Spyder Solutions. PrimeCrest is based on OpenConstructionERP
© Artem Boiko / DataDrivenConstruction, licensed under AGPL-3.0.

---

# پرائم کرسٹ پاکستان پیک

پرائم کرسٹ کنسٹرکشن مینجمنٹ کا پاکستان پیک، اسپائیڈر سلوشنز کی جانب سے۔ یہ پیک پاکستان میں سرکاری اور نجی
تعمیراتی کام کرنے والے ٹھیکیداروں کے لیے ورک اسپیس تیار کرتا ہے: پاکستانی روپیہ (PKR)، اشیاء پر وفاقی جی ایس ٹی اور
خدمات پر صوبائی سیلز ٹیکس (پنجاب PRA، سندھ SRB، خیبر پختونخوا KPRA) بل میں الگ لائن کے طور پر، سیکشن 153 کے تحت
ٹھیکیدار کی ادائیگیوں سے انکم ٹیکس کی کٹوتی، پی ای سی کی معیاری بولی دستاویزات کے مطابق عبوری ادائیگی سرٹیفکیٹ،
10 فیصد ریٹینشن اور موبلائزیشن ایڈوانس، پی ای سی کنٹریکٹر کیٹیگریز (C-A تا C-6)، پی پی آر اے خریداری قواعد،
پنجاب مارکیٹ ریٹ سسٹم (MRS) اور صوبائی کمپوزٹ شیڈول آف ریٹس (CSR)، مرلہ اور کنال، سرکاری تعطیلات، اور اردو
انٹرفیس۔ تمام اعداد و شمار غیر تصدیق شدہ ہیں؛ ٹینڈر یا ٹیکس فائلنگ سے پہلے کسی پاکستانی کوانٹیٹی سرویئر اور ٹیکس
مشیر سے تصدیق کروائیں۔
