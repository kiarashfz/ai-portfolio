import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

export const metadata: Metadata = {
  title: "PortfolioGPT — Your AI-Powered Portfolio",
  description:
    "Create your AI-powered portfolio in minutes. Share a link, let visitors ask anything about your experience, skills, and projects.",
  keywords: ["AI portfolio", "portfolio website", "GPT portfolio", "resume AI"],
  openGraph: {
    title: "PortfolioGPT — Your AI-Powered Portfolio",
    description: "Let AI represent you professionally.",
    url: "https://portfoliogpt.com",
    siteName: "PortfolioGPT",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "PortfolioGPT",
    description: "Your resume, reimagined with AI.",
  },
  metadataBase: new URL("https://portfoliogpt.com"),
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={GeistSans.className}>
      <body className="bg-white text-zinc-900 antialiased" suppressHydrationWarning={true}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
