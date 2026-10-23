"use client";

import { Portfolio } from "./types";

interface Props {
  portfolio: Portfolio;
}

export default function PortfolioHero({ portfolio }: Props) {
  const initials = `${portfolio.firstName?.[0] ?? ""}${portfolio.lastName?.[0] ?? ""}`;

  return (
    <div className="flex flex-col gap-6">
      {/* Avatar */}
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-zinc-900 text-xl font-bold text-white shadow-md">
        <span>{initials}</span>
      </div>

      {/* Name — the hero of the page */}
      <div>
        <h1 className="text-4xl font-bold leading-tight tracking-tight text-zinc-900 lg:text-5xl">
          <span>{portfolio.firstName}</span>
          <br />
          <span>{portfolio.lastName}</span>
        </h1>

        {portfolio.title && (
          <p className="mt-2 text-base font-medium text-zinc-500">
            {portfolio.title}
          </p>
        )}
      </div>

      {/* Summary */}
      {portfolio.summary && (
        <p className="text-sm leading-relaxed text-zinc-500 max-w-xs">
          {portfolio.summary}
        </p>
      )}

      {/* Social links */}
      <div className="flex flex-col gap-2">
        {portfolio.links?.github && (
          <SocialLink href={portfolio.links.github} label="GitHub">
            <GithubIcon />
          </SocialLink>
        )}
        {portfolio.links?.linkedin && (
          <SocialLink href={portfolio.links.linkedin} label="LinkedIn">
            <LinkedinIcon />
          </SocialLink>
        )}
        {portfolio.links?.website && (
          <SocialLink href={portfolio.links.website} label="Website">
            <GlobeIcon />
          </SocialLink>
        )}
      </div>
    </div>
  );
}

function SocialLink({
  href,
  label,
  children,
}: {
  href: string;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-900 transition-colors w-fit"
    >
      <span className="text-zinc-400">{children}</span>
      <span>{label}</span>
    </a>
  );
}

function GithubIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
    </svg>
  );
}

function LinkedinIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
    </svg>
  );
}

function GlobeIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10" />
      <path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" />
    </svg>
  );
}
