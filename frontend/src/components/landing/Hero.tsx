"use client";
import {motion} from "framer-motion";
import Link from "next/link";
import {Button} from "@/components/ui/button";
import {Badge} from "@/components/ui/badge";

export default function Hero() {
    return (
        <section className="flex min-h-screen flex-col items-center justify-center px-6 pt-24 text-center">
            <motion.div
                initial={{opacity: 0, y: 20}}
                animate={{opacity: 1, y: 0}}
                transition={{duration: 0.5}}
            >
                <Badge variant="secondary" className="mb-6 rounded-full px-4 py-1 text-xs font-medium">
                    ✦ AI-powered portfolios
                </Badge>

                <h1 className="mx-auto max-w-3xl text-5xl font-semibold leading-tight tracking-tight text-zinc-900 md:text-6xl">
                    Your resume,{" "}
                    <span className="text-zinc-400">reimagined</span>{" "}
                    with AI
                </h1>

                <p className="mx-auto mt-6 max-w-xl text-lg text-zinc-500">
                    Sign up, add your experience and skills — PortfolioGPT creates a
                    personal AI that answers any question about you, professionally.
                </p>

                <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
                    <Link href="/signup">
                        <Button size="lg" className="px-8">
                            Create your portfolio
                        </Button>
                    </Link>
                    <Link href="/kiarash_fazli">
                        <Button size="lg" variant="outline" className="px-8">
                            See a live demo
                        </Button>
                    </Link>
                </div>

                <p className="mt-4 text-xs text-zinc-400">Free to start · No credit card required</p>
            </motion.div>
        </section>
    );
}