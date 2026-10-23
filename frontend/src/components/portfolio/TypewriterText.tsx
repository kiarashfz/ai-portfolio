"use client";

import { useState, useEffect } from "react";

interface Props {
  text: string;
  speed?: number; // ms per character
  onComplete?: () => void;
}

export default function TypewriterText({ text, speed = 18, onComplete }: Props) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    setDisplayed("");
    setDone(false);
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) {
        clearInterval(interval);
        setDone(true);
        onComplete?.();
      }
    }, speed);
    return () => clearInterval(interval);
  }, [text, speed]);

  return (
    <span>
      {displayed}
      {!done && (
        <span className="ml-0.5 inline-block h-3.5 w-px animate-pulse bg-zinc-500 align-middle" />
      )}
    </span>
  );
}