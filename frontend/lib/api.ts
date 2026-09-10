import { clearToken, getStoredToken } from "@/lib/auth";
import type {
  Case,
  CaseEvidence,
  CaseCreate,
  CaseListParams,
  CaseListResponse,
  CaseStatusUpdate,
  ChatResponse,
  Donation,
  DonationCreate,
  DonationListResponse,
  Evidence,
  EvidenceListResponse,
  HybridAnalysisResponse,
  RecommendationCase,
  TokenResponse,
  User,
  VerificationStatus,
} from "@/types";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export const NETWORK_ERROR_MESSAGE = "Unable to connect to CareHaven backend.";

function getBaseUrl(): string {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (!base) {
    throw new ApiError(
      "The frontend is missing NEXT_PUBLIC_API_BASE_URL.",
      500,
    );
  }
  return base.replace(/\/$/, "");
}

function queryString(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === "") continue;
    search.set(key, String(value));
  }
  const encoded = search.toString();
  return encoded ? `?${encoded}` : "";
}

function humanMessage(status: number, detail: unknown): string {
  if (typeof detail === "string" && detail.trim()) return detail;
  if (detail && typeof detail === "object") {
    const record = detail as { message?: unknown; detail?: unknown };
    if (typeof record.message === "string") return record.message;
    if (Array.isArray(detail)) {
      const first = detail[0] as { msg?: string } | undefined;
      if (first?.msg) return first.msg;
    }
  }

  if (status === 401) {
    return "Your session is invalid or expired. Please sign in again.";
  }
  if (status === 403) return "You do not have permission to perform this action.";
  if (status === 404) return "The requested resource was not found.";
  if (status === 409) return "This conflicts with existing data.";
  if (status === 413) return "The uploaded image is too large. Maximum size is 10 MB.";
  if (status === 422) return "Please check the submitted information.";
  if (status === 503) {
    return "The CareHaven service is temporarily unavailable. Please try again later.";
  }
  if (status >= 500) {
    return "The CareHaven backend encountered an error. Please try again later.";
  }
  return NETWORK_ERROR_MESSAGE;
}

async function readBody(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  auth = true,
): Promise<T> {
  const headers = new Headers(options.headers);
  const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;

  if (!isFormData && options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  headers.set("Accept", "application/json");

  if (auth) {
    const token = getStoredToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(`${getBaseUrl()}${path}`, {
      ...options,
      headers,
    });
  } catch {
    throw new ApiError(NETWORK_ERROR_MESSAGE, 0);
  }

  const payload = await readBody(response);

  if (!response.ok) {
    if (response.status === 401) {
      clearToken();
    }
    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? (payload as { detail: unknown }).detail
        : payload;
    throw new ApiError(humanMessage(response.status, detail), response.status);
  }

  return payload as T;
}

export const api = {
  health: () => apiRequest<{ status: string }>("/health", { method: "GET" }, false),

  login: (email: string, password: string) =>
    apiRequest<TokenResponse>(
      "/auth/login",
      { method: "POST", body: JSON.stringify({ email, password }) },
      false,
    ),

  register: (email: string, password: string) =>
    apiRequest<User>(
      "/auth/register",
      { method: "POST", body: JSON.stringify({ email, password }) },
      false,
    ),

  me: () => apiRequest<User>("/auth/me"),

  caseEvidence: (caseId: string) =>
    apiRequest<CaseEvidence[]>(
      `/cases/${encodeURIComponent(caseId)}/evidence`,
    ),

  evidenceImage: async (imageUrl: string): Promise<Blob> => {
    const headers = new Headers({ Accept: "image/*" });
    const token = getStoredToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
    const response = await fetch(imageUrl, { headers });
    if (!response.ok) {
      throw new ApiError(humanMessage(response.status, null), response.status);
    }
    return response.blob();
  },

  listCases: (params: CaseListParams = {}) =>
    apiRequest<CaseListResponse>(
      `/cases${queryString({
        page: params.page,
        page_size: params.page_size,
        assistance_category: params.assistance_category,
        country: params.country,
        governorate: params.governorate,
        city: params.city,
        priority: params.priority,
        severity: params.severity,
        urgency: params.urgency,
        status: params.status,
      })}`,
    ),

  getCase: (caseId: string) => apiRequest<Case>(`/cases/${encodeURIComponent(caseId)}`),

  createCase: (payload: CaseCreate) =>
    apiRequest<Case>("/cases", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateCaseStatus: (caseId: string, payload: CaseStatusUpdate) =>
    apiRequest<Case>(`/cases/${encodeURIComponent(caseId)}/status`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  listDonations: (page = 1, pageSize = 20) =>
    apiRequest<DonationListResponse>(
      `/donations${queryString({ page, page_size: pageSize })}`,
    ),

  myDonationHistory: (page = 1, pageSize = 20) =>
    apiRequest<DonationListResponse>(
      `/donations/my-history${queryString({ page, page_size: pageSize })}`,
    ),

  createDonation: (payload: DonationCreate) =>
    apiRequest<Donation>("/donations", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  caseDonations: (caseId: string, page = 1, pageSize = 20) =>
    apiRequest<DonationListResponse>(
      `/cases/${encodeURIComponent(caseId)}/donations${queryString({
        page,
        page_size: pageSize,
      })}`,
    ),

  recommendations: (donorId: string) =>
    apiRequest<RecommendationCase[]>(
      `/recommendations/${encodeURIComponent(donorId)}`,
    ),

  chat: (question: string) =>
    apiRequest<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),

  reviewQueue: (page = 1, pageSize = 20) =>
    apiRequest<EvidenceListResponse>(
      `/cases/evidence/review-queue${queryString({
        page,
        page_size: pageSize,
      })}`,
    ),

  updateVerification: (evidenceId: string, verification_status: VerificationStatus) =>
    apiRequest<Evidence>(
      `/cases/evidence/${encodeURIComponent(evidenceId)}/verification`,
      {
        method: "PATCH",
        body: JSON.stringify({ verification_status }),
      },
    ),

  uploadEvidence: (caseId: string, file: File, description?: string) => {
    const body = new FormData();
    body.append("file", file);
    if (description) body.append("description", description);
    return apiRequest<Evidence>(`/cases/${encodeURIComponent(caseId)}/evidence`, {
      method: "POST",
      body,
    });
  },

  hybridAnalysis: (caseId: string) =>
    apiRequest<HybridAnalysisResponse>(
      `/ai/cases/${encodeURIComponent(caseId)}/hybrid-analysis`,
      { method: "POST" },
    ),
};
