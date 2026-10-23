"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi, ApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function SignupPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [username, setUsername] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);

    const form = new FormData(e.currentTarget);
    const password = form.get("password") as string;
    const confirm = form.get("confirmPassword") as string;

    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    setIsLoading(true);
    try {
      const res = await authApi.signup({ username, password });
      login(res.username, res.access_token);
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.status === 409 ? "That username is already taken." : err.message);
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-zinc-950 p-12">
        <Link href="/" className="text-white text-lg font-semibold tracking-tight">
          PortfolioGPT
        </Link>
        <div className="space-y-4">
          <p className="text-xs font-medium uppercase tracking-widest text-zinc-500">Your portfolio URL</p>
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 px-5 py-4 font-mono text-sm text-zinc-300">
            portfoliogpt.com/
            <span className="text-white">{username || "yourname"}</span>
            <span className="ml-0.5 inline-block h-4 w-px animate-pulse bg-white align-middle" />
          </div>
          <p className="text-sm text-zinc-500">
            This is the link you'll share with recruiters, teammates, and the world.
          </p>
        </div>
        <p className="text-xs text-zinc-600">© {new Date().getFullYear()} PortfolioGPT</p>
      </div>

      {/* Right panel */}
      <div className="flex w-full lg:w-1/2 flex-col items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <Link href="/" className="mb-10 block text-center text-lg font-semibold tracking-tight lg:hidden">
            PortfolioGPT
          </Link>

          <div className="mb-8">
            <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">Create your account</h1>
            <p className="mt-2 text-sm text-zinc-500">Get your AI portfolio live in minutes</p>
          </div>

          {error && (
            <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="username" className="text-sm font-medium text-zinc-700">Username</Label>
              <div className="flex h-11 items-center rounded-md border border-zinc-200 bg-zinc-50 px-3 focus-within:ring-2 focus-within:ring-zinc-900 focus-within:ring-offset-1">
                <span className="select-none text-sm text-zinc-400">portfoliogpt.com/</span>
                <input
                  id="username"
                  name="username"
                  type="text"
                  placeholder="yourname"
                  autoComplete="username"
                  required
                  value={username}
                  onChange={(e) =>
                    setUsername(e.target.value.toLowerCase().replace(/[^a-z0-9_-]/g, ""))
                  }
                  className="flex-1 bg-transparent text-sm text-zinc-900 placeholder:text-zinc-400 outline-none"
                />
              </div>
              <p className="text-xs text-zinc-400">Lowercase letters, numbers, - and _ only</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-zinc-700">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="••••••••"
                autoComplete="new-password"
                required
                minLength={8}
                className="h-11 border-zinc-200 bg-zinc-50 placeholder:text-zinc-400 focus-visible:ring-zinc-900"
              />
              <p className="text-xs text-zinc-400">Minimum 8 characters</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm-password" className="text-sm font-medium text-zinc-700">
                Confirm password
              </Label>
              <Input
                id="confirm-password"
                name="confirmPassword"
                type="password"
                placeholder="••••••••"
                autoComplete="new-password"
                required
                className="h-11 border-zinc-200 bg-zinc-50 placeholder:text-zinc-400 focus-visible:ring-zinc-900"
              />
            </div>

            <Button type="submit" className="h-11 w-full text-sm font-medium" disabled={isLoading}>
              {isLoading ? "Creating account…" : "Create account"}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-zinc-500">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-zinc-900 underline-offset-4 hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
