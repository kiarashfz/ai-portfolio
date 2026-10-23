"use client";

import {useState, useEffect} from "react";
import {useRouter} from "next/navigation";
import DashboardNav from "./DashboardNav";
import ProfileForm from "./ProfileForm";
import Celebration from "./Celebration";
import {ProfileData, EMPTY_PROFILE} from "./types";
import {portfolioApi, authApi, ApiError, PortfolioResponse} from "@/lib/api";
import {useAuth} from "@/context/AuthContext";

// Map backend PortfolioResponse → frontend ProfileData
function mapResponseToProfile(res: PortfolioResponse): ProfileData {
    const pd = res.profile_data;
    return {
        username: res.username,
        firstName: res.first_name,
        lastName: res.last_name,
        title: res.title,
        summary: res.summary,
        skills: pd?.skills?.map((skill, idx) => ({
            id: `skill-${idx}`,
            name: skill,
        })) ?? [{id: "1", name: ""}],
        experiences: pd?.experiences?.map((e) => ({
            id: `${e.company}-${e.position}`,
            company: e.company,
            position: e.position,
            startDate: e.start_date,
            endDate: e.end_date,
            description: e.description,
        })) ?? [{id: "1", company: "", position: "", startDate: "", endDate: "", description: ""}],
        education: pd?.education?.map((e, idx) => ({
            id: `edu-${idx}`,
            degree: e.degree,
            institution: e.institution,
            year: e.year,
        })) ?? [{id: "1", degree: "", institution: "", year: ""}],
        website: pd?.links?.website ?? "",
        github: pd?.links?.github ?? "",
        linkedin: pd?.links?.linkedin ?? "",
    };
}

export default function DashboardClient() {
    const router = useRouter();
    const {isAuthenticated, username, isLoading: authLoading, logout} = useAuth();

    const [profile, setProfile] = useState<ProfileData>(EMPTY_PROFILE);
    const [isComplete, setIsComplete] = useState(false);
    const [showCelebration, setShowCelebration] = useState(false);
    const [isFetching, setIsFetching] = useState(true);
    const [fetchError, setFetchError] = useState<string | null>(null);

    // Redirect if not authenticated
    useEffect(() => {
        if (!authLoading && !isAuthenticated) {
            router.push("/login");
        }
    }, [authLoading, isAuthenticated, router]);

    // Load existing portfolio on mount
    useEffect(() => {
        if (!isAuthenticated) return;

        async function load() {
            try {
                const res = await portfolioApi.getMyPortfolio();
                const mapped = mapResponseToProfile(res);
                setProfile(mapped);
                // If they already have a complete portfolio, show edit mode not celebration
                setIsComplete(true);
            } catch (err) {
                if (err instanceof ApiError && err.status === 404) {
                    // No portfolio yet — fresh user, show empty form
                    setProfile({...EMPTY_PROFILE, username: authApi.getUsername() ?? ""});
                } else {
                    setFetchError("Failed to load your portfolio. Please refresh.");
                }
            } finally {
                setIsFetching(false);
            }
        }

        load();
    }, [isAuthenticated]);

    function handleSubmit(data: ProfileData) {
        setProfile(data);
        setIsComplete(true);
        setShowCelebration(true);
    }

    function handleEdit() {
        setShowCelebration(false);
    }

    function handleLogout() {
        logout();
        router.push("/");
    }

    if (authLoading || isFetching) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-zinc-50">
                <div className="flex flex-col items-center gap-3">
                    <div className="h-6 w-6 animate-spin rounded-full border-2 border-zinc-300 border-t-zinc-900"/>
                    <p className="text-sm text-zinc-400">Loading your portfolio…</p>
                </div>
            </div>
        );
    }

    if (fetchError) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-zinc-50">
                <p className="text-sm text-red-500">{fetchError}</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-50">
            <DashboardNav username={profile.username} onLogout={handleLogout}/>
            <main className="mx-auto max-w-3xl px-6 py-12">
                {showCelebration ? (
                    <Celebration username={profile.username} onEdit={handleEdit}/>
                ) : (
                    <ProfileForm
                        initialData={profile}
                        isComplete={isComplete}
                        onSubmit={handleSubmit}
                    />
                )}
            </main>
        </div>
    );
}
