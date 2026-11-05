// DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
// Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
import clsx from 'clsx';

import { PRODUCT_SHORT_NAME } from '@/shared/lib/productIdentity';

interface LogoProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  animate?: boolean;
  className?: string;
}

/* Icon sizes — compact so the text dominates */
const sizeMap = {
  xs: 'h-5 w-5',
  sm: 'h-6 w-6',
  md: 'h-7 w-7',
  lg: 'h-10 w-10',
  xl: 'h-14 w-14',
};

/**
 * PrimeCrest mark — PC monogram on an ink shield with copper accent.
 *
 * `animate` triggers a staggered entrance on the shield and letters.
 */
export function Logo({ size = 'md', animate = false, className }: LogoProps) {
  const gradientId = `pc-lg-${size}-${animate ? 'a' : 's'}`;

  const bgStyle = animate
    ? {
        animation: `oeBgScale 450ms cubic-bezier(0.34,1.56,0.64,1) both`,
      }
    : undefined;

  const letterStyle = (delay: number) =>
    animate
      ? {
          animation: `oeWindowFade 400ms ease both`,
          animationDelay: `${delay}ms`,
        }
      : undefined;

  return (
    <div
      className={clsx(sizeMap[size], 'relative shrink-0', className)}
      style={animate ? { animation: 'oeLogoFloat 3s ease-in-out 1.2s infinite, oeLogoGlow 3s ease-in-out 1.2s infinite' } : undefined}
    >
      <svg viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full" aria-hidden>
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#12202B" />
            <stop offset="100%" stopColor="#1A3344" />
          </linearGradient>
        </defs>

        {/* Shield */}
        <path
          d="M256 40 L440 110 V250 C440 360 360 440 256 472 C152 440 72 360 72 250 V110 Z"
          fill={`url(#${gradientId})`}
          style={bgStyle}
        />
        {/* Copper rim */}
        <path
          d="M256 56 L424 120 V248 C424 348 352 420 256 450 C160 420 88 348 88 248 V120 Z"
          fill="none"
          stroke="#C4622D"
          strokeWidth="14"
          opacity=".9"
        />
        {/* PC monogram */}
        <text
          x="256"
          y="292"
          textAnchor="middle"
          fill="#F6F3EE"
          fontFamily="Georgia, 'Times New Roman', serif"
          fontSize="168"
          fontWeight="700"
          letterSpacing="-6"
          style={letterStyle(200)}
        >
          PC
        </text>
        {/* Copper accent bar under letters */}
        <rect x="168" y="328" width="176" height="12" rx="6" fill="#C4622D" style={letterStyle(350)} />
      </svg>
    </div>
  );
}

/* ── LogoWithText ──────────────────────────────────────────────────────── */

interface LogoWithTextProps extends LogoProps {
  showVersion?: boolean;
}

/* Text sizes — larger than icon to make the name prominent */
const textSizeMap = {
  xs: 'text-[15px] leading-none',
  sm: 'text-[16px] leading-none',
  md: 'text-[17px] leading-none',
  lg: 'text-xl leading-none',
  xl: 'text-2xl leading-none',
};

const gapSizeMap = {
  xs: 'gap-1.5',
  sm: 'gap-2',
  md: 'gap-2',
  lg: 'gap-2.5',
  xl: 'gap-3',
};

/**
 * Logo + PrimeCrest wordmark.
 * Display type uses Fraunces / Instrument Serif via --oe-font-display.
 */
export function LogoWithText({ size = 'md', animate, showVersion = true, className }: LogoWithTextProps) {
  return (
    <div className={clsx('flex items-center', gapSizeMap[size], className)}>
      <Logo size={size} animate={animate} />
      <span
        className={clsx(
          textSizeMap[size],
          'font-semibold text-content-primary whitespace-nowrap tracking-tight',
        )}
        style={{ fontFamily: 'var(--oe-font-display)', letterSpacing: '-0.02em' }}
      >
        <span className="text-content-primary">Prime</span>
        <span className="text-oe-blue">Crest</span>
        {showVersion && (
          <span className="ml-1 text-[0.65em] font-normal text-content-quaternary align-middle">
            CM
          </span>
        )}
        <span className="sr-only">{PRODUCT_SHORT_NAME}</span>
      </span>
    </div>
  );
}
