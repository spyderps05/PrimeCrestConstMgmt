import { beforeEach, describe, expect, it } from 'vitest';
import { clearErrorLog, getErrorLog, isExpectedEmptyRecord, logApiError } from './errorLogger';

const PID = 'dd2eb915-b7a3-4162-b176-6296b0dfb388';
const missing = (code: string) => JSON.stringify({ detail: { code, message: 'none yet' } });

describe('expected empty project records', () => {
  beforeEach(() => clearErrorLog());

  it.each([
    [`/v1/quality-concept/projects/${PID}/concept`, 'concept_missing'],
    [`/v1/procurement-concept/projects/${PID}/concept`, 'concept_missing'],
    [`/v1/permits/projects/${PID}/roadmap`, 'roadmap_missing'],
    [`/v1/staffing/projects/${PID}/plan`, 'plan_missing'],
    [`/v1/engineering_brief/projects/${PID}/brief`, 'brief_missing'],
    [`/v1/project_handbook/projects/${PID}/handbook`, 'handbook_missing'],
    [`/v1/commitment-release/projects/${PID}/matrix`, 'matrix_missing'],
    [`/v1/delivery-model/projects/${PID}/model`, 'model_missing'],
    [`/v1/project-governance/projects/${PID}/model`, 'model_missing'],
    [`/v1/stakeholders/projects/${PID}/settings`, 'settings_missing'],
    [`/v1/design-management/projects/${PID}/setup`, 'setup_missing'],
  ])('does not record the documented 404 of %s', (path, code) => {
    expect(isExpectedEmptyRecord(path, 404, missing(code))).toBe(true);
    logApiError(path, 404, missing(code));
    expect(getErrorLog()).toHaveLength(0);
  });

  it('matches the plain-text details of site prep and closeout', () => {
    expect(
      isExpectedEmptyRecord(
        `/v1/site-prep/projects/${PID}/plan`,
        404,
        JSON.stringify({ detail: 'Mobilisation plan not found for this project' }),
      ),
    ).toBe(true);
    expect(
      isExpectedEmptyRecord(
        `/v1/closeout/projects/${PID}/package`,
        404,
        JSON.stringify({ detail: 'No closeout package for this project' }),
      ),
    ).toBe(true);
  });

  it('still records a 404 that means the project is not visible', () => {
    const path = `/v1/staffing/projects/${PID}/plan`;
    const body = JSON.stringify({ detail: 'Project not found' });
    expect(isExpectedEmptyRecord(path, 404, body)).toBe(false);
    logApiError(path, 404, body);
    expect(getErrorLog()).toHaveLength(1);
  });

  it('still records other statuses, other codes and other paths', () => {
    expect(isExpectedEmptyRecord(`/v1/staffing/projects/${PID}/plan`, 500, missing('plan_missing'))).toBe(false);
    expect(isExpectedEmptyRecord(`/v1/staffing/projects/${PID}/plan`, 404, missing('roadmap_missing'))).toBe(false);
    expect(isExpectedEmptyRecord(`/v1/staffing/projects/${PID}/plan/positions`, 404, missing('plan_missing'))).toBe(
      false,
    );
    expect(isExpectedEmptyRecord(`/v1/staffing/projects/${PID}/plan`, 404, 'not json')).toBe(false);
  });
});
