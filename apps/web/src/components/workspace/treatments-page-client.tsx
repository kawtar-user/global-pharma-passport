"use client";

import Link from "next/link";
import { MedicationForm } from "@/components/dashboard/medication-form";
import { TreatmentList } from "@/components/dashboard/treatment-list";
import { SectionCard } from "@/components/ui/section-card";
import { WorkspaceShell } from "@/components/workspace/workspace-shell";
import { getDictionary, type Locale } from "@/lib/i18n";
import { usePatientWorkspace } from "@/components/workspace/use-patient-workspace";

export function TreatmentsPageClient({ locale }: { locale: Locale }) {
  const dictionary = getDictionary(locale);
  const {
    user,
    treatments,
    isLoading,
    error,
    isPremium,
    medicationLimit,
    medications,
    addMedication,
    upgradeToPremium,
  } = usePatientWorkspace(locale);

  if (isLoading) {
    return (
      <WorkspaceShell
        locale={locale}
        title={dictionary.workspace.treatmentsTitle}
        subtitle={dictionary.workspace.treatmentsSubtitle}
      >
        <p className="empty-state">Chargement des traitements en cours.</p>
      </WorkspaceShell>
    );
  }

  if (!user) {
    return (
      <WorkspaceShell
        locale={locale}
        title={dictionary.workspace.treatmentsTitle}
        subtitle={dictionary.workspace.treatmentsSubtitle}
      >
        <p className="form-feedback form-feedback--error">{error || "Impossible de charger les traitements."}</p>
      </WorkspaceShell>
    );
  }

  return (
    <WorkspaceShell
      locale={locale}
      title={dictionary.workspace.treatmentsTitle}
      subtitle={dictionary.workspace.treatmentsSubtitle}
      notice={
        user.is_verified ? null : <p className="form-note">{dictionary.workspace.emailVerificationPending}</p>
      }
      actions={
        <Link href={`/${locale}/passport`} className="secondary-button">
          {dictionary.workspace.passportShortcut}
        </Link>
      }
    >
      {error ? <p className="form-feedback form-feedback--error">{error}</p> : null}

      <div className="workspace-grid workspace-grid--split">
        <SectionCard
          eyebrow={dictionary.dashboard.medications}
          title={dictionary.dashboard.addMedication}
          action={<span className="workspace-chip">{medications.length} actif(s)</span>}
        >
          <p className="form-note">
            {dictionary.workspace.addMedicationHelp}
          </p>
          <MedicationForm
            onMedicationCreated={addMedication}
            locale={locale}
            defaultCountry={user.country_code ?? "MA"}
            currentMedicationCount={medications.length}
            medicationLimit={medicationLimit}
            isPremium={isPremium}
            onUpgrade={upgradeToPremium}
          />
        </SectionCard>

        <SectionCard
          eyebrow={dictionary.dashboard.activeTreatments}
          title={dictionary.workspace.activeTreatmentsTitle}
        >
          <TreatmentList items={treatments} />
        </SectionCard>
      </div>
    </WorkspaceShell>
  );
}
