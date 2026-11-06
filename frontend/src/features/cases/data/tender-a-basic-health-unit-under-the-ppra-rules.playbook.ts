// DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
// Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
//
// Case: "Tender a Basic Health Unit under the PPRA rules" (PK).
//
// A Basic Health Unit is a typical public works job in Punjab: a small
// building, an engineer's estimate, and a tender that has to follow the
// public procurement rules from advertisement to award. The BHU demo
// project carries this shape.
// Content strings are key plus inline English default and live only here.

import type { Playbook } from "../types";

const playbook: Playbook = {
  id: "tender-a-basic-health-unit-under-the-ppra-rules",
  order: 1711,
  region: "PK",
  category: "tendering",
  companyTypes: ["developer-client", "project-manager", "cost-consultant", "general-contractor"],
  roles: ["procurement-buyer", "contract-administrator", "estimator"],
  icon: "Gavel",
  titleKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.title",
  titleDefault: "Tender a Basic Health Unit under the PPRA rules",
  descKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.desc",
  descDefault:
    "Prepare the engineer's estimate, issue one bill to every bidder, open and compare the bids against the estimate, and record the award so it can stand up to a complaint.",
  estMinutes: 25,
  steps: [
    {
      id: "estimate",
      icon: "Calculator",
      inputs: [
        {
          labelKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.estimate.in.design",
          label: "The approved design",
        },
      ],
      outputs: [
        {
          labelKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.estimate.out.estimate",
          label: "The estimated cost",
        },
      ],
      titleKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.estimate.title",
      titleDefault: "Prepare the engineer's estimate",
      whatKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.estimate.what",
      whatDefault:
        "Price the bill on the schedule of rates that governs the job and fix the estimated cost the tender will be judged against.",
      whyKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.estimate.why",
      whyDefault:
        "Bids are read as above or below the estimate. An estimate that is out of date makes every bid look wrong, and a tender committee cannot defend an award against it.",
      moduleLabel: "Bill of Quantities",
      moduleLabelKey: "boq.title",
      to: "/projects/:projectId/boq",
    },
    {
      id: "issue",
      icon: "Send",
      inputs: [
        {
          labelKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.issue.in.estimate",
          label: "The tender documents",
        },
      ],
      outputs: [
        {
          labelKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.issue.out.issued",
          label: "A tender issued on equal terms",
        },
      ],
      titleKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.issue.title",
      titleDefault: "Issue the tender to every bidder alike",
      whatKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.issue.what",
      whatDefault:
        "Publish the tender with the same bill, drawings and conditions for every bidder, and record every clarification so all bidders receive it.",
      whyKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.issue.why",
      whyDefault:
        "Equal information is the core of the procurement rules. A clarification sent to one bidder only is a ground for complaint and can void the award.",
      moduleLabel: "Tendering",
      moduleLabelKey: "tendering.title",
      to: "/tendering",
    },
    {
      id: "evaluate",
      icon: "Scale",
      inputs: [
        {
          labelKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.evaluate.in.bids",
          label: "The bids received",
        },
      ],
      outputs: [
        {
          labelKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.evaluate.out.ranking",
          label: "A ranked, checked comparison",
        },
      ],
      titleKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.evaluate.title",
      titleDefault: "Open and compare the bids",
      whatKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.evaluate.what",
      whatDefault:
        "Record the bids at opening, then compare them item by item against the estimate, not only on the total, and note any item priced far below cost.",
      whyKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.evaluate.why",
      whyDefault:
        "A low total can hide a front-loaded bid that is paid ahead of the work. Reading the items finds it before the contract is signed.",
      moduleLabel: "Bid Management",
      moduleLabelKey: "nav.bid_management",
      to: "/bid-management",
    },
    {
      id: "award",
      icon: "FileSignature",
      inputs: [
        {
          labelKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.award.in.ranking",
          label: "The evaluation",
        },
      ],
      outputs: [
        {
          labelKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.award.out.contract",
          label: "The signed contract",
        },
      ],
      titleKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.award.title",
      titleDefault: "Award and record the reason",
      whatKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.award.what",
      whatDefault:
        "Award to the lowest evaluated responsive bidder, record the reasons, and issue the contract for signature.",
      whyKey: "cases.tender_a_basic_health_unit_under_the_ppra_rules.step.award.why",
      whyDefault:
        "A written reason is what answers a complaint or an audit. Without it, the award is only an opinion.",
      moduleLabel: "Contracts",
      moduleLabelKey: "nav.contracts",
      to: "/projects/:projectId/contracts",
    },
  ],
};

export default playbook;
