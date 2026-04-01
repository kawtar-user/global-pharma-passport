"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ApiError,
  AuthenticatedUser,
  checkInteractions,
  createCheckoutSession,
  EntitlementRead,
  findEquivalents,
  getCurrentUser,
  getMyEntitlements,
  listMyMedications,
  PatientMedication,
} from "@/lib/api";
import { mapEquivalentToItem, mapInteractionToAlertItem, mapMedicationToTreatmentItem } from "@/lib/dashboard-data";
import type { Locale } from "@/lib/i18n";
import { clearAccessToken, getAccessToken } from "@/lib/session";

function getTargetCountry(countryCode: string | null) {
  return countryCode === "FR" ? "MA" : "FR";
}

export function usePatientWorkspace(locale: Locale) {
  const router = useRouter();
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [entitlements, setEntitlements] = useState<EntitlementRead | null>(null);
  const [medications, setMedications] = useState<PatientMedication[]>([]);
  const [alerts, setAlerts] = useState<ReturnType<typeof mapInteractionToAlertItem>[]>([]);
  const [equivalents, setEquivalents] = useState<ReturnType<typeof mapEquivalentToItem>[]>([]);
  const [equivalentNotice, setEquivalentNotice] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [targetCountry, setTargetCountry] = useState("FR");

  useEffect(() => {
    let cancelled = false;

    async function loadWorkspace() {
      const token = getAccessToken();
      if (!token) {
        router.replace(`/${locale}/login`);
        return;
      }

      try {
        setIsLoading(true);
        setError("");
        const currentUser = await getCurrentUser(token);
        if (cancelled) {
          return;
        }

        setUser(currentUser);
        setTargetCountry(getTargetCountry(currentUser.country_code));

        const [medicationsResult, entitlementsResult] = await Promise.allSettled([
          listMyMedications(token),
          getMyEntitlements(token),
        ]);

        if (cancelled) {
          return;
        }

        if (medicationsResult.status === "fulfilled") {
          setMedications(medicationsResult.value);
        } else {
          setMedications([]);
          setError("Le profil est chargé, mais les traitements n'ont pas pu être récupérés pour le moment.");
        }

        if (entitlementsResult.status === "fulfilled") {
          setEntitlements(entitlementsResult.value);
        } else {
          setEntitlements(null);
          setError((current) =>
            current || "Le profil est chargé, mais les informations d'abonnement ne sont pas disponibles pour le moment.",
          );
        }
      } catch (loadError) {
        if (cancelled) {
          return;
        }
        if (loadError instanceof ApiError && loadError.status === 401) {
          clearAccessToken();
          router.replace(`/${locale}/login`);
          return;
        }
        setError(loadError instanceof Error ? loadError.message : "Impossible de charger l'espace patient.");
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadWorkspace();
    return () => {
      cancelled = true;
    };
  }, [locale, router]);

  useEffect(() => {
    let cancelled = false;

    async function loadDerivedData() {
      const token = getAccessToken();
      if (!token) {
        return;
      }

      const linkedMedications = medications.filter((medication) => medication.presentation_summary?.presentation_id);
      const presentationIds = linkedMedications
        .map((medication) => medication.presentation_summary?.presentation_id)
        .filter((value): value is string => Boolean(value));

      try {
        if (presentationIds.length >= 2) {
          const interactionResponse = await checkInteractions(presentationIds, token);
          if (!cancelled) {
            setAlerts(interactionResponse.matches.map(mapInteractionToAlertItem));
          }
        } else if (!cancelled) {
          setAlerts([]);
        }

        const nextEquivalents = [];
        let nextEquivalentNotice = "";

        for (const medication of linkedMedications) {
          const sourceCountry = medication.presentation_summary?.country_code;
          const presentationId = medication.presentation_summary?.presentation_id;
          if (!presentationId || !sourceCountry || sourceCountry === targetCountry) {
            continue;
          }

          const response = await findEquivalents(presentationId, targetCountry, token);
          if (!response.results.length && response.notice?.message) {
            nextEquivalentNotice = response.notice.message;
          }
          for (const item of response.results) {
            nextEquivalents.push(mapEquivalentToItem(medication.entered_name, item));
          }
        }

        if (!cancelled) {
          setEquivalents(nextEquivalents);
          setEquivalentNotice(nextEquivalentNotice);
        }
      } catch (derivedError) {
        if (!cancelled) {
          setError(derivedError instanceof Error ? derivedError.message : "Impossible de charger les données dérivées.");
        }
      }
    }

    void loadDerivedData();
    return () => {
      cancelled = true;
    };
  }, [medications, targetCountry]);

  async function handleUpgrade() {
    const token = getAccessToken();
    if (!token) {
      router.push(`/${locale}/login`);
      return;
    }

    try {
      const { checkout_url } = await createCheckoutSession(
        {
          success_path: `/${locale}/dashboard`,
          cancel_path: `/${locale}/dashboard`,
        },
        token,
      );
      window.location.href = checkout_url;
    } catch (upgradeError) {
      setError(upgradeError instanceof Error ? upgradeError.message : "Impossible d’ouvrir l’offre Premium.");
    }
  }

  const treatments = useMemo(() => medications.map(mapMedicationToTreatmentItem), [medications]);

  return {
    user,
    entitlements,
    medications,
    treatments,
    alerts,
    equivalents,
    equivalentNotice,
    targetCountry,
    error,
    isLoading,
    isPremium: entitlements?.is_premium ?? false,
    medicationLimit: entitlements?.limits.medications_max ?? 3,
    setError,
    addMedication: (medication: PatientMedication) => setMedications((current) => [medication, ...current]),
    removeMedication: (medicationId: string) =>
      setMedications((current) => current.filter((item) => item.id !== medicationId)),
    upgradeToPremium: () => void handleUpgrade(),
  };
}
