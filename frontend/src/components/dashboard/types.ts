// types.ts
export interface Experience {
  id: string;
  company: string;
  position: string;
  startDate: string;
  endDate: string;
  description: string;
}

export interface Skill {
  id: string;
  name: string;
}

export interface Education {
  id: string;
  degree: string;
  institution: string;
  year: string;
}

export interface ProfileData {
  username: string;
  firstName: string;
  lastName: string;
  title: string;
  summary: string;
  skills: Skill[];
  experiences: Experience[];
  education: Education[];
  website: string;
  github: string;
  linkedin: string;
}

export const EMPTY_PROFILE: ProfileData = {
  username: "",
  firstName: "",
  lastName: "",
  title: "",
  summary: "",
  skills: [
    { id: "1", name: "" },
  ],
  experiences: [
    { id: "1", company: "", position: "", startDate: "", endDate: "", description: "" },
  ],
  education: [
    { id: "1", degree: "", institution: "", year: "" },
  ],
  website: "",
  github: "",
  linkedin: "",
};