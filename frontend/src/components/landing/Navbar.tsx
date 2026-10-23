import Link from "next/link";
import {Button} from "@/components/ui/button";

export default function Navbar() {
    return (
        <header className="fixed top-0 left-0 right-0 z-50 border-b border-zinc-100 bg-white/80 backdrop-blur-md">
            <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
                <Link href="/" className="text-lg font-semibold tracking-tight">
                    PortfolioGPT
                </Link>
                <nav className="hidden items-center gap-8 text-sm text-zinc-500 md:flex">
                    <Link href="#how-it-works" className="hover:text-zinc-900 transition-colors">How it works</Link>
                    <Link href="#features" className="hover:text-zinc-900 transition-colors">Features</Link>
                    <Link href="#faq" className="hover:text-zinc-900 transition-colors">FAQ</Link>
                </nav>
                <div className="flex items-center gap-3">
                    <Link href="/login">
                        <Button variant="ghost" size="sm">Log in</Button>
                    </Link>
                    <Link href="/signup">
                        <Button size="sm">Get started</Button>
                    </Link>
                </div>
            </div>
        </header>
    );
}