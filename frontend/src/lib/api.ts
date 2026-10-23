const BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080").replace(/\/$/, "");

// ─── Types matching backend schemas ───────────────────────────────────────────

export interface SignUpRequest { username: string; password: string }
export interface SignUpResponse { username: string; access_token: string; refresh_token: string; token_type: string }
export interface SignInRequest { username: string; password: string }
export interface SignInResponse { access_token: string; refresh_token: string; token_type: string }

export interface ExperienceSchema { company: string; position: string; start_date: string; end_date: string; description: string }
export interface EducationSchema { degree: string; institution: string; year: string }
export interface LinksSchema { website: string; github: string; linkedin: string }

export interface UpsertPortfolioRequest {
  first_name: string;
  last_name: string;
  title: string;
  summary: string;
  skills: string[];
  experiences: ExperienceSchema[];
  education: EducationSchema[];
  links: LinksSchema;
}

export interface UpsertPortfolioResponse {
  username: string;
  portfolio_url: string;
  chunks_ingested: number;
  created: boolean;
}

export interface PortfolioResponse {
  username: string;
  first_name: string;
  last_name: string;
  title: string;
  summary: string;
  profile_data: {
    skills?: string[];
    experiences?: ExperienceSchema[];
    education?: EducationSchema[];
    links?: LinksSchema;
  } | null;
}

export interface AIChatResponse { message: string }

// ─── API Error ────────────────────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  auth = false
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
    // Sends session_id cookie automatically — backend uses it to track chat sessions
    credentials: "include",
  });

  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      message = body?.detail || body?.title || message;
    } catch { /* ignore parse errors */ }
    throw new ApiError(res.status, message);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// ─── Auth API ─────────────────────────────────────────────────────────────────

export const authApi = {
  async signup(data: SignUpRequest): Promise<SignUpResponse> {
    const res = await request<SignUpResponse>("/v1/users/signup", {
      method: "POST",
      body: JSON.stringify(data),
    });
    localStorage.setItem("access_token", res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    localStorage.setItem("username", res.username);
    return res;
  },

  async signin(data: SignInRequest): Promise<SignInResponse & { username?: string }> {
    const res = await request<SignInResponse>("/v1/users/signin", {
      method: "POST",
      body: JSON.stringify(data),
    });
    localStorage.setItem("access_token", res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    return res;
  },

  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("username");
  },

  isAuthenticated(): boolean {
    return !!getToken();
  },

  getUsername(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("username");
  },
};

// ─── Portfolio API ────────────────────────────────────────────────────────────

export const portfolioApi = {
  async getMyPortfolio(): Promise<PortfolioResponse> {
    return request<PortfolioResponse>("/v1/portfolio/me/portfolio", {}, true);
  },

  async upsertMyPortfolio(data: UpsertPortfolioRequest): Promise<UpsertPortfolioResponse> {
    return request<UpsertPortfolioResponse>(
      "/v1/portfolio/me/portfolio",
      { method: "PATCH", body: JSON.stringify(data) },
      true
    );
  },

  async getPublicPortfolio(username: string): Promise<PortfolioResponse> {
    return request<PortfolioResponse>(`/v1/portfolio/${username}`);
  },
};

// ─── Chat API ─────────────────────────────────────────────────────────────────

export const chatApi = {
  /**
   * session_id is managed automatically via the session_id cookie.
   * credentials: "include" sends the cookie on every request.
   * On the first request the backend creates the cookie; subsequent
   * requests in the same browser session reuse it for chat continuity.
   */
  async sendMessage(portfolioUsername: string, message: string): Promise<AIChatResponse> {
    return request<AIChatResponse>(`/v1/chat/${portfolioUsername}/chat`, {
      method: "POST",
      body: JSON.stringify({ message }),
    });
  },
};
