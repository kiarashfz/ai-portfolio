import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  {
    q: "How does PortfolioGPT work?",
    a: "You sign up, enter your professional experience and skills, and we index it into an AI. Visitors can then chat with your portfolio at your unique URL and ask anything about your background.",
  },
  {
    q: "Do I need technical knowledge to set up my portfolio?",
    a: "Not at all. The setup is fully guided — just fill in a form, and your AI portfolio is live within minutes.",
  },
  {
    q: "Can I update my information after publishing?",
    a: "Yes. You can update your profile anytime and the AI will reflect the changes immediately after re-indexing.",
  },
  {
    q: "What kind of questions can visitors ask?",
    a: "Anything related to your professional background — skills, experience, projects, education, tools you use, and more. Off-topic questions are gracefully declined.",
  },
  {
    q: "Is my data private?",
    a: "Only the information you explicitly add to your portfolio is accessible via the AI. Your account details and other data remain completely private.",
  },
];

export default function FAQ() {
  return (
    <section id="faq" className="border-t border-zinc-100 py-32 px-6">
      <div className="mx-auto max-w-2xl">
        <div className="mb-16 text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-zinc-400">FAQ</p>
          <h2 className="mt-3 text-4xl font-semibold tracking-tight text-zinc-900">
            Common questions
          </h2>
        </div>

        <Accordion type="single" collapsible className="w-full">
          {faqs.map((faq, i) => (
            <AccordionItem key={i} value={`item-${i}`}>
              <AccordionTrigger className="text-left text-sm font-medium text-zinc-900">
                {faq.q}
              </AccordionTrigger>
              <AccordionContent className="text-sm text-zinc-500 leading-relaxed">
                {faq.a}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
}