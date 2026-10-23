"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";
import { Button } from "@/components/ui/button";
import Link from "next/link";

interface Props {
  username: string;
  onEdit: () => void;
}

export default function Celebration({ username, onEdit }: Props) {
  const [giftOpen, setGiftOpen] = useState(false);
  const [linkVisible, setLinkVisible] = useState(false);
  const [copied, setCopied] = useState(false);
  const hasRun = useRef(false);
  const portfolioUrl = `portfoliogpt.com/${username}`;

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    // Burst confetti
    const end = Date.now() + 2200;
    const colors = ["#18181b", "#71717a", "#d4d4d8", "#f4f4f5"];

    (function frame() {
      confetti({
        particleCount: 3,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors,
      });
      confetti({
        particleCount: 3,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors,
      });
      if (Date.now() < end) requestAnimationFrame(frame);
    })();

    // Sequence: gift box opens → link appears
    setTimeout(() => setGiftOpen(true), 600);
    setTimeout(() => setLinkVisible(true), 1400);
  }, []);

  function handleCopy() {
    navigator.clipboard.writeText(`https://${portfolioUrl}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center py-24 text-center"
    >
      {/* Heading */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.5 }}
      >
        <p className="text-xs font-medium uppercase tracking-widest text-zinc-400">
          You're live
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight text-zinc-900">
          Your portfolio is ready 🎉
        </h1>
        <p className="mt-3 text-zinc-500 max-w-sm mx-auto">
          Your AI-powered portfolio is now live. Share it anywhere and let your work speak for itself.
        </p>
      </motion.div>

      {/* Gift box */}
      <motion.div
        className="mt-14 relative cursor-pointer select-none"
        onClick={() => {
          if (!giftOpen) {
            setGiftOpen(true);
            setTimeout(() => setLinkVisible(true), 800);
          }
        }}
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
      >
        {/* Box body */}
        <motion.div
          className="relative w-52 h-44 rounded-2xl bg-zinc-900 flex items-end justify-center pb-6 shadow-2xl"
          animate={giftOpen ? { scale: [1, 1.04, 1] } : {}}
          transition={{ duration: 0.3 }}
        >
          {/* Ribbon vertical */}
          <div className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-5 bg-zinc-700 rounded-sm" />

          {/* Link revealed inside box */}
          <AnimatePresence>
            {linkVisible && (
              <motion.div
                initial={{ opacity: 0, y: 10, scale: 0.9 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.4, type: "spring", stiffness: 200 }}
                className="relative z-10 bg-white rounded-lg px-4 py-2 shadow-md"
              >
                <span className="font-mono text-xs font-semibold text-zinc-900">
                  {portfolioUrl}
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Box lid */}
        <motion.div
          className="absolute -top-5 left-1/2 -translate-x-1/2 w-60 h-12 rounded-xl bg-zinc-800 shadow-lg flex items-center justify-center"
          animate={giftOpen ? { y: -48, opacity: 0, rotate: -8 } : { y: 0, opacity: 1 }}
          transition={{ duration: 0.5, type: "spring", stiffness: 120 }}
        >
          {/* Ribbon horizontal on lid */}
          <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-5 bg-zinc-700 rounded-sm" />
          {/* Bow */}
          <div className="relative z-10 flex gap-1">
            <div className="w-5 h-5 rounded-full border-4 border-zinc-500" />
            <div className="w-5 h-5 rounded-full border-4 border-zinc-500" />
          </div>
        </motion.div>
      </motion.div>

      {/* Actions */}
      <AnimatePresence>
        {linkVisible && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.4 }}
            className="mt-12 flex flex-col items-center gap-4"
          >
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopy}
                className="flex items-center gap-2 rounded-lg border border-zinc-200 bg-white px-4 py-2.5 text-sm font-medium text-zinc-700 hover:border-zinc-300 hover:bg-zinc-50 transition-all shadow-sm"
              >
                {copied ? "✓ Copied!" : "Copy link"}
              </button>
              <Link href={`/${username}`} target="_blank">
                <Button size="sm" className="px-4 py-2.5">
                  Visit portfolio ↗
                </Button>
              </Link>
            </div>

            <button
              onClick={onEdit}
              className="text-sm text-zinc-400 hover:text-zinc-700 transition-colors mt-2"
            >
              Edit my details
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
