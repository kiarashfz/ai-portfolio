"use client";

import { motion } from "framer-motion";
import { Portfolio } from "./types";

interface Props {
  portfolio: Portfolio;
}

export default function PortfolioContent({ portfolio }: Props) {
  return (
    <div className="space-y-14">

      {/* Skills */}
      {portfolio.skills?.length > 0 && (
        <Section title="Skills">
          <div className="flex flex-wrap gap-2">
            {portfolio.skills.map((skill, i) => (
              <motion.span
                key={skill}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.03, duration: 0.3 }}
                className="rounded-lg border border-zinc-200 bg-white px-3 py-1.5 text-sm font-medium text-zinc-700 shadow-sm hover:border-zinc-300 hover:shadow transition-all cursor-default"
              >
                {skill}
              </motion.span>
            ))}
          </div>
        </Section>
      )}

      {/* Experience */}
      {portfolio.experiences?.length > 0 && (
        <Section title="Experience">
          <div className="space-y-8">
            {portfolio.experiences.map((exp, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -8 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.4 }}
                className="group relative pl-5"
              >
                {/* Timeline dot */}
                <div className="absolute left-0 top-2 h-2.5 w-2.5 rounded-full border-2 border-zinc-300 bg-white group-hover:border-zinc-900 transition-colors" />
                {/* Timeline line */}
                {i < portfolio.experiences.length - 1 && (
                  <div className="absolute left-[4px] top-5 h-full w-px bg-zinc-200" />
                )}

                <div className="flex flex-wrap items-start justify-between gap-2 mb-1.5">
                  <div>
                    <h3 className="text-base font-semibold text-zinc-900">
                      {exp.position}
                    </h3>
                    <p className="text-sm text-zinc-500">{exp.company}</p>
                  </div>
                  <span className="shrink-0 rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium text-zinc-500">
                    {formatDate(exp.startDate)}
                    {" — "}
                    {exp.endDate ? formatDate(exp.endDate) : "Present"}
                  </span>
                </div>

                {exp.description && (
                  <p className="text-sm leading-relaxed text-zinc-500">
                    {exp.description}
                  </p>
                )}
              </motion.div>
            ))}
          </div>
        </Section>
      )}

      {/* Education */}
      {portfolio.education?.length > 0 && (
        <Section title="Education">
          <div className="space-y-3">
            {portfolio.education.map((edu, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 8 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.4 }}
                className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-zinc-200 bg-white px-5 py-4 shadow-sm"
              >
                <div>
                  <p className="text-sm font-semibold text-zinc-900">{edu.degree}</p>
                  <p className="text-xs text-zinc-500 mt-0.5">{edu.institution}</p>
                </div>
                <span className="text-sm font-medium text-zinc-400">{edu.year}</span>
              </motion.div>
            ))}
          </div>
        </Section>
      )}
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-5">
      <div className="flex items-center gap-4">
        <h2 className="text-xs font-bold uppercase tracking-[0.15em] text-zinc-400 shrink-0">
          {title}
        </h2>
        <div className="flex-1 h-px bg-zinc-200" />
      </div>
      {children}
    </div>
  );
}

function formatDate(yyyymm: string): string {
  if (!yyyymm) return "";
  const [year, month] = yyyymm.split("-");
  if (!month) return year;
  const date = new Date(parseInt(year), parseInt(month) - 1);
  return date.toLocaleDateString("en-US", { month: "short", year: "numeric" });
}
