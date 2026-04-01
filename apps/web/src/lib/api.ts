import { getAccessToken } from "@/lib/session";

export class ApiError extends Error {
  status: number;
  requestId: string | null;

  constructor(message: string, status: number, requestId: string | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.requestId = requestId;
  }
}

export type AuthenticatedUser = {
  id: string;
  email: string;
  full_name: string;
  preferred_language: string;
  country_code: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
};

export type AccessTokenResponse = {
  access_token: string;
  token_type: string;
  requires_verification: boolean;
};

export type DrugProduct = {
  id: string;
  brand_name: string;
  country_code: string;
  manufacturer: string | null;
  marketing_status: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  presentations: DrugPresentation[];
};

export type DrugPresentation = {
  id: string;
  drug_product_id: string;
  dosage_form_id: string;
  route: string | null;
  strength_text: string;
  package_description: string | null;
  pack_size: number | null;
  rx_required: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  ingredients: MedicationIngredient[];
};

export type MedicationIngredient = {
  id: string;
  active_ingredient_id: string;
  active_ingredient_name: string | null;
  strength_value: number | null;
  strength_unit: string | null;
  is_primary: boolean;
};

export type PatientMedication = {
  id: string;
  user_id: string;
  drug_presentation_id: string | null;
  entered_name: string;
  dose_text: string | null;
  frequency_text: string | null;
  indication: string | null;
  instructions_simple: string | null;
  status: "active" | "paused" | "stopped";
  created_at: string;
  updated_at: string;
  presentation_summary: MedicationPresentationSummary | null;
};

export type MedicationPresentationSummary = {
  presentation_id: string;
  brand_name: string;
  country_code: string;
  dosage_form: string;
  strength_text: string;
  route: string | null;
  active_ingredients: string[];
};

export type InteractionCheckResponse = {
  checked_pairs: number;
  matches: InteractionCheckMatch[];
};

export type InteractionCheckMatch = {
  interaction_id: string;
  ingredient_a_id: string;
  ingredient_b_id: string;
  ingredient_a_name: string;
  ingredient_b_name: string;
  severity: "minor" | "moderate" | "major" | "contraindicated";
  clinical_effect: string;
  recommendation: string;
};

export type EquivalentSearchResponse = {
  source_presentation_id: string;
  target_country_code: string | null;
  results: EquivalentPresentationSummary[];
  notice?: {
    code: string;
    message: string;
  } | null;
};

export type EntitlementRead = {
  plan_code: string;
  is_premium: boolean;
  limits: {
    medications_max: number | null;
    equivalent_results_per_search: number | null;
    travel_mode_enabled: boolean;
  };
};

export type CheckoutSessionResponse = {
  checkout_url: string;
};

export type EquivalentPresentationSummary = {
  presentation_id: string;
  brand_name: string;
  country_code: string;
  dosage_form: string;
  strength_text: string;
  route: string | null;
};

export type PassportMedicationItem = {
  medication_id: string;
  entered_name: string;
  brand_name: string | null;
  active_ingredients: string[];
  dosage: string | null;
  frequency: string | null;
  indication: string | null;
  country_code: string | null;
  dosage_form: string | null;
};

export type PassportInteractionItem = {
  interaction_id: string;
  severity: string;
  title: string;
  clinical_effect: string;
  recommendation: string;
};

export type PassportSnapshot = {
  passport_id: string;
  share_token: string;
  title: string;
  language_code: string;
  status: string;
  generated_at: string;
  share_path: string;
  share_url: string;
  patient: {
    full_name: string;
    preferred_language: string;
    country_code: string | null;
  };
  medications: PassportMedicationItem[];
  major_interactions: PassportInteractionItem[];
};

type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
  token?: string | null;
};

type ApiErrorPayload = {
  error?: {
    code?: string;
    message?: string;
    request_id?: string;
    details?: Array<{
      field?: string;
      message?: string;
    }>;
  };
  detail?: string | { message?: string };
};

function getApiBaseUrl() {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!apiBaseUrl) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not configured");
  }
  return apiBaseUrl;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const apiBaseUrl = getApiBaseUrl();
  const token = options.token ?? getAccessToken();
  const response = await fetch(`${apiBaseUrl}${path}`, {
    method: options.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
    cache: "no-store",
  });

  if (!response.ok) {
    let message = "Une erreur est survenue.";
    let requestId: string | null = response.headers.get("X-Request-ID");
    try {
      const data = (await response.json()) as ApiErrorPayload;
      if (data.error?.request_id) {
        requestId = data.error.request_id;
      }
      if (typeof data.error?.message === "string" && data.error.message.trim()) {
        message = data.error.message;
      } else if (data.error?.details?.length && data.error.details[0]?.message) {
        message = data.error.details[0].message;
      } else if (typeof data.detail === "string") {
        message = data.detail;
      } else if (data.detail && typeof data.detail.message === "string") {
        message = data.detail.message;
      }
    } catch {
      message = response.statusText || message;
    }
    if (requestId && response.status >= 500) {
      message = `${message} (ref: ${requestId})`;
    }
    throw new ApiError(message, response.status, requestId);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function register(payload: {
  email: string;
  password: string;
  full_name: string;
  preferred_language: string;
  country_code: string;
}) {
  return request<AccessTokenResponse>("/auth/register", {
    method: "POST",
    body: payload,
    token: null,
  });
}

export function login(payload: { email: string; password: string }) {
  return request<AccessTokenResponse>("/auth/login", {
    method: "POST",
    body: payload,
    token: null,
  });
}

export function getCurrentUser(token?: string | null) {
  return request<AuthenticatedUser>("/auth/me", { token });
}

export function getMyEntitlements(token?: string | null) {
  return request<EntitlementRead>("/billing/me/entitlements", { token });
}

export function listMyMedications(token?: string | null) {
  return request<PatientMedication[]>("/medications/me", { token });
}

export function createMyMedication(
  payload: {
    drug_presentation_id: string;
    entered_name: string;
    dose_text: string;
    frequency_text: string;
    indication: string;
  },
  token?: string | null,
) {
  return request<PatientMedication>("/medications/me", {
    method: "POST",
    body: payload,
    token,
  });
}

export function deleteMyMedication(medicationId: string, token?: string | null) {
  return request<void>(`/medications/me/${medicationId}`, {
    method: "DELETE",
    token,
  });
}

export function listDrugProducts(query: string, countryCode?: string | null, token?: string | null) {
  const searchParams = new URLSearchParams({ query });
  if (countryCode) {
    searchParams.set("country_code", countryCode);
  }
  return request<DrugProduct[]>(`/medications/products?${searchParams.toString()}`, { token });
}

export function checkInteractions(presentationIds: string[], token?: string | null) {
  return request<InteractionCheckResponse>("/interactions/check", {
    method: "POST",
    body: { presentation_ids: presentationIds },
    token,
  });
}

export function findEquivalents(
  presentationId: string,
  targetCountryCode: string,
  token?: string | null,
) {
  const searchParams = new URLSearchParams({ target_country_code: targetCountryCode });
  return request<EquivalentSearchResponse>(
    `/international-equivalents/search/${presentationId}?${searchParams.toString()}`,
    { token },
  );
}

export function getMyPassport(languageCode?: string, token?: string | null) {
  const searchParams = new URLSearchParams();
  if (languageCode) {
    searchParams.set("language_code", languageCode);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return request<PassportSnapshot>(`/passport/me${suffix}`, { token });
}

export function getSharedPassport(shareToken: string, languageCode?: string) {
  const searchParams = new URLSearchParams();
  if (languageCode) {
    searchParams.set("language_code", languageCode);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return request<PassportSnapshot>(`/passport/shared/${shareToken}${suffix}`, { token: null });
}

export function createCheckoutSession(
  payload: {
    success_path: string;
    cancel_path: string;
  },
  token?: string | null,
) {
  return request<CheckoutSessionResponse>("/billing/checkout-session", {
    method: "POST",
    body: payload,
    token,
  });
}
