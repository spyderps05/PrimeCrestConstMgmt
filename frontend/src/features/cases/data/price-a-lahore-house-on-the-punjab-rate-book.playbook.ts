// DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
// Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
//
// Case: "Price a Lahore house on the Punjab rate book" (PK).
//
// A private house in Lahore is priced the way the client will check it:
// item by item against the Punjab rate book, in PKR, with the grey
// structure and the finishes kept apart because they are usually
// contracted and paid separately. The Lahore house demo project is
// set up exactly this way.
// Content strings are key plus inline English default and live only here.

import type { Playbook } from "../types";

const playbook: Playbook = {
  id: "price-a-lahore-house-on-the-punjab-rate-book",
  order: 1710,
  region: "PK",
  category: "estimating",
  companyTypes: ["general-contractor", "cost-consultant", "developer-client"],
  roles: ["estimator", "quantity-surveyor"],
  icon: "Calculator",
  titleKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.title",
  titleDefault: "Price a Lahore house on the Punjab rate book",
  descKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.desc",
  descDefault:
    "Take off a ten marla house from its drawings, build the bill on the Punjab rate book in PKR, keep grey structure and finishes apart, and check the bill before the client sees it.",
  estMinutes: 20,
  steps: [
    {
      id: "takeoff",
      icon: "Ruler",
      inputs: [
        {
          labelKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.takeoff.in.drawings",
          label: "The architectural drawings",
        },
      ],
      outputs: [
        {
          labelKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.takeoff.out.quantities",
          label: "Measured quantities per item",
        },
      ],
      titleKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.takeoff.title",
      titleDefault: "Take the quantities off the drawings",
      whatKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.takeoff.what",
      whatDefault:
        "Measure excavation, foundations, brickwork, slabs and plaster from the plans, room by room, and record each quantity with the drawing it came from.",
      whyKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.takeoff.why",
      whyDefault:
        "A rate book only prices what you measured. A quantity that cannot be traced back to a drawing is the first thing a client's engineer will strike out.",
      moduleLabel: "PDF Measurements",
      moduleLabelKey: "nav.pdf_measurements",
      to: "/takeoff",
    },
    {
      id: "rates",
      icon: "Database",
      inputs: [
        {
          labelKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.rates.in.items",
          label: "Measured items",
        },
      ],
      outputs: [
        {
          labelKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.rates.out.rates",
          label: "Rates in PKR with their source",
        },
      ],
      titleKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.rates.title",
      titleDefault: "Price each item from the rate book",
      whatKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.rates.what",
      whatDefault:
        "Match every measured item to its Punjab rate book entry and carry the rate in PKR, adding market rates only where the book has no item, and saying so.",
      whyKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.rates.why",
      whyDefault:
        "Clients and banks compare a private estimate with the rate book. Rates that come from the book need no argument; rates that do not are the ones that get negotiated.",
      moduleLabel: "Cost Database",
      moduleLabelKey: "costs.title",
      to: "/costs",
    },
    {
      id: "bill",
      icon: "Table2",
      inputs: [
        {
          labelKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.bill.in.rates",
          label: "Priced items",
        },
      ],
      outputs: [
        {
          labelKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.bill.out.boq",
          label: "A sectioned bill of quantities",
        },
      ],
      titleKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.bill.title",
      titleDefault: "Build the bill in grey structure and finishes",
      whatKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.bill.what",
      whatDefault:
        "Group the priced items into the bill of quantities, with grey structure and finishing works as separate sections and a summary per section.",
      whyKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.bill.why",
      whyDefault:
        "Most houses in Pakistan are built on a grey structure contract first and finished later, often by different contractors. A bill split the same way can be tendered and paid the same way.",
      moduleLabel: "Bill of Quantities",
      moduleLabelKey: "boq.title",
      to: "/projects/:projectId/boq",
    },
    {
      id: "check",
      icon: "ShieldCheck",
      inputs: [
        {
          labelKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.check.in.boq",
          label: "The draft bill",
        },
      ],
      outputs: [
        {
          labelKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.check.out.checked",
          label: "A bill with its issues resolved",
        },
      ],
      titleKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.check.title",
      titleDefault: "Check the bill before it leaves",
      whatKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.check.what",
      whatDefault:
        "Run validation on the bill to catch missing units, zero rates, duplicated items and sections without a total.",
      whyKey: "cases.price_a_lahore_house_on_the_punjab_rate_book.step.check.why",
      whyDefault:
        "An error the client finds costs credibility for the whole estimate. The same error found here costs a minute.",
      moduleLabel: "Validation",
      moduleLabelKey: "validation.title",
      to: "/validation",
    },
  ],
};

export default playbook;
