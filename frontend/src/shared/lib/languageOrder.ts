// DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest​‌‍⁠​‌‍⁠​‌‍⁠​‌‍⁠
// Copyright (c) 2026 Artem Boiko / DataDrivenConstruction

import { compareNames } from './collator';

/**
 * The languages PrimeCrest's home market reads, pinned to the top of every
 * picker in this order: English, British English (the day-first dates the
 * Pakistan pack opens in) and Urdu. Everything else follows alphabetically.
 */
export const FEATURED_LANGUAGE_CODES: readonly string[] = ['en', 'en-GB', 'ur'];

/**
 * Order a language list alphabetically by the name the reader sees in the
 * picker (the native `name`), so a language added anywhere in
 * `SUPPORTED_LANGUAGES` lands in place without hand reordering. The registry
 * itself keeps its order because `SUPPORTED_LANGUAGES[0]` is the fallback.
 *
 * The collation locale is fixed rather than the reader's on purpose: this is
 * the list a reader uses to CHANGE the language, and a picker that reshuffles
 * the moment a language is picked loses the reader's place in it.
 */
export function sortLanguagesByName<T extends { readonly name: string }>(languages: readonly T[]): T[] {
  const featured = (l: T): number => {
    const code = (l as { readonly code?: string }).code;
    const i = code ? FEATURED_LANGUAGE_CODES.indexOf(code) : -1;
    return i < 0 ? FEATURED_LANGUAGE_CODES.length : i;
  };
  return [...languages].sort((a, b) => featured(a) - featured(b) || compareNames(a.name, b.name, 'en'));
}
