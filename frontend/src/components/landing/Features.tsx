"use client";
import { motion } from "framer-motion";

const features = [
  {
    icon: "⚡",
    title: "Instant AI responses",
    description:
      "Visitors ask questions in natural language and get accurate answers about your background in real time.",
  },
  {
    icon: "🔗",
    title: "Shareable portfolio URL",
    description:
      "Every user gets a unique, clean URL they can put on their resume, LinkedIn, or email signature.",
  },
  {
    icon: "🎯",
    title: "Relevance filtering",
    description:
      "Only portfolio-related questions get answered. Off-topic queries are gracefully declined.",
  },
  {
    icon: "🔒",
    title: "You control your data",
    description:
      "Update or delete your information anytime. Your portfolio reflects exactly what you choose to share.",
  },
  {
    icon: "📱",
    title: "Works on any device",
    description:
      "Your portfolio page is fully responsive and looks great on mobile, tablet, and desktop.",
  },
  {
    icon: "🌍",
    title: "SEO optimized",
    description:
      "Portfolio pages are server-rendered for maximum discoverability on Google and other search engines.",
  },
];

export default function Features() {
  return (
    <section id="features" className="border-t border-zinc-100 py-32 px-6">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-zinc-400">
            Features
          </p>
          <h2 className="mt-3 text-4xl font-semibold tracking-tight text-zinc-900">
            Everything you need to stand out
          </h2>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08, duration: 0.4 }}
              className="rounded-2xl border border-zinc-100 p-6 hover:border-zinc-200 hover:shadow-sm transition-all"
            >
              <span className="text-2xl">{feature.icon}</span>
              <h3 className="mt-4 font-semibold text-zinc-900">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-500">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}