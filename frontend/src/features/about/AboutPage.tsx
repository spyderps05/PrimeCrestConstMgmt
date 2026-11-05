// DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest​‌‍⁠​‌‍⁠​‌‍⁠​‌‍⁠
// Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
/**
 * AboutPage — Application info, author, license, consulting services.
 */

import { useEffect, useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Mail, Shield, BookOpen, Users, Award,
  Briefcase, Globe, ExternalLink,
  Linkedin, Rocket, ArrowRight,
  MessageCircle, ChevronDown,
  MessageSquareQuote,
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

// Clean product URL - "?source=search" is G2's search-result tracking.
const G2_REVIEWS_URL = 'https://www.g2.com/products/openconstructionerp/reviews';

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
            'Shows your installed version, recent release notes, the proprietary licence notice, and product information for PrimeCrest Construction Management by Spyder Solutions. Use it to confirm what build you are on before reporting an issue or planning an upgrade.',
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
          <div className="flex items-center justify-center lg:justify-start gap-2 mb-4">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
            </span>
            <span className="text-xs font-semibold uppercase tracking-widest text-emerald-600">Proprietary</span>
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
            <Badge variant="blue" size="sm">All rights reserved</Badge>
          </div>
          <p className="mt-4 max-w-xl text-xs leading-relaxed text-content-tertiary" data-testid="about-legal-notice">
            {t('about.legal_notice', { defaultValue: PRODUCT_LEGAL_NOTICE })}
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

      {/* Two-card band: Platform Capabilities + Community.
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
          {/* Stats — one row on wide screens (6 tiles × 1 row) so the card
              stays compact and lines up vertically with the right-hand
              Community card. Smaller tile padding + value font keep the
              shorter tile readable at narrower widths. */}
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

      {/* ── Card 2: Community — feedback channels.
          Uses the same blue-tinted gradient the old embedded block had, so
          the visual identity carries over but as its own bordered Card. ── */}
      <Card
        padding="none"
        className="animate-card-in h-full flex flex-col overflow-hidden border-oe-blue/20 bg-gradient-to-br from-oe-blue/5 via-transparent to-blue-50/40 dark:from-blue-950/20 dark:via-transparent dark:to-slate-900/30"
        style={{ animationDelay: '75ms' }}
      >
        <div className="p-6 flex flex-col flex-1">
            <div className="flex items-start gap-3 mb-4">
              {/* Plain Stroke — community icon, no chip wrapper. r-cleanup 2026-05-11. */}
              <MessageCircle size={20} strokeWidth={1.75} className="shrink-0 mt-0.5 text-oe-blue" />
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-content-primary">
                  {t('about.community_title', { defaultValue: 'Join the community - your feedback shapes the roadmap' })}
                </h3>
                <p className="text-xs text-content-secondary mt-1 leading-relaxed">
                  {t('about.community_desc', {
                    defaultValue:
                      'Share what works, what breaks, and what you want next. Every release in the changelog started as a user request. Pick the channel you already use - we read all three.',
                  })}
                </p>
              </div>
            </div>

            {/* Social channels — Telegram is featured on its own row (it's the
                primary live-support channel) so the chat invite reads first.
                LinkedIn and X follow on their own rows so the Community card
                stretches vertically to match the Platform Capabilities card
                on wide screens. Each tile carries a 2-line copy block instead
                of a 1-line truncated string. */}
            <div className="flex flex-col gap-2.5">

              {/* Featured row — Telegram, primary live channel. */}
              <a
                href="https://t.me/datadrivenconstruction"
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-center gap-3 rounded-lg border border-[#26A5E4]/25 bg-[#26A5E4]/[0.04] px-3.5 py-3 hover:border-[#26A5E4]/50 hover:bg-[#26A5E4]/[0.08] transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-oe-blue focus-visible:ring-offset-1"
              >
                <span className="shrink-0 h-10 w-10 rounded-lg bg-[#26A5E4]/15 text-[#26A5E4] flex items-center justify-center">
                  <svg viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5" aria-hidden>
                    <path d="M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.19L7.74 13.3 3.64 12c-.88-.25-.89-.86.2-1.3l15.97-6.16c.73-.33 1.43.18 1.15 1.3l-2.72 12.81c-.19.91-.74 1.13-1.5.71l-4.14-3.06-1.99 1.93c-.23.23-.42.42-.83.42z"/>
                  </svg>
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-content-primary leading-tight">
                      Telegram
                    </p>
                    <span className="inline-flex items-center rounded-md bg-[#26A5E4]/15 text-[#26A5E4] text-2xs font-semibold px-1.5 py-0.5">
                      {t('about.community_tg_badge', { defaultValue: 'Live' })}
                    </span>
                  </div>
                  <p className="text-xs text-content-secondary mt-0.5 leading-snug">
                    {t('about.community_telegram_v2', { defaultValue: 'Fastest replies from the maintainers - questions, ideas, bug reports, partnerships.' })}
                  </p>
                </div>
                <ExternalLink size={13} className="text-content-quaternary group-hover:text-[#26A5E4] shrink-0" />
              </a>

              {/* LinkedIn + X — paired on one row so the Community card stays
                  compact and matches the Platform Capabilities card's height. */}
              <div className="grid grid-cols-2 gap-2.5">
                <a
                  href="https://www.linkedin.com/company/78381569"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center gap-2.5 rounded-lg border border-border-light bg-surface-primary px-3 py-2.5 hover:border-[#0A66C2]/50 hover:bg-[#0A66C2]/[0.04] transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-oe-blue focus-visible:ring-offset-1"
                >
                  <span className="shrink-0 h-9 w-9 rounded-lg bg-[#0A66C2]/10 text-[#0A66C2] flex items-center justify-center">
                    <Linkedin size={16} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold text-content-primary leading-tight">
                      LinkedIn
                    </p>
                    <p className="text-2xs text-content-tertiary mt-0.5 leading-snug">
                      {t('about.community_linkedin_short', { defaultValue: 'Articles + industry posts' })}
                    </p>
                  </div>
                </a>

                <a
                  href="https://x.com/datadrivenconst"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center gap-2.5 rounded-lg border border-border-light bg-surface-primary px-3 py-2.5 hover:border-slate-700/50 hover:bg-slate-900/[0.04] dark:hover:border-slate-300/40 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-oe-blue focus-visible:ring-offset-1"
                >
                  <span className="shrink-0 h-9 w-9 rounded-lg bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900 flex items-center justify-center">
                    <svg viewBox="0 0 24 24" fill="currentColor" className="h-3.5 w-3.5" aria-hidden>
                      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231 5.45-6.231zm-1.161 17.52h1.833L7.084 4.126H5.117l11.966 15.644z"/>
                    </svg>
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold text-content-primary leading-tight">
                      X / Twitter
                    </p>
                    <p className="text-2xs text-content-tertiary mt-0.5 leading-snug">
                      {t('about.community_x_short', { defaultValue: 'Release announcements' })}
                    </p>
                  </div>
                </a>
              </div>

              {/* Review on G2 — a review from a real user helps other teams
                  find and trust the project. Full-width row like Telegram. */}
              <a
                href={G2_REVIEWS_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-center gap-3 rounded-lg border border-[#FF492C]/25 bg-[#FF492C]/[0.04] px-3.5 py-3 hover:border-[#FF492C]/50 hover:bg-[#FF492C]/[0.08] transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-oe-blue focus-visible:ring-offset-1"
              >
                <span className="shrink-0 h-10 w-10 rounded-lg bg-[#FF492C]/15 text-[#FF492C] flex items-center justify-center">
                  <MessageSquareQuote size={18} />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-content-primary leading-tight">
                      {t('about.community_g2_title', { defaultValue: 'Review us on G2' })}
                    </p>
                    <span className="inline-flex items-center rounded-md bg-[#FF492C]/15 text-[#FF492C] text-2xs font-semibold px-1.5 py-0.5">
                      {t('about.community_g2_badge', { defaultValue: 'Means a lot' })}
                    </span>
                  </div>
                  <p className="text-xs text-content-secondary mt-0.5 leading-snug">
                    {t('about.community_g2_desc', { defaultValue: 'We would be grateful if you rate us or write a short review - it helps other construction teams find and trust the platform.' })}
                  </p>
                </div>
                <ExternalLink size={13} className="text-content-quaternary group-hover:text-[#FF492C] shrink-0" />
              </a>
            </div>

            <p className="mt-auto pt-4 text-[11px] text-content-tertiary text-center">
              {t('about.community_cta', {
                defaultValue:
                  'Have a feature idea? A bug? A workflow we haven\'t thought of? Drop a message - we reply.',
              })}
            </p>
        </div>
      </Card>

      </div>
      {/* /Two-card band */}

      {/* About the project — founder's note (left) + DDC ecosystem (right).
          Two-column inside one Card so heights stay synced on wide screens.
          On narrow screens the right column stacks below. */}
      <Card className="animate-card-in" style={{ animationDelay: '150ms' }}>
        <div className="p-6 grid grid-cols-1 lg:grid-cols-5 gap-x-8 gap-y-6">
          {/* ── Left column — narrative (3 of 5 cols on wide screens) ── */}
          <div className="lg:col-span-3">
          {/* Block heading — short, sets context for the bio below. */}
          <div className="mb-5 flex items-center gap-2">
            <BookOpen size={18} className="text-oe-blue" />
            <h2 className="text-lg font-semibold text-content-primary">
              {t('about.story_title', { defaultValue: 'About the project' })}
            </h2>
          </div>
          <p className="mb-5 text-sm text-content-secondary">
            {t('about.story_subtitle', { defaultValue: 'Why PrimeCrest Construction Management exists, and where it\'s going.' })}
          </p>
          {/* Bio — line length now governed by the col width itself. */}
          <div>
            <div className="min-w-0 flex-1">
              <div className="space-y-3 text-sm text-content-secondary leading-relaxed">
                <p>
                  {t('about.founder_bio_p1', {
                    defaultValue:
                      'For the past decade our team has worked on resource management for construction projects. Along the way we got curious about how the industry\'s tools came to be - from the first attempts at design automation to today\'s ERP platforms - and that turned into a couple of longer pieces ("The Lobbyists\' Wars and the Development of BIM" and "The History of the BIM Map"). It\'s hard to see where things are heading without a sense of how we got here.',
                  })}
                </p>
                <p>
                  <Trans
                    i18nKey="about.founder_bio_p2"
                    defaults='We&rsquo;ve written a fair amount on these topics over the years, and some of it found a wide readership. Alongside the writing, we&rsquo;ve consulted for construction and consulting firms, developers, and software vendors on how they handle project data - treating it as the basis for decisions rather than a byproduct of them. That work let us see the industry from both sides: the people who build the tools, and the people who use them every day. A lot of those observations ended up in the book <book>Data-Driven Construction</book>, now available in 16 languages (<books>datadrivenconstruction.io/books</books>). It is free of charge in every one of them.'
                    components={{
                      book: (
                        <a
                          href="https://datadrivenconstruction.io/books"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-oe-blue hover:underline italic font-medium"
                        />
                      ),
                      books: (
                        <a
                          href="https://datadrivenconstruction.io/books"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-oe-blue hover:underline"
                        />
                      ),
                    }}
                  />
                </p>
                <p>
                  <Trans
                    i18nKey="about.founder_bio_p3"
                    defaults='Two other problems kept us busy. One was helping teams work with file formats that were never meant to be opened. The other was finding a clearer way to describe construction work through a resource model. PrimeCrest Construction Management, the product on this page, is proprietary software of Spyder Solutions. It is not free and it is not built in the open.'
                    components={{
                      cad: (
                        <a
                          href="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-oe-blue hover:underline font-medium"
                        />
                      ),
                      gh: (
                        <a
                          href="https://github.com/datadrivenconstruction"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-oe-blue hover:underline"
                        />
                      ),
                      cwicr: (
                        <a
                          href="https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-oe-blue hover:underline font-medium"
                        />
                      ),
                    }}
                  />
                </p>
                <blockquote className="my-4 rounded-r-lg border-l-4 border-oe-blue bg-oe-blue/[0.04] py-3 px-4 text-[15px] italic text-content-primary leading-relaxed">
                  {t('about.founder_bio_p4', {
                    defaultValue:
                      "All of it was groundwork for something we'd wanted to build for a long time: a modular construction management platform. The latest generation of tooling finally made it practical to pull the methodology, data models, and earlier implementations together into one product owned by Spyder Solutions.",
                  })}
                </blockquote>
                <p className="border-l-2 border-oe-blue/40 pl-3 italic text-content-primary">
                  {t('about.founder_bio_p5', {
                    defaultValue:
                      'In our experience the best ideas tend to come out of conversation - and out of disagreement. If the questions around construction\'s move toward "Uberization," and toward more transparent cost and time estimation, are interesting to you, we\'d be glad to have you in that discussion.',
                  })}
                </p>
              </div>
              {/* Author attribution — moved to the bottom of the bio per request. */}
              <div className="mt-5 flex items-center gap-3 border-t border-border-light pt-4">
                <img
                  src="/brand/ddc-logo.webp"
                  alt={t('about.team_name', { defaultValue: PRODUCT_DEVELOPER })}
                  className="h-12 w-12 shrink-0 rounded-xl object-cover bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-800 dark:to-slate-900 ring-1 ring-border-light shadow-sm p-1.5"
                  loading="lazy"
                />
                <div className="min-w-0 flex-1">
                  <h3 className="flex items-center gap-1.5 text-base font-bold text-content-primary leading-tight">
                    {t('about.team_name', { defaultValue: PRODUCT_DEVELOPER })}
                    <span
                      className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded text-oe-blue"
                      title={t('about.team_linkedin', { defaultValue: 'Spyder Solutions' })}
                      aria-label={t('about.team_linkedin', { defaultValue: 'Spyder Solutions' })}
                    >
                      <Linkedin size={15} />
                    </span>
                  </h3>
                  <p className="text-xs text-oe-blue font-medium mt-0.5">
                    {t('about.team_role', { defaultValue: 'Automation, data and open standards for construction' })}
                  </p>
                </div>
              </div>
              {/* Social buttons removed — the same links live in the right
                  column's "Find us across the network" row, so the bio side
                  stays clean and the social channels are not duplicated. */}
            </div>
          </div>
          </div>
          {/* /Left column */}

          {/* ── Right column — developer + legal ── */}
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
                {t('about.legal_notice', { defaultValue: PRODUCT_LEGAL_NOTICE })}
              </p>
            </div>
            <div className="mb-6 rounded-lg border border-border-light bg-surface-secondary/40 px-3.5 py-3.5">
              <p className="text-xs font-semibold text-content-primary leading-tight">
                {PRODUCT_NAME}
              </p>
              <p className="text-[11px] text-content-tertiary mt-1 leading-snug">
                {t('about.repo_desc', { defaultValue: '© 2026 Spyder Solutions. All rights reserved.' })}
              </p>
              <p className="text-[11px] text-content-tertiary mt-2 leading-snug">
                {t('about.third_party_hint', {
                  defaultValue: 'Third-party component licences are listed below on this page.',
                })}
              </p>
            </div>
          </aside>
          {/* /Right column */}
        </div>
      </Card>

      {/* Consulting Services — matches the "Build 01 / Workshops 02 / Consulting 03"
          structure on openconstructionerp.com so users coming from the marketing
          page see the same offering shape inside the product. */}
      <Card>
        <div className="p-6">
          <div className="flex items-center gap-2 mb-2">
            <Briefcase size={18} className="text-oe-blue" />
            <h2 className="text-lg font-semibold text-content-primary">
              {t('about.services_title', { defaultValue: 'Consulting & Professional Services' })}
            </h2>
          </div>
          <p className="text-sm text-content-secondary leading-relaxed mb-5 max-w-3xl">
            {t('about.services_desc_v2', { defaultValue: 'Need a custom build, a workshop, or an outside expert on data + cost workflows? Spyder Solutions delivers three engagement shapes - pick what fits and we scope from there.' })}
          </p>

          {/* Three numbered service cards — Build · Workshops · Consulting */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              {
                num: '01',
                icon: Rocket,
                title: t('about.svc_build_title', { defaultValue: 'Custom Build' }),
                tagline: t('about.svc_build_tagline', { defaultValue: 'FROM 4 WEEKS' }),
                desc: t('about.svc_build_desc', { defaultValue: 'Discovery → workshop → modules picked → built → deployed on your hardware. Source delivered.' }),
                bullets: [
                  t('about.svc_build_b1', { defaultValue: '4–12 weeks engagement' }),
                  t('about.svc_build_b2', { defaultValue: 'Proprietary commercial licence' }),
                  t('about.svc_build_b3', { defaultValue: '30 days post-launch support' }),
                ],
              },
              {
                num: '02',
                icon: Users,
                title: t('about.svc_workshop_title', { defaultValue: 'Workshops' }),
                tagline: t('about.svc_workshop_tagline', { defaultValue: '1–3 DAYS · ON-SITE OR REMOTE' }),
                desc: t('about.svc_workshop_desc', { defaultValue: 'Hands-on sessions: estimating, BIM-to-BOQ, AI takeoff, GAEB pipelines. Recorded for your team library.' }),
                bullets: [
                  t('about.svc_workshop_b1', { defaultValue: 'Up to 12 participants' }),
                  t('about.svc_workshop_b2', { defaultValue: 'Tailored agenda + exercises' }),
                  t('about.svc_workshop_b3', { defaultValue: 'Slides + recordings retained by client' }),
                ],
              },
              {
                num: '03',
                icon: Briefcase,
                title: t('about.svc_consulting_title', { defaultValue: 'Consulting' }),
                tagline: t('about.svc_consulting_tagline', { defaultValue: 'BY THE DAY · OR RETAINER' }),
                desc: t('about.svc_consulting_desc', { defaultValue: 'Standards mapping, cost-DB strategy, pipeline architecture, code review.' }),
                bullets: [
                  t('about.svc_consulting_b1', { defaultValue: 'Async review option' }),
                  t('about.svc_consulting_b2', { defaultValue: 'Outcome document + recommendations' }),
                  t('about.svc_consulting_b3', { defaultValue: 'Rollover into custom build' }),
                ],
              },
            ].map(svc => (
              <div
                key={svc.num}
                className="group relative flex flex-col rounded-2xl border border-border-light bg-surface-secondary/30 p-5 hover:border-oe-blue/40 hover:bg-oe-blue/[0.025] hover:shadow-sm transition-all"
              >
                {/* Numbered badge — Build 01 / Workshops 02 / Consulting 03 */}
                <div className="flex items-center gap-3 mb-3">
                  <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-oe-blue/10 text-oe-blue font-mono text-sm font-bold ring-1 ring-oe-blue/20">
                    {svc.num}
                  </span>
                  <svc.icon size={18} className="text-content-tertiary group-hover:text-oe-blue transition-colors" />
                </div>

                <h3 className="text-base font-bold text-content-primary mb-0.5">{svc.title}</h3>
                <p className="text-[11px] font-semibold uppercase tracking-wider text-oe-blue mb-3">
                  {svc.tagline}
                </p>
                <p className="text-xs text-content-secondary leading-relaxed mb-4">
                  {svc.desc}
                </p>

                <ul className="mt-auto space-y-1.5">
                  {svc.bullets.map((b, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-content-secondary">
                      <ArrowRight size={11} className="mt-1 shrink-0 text-oe-blue" />
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Trusted-by chip list — public client engagements from the site */}
          <div className="mt-6 pt-5 border-t border-border-light">
            <p className="mb-3 text-2xs font-semibold uppercase tracking-wider text-content-tertiary">
              {t('about.svc_trusted_label', { defaultValue: 'Selected engagements' })}
            </p>
            <div className="flex flex-wrap items-center gap-1.5">
              {[
                'Drees & Sommer',
                'Lindner Group',
                'OTWB',
                'ShapeMaker',
                'Bauindustrie Bayern',
                'TUM',
                'BIM Cluster BW',
                'BIM DAY GENF',
                'Herbert Gruppe',
              ].map(name => (
                <span
                  key={name}
                  className="inline-flex items-center rounded-md border border-border-light bg-surface-primary px-2.5 py-1 text-xs text-content-secondary"
                >
                  {name}
                </span>
              ))}
              <span className="inline-flex items-center rounded-md border border-border-light bg-surface-secondary/40 px-2.5 py-1 text-xs text-content-tertiary italic">
                {t('about.svc_trusted_more', { defaultValue: '+ engagements under NDA' })}
              </span>
            </div>
          </div>

          {/* CTA row — primary contact button (case-studies link removed per
              user request 2026-05-20). */}
          <div className="mt-5 flex flex-wrap items-center gap-3">
            <a href="https://datadrivenconstruction.io/contact-support/" target="_blank" rel="noopener noreferrer">
              <Button variant="primary" size="md" icon={<Mail size={15} />}>
                {t('about.contact_us', { defaultValue: 'Contact Us' })}
              </Button>
            </a>
          </div>
        </div>
      </Card>

      {/* Documentation block — moved down next to License (2-col reference band). */}

      {/* Free Guidebook — 5-col internal split: book cover gets 2/5 of the
          width so the cover image can render larger; the 10-part TOC keeps
          3/5 and its tiles read tighter and more uniform. */}
      <Card className="animate-card-in" style={{ animationDelay: '300ms' }}>
        <div className="p-6 grid grid-cols-1 lg:grid-cols-5 gap-6">

          {/* ── Left column — larger book cover + headline + download CTA ── */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2 mb-3 flex-wrap">
              <BookOpen size={18} className="text-oe-blue" />
              <h2 className="text-lg font-semibold text-content-primary">
                {t('about.book_title', { defaultValue: 'Data-Driven Construction' })}
              </h2>
              <Badge variant="blue" size="sm">Free</Badge>
            </div>
            <p className="text-xs text-content-tertiary mb-4">
              {t('about.book_subtitle', { defaultValue: 'Developed by Spyder Solutions' })}
            </p>
            <a
              href="https://datadrivenconstruction.io/books/"
              target="_blank"
              rel="noopener noreferrer"
              className="group block overflow-hidden rounded-xl bg-gradient-to-br from-slate-50 via-white to-blue-50 dark:from-slate-900 dark:via-slate-900 dark:to-slate-800 border border-border-light hover:border-oe-blue/40 hover:shadow-lg transition-all max-w-[320px] mx-auto lg:mx-0"
              title={t('about.book_cta', { defaultValue: 'Pick your language on datadrivenconstruction.io' })}
            >
              <img
                src="/brand/ddc-book.png"
                alt={t('about.book_title', { defaultValue: 'Data-Driven Construction' })}
                className="block w-full h-auto transition-transform duration-500 group-hover:scale-[1.02]"
                loading="lazy"
              />
            </a>
            <a
              href="https://datadrivenconstruction.io/books/"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-oe-blue px-4 py-2 text-sm font-medium text-white hover:bg-oe-blue-hover transition-colors shadow-sm"
            >
              <BookOpen size={16} />
              {t('about.book_download', { defaultValue: 'Download Free' })}
              <ExternalLink size={14} />
            </a>
          </div>
          {/* /Left column */}

          {/* ── Right column — Part-level table of contents (narrower) ── */}
          <div className="lg:col-span-3">
            <p className="text-2xs font-semibold uppercase tracking-wider text-content-tertiary mb-3">
              {t('about.book_toc_label', { defaultValue: 'Inside the book - 10 parts' })}
            </p>
            <ol className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {[
                { num: 'I',    title: t('about.book_p1',  { defaultValue: 'How information has evolved in construction' }) },
                { num: 'II',   title: t('about.book_p2',  { defaultValue: 'How the construction business is drowning in data chaos' }) },
                { num: 'III',  title: t('about.book_p3',  { defaultValue: 'Data framework in construction business processes' }) },
                { num: 'IV',   title: t('about.book_p4',  { defaultValue: 'Data quality: organization, structuring, modeling' }) },
                { num: 'V',    title: t('about.book_p5',  { defaultValue: 'Cost & time calculations: incorporating data into processes' }) },
                { num: 'VI',   title: t('about.book_p6',  { defaultValue: 'CAD & BIM - marketing, reality and the future of design data' }) },
                { num: 'VII',  title: t('about.book_p7',  { defaultValue: 'Data-driven decision-making, analytics and automation' }) },
                { num: 'VIII', title: t('about.book_p8',  { defaultValue: 'Data storage and management in construction' }) },
                { num: 'IX',   title: t('about.book_p9',  { defaultValue: 'Big Data, machine learning and forecasts' }) },
                { num: 'X',    title: t('about.book_p10', { defaultValue: 'The construction industry in the digital age - opportunities & challenges' }) },
              ].map(p => (
                <li key={p.num} className="group flex items-start gap-2.5 rounded-lg border border-border-light bg-surface-secondary/30 px-3 py-2.5 hover:border-oe-blue/30 hover:bg-oe-blue/[0.025] transition-colors">
                  <span className="shrink-0 inline-flex h-6 min-w-[2rem] items-center justify-center rounded-md bg-oe-blue/10 text-oe-blue font-mono text-2xs font-bold ring-1 ring-oe-blue/20 px-1.5">
                    {p.num}
                  </span>
                  <span className="text-xs text-content-secondary leading-snug group-hover:text-content-primary transition-colors">
                    {p.title}
                  </span>
                </li>
              ))}
            </ol>
            <p className="mt-3 text-2xs text-content-tertiary italic">
              {t('about.book_toc_note', { defaultValue: '173 chapters total. Free to read online or download.' })}
            </p>
          </div>
          {/* /Right column */}

        </div>
      </Card>

      {/* Reference band — Documentation + License side-by-side with matched heights. */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">

        {/* Documentation — same h-full + flex-col + mt-auto pattern as License so
            both cards land their CTA button on the same baseline. The body is
            enriched with a "Popular topics" 2x3 mini-grid to fill the column
            instead of leaving whitespace below the 4 high-level bullets. */}
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

            {/* ── Popular topics — deep-links into the repo's docs/ tree on
                GitHub (the marketing-site docs.html 404s). Topics with a
                dedicated doc file link straight to it; the rest fall back to
                the browsable docs/ tree root. ── */}
            <p className="mb-2 text-2xs font-semibold uppercase tracking-wider text-content-tertiary">
              {t('about.docs_popular_label', { defaultValue: 'Popular topics' })}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {[
                { id: 'quickstart', href: 'https://datadrivenconstruction.io', label: t('about.docs_pop_quickstart', { defaultValue: 'Quick start - Docker compose' }) },
                { id: 'bim', href: 'https://datadrivenconstruction.io', label: t('about.docs_pop_bim', { defaultValue: 'Import BIM (RVT/IFC) → BOQ' }) },
                { id: 'gaeb', href: 'https://datadrivenconstruction.io', label: t('about.docs_pop_gaeb', { defaultValue: 'GAEB X83/X84 import & export' }) },
                { id: 'takeoff', href: 'https://datadrivenconstruction.io', label: t('about.docs_pop_takeoff', { defaultValue: 'PDF takeoff with annotations' }) },
                { id: 'sdk', href: 'https://datadrivenconstruction.io/module-development', label: t('about.docs_pop_sdk', { defaultValue: 'Module SDK · write a plugin' }) },
                { id: 'deploy', href: 'https://datadrivenconstruction.io', label: t('about.docs_pop_deploy', { defaultValue: 'VPS deployment guide' }) },
              ].map(topic => (
                <a
                  key={topic.id}
                  href={topic.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center justify-between gap-2 rounded-lg border border-border-light bg-surface-secondary/40 px-3 py-2 hover:border-oe-blue/40 hover:bg-oe-blue/[0.04] transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-oe-blue focus-visible:ring-offset-1"
                >
                  <span className="text-2xs text-content-secondary group-hover:text-content-primary leading-snug">
                    {topic.label}
                  </span>
                  <ArrowRight size={11} className="shrink-0 text-content-quaternary group-hover:text-oe-blue group-hover:translate-x-0.5 transition-all" />
                </a>
              ))}
            </div>

            <div className="mt-auto pt-4">
              <a href="https://datadrivenconstruction.io" target="_blank" rel="noopener noreferrer">
                <Button variant="primary" size="md" icon={<BookOpen size={15} />}>
                  {t('about.docs_open', { defaultValue: 'Open Docs' })}
                </Button>
              </a>
            </div>
          </div>
        </Card>

        {/* License — restructured into "You can / You must" so users see the
            licence terms at a glance instead of reading prose. CTA at bottom
            matches the Documentation card's "Open Docs" button position. */}
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
                <p className="text-xs text-content-tertiary">
                  {t('about.license_subtitle', { defaultValue: '© 2026 Spyder Solutions. All rights reserved.' })}
                </p>
              </div>
            </div>
            <p className="text-sm text-content-secondary leading-relaxed mb-4">
              {t('about.license_desc_short', { defaultValue: 'PrimeCrest Construction Management Software is proprietary. No one may copy, modify, or redistribute it without written permission from Spyder Solutions.' })}
            </p>

            {/* ── You can / You must — concrete bullet pairs so the
                obligations are visible before download, not after lawyers. ── */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-3 mb-4">
              <div>
                <p className="mb-1.5 text-2xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                  {t('about.license_youcan_label', { defaultValue: 'You can' })}
                </p>
                <ul className="space-y-1 text-xs text-content-secondary leading-snug">
                  {[
                    t('about.license_youcan_1', { defaultValue: 'Use under your Spyder Solutions licence' }),
                    t('about.license_youcan_2', { defaultValue: 'Self-host on your own hardware' }),
                    t('about.license_youcan_3', { defaultValue: 'Configure modules for your organisation' }),
                    t('about.license_youcan_4', { defaultValue: 'Request custom modules from Spyder Solutions' }),
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
                    t('about.license_youmust_1', { defaultValue: 'Keep the software confidential' }),
                    t('about.license_youmust_2', { defaultValue: 'Do not copy or redistribute the product' }),
                    t('about.license_youmust_3', { defaultValue: 'Keep copyright notices intact' }),
                    t('about.license_youmust_4', { defaultValue: 'Obtain written permission for any redistribution' }),
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
              <Badge variant="success" size="sm">{t('about.license_badge_free', { defaultValue: 'Proprietary' })}</Badge>
              <Badge variant="success" size="sm">{t('about.license_badge_oss', { defaultValue: 'All rights reserved' })}</Badge>
              <Badge variant="success" size="sm">{t('about.license_badge_selfhost', { defaultValue: 'Self-hosted' })}</Badge>
              <Badge variant="success" size="sm">{t('about.license_badge_nolockin', { defaultValue: 'No vendor lock-in' })}</Badge>
              <Badge variant="blue" size="sm">© Spyder Solutions</Badge>
            </div>

            {/* Third-party components. The proprietary notice above is the product licence and
                not the whole story: the build also redistributes LGPL-2.1 and
                LGPL-3.0 components, and their texts ship inside the artefact
                where nothing could read them until /api/v1/licenses/. */}
            <ThirdPartyLicenses className="mb-4" />

            <div className="mt-auto pt-3 border-t border-border-light">
              <p className="text-xs text-content-secondary mb-2">
                {t('about.license_commercial_short', { defaultValue: 'Need an enterprise licence or SLA?' })}
              </p>
              <a href="https://datadrivenconstruction.io/contact-support/" target="_blank" rel="noopener noreferrer">
                <Button variant="secondary" size="md" icon={<Shield size={15} />}>
                  {t('about.license_commercial_cta', { defaultValue: 'Commercial licensing' })}
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

      {/* Development and Contribution Model */}
      <Card padding="md" className="mt-6">
        <h2 className="text-lg font-semibold text-content-primary mb-3">
          {t('about.dev_model_title', { defaultValue: 'Development and Contribution Model' })}
        </h2>
        <div className="space-y-2 text-sm text-content-secondary leading-relaxed">
          <p>
            {t('about.dev_model_p1', { defaultValue: 'PrimeCrest Construction Management is developed by Spyder Solutions, with ongoing product work, feedback, testing, and domain expertise from construction professionals.' })}
          </p>
          <p>
            {t('about.dev_model_p2', { defaultValue: 'To maintain a consistent architecture and reduce security, dependency, and integration risks, Spyder Solutions follows a centralized integration model. Production code is reviewed, consolidated, and tested before release.' })}
          </p>
          <p>
            {t('about.dev_model_p3', { defaultValue: 'Rather than allowing the codebase to evolve into a collection of loosely connected components, changes are integrated into one coherent development line and undergo review and testing before being merged into the main project. A single publishing account represents a controlled integration and release process designed to preserve stability, security, and architectural consistency.' })}
          </p>
        </div>
      </Card>

      {/* Credits */}
      <div className="text-center py-4 text-xs text-content-quaternary">
        <p className="flex items-center justify-center gap-1">
          {t('about.built_by', { defaultValue: `Developed by ${PRODUCT_DEVELOPER}` })}
          {' · '}
          <a href="https://datadrivenconstruction.io" target="_blank" rel="noopener noreferrer" className="hover:text-oe-blue transition-colors">
            datadrivenconstruction.io
          </a>
        </p>
        <p className="mt-1">&copy; 2026 Spyder Solutions. All rights reserved.</p>
      </div>
    </div>
  );
}
