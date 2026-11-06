// DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
// Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
//
// Case: "Keep a district road to its measurements and tests" (PK).
//
// A district road, like the Faisalabad road demo project, is measured
// layer by layer: subgrade, sub-base, base course and asphalt. Each
// layer is tested before the next covers it, and only tested layers
// are billed.
// Content strings are key plus inline English default and live only here.

import type { Playbook } from "../types";

const playbook: Playbook = {
  id: "keep-a-district-road-to-its-measurements-and-tests",
  order: 1713,
  region: "PK",
  category: "quality",
  companyTypes: ["general-contractor", "project-manager", "developer-client"],
  roles: ["site-manager", "quantity-surveyor", "foreman"],
  icon: "Route",
  titleKey: "cases.keep_a_district_road_to_its_measurements_and_tests.title",
  titleDefault: "Keep a district road to its measurements and tests",
  descKey: "cases.keep_a_district_road_to_its_measurements_and_tests.desc",
  descDefault:
    "Record each layer of the road in the site diary, test it before the next layer covers it, measure what passed, and bill only that.",
  estMinutes: 20,
  steps: [
    {
      id: "diary",
      icon: "NotebookPen",
      inputs: [
        {
          labelKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.diary.in.work",
          label: "Work done on site",
        },
      ],
      outputs: [
        {
          labelKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.diary.out.log",
          label: "A dated layer log by chainage",
        },
      ],
      titleKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.diary.title",
      titleDefault: "Record each layer in the site diary",
      whatKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.diary.what",
      whatDefault:
        "Log the chainage, layer, crew, plant and weather for every day of work on the road.",
      whyKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.diary.why",
      whyDefault:
        "A road is built in layers that disappear under the next one. The diary is the only record of what was laid, where and when.",
      moduleLabel: "Daily Diary",
      moduleLabelKey: "nav.daily_diary",
      to: "/projects/:projectId/daily-diary",
    },
    {
      id: "test",
      icon: "FlaskConical",
      inputs: [
        {
          labelKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.test.in.log",
          label: "The layer log",
        },
      ],
      outputs: [
        {
          labelKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.test.out.passed",
          label: "Sections that passed their tests",
        },
      ],
      titleKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.test.title",
      titleDefault: "Test the layer before it is covered",
      whatKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.test.what",
      whatDefault:
        "Record the compaction and material tests for each layer and section, and hold any section whose test failed or is outstanding.",
      whyKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.test.why",
      whyDefault:
        "A failed layer found after the asphalt is down means digging up the road. Found before, it means rolling it again.",
      moduleLabel: "Inspections",
      moduleLabelKey: "nav.inspections",
      to: "/projects/:projectId/inspections",
    },
    {
      id: "measure",
      icon: "Ruler",
      inputs: [
        {
          labelKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.measure.in.passed",
          label: "Passed sections",
        },
      ],
      outputs: [
        {
          labelKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.measure.out.quantities",
          label: "Quantities per chainage",
        },
      ],
      titleKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.measure.title",
      titleDefault: "Measure what passed",
      whatKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.measure.what",
      whatDefault:
        "Measure the length, width and thickness of every passed section and record the quantities per chainage.",
      whyKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.measure.why",
      whyDefault:
        "Quantities tied to a chainage and a test result are checked quickly. Quantities without them are questioned item by item.",
      moduleLabel: "Quantity Takeoff",
      moduleLabelKey: "nav.quantities",
      to: "/quantities",
    },
    {
      id: "report",
      icon: "FileBarChart",
      inputs: [
        {
          labelKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.report.in.quantities",
          label: "Quantities and tests",
        },
      ],
      outputs: [
        {
          labelKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.report.out.report",
          label: "The monthly progress report",
        },
      ],
      titleKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.report.title",
      titleDefault: "Report progress and quality together",
      whatKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.report.what",
      whatDefault:
        "Produce the monthly report with quantities done, tests passed and sections on hold side by side.",
      whyKey: "cases.keep_a_district_road_to_its_measurements_and_tests.step.report.why",
      whyDefault:
        "The engineer approves payment on quality as much as on quantity. A report that shows both gets approved in one pass.",
      moduleLabel: "Reports",
      moduleLabelKey: "nav.reports",
      to: "/reports",
    },
  ],
};

export default playbook;
