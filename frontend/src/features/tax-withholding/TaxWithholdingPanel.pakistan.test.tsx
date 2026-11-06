/**
 * A Pakistani withholding scheme is offered and explained like any other.
 *
 * The page lists whatever schemes the server has installed, so the Pakistan
 * (FBR section 153) scheme appears in the preview picker and as its own card,
 * with its four bands (company or not, on the Active Taxpayer List or not)
 * and a hint about checking the list before paying.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import type { Regime } from './api';

vi.mock('./api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./api')>();
  return {
    ...actual,
    listRegimes: vi.fn(),
    listPartyStatuses: vi.fn(),
    listExpiringPartyStatuses: vi.fn(),
  };
});

import { listExpiringPartyStatuses, listPartyStatuses, listRegimes } from './api';
import { TaxWithholdingPanel } from './TaxWithholdingPanel';

const band = (code: string, label: string, rate: string, verified: boolean) => ({
  code,
  label,
  rate_pct: rate,
  requires_verification: verified,
});

const PK: Regime = {
  id: 'regime-pk',
  country_code: 'PK',
  scheme_code: 'PK_ITO_153_CONTRACTS',
  scheme_name: 'Withholding on contract payments (Income Tax Ordinance 2001 s.153(1)(c))',
  legal_reference: 'Income Tax Ordinance, 2001, s.153(1)(c); First Schedule Part III Division III',
  authority: 'Federal Board of Revenue',
  currency_code: 'PKR',
  bands: [
    band('COMPANY_ATL', 'Company on the Active Taxpayer List', '7.5', true),
    band('OTHER_ATL', 'Individual or association of persons on the Active Taxpayer List', '8', true),
    band('COMPANY_NON_ATL', 'Company not on the Active Taxpayer List', '15', false),
    band('OTHER_NON_ATL', 'Individual or association of persons not on the Active Taxpayer List', '16', false),
  ],
  default_band_code: 'OTHER_NON_ATL',
  materials_excluded: false,
  vat_excluded: false,
  verification_validity_months: 12,
  threshold_amount: null,
  notes: 'Off the list the rate is doubled.',
  is_active: true,
  created_at: '2026-11-06T00:00:00Z',
  updated_at: '2026-11-06T00:00:00Z',
};

const GB: Regime = {
  ...PK,
  id: 'regime-gb',
  country_code: 'GB',
  scheme_code: 'UK_CIS',
  scheme_name: 'Construction Industry Scheme',
  legal_reference: 'Finance Act 2004 Part 3 Chapter 3',
  authority: 'HM Revenue & Customs',
  currency_code: 'GBP',
  bands: [band('HIGHER', 'Unverified or unmatched subcontractor', '30', false)],
  default_band_code: 'HIGHER',
  notes: '',
};

function renderPanel() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <TaxWithholdingPanel />
    </QueryClientProvider>,
  );
}

describe('the Pakistan withholding scheme', () => {
  beforeEach(() => {
    vi.mocked(listRegimes).mockResolvedValue([GB, PK]);
    vi.mocked(listPartyStatuses).mockResolvedValue([]);
    vi.mocked(listExpiringPartyStatuses).mockResolvedValue([]);
  });

  it('is offered in the preview picker', async () => {
    renderPanel();
    expect(await screen.findByRole('option', { name: `PK - ${PK.scheme_name}` })).toBeInTheDocument();
  });

  it('shows its four payee bands with the doubled rates off the list', async () => {
    renderPanel();
    const name = await screen.findByText(PK.scheme_name, { selector: 'span' });
    const card = name.closest('li') as HTMLElement;
    for (const [label, rate] of [
      ['Company on the Active Taxpayer List', '7.5%'],
      ['Company not on the Active Taxpayer List', '15%'],
      ['Individual or association of persons on the Active Taxpayer List', '8%'],
      ['Individual or association of persons not on the Active Taxpayer List', '16%'],
    ]) {
      const row = within(card).getByText(label).closest('tr') as HTMLElement;
      expect(within(row).getByText(rate)).toBeInTheDocument();
    }
    expect(within(card).getByTestId('tax-withholding-pk-hint').textContent).toContain('Active Taxpayer List');
    expect(within(card).getByText(PK.notes)).toBeInTheDocument();
  });

  it('gives the hint to the Pakistan card only', async () => {
    renderPanel();
    await screen.findByText(PK.scheme_name, { selector: 'span' });
    expect(screen.getAllByTestId('tax-withholding-pk-hint')).toHaveLength(1);
  });
});
