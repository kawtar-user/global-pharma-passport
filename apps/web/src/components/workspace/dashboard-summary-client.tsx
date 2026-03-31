"use client";

import Link from "next/link";
import { AlertList } from "@/components/dashboard/alert-list";
import { PassportPreview } from "@/components/dashboard/passport-preview";
import { StatsGrid } from "@/components/dashboard/stats-grid";
import { SectionCard } from "@/components/ui/section-card";
import { WorkspaceShell } from "@/components/workspace/workspace-shell";
import { usePatientWorkspace } from "@/components/workspace/use-patient-workspace";
import { buildStats } from "@/lib/dashboard-data";
import { getDictionary, type Locale } from "@/lib/i18n";

export function DashboardSummaryClient({ locale }: { locale: Locale }) {
  const dictionary = getDictionary(locale);
  const {
    user,
    medications,
    treatments,
    alerts,
    equivalents,
    isLoading,
    error,
    isPremium,
    upgradeToPremium,
  } = usePatientWorkspace(locale);

  if (isLoading) {
    return (
      <WorkspaceShell
        locale={locale}
        title={dictionary.workspace.summaryTitle}
        subtitle={dictionary.workspace.summarySubtitle}
      >
        <p className="empty-state">Chargement de l’espace patient.</p>
      </WorkspaceShell>
    );
  }

  if (!user) {
    return (
      <WorkspaceShell
        locale={locale}
        title={dictionary.workspace.summaryTitle}
        subtitle={dictionary.workspace.summarySubtitle}
      >
        <p className="form-feedback form-feedback--error">{error || "Impossible de charger le résumé patient."}</p>
      </WorkspaceShell>
    );
  }

  const stats = buildStats({
    treatments: medications,
    alerts,
    equivalents,
    countryCode: user.country_code,
  });

  return (
    <WorkspaceShell
      locale={locale}
      title={dictionary.workspace.summaryTitle}
      subtitle={dictionary.workspace.summarySubtitle}
    >
      {error ? <p className="form-feedback form-feedback--error">{error}</p> : null}

      <div className="summary-actions">
        <article className="action-card">
          <p className="section-card__eyebrow">{dictionary.dashboard.medications}</p>
          <h2>{dictionary.workspace.addTreatmentShortcut}</h2>
          <p>{dictionary.workspace.summaryAddTreatmentBody}</p>
          <Link href={`/${locale}/treatments`} className="primary-button">
            {dictionary.workspace.addTreatmentShortcut}
          </Link>
        </article>

        <article className="action-card">
          <p className="section-card__eyebrow">{dictionary.dashboard.equivalents}</p>
          <h2>{dictionary.workspace.compareEquivalentShortcut}</h2>
          <p>{dictionary.workspace.summaryCompareBody}</p>
          <Link href={`/${locale}/equivalents`} className="primary-button">
            {dictionary.workspace.compareEquivalentShortcut}
          </Link>
        </article>

        <article className="action-card">
          <p className="section-card__eyebrow">{dictionary.dashboard.travelPassport}</p>
          <h2>{dictionary.workspace.passportShortcut}</h2>
          <p>{dictionary.workspace.summaryPassportBody}</p>
          <Link href={`/${locale}/passport`} className="primary-button">
            {dictionary.workspace.passportShortcut}
          </Link>
        </article>
      </div>

      <StatsGrid stats={stats} />

      <div className="workspace-grid">
        <SectionCard eyebrow={dictionary.dashboard.travelPassport} title={dictionary.workspace.passportCardTitle}>
          <PassportPreview
            medicationCount={treatments.length}
            preferredLanguage={user.preferred_language}
            countryCode={user.country_code ?? "N/A"}
            locale={locale}
            majorInteractionCount={alerts.length}
            equivalentCount={equivalents.length}
            isPremium={isPremium}
            onUpgrade={upgradeToPremium}
          />
        </SectionCard>

        <SectionCard eyebrow={dictionary.dashboard.interactions} title={dictionary.workspace.alertsTitle}>
          <AlertList items={alerts} />
        </SectionCard>
      </div>
    </WorkspaceShell>
  );
}
