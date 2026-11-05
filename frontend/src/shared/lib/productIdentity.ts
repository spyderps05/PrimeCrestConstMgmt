/**
 * Product identity for PrimeCrest Construction Management.
 * Use these constants anywhere the UI falls back to the platform brand
 * (window title, wordmark, about, login) so the name stays in one place.
 *
 * The raw values live in `@/shared/brand`; this module keeps the older
 * PRODUCT_* names used across the app.
 */

import {
  COMPANY,
  COPYRIGHT,
  LEGAL_NOTICE,
  PRODUCT_NAME,
  PRODUCT_SHORT_NAME,
} from '@/shared/brand';

export { PRODUCT_NAME, PRODUCT_SHORT_NAME };
export const PRODUCT_DEVELOPER = COMPANY;
export const PRODUCT_DEVELOPER_LINE = `Developed by ${PRODUCT_DEVELOPER}`;
export const PRODUCT_TAGLINE =
  'Construction project management, cost estimation, and resource control';

/** Short legal notice for the About / Legal surface. */
export const PRODUCT_LEGAL_NOTICE = LEGAL_NOTICE;

export const PRODUCT_COPYRIGHT = COPYRIGHT;
