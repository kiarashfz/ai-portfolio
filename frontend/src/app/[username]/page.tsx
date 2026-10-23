import type { Metadata } from "next";
import { notFound } from "next/navigation";
import PortfolioPage from "@/components/portfolio/PortfolioPage";
import { PortfolioResponse } from "@/lib/api";
import { Portfolio } from "@/components/portfolio/types";

const BASE_URL = "http://localhost:8080";

async function fetchPortfolio(username: string): Promise<PortfolioResponse | null> {
  try {
    const res = await fetch(`${BASE_URL}/v1/portfolio/${username}`, {
      next: { revalidate: 60 }, // ISR — revalidate every 60s
    });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch {
    return null;
  }
}

function mapToPortfolio(res: PortfolioResponse): Portfolio {
  const pd = res.profile_data;
  return {
    username: res.username,
    firstName: res.first_name,
    lastName: res.last_name,
    title: res.title,
    summary: res.summary,
    skills: pd?.skills ?? [],
    experiences: pd?.experiences?.map((e) => ({
      company: e.company,
      position: e.position,
      startDate: e.start_date,
      endDate: e.end_date,
      description: e.description,
    })) ?? [],
    education: pd?.education?.map((e) => ({
      degree: e.degree,
      institution: e.institution,
      year: e.year,
    })) ?? [],
    links: {
      website: pd?.links?.website || undefined,
      github: pd?.links?.github || undefined,
      linkedin: pd?.links?.linkedin || undefined,
    },
  };
}

type Props = { params: { username: string } };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { username } = await params;
  const data = await fetchPortfolio(username);
  if (!data) return { title: "Portfolio not found" };

  return {
    title: `${data.first_name} ${data.last_name} — ${data.title}`,
    description: data.summary,
    openGraph: {
      title: `${data.first_name} ${data.last_name}`,
      description: data.summary,
      type: "profile",
    },
  };
}

export default async function Page({ params }: Props) {
  const { username } = await params;
  const data = await fetchPortfolio(username);

  if (!data) notFound();

  const portfolio = mapToPortfolio(data);
  return <PortfolioPage portfolio={portfolio} />;
}