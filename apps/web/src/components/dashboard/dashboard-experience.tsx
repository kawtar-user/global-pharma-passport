"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AlertList } from "@/components/dashboard/alert-list";
import { EquivalentsTable } from "@/components/dashboard/equivalents-table";
import { HeroBanner } from "@/components/dashboard/hero-banner";
import { MedicationForm } from "@/components/dashboard/medication-form";
import { OnboardingCard } from "@/components/dashboard/onboarding-card";
import { PassportPreview } from "@/components/dashboard/passport-preview";
import { Sidebar } from "@/components/dashboard/sidebar";
import { StatsGrid } from "@/components/dashboard/stats-grid";
import { Timeline } from "@/components/dashboard/timeline";
import { Topbar } from "@/components/dashboard/topbar";
import { TravelModeButton } from "@/components/dashboard/travel-mode-button";
import { TreatmentList } from "@/components/dashboard/treatment-list";
import { SectionCard } from "@/components/ui/section-card";
import {
  buildTimeline,
  buildStats,
  mapEquivalentToItem,
  mapInteractionToAlertItem,
  mapMedicationToTreatmentItem,
} from "@/lib/dashboard-data";
import { getDictionary, type Locale } from "@/lib/i18n";
import { trackEvent } from "@/lib/analytics";
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
import { clearAccessToken, getAccessToken } from "@/lib/session";

type DashboardExperienceProps = {
  locale: Locale;
};

function formatMemberSince(date: string, locale: string) {
  return new Intl.DateTimeFormat(locale, {
    month: "long",
    year: "numeric",
  }).format(new Date(date));
}

function getTargetCountry(countryCode: string | null) {
  return countryCode === "FR" ? "MA" : "FR";
}

export function DashboardExperience({ locale }: DashboardExperienceProps) {
  const router = useRouter();
  const dictionary = getDictionary(locale);
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [entitlements, setEntitlements] = useState<EntitlementRead | null>(null);
  const [medications, setMedications] = useState<PatientMedication[]>([]);
  const [alerts, setAlerts] = useState<ReturnType<typeof mapInteractionToAlertItem>[]>([]);
  const [equivalents, setEquivalents] = useState<ReturnType<typeof mapEquivalentToItem>[]>([]);
  const [equivalentNotice, setEquivalentNotice] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [travelModeEnabled, setTravelModeEnabled] = useState(false);
  const [targetCountry, setTargetCountry] = useState("FR");

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
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

        void trackEvent({
          eventName: "dashboard_viewed",
          locale,
          properties: {
            treatment_count: medicationsResult.status === "fulfilled" ? medicationsResult.value.length : 0,
          },
        });
      } catch (error) {
        if (cancelled) {
          return;
        }
        if (error instanceof ApiError && error.status === 401) {
          clearAccessToken();
          router.replace(`/${locale}/login`);
          return;
        }
        setError(error instanceof Error ? error.message : "Impossible de charger ton espace patient.");
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadDashboard();
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

      const linkedMedications = medications.filter(
        (medication) => medication.presentation_summary?.presentation_id,
      );
      const presentationIds = linkedMedications
        .map((medication) => medication.presentation_summary?.presentation_id)
        .filter((value): value is string => Boolean(value));

      try {
        setError("");
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
      } catch (error) {
        if (!cancelled) {
          setError(error instanceof Error ? error.message : "Impossible de charger les alertes et équivalents.");
        }
      }
    }

    void loadDerivedData();
    return () => {
      cancelled = true;
    };
  }, [medications, targetCountry]);

  function handleMedicationCreated(medication: PatientMedication) {
    setError("");
    setMedications((current) => [medication, ...current]);
  }

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
    } catch (error) {
      setError(error instanceof Error ? error.message : "Impossible d’ouvrir l’offre Premium pour le moment.");
    }
  }

  if (isLoading) {
    return (
      <main className="dashboard-shell">
        <div className="dashboard-content">
          <section className="section-card">
            <div className="section-card__header">
              <div>
                <p className="section-card__eyebrow">Chargement</p>
                <h2>Connexion à ton espace patient</h2>
              </div>
            </div>
            <p className="empty-state">Récupération du profil, des traitements et des alertes en cours.</p>
          </section>
        </div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="dashboard-shell">
        <div className="dashboard-content">
          <section className="section-card">
            <div className="section-card__header">
              <div>
                <p className="section-card__eyebrow">Espace patient</p>
                <h2>Impossible d'afficher le tableau de bord</h2>
              </div>
            </div>
            <p className="empty-state">
              {error || "Le profil n'a pas pu être chargé après la connexion. Réessaie dans quelques secondes."}
            </p>
          </section>
        </div>
      </main>
    );
  }

  const treatments = medications.map(mapMedicationToTreatmentItem);
  const stats = buildStats({
    treatments: medications,
    alerts,
    equivalents,
    countryCode: user.country_code,
  });
  const timeline = buildTimeline(user, medications, locale);
  const memberSince = formatMemberSince(user.created_at, locale);
  const medicationAdded = medications.length > 0;
  const isPremium = entitlements?.is_premium ?? false;
  const medicationLimit = entitlements?.limits.medications_max ?? 3;
  const passportProof = medicationAdded
    ? "Passeport prêt à consulter et partager"
    : "Ajoute un premier traitement pour préparer ton passeport";

  return (
    <main className="dashboard-shell">
      <Sidebar
        labels={{
          overview: dictionary.dashboard.overview,
          medications: dictionary.dashboard.medications,
          interactions: dictionary.dashboard.interactions,
          equivalents: dictionary.dashboard.equivalents,
          travelPassport: dictionary.dashboard.travelPassport,
          documents: dictionary.dashboard.documents,
          travelMode: dictionary.dashboard.travelMode,
          travelText: dictionary.dashboard.travelText,
          travelCta: dictionary.dashboard.travelCta,
          patientDashboard: dictionary.dashboard.patientDashboard,
        }}
      />

      <div className="dashboard-content">
        {error ? <p className="form-feedback form-feedback--error">{error}</p> : null}

        <Topbar
          name={user.full_name}
          memberSince={memberSince}
          countryCode={user.country_code ?? "N/A"}
          preferredLanguage={user.preferred_language}
        />

        <div className="dashboard-toolbar">
          <HeroBanner
            homeCountry={user.country_code ?? "N/A"}
            treatmentCount={treatments.length}
            targetCountry={targetCountry}
            isPremium={isPremium}
            onUpgrade={() => void handleUpgrade()}
          />
          <TravelModeButton
            label={dictionary.dashboard.travelMode}
            enabledLabel={dictionary.dashboard.travelModeEnabled}
            helperText={dictionary.dashboard.travelText}
            enabledHelperText={dictionary.dashboard.travelCta}
            locale={locale}
            enabled={travelModeEnabled}
            isPremium={isPremium}
            onToggle={setTravelModeEnabled}
            onUpgrade={() => void handleUpgrade()}
          />
        </div>

        <p className="form-note">
          {isPremium
            ? `Premium actif : ton passeport reste central pour voyager entre ${user.country_code ?? "MA"} et ${targetCountry}.`
            : "Free te permet de commencer simplement. Premium débloque les traitements illimités, les équivalents sans limite et le mode voyage complet."}
        </p>

        <OnboardingCard
          locale={locale}
          medicationAdded={medicationAdded}
          travelModeEnabled={travelModeEnabled}
        />

        <StatsGrid stats={stats} />

        <div className="dashboard-grid">
          <SectionCard eyebrow="Passeport" title="Passeport patient central">
            <PassportPreview
              medicationCount={treatments.length}
              preferredLanguage={user.preferred_language}
              countryCode={user.country_code ?? "N/A"}
              locale={locale}
              majorInteractionCount={alerts.length}
              equivalentCount={equivalents.length}
              isPremium={isPremium}
              onUpgrade={() => void handleUpgrade()}
            />
            <p className="form-note">{passportProof}</p>
          </SectionCard>

          <SectionCard eyebrow={dictionary.dashboard.medications} title={dictionary.dashboard.addMedication}>
            <MedicationForm
              onMedicationCreated={handleMedicationCreated}
              locale={locale}
              defaultCountry={user.country_code ?? "MA"}
              currentMedicationCount={medications.length}
              medicationLimit={medicationLimit}
              isPremium={isPremium}
              onUpgrade={() => void handleUpgrade()}
            />
          </SectionCard>

          <SectionCard eyebrow={dictionary.dashboard.medications} title={dictionary.dashboard.activeTreatments}>
            <TreatmentList items={treatments} />
          </SectionCard>

          <SectionCard eyebrow="Safety" title={dictionary.dashboard.safety}>
            <AlertList items={alerts} />
          </SectionCard>

          <SectionCard eyebrow="International" title={dictionary.dashboard.international}>
            <EquivalentsTable
              items={equivalents}
              isPremium={isPremium}
              notice={equivalentNotice}
              onUpgrade={() => void handleUpgrade()}
            />
          </SectionCard>

          <SectionCard eyebrow="History" title={dictionary.dashboard.recentActivity}>
            <Timeline items={timeline} />
          </SectionCard>
        </div>
      </div>
    </main>
  );
}
