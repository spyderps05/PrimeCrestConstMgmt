# DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
# Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
"""​‌‍⁠​‌‍⁠​‌‍⁠​‌‍⁠Pakistan payment tax rows: income tax withheld from payments under a works contract.

The rows cover section 153(1) of the Income Tax Ordinance, 2001: a withholding
agent (a federal or provincial body, a company, an association of persons and
the other payers the section names) deducts income tax from a payment

* for the supply of goods, clause (a);
* for services rendered, clause (b);
* on the execution of a contract, clause (c), which is the works contract a
  contractor's interim payment certificate is paid under.

**Who decides the row.** The rate is in Division III of Part III of the First
Schedule and depends on things the payee is, not on the document: whether the
payee is a company (an association of persons and an individual share the
"any other case" rate), and whether the payee is on the Active Taxpayer List
(ATL) of the Federal Board of Revenue. Off the list the rate is doubled (rule 1
of the Tenth Schedule). The person preparing the certificate selects the row
that fits the payee; nothing here infers it.

**Sources, read 2026-11-06.** The FBR publishes one withholding rate card per
tax year (1 July to 30 June); its index is
https://fbr.gov.pk/withholding-taxes-rate-card/174298/174301

* Tax year 2026, "updated up to June 30, 2025 as per Finance Act, 2025":
  https://download1.fbr.gov.pk/Docs/20258181281745641WHT-RateCard.pdf
  (rows from 1 July 2025 to 30 June 2026);
* Tax year 2027, "updated up to June 30, 2026 as per Finance Act, 2026":
  https://download1.fbr.gov.pk/Docs/202681113864992WithholdingTaxRatesCard2027.pdf
  (rows from 1 July 2026, open-ended until the next Finance Act).

What the two cards say for the rows below (ATL / not on the ATL, percent of
the gross amount payable):

=====================================  ===========  ===========
Payment                                TY 2026      TY 2027
=====================================  ===========  ===========
153(1)(c) contract, company            7.5 / 15     7.5 / 15
153(1)(c) contract, any other case     8 / 16       8 / 16
153(1)(a) goods, company               5 / 10       5 / 10
153(1)(a) goods, any other case        5.5 / 11     5.5 / 11
153(1)(b) "certain services"           6 / 12       7 / 14
153(1)(b) other services               15 / 30      14 / 28
153(1)(b) independent professionals    (other)      15 / 30
=====================================  ===========  ===========

Each card says on its face that the Ordinance prevails over it, so every row is
``unconfirmed`` until a Pakistani tax adviser has read the Ordinance and the
First Schedule. The cards give "the gross amount payable" as the base; whether
the provincial sales tax on the invoice sits inside that amount is not settled
here, and the rows take the amount with the tax (``net_plus_vat``) as the cards
read. A tax year is a window: a new Finance Act adds rows from the next
1 July and closes the earlier ones, it does not overwrite them.

**What is not here.** Withholding of sales tax on services by the paying body.
Each province runs its own withholding rules (the Punjab Sales Tax on Services
(Withholding) Rules 2015, amended in July 2025 so that telecom, banking and
insurance companies withhold four fifths and other companies one fifth of the
tax charged by an active-taxpayer company, as reported at
https://pkrevenue.com/punjab-directs-three-major-sectors-to-withhold-80-tax-on-services/;
the Sindh Sales Tax Special Procedure (Withholding) Rules 2014; and the
Khyber Pakhtunkhwa, Balochistan and Islamabad equivalents). The primary text
of the current fractions was not read, so no fraction is shipped: the
certificate's sales tax withholding line is held until a person decides it.
Also not here: toll manufacturing, rice/cotton seed/edible oil, IT, advertising
and port-operator rows; the minimum tax and any exemption certificate under
section 159; the late-filer column; and the provincial stamp duty on a
contract. Each is a separate decision and none is guessed.

The income tax is credited against the payee's final liability; for a
contractor it is usually a final or adjustable deduction depending on the
payee's status, which the row does not decide.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.core.payment_taxes.tables import RateRow

__all__ = ["ROWS"]

_READ = "2026-11-06"

#: One tax year of the FBR rate card: where it was read, what it is called,
#: and the first and last day it applies to.
_Window = tuple[str, str, date, date | None]

_TY2026: _Window = (
    "https://download1.fbr.gov.pk/Docs/20258181281745641WHT-RateCard.pdf",
    "FBR Withholding Income Tax Rate Card for tax year 2026, updated up to 30 June 2025 (Finance Act, 2025)",
    date(2025, 7, 1),
    date(2026, 6, 30),
)
_TY2027: _Window = (
    "https://download1.fbr.gov.pk/Docs/202681113864992WithholdingTaxRatesCard2027.pdf",
    "FBR Withholding Income Tax Rate Card for tax year 2027, updated up to 30 June 2026 (Finance Act, 2026)",
    date(2026, 7, 1),
    None,
)

_CLAUSE_REFERENCE = {
    "1A": "Income Tax Ordinance, 2001, section 153(1)(a)",
    "1B": "Income Tax Ordinance, 2001, section 153(1)(b)",
    "1C": "Income Tax Ordinance, 2001, section 153(1)(c)",
}
_SCHEDULE = "First Schedule, Part III, Division III, read with rule 1 of the Tenth Schedule"

_COMMON_EN = (
    "Withheld by the paying body (a government body, a company, an association of persons or another "
    "withholding agent named in section 153). The rate depends on whether the payee is on the Active "
    "Taxpayer List: off the list the rate is double. Taken on the gross amount payable as the rate card "
    "reads; whether the sales tax on the invoice is inside that amount is to be confirmed with a "
    "Pakistani tax adviser."
)
_COMMON_UR = (
    "ادائیگی کرنے والا ادارہ (سرکاری ادارہ، کمپنی، افراد کی انجمن یا دفعہ 153 میں مذکور دیگر کٹوتی ایجنٹ) "
    "کاٹتا ہے۔ شرح اس پر منحصر ہے کہ وصول کنندہ فعال ٹیکس دہندگان کی فہرست میں شامل ہے یا نہیں؛ فہرست میں "
    "نہ ہونے پر شرح دگنی ہے۔ شرح کارڈ کے مطابق قابلِ ادائیگی مجموعی رقم پر لی گئی ہے؛ انوائس پر سیلز ٹیکس "
    "اس رقم میں شامل ہے یا نہیں، اس کی تصدیق پاکستانی ٹیکس مشیر سے کریں۔"
)

_CONDITIONS = {
    "1A": {
        "en": "From a payment for the supply of goods. " + _COMMON_EN,
        "ur": "اشیا کی فراہمی کی ادائیگی سے۔ " + _COMMON_UR,
    },
    "1B": {
        "en": "From a payment for services rendered. " + _COMMON_EN,
        "ur": "فراہم کردہ خدمات کی ادائیگی سے۔ " + _COMMON_UR,
    },
    "1C": {
        "en": "From a payment under a works contract. " + _COMMON_EN,
        "ur": "تعمیراتی ٹھیکے کے تحت ادائیگی سے۔ " + _COMMON_UR,
    },
}

_ATL_EN = {True: "on the Active Taxpayer List", False: "not on the Active Taxpayer List"}
_ATL_UR = {True: "فعال ٹیکس دہندگان کی فہرست میں", False: "فعال ٹیکس دہندگان کی فہرست سے باہر"}
_SUFFIX = {True: "ATL", False: "NON_ATL"}


def _row(window: _Window, clause: str, code: str, label_en: str, label_ur: str, rate: str) -> RateRow:
    """One payee class of section 153(1), at ``rate`` percent of the gross amount payable."""
    source_url, card, start, end = window
    return RateRow(
        country_code="PK",
        kind="income_withholding",
        code=code,
        labels={"en": label_en, "ur": label_ur},
        base="net_plus_vat",
        rate_pct=Decimal(rate),
        numerator=None,
        denominator=None,
        threshold_amount=None,
        threshold_currency="",
        threshold_scope="",
        threshold_measure="",
        cap_amount=None,
        effective_from=start,
        effective_to=end,
        legal_reference=f"{_CLAUSE_REFERENCE[clause]}; {_SCHEDULE}; {card}",
        source_url=source_url,
        read_date=_READ,
        review_status="unconfirmed",
        buyer_scope="designated_only",
        conditions=_CONDITIONS[clause],
    )


def _pair(
    window: _Window, clause: str, stem: str, what: tuple[str, str], rates: tuple[str, str]
) -> tuple[RateRow, RateRow]:
    """The two rows of one payee class: on the Active Taxpayer List, then off it."""
    what_en, what_ur = what
    atl_rate, non_atl_rate = rates
    return (
        _row(
            window,
            clause,
            f"PK_153_{clause}_{stem}_ATL",
            f"{what_en}, {_ATL_EN[True]}",
            f"{what_ur}، {_ATL_UR[True]}",
            atl_rate,
        ),
        _row(
            window,
            clause,
            f"PK_153_{clause}_{stem}_NON_ATL",
            f"{what_en}, {_ATL_EN[False]}",
            f"{what_ur}، {_ATL_UR[False]}",
            non_atl_rate,
        ),
    )


_WORKS_COMPANY = ("Works contract, company", "تعمیراتی ٹھیکہ، کمپنی")
_WORKS_OTHER = (
    "Works contract, individual or association of persons",
    "تعمیراتی ٹھیکہ، فرد یا افراد کی انجمن",
)
_GOODS_COMPANY = ("Supply of goods, company", "اشیا کی فراہمی، کمپنی")
_GOODS_OTHER = ("Supply of goods, individual or association of persons", "اشیا کی فراہمی، فرد یا افراد کی انجمن")
_SERVICES_CERTAIN = (
    "Services listed in Division III paragraph 2(i) (transport, security, building maintenance and the like)",
    "ڈویژن III پیرا 2(i) میں درج خدمات (ٹرانسپورٹ، سیکیورٹی، عمارت کی دیکھ بھال وغیرہ)",
)
_SERVICES_OTHER = ("Other services", "دیگر خدمات")
_SERVICES_PROFESSIONAL = (
    "Independent professional services (architects, engineers, lawyers, accountants)",
    "آزاد پیشہ ورانہ خدمات (آرکیٹیکٹ، انجینئر، وکلا، اکاؤنٹنٹ)",
)


ROWS: tuple[RateRow, ...] = (
    # Tax year 2026 (Finance Act, 2025): 1 July 2025 to 30 June 2026.
    *_pair(_TY2026, "1C", "COMPANY", _WORKS_COMPANY, ("7.5", "15")),
    *_pair(_TY2026, "1C", "OTHER", _WORKS_OTHER, ("8", "16")),
    *_pair(_TY2026, "1A", "COMPANY", _GOODS_COMPANY, ("5", "10")),
    *_pair(_TY2026, "1A", "OTHER", _GOODS_OTHER, ("5.5", "11")),
    *_pair(_TY2026, "1B", "CERTAIN", _SERVICES_CERTAIN, ("6", "12")),
    *_pair(_TY2026, "1B", "OTHER", _SERVICES_OTHER, ("15", "30")),
    # Tax year 2027 (Finance Act, 2026): from 1 July 2026. Contracts and goods
    # are unchanged; "certain services" went up a point, other services down
    # one, and independent professionals got a row of their own.
    *_pair(_TY2027, "1C", "COMPANY", _WORKS_COMPANY, ("7.5", "15")),
    *_pair(_TY2027, "1C", "OTHER", _WORKS_OTHER, ("8", "16")),
    *_pair(_TY2027, "1A", "COMPANY", _GOODS_COMPANY, ("5", "10")),
    *_pair(_TY2027, "1A", "OTHER", _GOODS_OTHER, ("5.5", "11")),
    *_pair(_TY2027, "1B", "CERTAIN", _SERVICES_CERTAIN, ("7", "14")),
    *_pair(_TY2027, "1B", "OTHER", _SERVICES_OTHER, ("14", "28")),
    *_pair(_TY2027, "1B", "PROFESSIONAL", _SERVICES_PROFESSIONAL, ("15", "30")),
)
