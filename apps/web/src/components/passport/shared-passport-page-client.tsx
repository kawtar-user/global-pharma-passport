"use client";

import { useEffect, useState } from "react";
import { ApiError, getSharedPassport, PassportSnapshot } from "@/lib/api";
import { PassportSheet } from "@/components/passport/passport-sheet";

export function SharedPassportPageClient({ locale, shareToken }: { locale: string; shareToken: string }) {
  const [snapshot, setSnapshot] = useState<PassportSnapshot | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadPassport() {
      try {
        const result = await getSharedPassport(shareToken, locale);
        if (!cancelled) {
          setSnapshot(result);
        }
      } catch (error) {
        if (!cancelled) {
          setError(error instanceof ApiError ? error.message : "Impossible de charger le passeport partagé.");
        }
      }
    }

    void loadPassport();
    return () => {
      cancelled = true;
    };
  }, [locale, shareToken]);

  if (error) {
    return <main className="passport-sheet"><p className="form-feedback form-feedback--error">{error}</p></main>;
  }

  if (!snapshot) {
    return <main className="passport-sheet"><p className="empty-state">Chargement du passeport partagé.</p></main>;
  }

  return <PassportSheet snapshot={snapshot} isSharedView />;
}
