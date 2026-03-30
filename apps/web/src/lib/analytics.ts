"use client";

import { Locale } from "@/lib/i18n";

const SESSION_STORAGE_KEY = "gpp_session_id";

function getSessionId(): string {
  if (typeof window === "undefined") {
    return "server-session";
  }

  const existing = window.localStorage.getItem(SESSION_STORAGE_KEY);
  if (existing) {
    return existing;
  }

  const created = `sess_${Math.random().toString(36).slice(2)}_${Date.now()}`;
  window.localStorage.setItem(SESSION_STORAGE_KEY, created);
  return created;
}

export async function trackEvent({
  eventName,
  locale,
  countryCode,
  properties = {},
}: {
  eventName: string;
  locale: Locale;
  countryCode?: string;
  properties?: Record<string, string | number | boolean | null | undefined>;
}) {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!apiBaseUrl || typeof window === "undefined") {
    return;
  }

  const payload = {
    event_name: eventName,
    session_id: getSessionId(),
    locale,
    country_code: countryCode,
    source: "web",
    properties,
  };

  try {
    await fetch(`${apiBaseUrl}/analytics/track`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      keepalive: true,
    });
  } catch {
    // Analytics should never break the user journey.
  }
}
