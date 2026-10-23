"use client";

import {useState, useEffect} from "react";
import {motion} from "framer-motion";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {Label} from "@/components/ui/label";
import {Textarea} from "@/components/ui/textarea";
import {Separator} from "@/components/ui/separator";
import {ProfileData, Experience, Education} from "./types";
import {portfolioApi, ApiError} from "@/lib/api";

interface Props {
    initialData: ProfileData;
    isComplete: boolean;
    onSubmit: (data: ProfileData) => void;
}

function calcProgress(data: ProfileData): number {
    const fields = [
        data.firstName, data.lastName, data.title, data.summary,
        data.skills[0]?.name, data.experiences[0]?.company, data.experiences[0]?.position,
    ];
    const filled = fields.filter((f) => f && String(f).trim() !== "").length;
    return Math.round((filled / fields.length) * 100);
}

export default function ProfileForm({initialData, isComplete, onSubmit}: Props) {
    const [data, setData] = useState<ProfileData>(initialData);
    const [isSaving, setIsSaving] = useState(false);
    const [savedOnce, setSavedOnce] = useState(isComplete);
    const [error, setError] = useState<string | null>(null);
    const progress = calcProgress(data);

    useEffect(() => {
        setData(initialData);
    }, [initialData]);

    function set(field: keyof ProfileData, value: string) {
        setData((prev) => ({...prev, [field]: value}));
    }

    function setExp(id: string, field: keyof Experience, value: string) {
        setData((prev) => ({
            ...prev,
            experiences: prev.experiences.map((e) => e.id === id ? {...e, [field]: value} : e),
        }));
    }

    function addExperience() {
        setData((prev) => ({
            ...prev,
            experiences: [...prev.experiences, {
                id: Date.now().toString(),
                company: "",
                position: "",
                startDate: "",
                endDate: "",
                description: ""
            }],
        }));
    }

    function removeExperience(id: string) {
        if (data.experiences.length === 1) return;
        setData((prev) => ({...prev, experiences: prev.experiences.filter((e) => e.id !== id)}));
    }

    function setSkill(id: string, value: string) {
        setData((prev) => ({
            ...prev,
            skills: prev.skills.map((s) => s.id === id ? {...s, name: value} : s),
        }));
    }

    function addSkill() {
        setData((prev) => ({
            ...prev,
            skills: [...prev.skills, {
                id: Date.now().toString(),
                name: "",
            }],
        }));
    }

    function removeSkill(id: string) {
        if (data.skills.length === 1) return;
        setData((prev) => ({...prev, skills: prev.skills.filter((s) => s.id !== id)}));
    }

    function setEducation(id: string, field: keyof Education, value: string) {
        setData((prev) => ({
            ...prev,
            education: prev.education.map((e) => e.id === id ? {...e, [field]: value} : e),
        }));
    }

    function addEducation() {
        setData((prev) => ({
            ...prev,
            education: [...prev.education, {
                id: Date.now().toString(),
                degree: "",
                institution: "",
                year: "",
            }],
        }));
    }

    function removeEducation(id: string) {
        if (data.education.length === 1) return;
        setData((prev) => ({...prev, education: prev.education.filter((e) => e.id !== id)}));
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        setIsSaving(true);

        try {
            await portfolioApi.upsertMyPortfolio({
                first_name: data.firstName,
                last_name: data.lastName,
                title: data.title,
                summary: data.summary,
                skills: data.skills.map((s) => s.name).filter(Boolean),
                experiences: data.experiences.map((exp) => ({
                    company: exp.company,
                    position: exp.position,
                    start_date: exp.startDate,
                    end_date: exp.endDate,
                    description: exp.description,
                })),
                education: data.education
                    .filter((e) => e.degree)
                    .map((e) => ({
                        degree: e.degree,
                        institution: e.institution,
                        year: e.year,
                    })),
                links: {
                    website: data.website,
                    github: data.github,
                    linkedin: data.linkedin,
                },
            });

            setSavedOnce(true);
            onSubmit(data);
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.status === 401 ? "Session expired. Please sign in again." : err.message);
            } else {
                setError("Failed to save. Please try again.");
            }
        } finally {
            setIsSaving(false);
        }
    }

    return (
        <motion.div initial={{opacity: 0, y: 16}} animate={{opacity: 1, y: 0}} transition={{duration: 0.4}}>
            {/* Header */}
            <div className="mb-8">
                <div className="flex items-center justify-between mb-1">
                    <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
                        {savedOnce ? "Edit your profile" : "Build your portfolio"}
                    </h1>
                    <span className="text-sm font-medium text-zinc-500">{progress}%</span>
                </div>
                <p className="text-sm text-zinc-500 mb-4">
                    {savedOnce ? "Update your details and hit save to sync your AI portfolio." : "Complete all sections to publish your AI-powered portfolio."}
                </p>
                <div className="h-1.5 w-full rounded-full bg-zinc-200">
                    <motion.div
                        className="h-1.5 rounded-full bg-zinc-900"
                        initial={{width: 0}}
                        animate={{width: `${progress}%`}}
                        transition={{duration: 0.4}}
                    />
                </div>
            </div>

            {error && (
                <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-10">
                {/* Basic Info */}
                <Section title="Basic information" description="How you'll appear on your portfolio.">
                    <div className="grid grid-cols-2 gap-4">
                        <Field label="First name">
                            <Input placeholder="Kiarash" value={data.firstName}
                                   onChange={(e) => set("firstName", e.target.value)} required/>
                        </Field>
                        <Field label="Last name">
                            <Input placeholder="Fazli" value={data.lastName}
                                   onChange={(e) => set("lastName", e.target.value)} required/>
                        </Field>
                    </div>
                    <Field label="Professional title">
                        <Input placeholder="Full-stack Developer" value={data.title}
                               onChange={(e) => set("title", e.target.value)} required/>
                    </Field>
                    <Field label="Summary" hint="2–4 sentences about who you are and what you do.">
                        <Textarea placeholder="Experienced developer specializing in…" value={data.summary}
                                  onChange={(e) => set("summary", e.target.value)} rows={4} required/>
                    </Field>
                </Section>

                <Separator/>

                {/* Skills */}
                <Section title="Skills" description="List your technical and professional skills.">
                    <div className="space-y-4">
                        {data.skills.map((skill, idx) => (
                            <div key={skill.id} className="flex items-end gap-3">
                                <div className="flex-1">
                                    <Field label={idx === 0 ? "Skills" : ""}>
                                        <Input placeholder="e.g. Python, React, Docker" value={skill.name}
                                               onChange={(e) => setSkill(skill.id, e.target.value)}/>
                                    </Field>
                                </div>
                                {data.skills.length > 1 && (
                                    <button type="button" onClick={() => removeSkill(skill.id)}
                                            className="mb-1.5 text-xs text-red-400 hover:text-red-600 transition-colors">Remove</button>
                                )}
                            </div>
                        ))}
                    </div>
                    <button type="button" onClick={addSkill}
                            className="mt-2 text-sm font-medium text-zinc-500 hover:text-zinc-900 transition-colors">
                        + Add another skill
                    </button>
                </Section>

                <Separator/>

                {/* Experience */}
                <Section title="Work experience" description="Add your professional roles.">
                    <div className="space-y-6">
                        {data.experiences.map((exp, idx) => (
                            <div key={exp.id} className="rounded-xl border border-zinc-200 bg-white p-5 space-y-4">
                                <div className="flex items-center justify-between">
                                    <span
                                        className="text-xs font-medium uppercase tracking-widest text-zinc-400">Position {idx + 1}</span>
                                    {data.experiences.length > 1 && (
                                        <button type="button" onClick={() => removeExperience(exp.id)}
                                                className="text-xs text-red-400 hover:text-red-600 transition-colors">Remove</button>
                                    )}
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <Field label="Company"><Input placeholder="Irancell" value={exp.company}
                                                                  onChange={(e) => setExp(exp.id, "company", e.target.value)}/></Field>
                                    <Field label="Position"><Input placeholder="Backend Developer" value={exp.position}
                                                                   onChange={(e) => setExp(exp.id, "position", e.target.value)}/></Field>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <Field label="Start date"><Input type="month" value={exp.startDate}
                                                                     onChange={(e) => setExp(exp.id, "startDate", e.target.value)}/></Field>
                                    <Field label="End date" hint="Leave blank if current"><Input type="month"
                                                                                                 value={exp.endDate}
                                                                                                 onChange={(e) => setExp(exp.id, "endDate", e.target.value)}/></Field>
                                </div>
                                <Field label="Description">
                                    <Textarea placeholder="What did you build or achieve?" value={exp.description}
                                              onChange={(e) => setExp(exp.id, "description", e.target.value)} rows={3}/>
                                </Field>
                            </div>
                        ))}
                    </div>
                    <button type="button" onClick={addExperience}
                            className="mt-2 text-sm font-medium text-zinc-500 hover:text-zinc-900 transition-colors">
                        + Add another position
                    </button>
                </Section>

                <Separator/>

                {/* Education */}
                <Section title="Education" description="Your academic background.">
                    <div className="space-y-6">
                        {data.education.map((edu, idx) => (
                            <div key={edu.id} className="rounded-xl border border-zinc-200 bg-white p-5 space-y-4">
                                <div className="flex items-center justify-between">
                                    <span
                                        className="text-xs font-medium uppercase tracking-widest text-zinc-400">Education {idx + 1}</span>
                                    {data.education.length > 1 && (
                                        <button type="button" onClick={() => removeEducation(edu.id)}
                                                className="text-xs text-red-400 hover:text-red-600 transition-colors">Remove</button>
                                    )}
                                </div>
                                <Field label="Degree"><Input placeholder="B.S. Computer Science" value={edu.degree}
                                                            onChange={(e) => setEducation(edu.id, "degree", e.target.value)}/></Field>
                                <Field label="Institution"><Input placeholder="MIT" value={edu.institution}
                                                                  onChange={(e) => setEducation(edu.id, "institution", e.target.value)}/></Field>
                                <Field label="Year"><Input placeholder="2020" value={edu.year}
                                                          onChange={(e) => setEducation(edu.id, "year", e.target.value)}/></Field>
                            </div>
                        ))}
                    </div>
                    <button type="button" onClick={addEducation}
                            className="mt-2 text-sm font-medium text-zinc-500 hover:text-zinc-900 transition-colors">
                        + Add another education
                    </button>
                </Section>

                <Separator/>

                {/* Links */}
                <Section title="Links" description="Optional — helps visitors find more about you.">
                    <Field label="Personal website"><Input placeholder="https://kiarash.dev" value={data.website}
                                                           onChange={(e) => set("website", e.target.value)}/></Field>
                    <Field label="GitHub"><Input placeholder="https://github.com/kiarashfz" value={data.github}
                                                 onChange={(e) => set("github", e.target.value)}/></Field>
                    <Field label="LinkedIn"><Input placeholder="https://linkedin.com/in/kiarashfz" value={data.linkedin}
                                                   onChange={(e) => set("linkedin", e.target.value)}/></Field>
                </Section>

                <div className="flex items-center justify-between pt-4 pb-16">
                    <p className="text-xs text-zinc-400">
                        {progress < 100 ? `${100 - progress}% left to complete` : "Your profile is ready to publish ✦"}
                    </p>
                    <Button type="submit" disabled={isSaving} className="px-8">
                        {isSaving ? "Saving…" : savedOnce ? "Save changes" : "Publish portfolio"}
                    </Button>
                </div>
            </form>
        </motion.div>
    );
}

function Section({title, description, children}: { title: string; description: string; children: React.ReactNode }) {
    return (
        <div className="grid gap-6 md:grid-cols-[200px_1fr]">
            <div>
                <h2 className="font-medium text-zinc-900">{title}</h2>
                <p className="mt-1 text-sm text-zinc-500">{description}</p>
            </div>
            <div className="space-y-4">{children}</div>
        </div>
    );
}

function Field({label, hint, children}: { label: string; hint?: string; children: React.ReactNode }) {
    return (
        <div className="space-y-1.5">
            <Label className="text-sm font-medium text-zinc-700">{label}</Label>
            {children}
            {hint && <p className="text-xs text-zinc-400">{hint}</p>}
        </div>
    );
}
