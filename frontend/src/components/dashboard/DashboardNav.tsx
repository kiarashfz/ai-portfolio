import Link from "next/link";
import { Button } from "@/components/ui/button";

interface Props {
  username: string;
  onLogout: () => void;
}

export default function DashboardNav({ username, onLogout }: Props) {
  return (
    <header className="border-b border-zinc-200 bg-white">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="text-lg font-semibold tracking-tight text-zinc-900">
          PortfolioGPT
        </Link>
        <div className="flex items-center gap-4">
          {username && (
            <Link
              href={`/${username}`}
              target="_blank"
              className="text-sm text-zinc-500 hover:text-zinc-900 transition-colors"
            >
              portfoliogpt.com/{username} ↗
            </Link>
          )}
          <Button variant="outline" size="sm" onClick={onLogout}>
            Log out
          </Button>
        </div>
      </div>
    </header>
  );
}
