/**
 * Single source of truth for user-visible product branding.
 *
 * Every place in the UI that shows the product name, the company, a public
 * URL or a contact address should import from here instead of hard-coding
 * it, so a future rename touches one file.
 */

export const PRODUCT_NAME = 'PrimeCrest Construction Management';
export const PRODUCT_SHORT_NAME = 'PrimeCrest';
export const COMPANY = 'Spyder Solutions';

export const SITE_URL = 'https://primecrest.pk';
export const SITE_HOST = 'primecrest.pk';
export const DOCS_URL = 'https://docs.primecrest.pk';
export const SUPPORT_EMAIL = 'support@primecrest.pk';
export const SUPPORT_MAILTO = `mailto:${SUPPORT_EMAIL}`;
/** GitHub `owner/name` slug, for API and issue-form URLs. */
export const REPO_SLUG = 'spyderps05/PrimeCrestConstMgmt';
export const REPO_URL = `https://github.com/${REPO_SLUG}`;
export const ISSUES_URL = `${REPO_URL}/issues`;
export const NEW_ISSUE_URL = `${ISSUES_URL}/new`;
export const RELEASES_URL = `${REPO_URL}/releases`;
export const DOWNLOAD_URL = `${SITE_URL}/download`;

/** Python distribution and CLI names shown in install instructions. */
export const PIP_PACKAGE = 'primecrest';
export const CLI_COMMAND = 'primecrest';
export const PIP_INSTALL_CMD = `pip install ${PIP_PACKAGE}`;
export const PIP_UPGRADE_CMD = `pip install --upgrade ${PIP_PACKAGE}`;

/**
 * Product legal text. PrimeCrest is proprietary software of Spyder Solutions,
 * distributed under a commercial licence; no open-source licence or source
 * offer applies to the product as shipped.
 */
export const LICENSE_NAME = 'Proprietary';
export const COPYRIGHT = `© 2026 ${COMPANY}.`;
export const LEGAL_NOTICE = `© 2026 ${COMPANY}. All rights reserved.`;

/** Short legal line for compact surfaces such as the sidebar footer. */
export const LEGAL_FOOTER = `© ${COMPANY}. All rights reserved.`;
