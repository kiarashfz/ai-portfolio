export default function Footer() {
  return (
    <footer className="border-t border-zinc-100 py-10 px-6">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 text-sm text-zinc-400 sm:flex-row">
        <span>© {new Date().getFullYear()} PortfolioGPT. All rights reserved.</span>
        <div className="flex gap-6">
          <a href="/privacy" className="hover:text-zinc-600 transition-colors">Privacy</a>
          <a href="/terms" className="hover:text-zinc-600 transition-colors">Terms</a>
          <a href="mailto:hello@portfoliogpt.com" className="hover:text-zinc-600 transition-colors">Contact</a>
        </div>
      </div>
    </footer>
  );
}