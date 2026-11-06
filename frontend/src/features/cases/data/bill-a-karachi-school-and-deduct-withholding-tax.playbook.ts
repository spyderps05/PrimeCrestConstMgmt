// DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
// Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
//
// Case: "Bill a Karachi school and deduct withholding tax" (PK).
//
// A school building in Karachi is paid by running bills. Each payment
// has income tax and sales tax withheld at source, and the deduction
// has to be shown on the bill and matched to a certificate. The school
// demo project is set up this way.
// Content strings are key plus inline English default and live only here.

import type { Playbook } from "../types";

const playbook: Playbook = {
  id: "bill-a-karachi-school-and-deduct-withholding-tax",
  order: 1712,
  region: "PK",
  category: "commercial",
  companyTypes: ["general-contractor", "subcontractor", "developer-client"],
  roles: ["quantity-surveyor", "accountant", "commercial-manager"],
  icon: "Receipt",
  titleKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.title",
  titleDefault: "Bill a Karachi school and deduct withholding tax",
  descKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.desc",
  descDefault:
    "Measure the work done this period, turn it into a running bill, show the income tax and sales tax withheld at source, and track the payment the contract allows.",
  estMinutes: 20,
  steps: [
    {
      id: "progress",
      icon: "TrendingUp",
      inputs: [
        {
          labelKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.progress.in.site",
          label: "Work done on site",
        },
      ],
      outputs: [
        {
          labelKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.progress.out.measured",
          label: "Quantities completed this period",
        },
      ],
      titleKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.progress.title",
      titleDefault: "Record the work done this period",
      whatKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.progress.what",
      whatDefault:
        "Update progress against the bill items and measure the quantities completed since the last bill.",
      whyKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.progress.why",
      whyDefault:
        "A running bill is only as good as the measurement under it. Progress recorded on the day is easier to agree than progress remembered at month end.",
      moduleLabel: "Progress",
      moduleLabelKey: "nav.progress",
      to: "/progress",
    },
    {
      id: "bill",
      icon: "Receipt",
      inputs: [
        {
          labelKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.bill.in.measured",
          label: "Measured quantities",
        },
      ],
      outputs: [
        {
          labelKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.bill.out.bill",
          label: "The gross running bill",
        },
      ],
      titleKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.bill.title",
      titleDefault: "Prepare the running bill",
      whatKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.bill.what",
      whatDefault:
        "Price the completed quantities at the contract rates, deduct what earlier bills paid, and recover any advance and retention due.",
      whyKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.bill.why",
      whyDefault:
        "Recoveries missed in one bill are taken back later without warning. Showing them on the bill keeps both sides on the same running position.",
      moduleLabel: "Finance",
      moduleLabelKey: "nav.finance",
      to: "/projects/:projectId/finance",
    },
    {
      id: "tax",
      icon: "Percent",
      inputs: [
        {
          labelKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.tax.in.bill",
          label: "The gross bill",
        },
      ],
      outputs: [
        {
          labelKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.tax.out.net",
          label: "Net payable and tax deducted",
        },
      ],
      titleKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.tax.title",
      titleDefault: "Show the tax withheld at source",
      whatKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.tax.what",
      whatDefault:
        "Apply the income tax and sales tax withholding rates for the contract and show the deductions and the net payable on the bill.",
      whyKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.tax.why",
      whyDefault:
        "The client deducts these taxes whether or not the bill shows them. Showing them first means the payment received matches the bill, and the certificate can be claimed against your return.",
      moduleLabel: "Withholding Tax",
      moduleLabelKey: "nav.tax_withholding",
      to: "/tax-withholding",
    },
    {
      id: "clock",
      icon: "Clock",
      inputs: [
        {
          labelKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.clock.in.submitted",
          label: "The submitted bill",
        },
      ],
      outputs: [
        {
          labelKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.clock.out.due",
          label: "When payment falls due",
        },
      ],
      titleKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.clock.title",
      titleDefault: "Track the payment date",
      whatKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.clock.what",
      whatDefault:
        "Record the submission date and the period the contract allows for payment, and watch for bills that run past it.",
      whyKey: "cases.bill_a_karachi_school_and_deduct_withholding_tax.step.clock.why",
      whyDefault:
        "Late payment is common on public jobs. A dated record is what makes a claim for delay possible.",
      moduleLabel: "Payment Clock",
      moduleLabelKey: "nav.payment_clock",
      to: "/payment-clock",
    },
  ],
};

export default playbook;
