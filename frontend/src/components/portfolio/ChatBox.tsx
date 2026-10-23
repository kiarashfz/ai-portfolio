"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Portfolio, ChatMessage } from "./types";
import TypewriterText from "./TypewriterText";
import { chatApi, ApiError } from "@/lib/api";
import ReactMarkdown from "react-markdown";

interface Props {
  username: string;
  portfolio: Portfolio;
}

// Detect if text contains Persian characters
function hasPersianCharacters(text: string): boolean {
  const persianRegex = /[\u0600-\u06FF]/g;
  return persianRegex.test(text);
}

const SUGGESTED_QUESTIONS = [
  "What's your tech stack?",
  "Tell me about your experience",
  "What are your strongest skills?",
  "What have you built recently?",
];

export default function ChatBox({ username, portfolio }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [streamingId, setStreamingId] = useState<string | null>(null);
  const [hasInteracted, setHasInteracted] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [input]);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isThinking) return;

      setHasInteracted(true);
      setInput("");

      const userMsg: ChatMessage = {
        id: Date.now().toString(),
        role: "user",
        content: trimmed,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsThinking(true);

      try {
        // session_id cookie is sent automatically via credentials: "include" in api.ts
        // The browser stores the cookie after the first response and reuses it
        // giving continuous chat history for this visitor's session
        const res = await chatApi.sendMessage(username, trimmed);
        const reply = res.message;

        const assistantId = (Date.now() + 1).toString();
        setIsThinking(false);
        setStreamingId(assistantId);

        setMessages((prev) => [
          ...prev,
          { id: assistantId, role: "assistant", content: reply, timestamp: new Date() },
        ]);

        setTimeout(() => setStreamingId(null), reply.length * 16 + 500);
      } catch (err) {
        setIsThinking(false);
        let errorMsg = "Something went wrong. Please try again.";
        if (err instanceof ApiError && err.status === 404) {
          errorMsg = "This portfolio doesn't exist yet.";
        }
        setMessages((prev) => [
          ...prev,
          { id: (Date.now() + 1).toString(), role: "assistant", content: errorMsg, timestamp: new Date() },
        ]);
      }
    },
    [isThinking, username]
  );

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-zinc-100 px-5 py-4">
        <div className="relative flex h-8 w-8 items-center justify-center rounded-full bg-zinc-900">
          <span className="text-xs font-bold text-white">AI</span>
          <motion.span
            className="absolute -right-0.5 -top-0.5 h-3 w-3 rounded-full border-2 border-white bg-emerald-400"
            animate={{ scale: [1, 1.3, 1], opacity: [1, 0.6, 1] }}
            transition={{ repeat: Infinity, duration: 2.5, ease: "easeInOut" }}
          />
        </div>
        <div>
          <p className="text-sm font-semibold text-zinc-900">
            Ask {portfolio.firstName} anything
          </p>
          <p className="text-xs text-zinc-400">AI · usually responds instantly</p>
        </div>
      </div>

      {/* Messages */}
      <div
        className="flex flex-col gap-5 overflow-y-auto px-5 py-6"
        style={{ minHeight: 300, maxHeight: 460 }}
      >
        {/* Empty state */}
        {!hasInteracted && messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="flex flex-col items-center justify-center py-10 text-center"
          >
            <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-zinc-100 text-2xl">
              💬
            </div>
            <p className="text-base font-semibold text-zinc-800">
              Chat with {portfolio.firstName}&apos;s AI
            </p>
            <p className="mt-1.5 text-sm text-zinc-400">
              Ask anything about experience, skills, or projects
            </p>
            <div className="mt-7 flex flex-wrap justify-center gap-2">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="rounded-full border border-zinc-200 bg-zinc-50 px-4 py-2 text-xs font-medium text-zinc-600 hover:border-zinc-300 hover:bg-zinc-100 transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Messages */}
        <AnimatePresence initial={false}>
          {messages.map((msg) => {
            const isPersian = hasPersianCharacters(msg.content);
            return (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.25, ease: "easeOut" }}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-zinc-900">
                  <span className="text-[10px] font-bold text-white">AI</span>
                </div>
              )}
              <div
                dir={isPersian ? "rtl" : "ltr"}
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                  msg.role === "user"
                    ? "rounded-tr-sm bg-zinc-900 text-white"
                    : "rounded-tl-sm border border-zinc-200 bg-zinc-50 text-zinc-800"
                }`}
              >
                {msg.role === "assistant" && msg.id === streamingId ? (
                  <TypewriterText text={msg.content} speed={16} />
                ) : (
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => (
                        <p className={`mb-2 last:mb-0 text-sm leading-relaxed ${
                          msg.role === "user" ? "text-white" : "text-zinc-800"
                        }`}>
                          {children}
                        </p>
                      ),
                      strong: ({ children }) => (
                        <strong className={`font-semibold ${
                          msg.role === "user" ? "text-white" : "text-zinc-900"
                        }`}>
                          {children}
                        </strong>
                      ),
                      ul: ({ children }) => (
                        <ul className="mb-2 ml-4 list-disc space-y-1">
                          {children}
                        </ul>
                      ),
                      ol: ({ children }) => (
                        <ol className="mb-2 ml-4 list-decimal space-y-1">
                          {children}
                        </ol>
                      ),
                      li: ({ children }) => (
                        <li className="text-sm">
                          {children}
                        </li>
                      ),
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                )}
              </div>
            </motion.div>
            );
          })}
        </AnimatePresence>

        {/* Thinking dots */}
        <AnimatePresence>
          {isThinking && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex items-end gap-3"
            >
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-zinc-900">
                <span className="text-[10px] font-bold text-white">AI</span>
              </div>
              <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-sm border border-zinc-200 bg-zinc-50 px-4 py-3 shadow-sm">
                {[0, 1, 2].map((i) => (
                  <motion.span
                    key={i}
                    className="block h-1.5 w-1.5 rounded-full bg-zinc-400"
                    animate={{ y: [0, -5, 0], opacity: [0.3, 1, 0.3] }}
                    transition={{ repeat: Infinity, duration: 0.9, delay: i * 0.18, ease: "easeInOut" }}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/*<div ref={bottomRef} />*/}
        <div/>
      </div>

      {/* Input */}
      <div className="border-t border-zinc-100 px-4 py-4">
        <div className="flex items-end gap-3 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3 focus-within:border-zinc-400 focus-within:bg-white transition-all">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`Ask ${portfolio.firstName} something…`}
            rows={1}
            disabled={isThinking}
            dir={hasPersianCharacters(input) ? "rtl" : "ltr"}
            className="flex-1 resize-none bg-transparent text-sm text-zinc-900 placeholder:text-zinc-400 outline-none disabled:opacity-50"
            style={{ maxHeight: 120, overflowY: "auto" }}
          />
          <motion.button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || isThinking}
            whileTap={{ scale: 0.88 }}
            className="mb-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-zinc-900 text-white disabled:opacity-30 disabled:cursor-not-allowed hover:bg-zinc-700 transition-colors"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 2L11 13M22 2L15 22 11 13 2 9l20-7z" />
            </svg>
          </motion.button>
        </div>
        <p className="mt-2 text-center text-[10px] text-zinc-300">
          Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
