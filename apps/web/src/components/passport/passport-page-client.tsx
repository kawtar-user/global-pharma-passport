"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, getMyPassport, PassportSnapshot } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { PassportSheet } from "@/components/passport/passport-sheet";

export function PassportPageClient({ locale }: { locale: string }) {
  const router = useRouter();
  const [snapshot, setSnapshot] = useState<PassportSnapshot | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadPassport() {
      const token = getAccessToken();
      if (!token) {
        router.replace(`/${locale}/login`);
        return;
      }

      try {
        const result = await getMyPassport(locale, token);
        if (!cancelled) {
          setSnapshot(result);
        }
      } catch (error) {
        if (!cancelled) {
          setError(error instanceof ApiError ? error.message : "Impossible de charger le passeport.");
        }
      }
    }

    void loadPassport();
    return () => {
      cancelled = true;
    };
  }, [locale, router]);

  if (error) {
    return <main className="passport-sheet"><p className="form-feedback form-feedback--error">{error}</p></main>;
  }

  if (!snapshot) {
    return <main className="passport-sheet"><p className="empty-state">Génération du passeport en cours.</p></main>;
  }

  return <PassportSheet snapshot={snapshot} shareUrl={snapshot.share_url} />;
}
