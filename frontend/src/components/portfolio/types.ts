export interface Experience {
  company: string;
  position: string;
  startDate: string;
  endDate: string;
  description: string;
}

export interface Education {
  degree: string;
  institution: string;
  year: string;
}

export interface Portfolio {
  username: string;
  firstName: string;
  lastName: string;
  title: string;
  summary: string;
  skills: string[];
  experiences: Experience[];
  education: Education[];
  links: {
    website?: string;
    github?: string;
    linkedin?: string;
  };
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}