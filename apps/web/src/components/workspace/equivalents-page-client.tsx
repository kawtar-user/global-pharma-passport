"use client";

import Link from "next/link";
import { AlertList } from "@/components/dashboard/alert-list";
import { EquivalentsTable } from "@/components/dashboard/equivalents-table";
import { TreatmentList } from "@/components/dashboard/treatment-list";
import { SectionCard } from "@/components/ui/section-card";
import { WorkspaceShell } from "@/components/workspace/workspace-shell";
import { usePatientWorkspace } from "@/components/workspace/use-patient-workspace";
import { getDictionary, type Locale } from "@/lib/i18n";

export function EquivalentsPageClient({ locale }: { locale: Locale }) {
  const dictionary = getDictionary(locale);
  const {
    user,
    treatments,
    equivalents,
    equivalentNotice,
    alerts,
    isLoading,
    error,
    isPremium,
    upgradeToPremium,
  } = usePatientWorkspace(locale);

  if (isLoading) {
    return (
      <WorkspaceShell
        locale={locale}
        title={dictionary.workspace.equivalentsTitle}
        subtitle={dictionary.workspace.equivalentsSubtitle}
      >
        <p className="empty-state">Chargement des équivalents en cours.</p>
      </WorkspaceShell>
    );
  }

  if (!user) {
    return (
      <WorkspaceShell
        locale={locale}
        title={dictionary.workspace.equivalentsTitle}
        subtitle={dictionary.workspace.equivalentsSubtitle}
      >
        <p className="form-feedback form-feedback--error">{error || "Impossible de charger les équivalents."}</p>
      </WorkspaceShell>
    );
  }

  return (
    <WorkspaceShell
      locale={locale}
      title={dictionary.workspace.equivalentsTitle}
      subtitle={`${dictionary.workspace.equivalentsSubtitle} ${dictionary.workspace.corridorLabel}: ${user.country_code ?? "MA"} -> ${user.country_code === "FR" ? "MA" : "FR"}.`}
      notice={
        user.is_verified ? null : <p className="form-note">{dictionary.workspace.emailVerificationPending}</p>
      }
      actions={
        <Link href={`/${locale}/treatments`} className="secondary-button">
          {dictionary.workspace.addTreatmentShortcut}
        </Link>
      }
    >
      {error ? <p className="form-feedback form-feedback--error">{error}</p> : null}

      {treatments.length === 0 ? (
        <SectionCard eyebrow={dictionary.dashboard.equivalents} title={dictionary.workspace.equivalentsEmptyTitle}>
          <p className="empty-state">{dictionary.workspace.equivalentsEmptyBody}</p>
          <Link href={`/${locale}/treatments`} className="primary-button">
            {dictionary.workspace.addTreatmentShortcut}
          </Link>
        </SectionCard>
      ) : (
        <div className="workspace-grid">
          <SectionCard eyebrow={dictionary.dashboard.equivalents} title={dictionary.workspace.equivalentsResultsTitle}>
            <EquivalentsTable
              items={equivalents}
              notice={equivalentNotice}
              isPremium={isPremium}
              onUpgrade={upgradeToPremium}
            />
          </SectionCard>

          <SectionCard eyebrow={dictionary.dashboard.medications} title={dictionary.workspace.sourceTreatmentsTitle}>
            <TreatmentList items={treatments} />
          </SectionCard>

          <SectionCard eyebrow={dictionary.dashboard.interactions} title={dictionary.workspace.alertsTitle}>
            <AlertList items={alerts} />
          </SectionCard>
        </div>
      )}
    </WorkspaceShell>
  );
}
