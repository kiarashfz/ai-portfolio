import DashboardClient from "@/components/dashboard/DashboardClient";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard — PortfolioGPT",
};

export default function DashboardPage() {
  return <DashboardClient />;
}