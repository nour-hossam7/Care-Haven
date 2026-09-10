export type UserRole = "user" | "admin";

export type CaseLevel = "Low" | "Medium" | "High" | "Critical";
export type CaseStatus = "Active" | "Under Review" | "Funded" | "Completed";
export type VerificationStatus = "unreviewed" | "approved" | "rejected";

export interface User {
  user_id: string;
  email: string;
  role: UserRole | string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Case {
  case_id: string;
  description: string | null;
  assistance_category: string | null;
  people_affected: number | null;
  country: string | null;
  governorate: string | null;
  city: string | null;
  latitude: unknown;
  longitude: unknown;
  severity: string | null;
  urgency: string | null;
  required_resources: string | null;
  estimated_funding: unknown;
  current_funding: unknown;
  submission_date: string | null;
  status: string | null;
  priority: string | null;
  created_by: string | null;
}

export interface CaseCreate {
  description: string;
  assistance_category: string;
  people_affected: number;
  country: string;
  governorate?: string;
  city?: string;
  latitude?: number;
  longitude?: number;
  severity: CaseLevel;
  urgency: CaseLevel;
  required_resources?: string;
  estimated_funding?: number;
}

export interface CaseStatusUpdate {
  status: CaseStatus;
}

export interface Paginated<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export type CaseListResponse = Paginated<Case>;

export interface Donation {
  donation_id: string;
  case_id: string | null;
  user_id: string | null;
  donor_id: string | null;
  amount: unknown;
  date: string | null;
}

export interface DonationCreate {
  case_id: string;
  amount: number;
}

export type DonationListResponse = Paginated<Donation>;

export interface RecommendationCase extends Case {
  recommendation_rank: number;
  recommendation_score: number;
  recommendation_reasons: string[];
  recommendation_breakdown: Record<string, number>;
}

export interface ChatSource {
  document: string | null;
  page: number | null;
  source: string | null;
  chunk_id: string;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
}

export interface Evidence {
  evidence_id: string;
  case_id: string | null;
  evidence_type: string | null;
  file_path: string | null;
  source_type: string | null;
  uploaded_at: string | null;
  description: string | null;
  verification_status: string | null;
}

export interface CaseEvidence extends Evidence {
  image_url: string | null;
}

export type EvidenceListResponse = Paginated<Evidence>;

export interface CaseListParams {
  page?: number;
  page_size?: number;
  assistance_category?: string;
  country?: string;
  governorate?: string;
  city?: string;
  priority?: string;
  severity?: string;
  urgency?: string;
  status?: string;
}

export interface CaseAnalysisResult {
  category: string;
  assistance: string[];
  people_affected: number;
  severity: CaseLevel | string;
  summary: string;
}

export interface HybridPriorityResult {
  score: number;
  priority_level: string;
  reasons: string[];
}

export interface HybridAnalysisResponse {
  analysis_id: number;
  case_id: string;
  llm_analysis: CaseAnalysisResult | null;
  priority: HybridPriorityResult | null;
  unavailable_components: string[];
  created_at: string | null;
}
