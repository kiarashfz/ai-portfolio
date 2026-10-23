"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi, ApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const form = new FormData(e.currentTarget);
    const username = form.get("username") as string;
    const password = form.get("password") as string;

    try {
      const res = await authApi.signin({ username, password });
      // signin response doesn't return username — store it from the form input
      localStorage.setItem("username", username);
      login(username, res.access_token);
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.status === 401 ? "Invalid username or password." : err.message);
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
        <blockquote className="space-y-3">
          <p className="text-xl font-light leading-relaxed text-zinc-200">
            "I shared my PortfolioGPT link in my job application and the hiring
            manager said it was the most impressive thing they'd seen."
          </p>
          <footer className="text-sm text-zinc-500">— Alex M., Software Engineer</footer>
        </blockquote>
        <p className="text-xs text-zinc-600">© {new Date().getFullYear()} PortfolioGPT</p>
      </div>

      {/* Right panel */}
      <div className="flex w-full lg:w-1/2 flex-col items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <Link href="/" className="mb-10 block text-center text-lg font-semibold tracking-tight lg:hidden">
            PortfolioGPT
          </Link>

          <div className="mb-8">
            <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">Welcome back</h1>
            <p className="mt-2 text-sm text-zinc-500">Enter your credentials to continue</p>
          </div>

          {error && (
            <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="username" className="text-sm font-medium text-zinc-700">Username</Label>
              <Input
                id="username"
                name="username"
                type="text"
                placeholder="yourname"
                autoComplete="username"
                required
                className="h-11 border-zinc-200 bg-zinc-50 placeholder:text-zinc-400 focus-visible:ring-zinc-900"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-zinc-700">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="••••••••"
                autoComplete="current-password"
                required
                className="h-11 border-zinc-200 bg-zinc-50 placeholder:text-zinc-400 focus-visible:ring-zinc-900"
              />
            </div>

            <Button type="submit" className="h-11 w-full text-sm font-medium" disabled={isLoading}>
              {isLoading ? "Signing in…" : "Sign in"}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-zinc-500">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="font-medium text-zinc-900 underline-offset-4 hover:underline">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
