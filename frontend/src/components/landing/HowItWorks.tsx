"use client";
import { motion } from "framer-motion";

const steps = [
  {
    number: "01",
    title: "Create your account",
    description: "Sign up in seconds and set your unique portfolio username.",
  },
  {
    number: "02",
    title: "Add your experience",
    description:
      "Fill in your skills, work history, and projects. We handle the rest.",
  },
  {
    number: "03",
    title: "Share your link",
    description:
      "Share portfoliogpt.com/yourname — visitors can ask your AI anything.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-32 px-6">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-zinc-400">
            How it works
          </p>
          <h2 className="mt-3 text-4xl font-semibold tracking-tight text-zinc-900">
            Up and running in minutes
          </h2>
        </div>

        <div className="grid gap-8 md:grid-cols-3">
          {steps.map((step, i) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1, duration: 0.4 }}
              className="rounded-2xl border border-zinc-100 bg-zinc-50 p-8"
            >
              <span className="text-4xl font-bold text-zinc-200">{step.number}</span>
              <h3 className="mt-4 text-lg font-semibold text-zinc-900">{step.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-500">{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}