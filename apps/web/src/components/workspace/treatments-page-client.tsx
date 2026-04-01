"use client";

import Link from "next/link";
import { useState } from "react";
import { MedicationForm } from "@/components/dashboard/medication-form";
import { TreatmentList } from "@/components/dashboard/treatment-list";
import { SectionCard } from "@/components/ui/section-card";
import { WorkspaceShell } from "@/components/workspace/workspace-shell";
import { deleteMyMedication, ApiError } from "@/lib/api";
import { getDictionary, type Locale } from "@/lib/i18n";
import { usePatientWorkspace } from "@/components/workspace/use-patient-workspace";
import type { TreatmentItem } from "@/lib/dashboard-data";
import { getAccessToken } from "@/lib/session";

export function TreatmentsPageClient({ locale }: { locale: Locale }) {
  const dictionary = getDictionary(locale);
  const [actionFeedback, setActionFeedback] = useState<{ kind: "success" | "error"; message: string } | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const {
    user,
    treatments,
    isLoading,
    error,
    isPremium,
    medicationLimit,
    medications,
    addMedication,
    removeMedication,
    upgradeToPremium,
  } = usePatientWorkspace(locale);

  async function handleDeleteTreatment(item: TreatmentItem) {
    const confirmed = window.confirm(`Supprimer "${item.name}" de la liste des traitements ?`);
    if (!confirmed) {
      return;
    }

    const token = getAccessToken();
    if (!token) {
      setActionFeedback({ kind: "error", message: "Ta session a expiré. Reconnecte-toi pour gérer tes traitements." });
      return;
    }

    try {
      setDeletingId(item.id);
      setActionFeedback(null);
      await deleteMyMedication(item.id, token);
      removeMedication(item.id);
      setActionFeedback({ kind: "success", message: "Traitement supprimé. La liste a été mise à jour." });
    } catch (error) {
      setActionFeedback({
        kind: "error",
        message: error instanceof ApiError ? error.message : "Impossible de supprimer ce traitement pour le moment.",
      });
    } finally {
      setDeletingId(null);
    }
  }

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
      {actionFeedback ? (
        <p className={`form-feedback ${actionFeedback.kind === "success" ? "form-feedback--success" : "form-feedback--error"}`}>
          {actionFeedback.message}
        </p>
      ) : null}

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
          <TreatmentList items={treatments} onDelete={handleDeleteTreatment} deletingId={deletingId} />
        </SectionCard>
      </div>
    </WorkspaceShell>
  );
}
