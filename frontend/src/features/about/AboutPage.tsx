// DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest​‌‍⁠​‌‍⁠​‌‍⁠​‌‍⁠
// Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
/**
 * AboutPage — Application info, developer, licence and upstream attribution.
 */

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Mail, Shield, BookOpen, Users, Award,
  Globe, ExternalLink, ArrowRight,
  MessageCircle, ChevronDown, Github,
} from 'lucide-react';
import clsx from 'clsx';
import { Card, Button, Badge, Breadcrumb, DismissibleInfo, IntroRichText } from '@/shared/ui';
import { SUPPORTED_LANGUAGES } from '@/app/i18n';
import { PageHeader } from '@/shared/ui/PageHeader';
import { APP_VERSION } from '@/shared/lib/version';
import { CheckForUpdatesButton, UpdateInlineNotice } from '@/shared/ui/UpdateChecker';
import { Changelog, getRecentReleases } from './Changelog';
import { ThirdPartyLicenses } from './ThirdPartyLicenses';
import {
  PRODUCT_DEVELOPER,
  PRODUCT_DEVELOPER_LINE,
  PRODUCT_LEGAL_NOTICE,
  PRODUCT_NAME,
  PRODUCT_TAGLINE,
} from '@/shared/lib/productIdentity';
import {
  COPYRIGHT,
  DOCS_URL,
  ISSUES_URL,
  REPO_URL,
  SITE_HOST,
  SITE_URL,
  SUPPORT_EMAIL,
  SUPPORT_MAILTO,
  UPSTREAM_ATTRIBUTION,
  UPSTREAM_LICENSE,
} from '@/shared/brand';

const DEMO_TEAM = [
  {
    name: 'Imran Shah',
    role: 'Administrator',
    portrait: '/assets/demo-people/imran-shah.jpg',
  },
  {
    name: 'Hassan Raza',
    role: 'Manager',
    portrait: '/assets/demo-people/hassan-raza.jpg',
  },
  {
    name: 'Usman Ali',
    role: 'Estimator',
    portrait: '/assets/demo-people/usman-ali.jpg',
  },
] as const;

export function AboutPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { hash, key } = useLocation();

  // The changelog is long, so on the About page it starts collapsed to a
  // single latest release with a toggle to reveal the full history. Deep
  // links (the header "View all" and /about#changelog) expand it on arrival.
  const [changelogExpanded, setChangelogExpanded] = useState(false);

  // When arriving via /about#changelog (from the header News button or the
  // sidebar What's-new card) scroll the changelog section into view. We key the
  // effect on the router location key as well as the hash: react-router mints a
  // fresh key on every navigation, so clicking "View in-app changelog" again
  // while already at /about#changelog (same hash value, after the user scrolled
  // away) still re-fires the scroll instead of silently doing nothing.
  useEffect(() => {
    if (hash !== '#changelog') return;
    // A deep link to the changelog should reveal the full list, not the
    // collapsed single-release preview.
    setChangelogExpanded(true);
    // Defer to the next frame so the changelog section is laid out first.
    const frame = window.requestAnimationFrame(() => {
      const changelog = document.querySelector('[data-changelog-anchor]');
      if (changelog) changelog.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [hash, key]);

  // A deep link to the demo team row (/about#community).
  useEffect(() => {
    if (hash !== '#community') return;
    const frame = window.requestAnimationFrame(() => {
      const community = document.querySelector('[data-demo-team-anchor]');
      if (community) community.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [hash, key]);

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Breadcrumb — single-item trail auto-hides (canonical top block). */}
      <Breadcrumb items={[{ label: t('nav.about', { defaultValue: 'About' }) }]} />

      {/* Canonical header row — sr-only title for AT; the module name + icon
          live in the top app bar. About keeps its brand identity block below. */}
      <PageHeader srTitle={t('nav.about', { defaultValue: 'About' })} />

      {/* Canonical module intro — pain-named, copy from MODULE_INTRO_COPY. */}
      <DismissibleInfo
        storageKey="about"
        title={t('about.intro_title', {
          defaultValue: 'Know what you are running and why',
        })}
        more={
          t('about.intro_more', { defaultValue: '' })
            ? <IntroRichText text={t('about.intro_more')} />
            : undefined
        }
        links={[
          { label: t('nav.modules', { defaultValue: 'Modules' }), onClick: () => navigate('/modules') },
          { label: t('nav.settings', { defaultValue: 'Settings' }), onClick: () => navigate('/settings') },
        ]}
      >
        {t('about.intro_body', {
          defaultValue:
            'Shows your installed version, recent release notes, the licence notice, and product information for PrimeCrest Construction Management by Spyder Solutions. Use it to confirm what build you are on before reporting an issue or planning an upgrade.',
        })}
      </DismissibleInfo>

      {/* Header — two columns on wide screens: identity on the left,
          update-availability notification on the right so users can
          spot a new release at a glance. */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 py-6 items-center">

        {/* ── Left column — project identity (left-aligned on wide) ── */}
        <div className="text-center lg:text-left">
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-oe-blue mb-4">
            <Globe size={13} />
            {PRODUCT_DEVELOPER}
          </div>
          <h2
            className="text-3xl font-bold text-content-primary tracking-tight"
            style={{ fontFamily: 'var(--oe-font-display)' }}
          >
            {PRODUCT_NAME}
          </h2>
          <p className="mt-1 text-sm font-medium text-oe-blue">{PRODUCT_DEVELOPER_LINE}</p>
          <p className="mt-2 text-base text-content-secondary">
            {t('about.tagline', { defaultValue: PRODUCT_TAGLINE })}
          </p>
          <div className="mt-3 flex items-center justify-center lg:justify-start gap-3 text-sm text-content-tertiary">
            <span className="font-mono">v{APP_VERSION}</span>
            <span>&middot;</span>
            <span>2026</span>
            <span>&middot;</span>
            <Badge variant="blue" size="sm">{UPSTREAM_LICENSE}</Badge>
          </div>
          <p className="mt-4 max-w-xl text-xs leading-relaxed text-content-tertiary" data-testid="about-legal-notice">
            {PRODUCT_LEGAL_NOTICE}
          </p>
        </div>

        {/* ── Right column — update notification + recent releases ──
            UpdateInlineNotice renders one line when an update is on offer
            and not dismissed; the recent-releases
            mini-list lives below it so the right column visually matches
            the left identity block's height on wide screens. */}
        <div className="flex flex-col gap-3">
          <UpdateInlineNotice />
          <CheckForUpdatesButton />

          {/* Recent releases — last 3 published versions with date so
              users can see the cadence at a glance without scrolling
              into the Changelog further down. */}
          <div className="rounded-xl border border-border-light bg-surface-secondary/40 px-4 py-3">
            <div className="mb-2 flex items-center justify-between gap-2">
              <p className="text-2xs font-semibold uppercase tracking-wider text-content-tertiary">
                {t('about.header_recent_label', { defaultValue: 'Recent releases' })}
              </p>
              <a
                href="#changelog"
                className="text-2xs text-oe-blue hover:underline"
                onClick={(e) => {
                  e.preventDefault();
                  setChangelogExpanded(true);
                  const changelog = document.querySelector('[data-changelog-anchor]');
                  if (changelog) changelog.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }}
              >
                {t('about.header_recent_more', { defaultValue: 'View all →' })}
              </a>
            </div>
            <ul className="space-y-1.5">
              {getRecentReleases(3).map(entry => ({ v: entry.version, date: entry.date, note: entry.summary })).map(r => (
                <li key={r.v} className="flex items-start gap-2 text-2xs leading-snug">
                  <span className="shrink-0 inline-flex items-center rounded-md bg-oe-blue/10 text-oe-blue font-mono font-semibold px-1.5 py-0.5">
                    v{r.v}
                  </span>
                  <span className="shrink-0 font-mono text-content-quaternary">{r.date}</span>
                  <span className="min-w-0 flex-1 truncate text-content-secondary" title={r.note}>
                    {r.note}
                  </span>
                </li>
              ))}
            </ul>
          </div>

        </div>
      </div>

      {/* Two-card band: Platform Capabilities + Contact & support.
          Each is its own Card so they visually read as separate blocks; both
          carry h-full + flex-col so the row stretches to the tallest sibling
          and the inside content fills the matched height. */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">

      {/* ── Card 1: Platform Capabilities ── */}
      <Card className="animate-card-in h-full flex flex-col" style={{ animationDelay: '50ms' }}>
        <div className="p-6 flex flex-col flex-1">
          <div className="flex items-center gap-2 mb-4">
            <Award size={18} className="text-amber-500" />
            <h2 className="text-lg font-semibold text-content-primary">
              {t('about.platform_title', { defaultValue: 'Platform Capabilities' })}
            </h2>
          </div>
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2.5">
            {[
              { value: '120K+', label: t('about.stat_costs', { defaultValue: 'Cost Items' }) },
              { value: String(SUPPORTED_LANGUAGES.length), label: t('about.stat_langs', { defaultValue: 'Languages' }) },
              { value: '47', label: t('about.stat_regions', { defaultValue: 'Countries covered' }) },
              { value: '6', label: t('about.stat_cad_formats', { defaultValue: 'CAD/BIM formats supported' }) },
              { value: '180+', label: t('about.stat_modules', { defaultValue: 'Backend modules' }) },
              { value: '28', label: t('about.stat_sections', { defaultValue: 'Menu sections' }) },
            ].map((s, i) => (
              <div key={i} className="text-center rounded-xl bg-surface-secondary/50 px-2 py-3">
                <div className="text-xl font-bold text-content-primary leading-none">{s.value}</div>
                <div className="text-2xs text-content-tertiary mt-1.5 leading-snug">{s.label}</div>
              </div>
            ))}
          </div>
          <p className="mt-auto pt-4 text-sm text-content-secondary leading-relaxed">
            {t('about.platform_desc', { defaultValue: 'PrimeCrest Construction Management covers the full construction estimation workflow - BOQ editing, 4D scheduling, 5D cost modeling, AI-powered estimation, CAD/BIM quantity takeoff (RVT, IFC, DWG), tendering, and reporting. Supports regional classification standards and custom schemas.' })}
          </p>
        </div>
      </Card>

      {/* ── Card 2: Contact & support — first-party channels only. ── */}
      <Card
        padding="none"
        className="animate-card-in h-full flex flex-col overflow-hidden border-oe-blue/20 bg-gradient-to-br from-oe-blue/5 via-transparent to-blue-50/40 dark:from-blue-950/20 dark:via-transparent dark:to-slate-900/30"
        style={{ animationDelay: '75ms' }}
      >
        <div className="p-6 flex flex-col flex-1">
            <div className="flex items-start gap-3 mb-4">
              <MessageCircle size={20} strokeWidth={1.75} className="shrink-0 mt-0.5 text-oe-blue" />
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-content-primary">
                  {t('about.contact_title', { defaultValue: 'Contact & support' })}
                </h3>
                <p className="text-xs text-content-secondary mt-1 leading-relaxed">
                  {t('about.contact_desc', {
                    defaultValue:
                      'Questions, bug reports and feature requests go straight to the Spyder Solutions team.',
                  })}
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-2.5">
              {[
                {
                  id: 'email',
                  href: SUPPORT_MAILTO,
                  icon: Mail,
                  title: t('about.contact_email', { defaultValue: 'Email support' }),
                  desc: SUPPORT_EMAIL,
                  external: false,
                },
                {
                  id: 'site',
                  href: SITE_URL,
                  icon: Globe,
                  title: t('about.contact_site', { defaultValue: 'Website' }),
                  desc: SITE_HOST,
                  external: true,
                },
                {
                  id: 'issues',
                  href: ISSUES_URL,
                  icon: Github,
                  title: t('about.contact_issues', { defaultValue: 'Issue tracker' }),
                  desc: t('about.contact_issues_desc', { defaultValue: 'Report a bug or request a feature' }),
                  external: true,
                },
              ].map(ch => (
                <a
                  key={ch.id}
                  href={ch.href}
                  {...(ch.external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
                  className="group flex items-center gap-3 rounded-lg border border-border-light bg-surface-primary px-3.5 py-3 hover:border-oe-blue/40 hover:bg-oe-blue/[0.04] transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-oe-blue focus-visible:ring-offset-1"
                >
                  <span className="shrink-0 h-9 w-9 rounded-lg bg-oe-blue/10 text-oe-blue flex items-center justify-center">
                    <ch.icon size={16} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-content-primary leading-tight">{ch.title}</p>
                    <p className="text-xs text-content-secondary mt-0.5 leading-snug truncate">{ch.desc}</p>
                  </div>
                  {ch.external && (
                    <ExternalLink size={13} className="text-content-quaternary group-hover:text-oe-blue shrink-0" />
                  )}
                </a>
              ))}
            </div>
        </div>
      </Card>

      </div>
      {/* /Two-card band */}

      {/* About the product — description (left) + developer & legal (right). */}
      <Card className="animate-card-in" style={{ animationDelay: '150ms' }}>
        <div className="p-6 grid grid-cols-1 lg:grid-cols-5 gap-x-8 gap-y-6">
          <div className="lg:col-span-3">
            <div className="mb-5 flex items-center gap-2">
              <BookOpen size={18} className="text-oe-blue" />
              <h2 className="text-lg font-semibold text-content-primary">
                {t('about.story_title', { defaultValue: 'About the project' })}
              </h2>
            </div>
            <div className="space-y-3 text-sm text-content-secondary leading-relaxed">
              <p>
                {t('about.pc_story_p1', {
                  defaultValue:
                    'PrimeCrest Construction Management brings estimating, cost control, scheduling, BIM quantity takeoff, procurement and project reporting into one self-hosted platform, adapted for construction teams in Pakistan.',
                })}
              </p>
              <p>
                {t('about.pc_story_p2', {
                  defaultValue:
                    'It is developed and maintained by Spyder Solutions on top of the open-source OpenConstructionERP platform, with local defaults, workflows and support for the Pakistani market.',
                })}
              </p>
            </div>
          </div>

          <aside className="lg:col-span-2 lg:border-l lg:border-border-light lg:pl-8 flex flex-col h-full">
            <div className="mb-5 flex items-center gap-2">
              <Globe size={16} className="text-oe-blue" />
              <h3 className="text-sm font-semibold text-content-primary">
                {t('about.developer_title', { defaultValue: PRODUCT_DEVELOPER })}
              </h3>
            </div>
            <p className="text-xs text-content-tertiary mb-4">
              {t('about.developer_subtitle', {
                defaultValue: 'PrimeCrest Construction Management is developed and maintained by Spyder Solutions.',
              })}
            </p>
            <div className="mb-6 rounded-lg border border-border-light bg-surface-secondary/40 px-3.5 py-3.5">
              <p className="text-2xs font-semibold uppercase tracking-wider text-content-tertiary mb-2">
                {t('about.legal_heading', { defaultValue: 'Legal' })}
              </p>
              <p className="text-[11px] leading-relaxed text-content-secondary">
                {PRODUCT_LEGAL_NOTICE}
              </p>
              <p className="mt-2 text-[11px] leading-relaxed text-content-tertiary" data-testid="about-upstream-attribution">
                {UPSTREAM_ATTRIBUTION}
              </p>
              <p className="text-[11px] text-content-tertiary mt-2 leading-snug">
                {t('about.third_party_hint', {
                  defaultValue: 'Third-party component licences are listed below on this page.',
                })}
              </p>
            </div>
          </aside>
        </div>
      </Card>

      {/* Reference band — Documentation + License side-by-side with matched heights. */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">

        <Card className="animate-card-in h-full flex flex-col" style={{ animationDelay: '240ms' }}>
          <div className="p-6 flex flex-col flex-1">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-oe-blue-subtle">
                <BookOpen size={20} className="text-oe-blue" />
              </div>
              <div className="flex-1 min-w-0">
                <h2 className="text-lg font-semibold text-content-primary">
                  {t('about.docs_title', { defaultValue: 'Documentation' })}
                </h2>
                <p className="text-xs text-content-tertiary">
                  {t('about.docs_desc', { defaultValue: 'Installation guides, feature overview, API reference, and tutorials' })}
                </p>
              </div>
            </div>
            <ul className="space-y-1.5 text-xs text-content-secondary mb-4">
              {[
                t('about.docs_b1', { defaultValue: 'Installation & deployment guides (Docker, VPS, Kubernetes)' }),
                t('about.docs_b2', { defaultValue: 'Feature walkthroughs - BOQ editor, BIM viewer, takeoff' }),
                t('about.docs_b3', { defaultValue: 'OpenAPI reference for all 100+ backend modules' }),
                t('about.docs_b4', { defaultValue: 'Module SDK - write your own plugin' }),
              ].map((b, i) => (
                <li key={i} className="flex items-start gap-2">
                  <ArrowRight size={11} className="mt-1 shrink-0 text-oe-blue" />
                  <span>{b}</span>
                </li>
              ))}
            </ul>

            <div className="mt-auto pt-4">
              <a href={DOCS_URL} target="_blank" rel="noopener noreferrer">
                <Button variant="primary" size="md" icon={<BookOpen size={15} />}>
                  {t('about.docs_open', { defaultValue: 'Open Docs' })}
                </Button>
              </a>
            </div>
          </div>
        </Card>

        {/* Licence — the upstream code is AGPL-3.0, so the terms shown here
            are the AGPL obligations, plus the required upstream credit. */}
        <Card className="animate-card-in h-full flex flex-col" style={{ animationDelay: '260ms' }}>
          <div className="p-6 flex flex-col flex-1">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 dark:bg-emerald-900/20">
                <Shield size={20} className="text-emerald-500" />
              </div>
              <div className="flex-1 min-w-0">
                <h2 className="text-lg font-semibold text-content-primary">
                  {t('about.license_title', { defaultValue: 'Licence & Ownership' })}
                </h2>
                <p className="text-xs text-content-tertiary">{COPYRIGHT}</p>
              </div>
            </div>
            <p className="text-sm text-content-secondary leading-relaxed mb-4">
              {PRODUCT_LEGAL_NOTICE}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-3 mb-4">
              <div>
                <p className="mb-1.5 text-2xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                  {t('about.license_youcan_label', { defaultValue: 'You can' })}
                </p>
                <ul className="space-y-1 text-xs text-content-secondary leading-snug">
                  {[
                    t('about.agpl_youcan_1', { defaultValue: 'Use it for any purpose' }),
                    t('about.agpl_youcan_2', { defaultValue: 'Self-host on your own hardware' }),
                    t('about.agpl_youcan_3', { defaultValue: 'Study and modify the source' }),
                    t('about.agpl_youcan_4', { defaultValue: 'Share copies under the same licence' }),
                  ].map((b, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="mt-1 inline-block h-1 w-1 rounded-full bg-emerald-500 shrink-0" />
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="mb-1.5 text-2xs font-semibold uppercase tracking-wider text-amber-600 dark:text-amber-400">
                  {t('about.license_youmust_label', { defaultValue: 'You must' })}
                </p>
                <ul className="space-y-1 text-xs text-content-secondary leading-snug">
                  {[
                    t('about.agpl_youmust_1', { defaultValue: 'Keep copyright and licence notices intact' }),
                    t('about.agpl_youmust_2', { defaultValue: 'License modified versions under AGPL-3.0' }),
                    t('about.agpl_youmust_3', { defaultValue: 'Offer the source to users of a network deployment' }),
                    t('about.agpl_youmust_4', { defaultValue: 'Keep the upstream attribution' }),
                  ].map((b, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="mt-1 inline-block h-1 w-1 rounded-full bg-amber-500 shrink-0" />
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="flex flex-wrap gap-1.5 mb-4">
              <Badge variant="success" size="sm">{UPSTREAM_LICENSE}</Badge>
              <Badge variant="success" size="sm">{t('about.license_badge_selfhost', { defaultValue: 'Self-hosted' })}</Badge>
              <Badge variant="success" size="sm">{t('about.license_badge_nolockin', { defaultValue: 'No vendor lock-in' })}</Badge>
              <Badge variant="blue" size="sm">© {PRODUCT_DEVELOPER}</Badge>
            </div>

            <p className="mb-4 text-[11px] leading-relaxed text-content-tertiary">{UPSTREAM_ATTRIBUTION}</p>

            {/* Third-party components shipped inside the build. */}
            <ThirdPartyLicenses className="mb-4" />

            <div className="mt-auto pt-3 border-t border-border-light">
              <a href={REPO_URL} target="_blank" rel="noopener noreferrer">
                <Button variant="secondary" size="md" icon={<Github size={15} />}>
                  {t('about.view_source', { defaultValue: 'View source code' })}
                </Button>
              </a>
            </div>
          </div>
        </Card>

      </div>

      {/* Demo team — fictional Pakistani names and portraits used in the product demo. */}
      <Card className="animate-card-in" style={{ animationDelay: '280ms' }}>
        <div className="p-6" data-demo-team-anchor style={{ scrollMarginTop: '80px' }}>
          <div className="flex items-center gap-2.5 mb-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-oe-blue/10 ring-1 ring-oe-blue/20">
              <Users size={18} className="text-oe-blue" />
            </div>
            <h2 className="text-lg font-semibold text-content-primary">
              {t('about.demo_team_title', { defaultValue: 'Demo team' })}
            </h2>
          </div>
          <p className="text-sm text-content-secondary leading-relaxed mb-6 max-w-3xl">
            {t('about.demo_team_subtitle', {
              defaultValue:
                'Showcase accounts used for product demos. Names and portraits are fictional.',
            })}
          </p>
          <div className="flex flex-wrap gap-4">
            {DEMO_TEAM.map((person) => (
              <div
                key={person.name}
                className="flex items-center gap-3 rounded-xl border border-border-light bg-surface-secondary/40 px-3.5 py-3 min-w-[220px]"
              >
                <img
                  src={person.portrait}
                  alt={person.name}
                  className="h-12 w-12 rounded-full object-cover ring-1 ring-border-light"
                  loading="lazy"
                />
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-content-primary leading-tight">{person.name}</p>
                  <p className="text-xs text-content-tertiary mt-0.5">{person.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Changelog - collapsed to the latest release by default with a toggle
          to reveal the full history. maxEntries caps the releases, so while
          unreleased work is pending the collapsed view shows two cards rather
          than one: that card is rendered above the list and is deliberately
          not a member of it. Anchored so the header's "View all" jump target
          lands on the section heading instead of mid-scroll. */}
      <Card>
        <div className="p-6" data-changelog-anchor>
          <Changelog maxEntries={changelogExpanded ? undefined : 1} />
          <div className="mt-4 flex justify-center">
            <button
              type="button"
              onClick={() => setChangelogExpanded(v => !v)}
              aria-expanded={changelogExpanded}
              className="inline-flex items-center gap-1.5 rounded-lg border border-border-light bg-surface-secondary/40 px-3.5 py-2 text-xs font-semibold text-oe-blue hover:border-oe-blue/40 hover:bg-oe-blue/[0.04] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-oe-blue focus-visible:ring-offset-1"
            >
              {changelogExpanded
                ? t('about.changelog_show_less', { defaultValue: 'Show less' })
                : t('about.changelog_show_all', { defaultValue: 'Show full changelog' })}
              <ChevronDown
                size={14}
                className={clsx('transition-transform', changelogExpanded && 'rotate-180')}
                aria-hidden
              />
            </button>
          </div>
        </div>
      </Card>

      {/* Credits */}
      <div className="text-center py-4 text-xs text-content-quaternary">
        <p className="flex items-center justify-center gap-1">
          {PRODUCT_DEVELOPER_LINE}
          {' · '}
          <a href={SITE_URL} target="_blank" rel="noopener noreferrer" className="hover:text-oe-blue transition-colors">
            {SITE_HOST}
          </a>
        </p>
        <p className="mt-1">{COPYRIGHT}</p>
        <p className="mt-1">{UPSTREAM_ATTRIBUTION}</p>
      </div>
    </div>
  );
}
