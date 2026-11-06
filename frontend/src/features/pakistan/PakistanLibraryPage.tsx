// DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
// Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
/**
 * Pakistan code library and the Punjab rate book.
 * Figures are for the walkthrough. Each instrument links to its publisher.
 */

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { apiGet } from '@/shared/lib/api';
import { fmtList, fmtNumber } from '@/shared/lib/formatters';
import { PageHeader } from '@/shared/ui/PageHeader';

type Instrument = {
  id: string;
  title: string;
  publisher?: string;
  note?: string;
  source_url: string;
};

type Chapter = { number: number; title: string };

type RateDistrict = {
  district: string;
  period: string;
  source_url: string;
  items?: unknown[];
};

type Library = {
  codes: { title: string; review: string; instruments: Instrument[] };
  rates: {
    title: string;
    review: string;
    latest_period_on_the_portal: string;
    input_rates_url: string;
    chapters: Chapter[];
    districts: RateDistrict[];
    carriage_notes: string[];
    importer: string;
  };
  contract_forms: {
    threshold_pkr: number;
    forms: Record<string, { name: string; applies_when: string; source_url: string; note?: string }>;
  };
};

export function PakistanLibraryPage() {
  const { t } = useTranslation();
  const [library, setLibrary] = useState<Library | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    apiGet<Library>('/v1/partner-pack/pakistan/library')
      .then((data) => {
        if (!cancelled) setLibrary(data);
      })
      .catch(() => {
        if (!cancelled) setError('The Pakistan library could not be loaded.');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="mx-auto max-w-3xl space-y-8 p-6">
      <PageHeader
        srTitle={t('nav.pakistan_library')}
        subtitle={t('nav.pakistan_library_subtitle')}
      />
      {error ? <p>{error}</p> : null}
      {library ? (
        <>
          <p className="rounded border border-amber-600/40 bg-amber-50 p-3 text-sm dark:bg-amber-950/30">
            {library.codes.review}
          </p>
          <section>
            <h2 className="mb-3 text-lg font-semibold">Codes</h2>
            <ul className="space-y-3">
              {library.codes.instruments.map((item) => (
                <li key={item.id}>
                  <a className="font-medium underline" href={item.source_url} target="_blank" rel="noreferrer">
                    {item.title}
                  </a>
                  {item.publisher ? <span className="text-sm"> — {item.publisher}</span> : null}
                  {item.note ? <p className="text-sm text-neutral-600 dark:text-neutral-300">{item.note}</p> : null}
                </li>
              ))}
            </ul>
          </section>
          <section>
            <h2 className="mb-3 text-lg font-semibold">Contract forms</h2>
            <p className="mb-3 text-sm">
              A job above Rs {fmtNumber(library.contract_forms.threshold_pkr, 0)} is offered the December 2023 form.
              A smaller job is offered the older civil-works form.
            </p>
            <ul className="space-y-3">
              {Object.entries(library.contract_forms.forms).map(([id, form]) => (
                <li key={id}>
                  <a className="font-medium underline" href={form.source_url} target="_blank" rel="noreferrer">
                    {form.name}
                  </a>
                  <p className="text-sm">{form.applies_when}</p>
                  {form.note ? <p className="text-sm">{form.note}</p> : null}
                </li>
              ))}
            </ul>
          </section>
          <section>
            <h2 className="mb-3 text-lg font-semibold">{library.rates.title}</h2>
            <p className="mb-2 text-sm">{library.rates.review}</p>
            <p className="mb-2 text-sm">
              Latest period the portal lists: {library.rates.latest_period_on_the_portal}.{' '}
              <a className="underline" href={library.rates.input_rates_url} target="_blank" rel="noreferrer">
                Finance Department input rates
              </a>
            </p>
            <p className="mb-2 text-sm">
              Districts loaded as slots: {fmtList(library.rates.districts.map((d) => d.district))}.
            </p>
            {library.rates.districts.every((d) => (d.items?.length ?? 0) === 0) ? (
              <p className="mb-2 text-sm">
                No item rates are loaded. The chapter list is the book’s headings only. Download the
                official file from the Finance Department link above. A row is kept only when its
                address is on finance.punjab.gov.pk or nha.gov.pk.
              </p>
            ) : null}
            <p className="mb-2 text-sm">Carriage notes: {library.rates.carriage_notes.join('; ')}.</p>
            <ol className="list-decimal pl-5 text-sm">
              {library.rates.chapters.map((chapter) => (
                <li key={chapter.number}>{chapter.title}</li>
              ))}
            </ol>
            <p className="mt-3 text-sm">{library.rates.importer}</p>
          </section>
        </>
      ) : null}
    </div>
  );
}
