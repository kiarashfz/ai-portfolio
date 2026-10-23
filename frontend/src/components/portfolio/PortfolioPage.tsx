"use client";

import { motion } from "framer-motion";
import { Portfolio } from "./types";
import PortfolioHero from "./PortfolioHero";
import PortfolioContent from "./PortfolioContent";
import ChatBox from "./ChatBox";

interface Props {
  portfolio: Portfolio;
}

export const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: {
    delay,
    duration: 0.6,
    ease: [0.25, 0.1, 0.25, 1] as const,
  },
});

export default function PortfolioPage({ portfolio }: Props) {
  if (!portfolio) return null;

  return (
    <div className="min-h-screen bg-[#fafaf9]">
      {/* Subtle grid */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(rgba(0,0,0,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,0.025) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
        }}
      />

      <div className="relative mx-auto max-w-7xl px-6 lg:px-16">
        <div className="lg:grid lg:grid-cols-[300px_1fr] lg:gap-20">

          {/* ── LEFT SIDEBAR: sticky, holds identity ── */}
          <aside className="lg:sticky lg:top-0 lg:h-screen lg:flex lg:flex-col lg:justify-between lg:py-20 pt-14 pb-0">
            <motion.div {...fadeUp(0)}>
              <PortfolioHero portfolio={portfolio} />
            </motion.div>

            <motion.div {...fadeUp(0.4)} className="hidden lg:block mt-auto">
              <p className="text-xs text-zinc-400">
                portfoliogpt.com/{portfolio.username}
              </p>
              <a
                href="/"
                className="mt-1 block text-xs text-zinc-300 hover:text-zinc-500 transition-colors"
              >
                Powered by PortfolioGPT
              </a>
            </motion.div>
          </aside>

          {/* ── RIGHT: main scrollable area ── */}
          <main className="py-14 lg:py-20 flex flex-col gap-14">

            {/* Chat — prominent, first thing visitor sees */}
            <motion.div {...fadeUp(0.1)}>
              <ChatBox username={portfolio.username} portfolio={portfolio} />
            </motion.div>

            {/* Full portfolio content */}
            <motion.div {...fadeUp(0.2)}>
              <PortfolioContent portfolio={portfolio} />
            </motion.div>

            {/* Mobile-only footer */}
            <motion.div
              {...fadeUp(0.3)}
              className="lg:hidden flex items-center justify-between border-t border-zinc-200 pt-8 text-xs text-zinc-400 pb-12"
            >
              <span>portfoliogpt.com/{portfolio.username}</span>
              <a href="/" className="hover:text-zinc-600 transition-colors">
                Powered by PortfolioGPT
              </a>
            </motion.div>
          </main>

        </div>
      </div>
    </div>
  );
}
