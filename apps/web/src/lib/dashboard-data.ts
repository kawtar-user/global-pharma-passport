import type {
  AuthenticatedUser,
  EquivalentPresentationSummary,
  InteractionCheckMatch,
  PatientMedication,
} from "@/lib/api";

export type TreatmentItem = {
  id: string;
  name: string;
  activeIngredient: string;
  schedule: string;
  purpose: string;
  dosageForm: string;
  country: string;
  status: "stable" | "attention";
};

export type AlertItem = {
  id: string;
  title: string;
  severity: "minor" | "moderate" | "major" | "contraindicated";
  summary: string;
  action: string;
};

export type EquivalentItem = {
  id: string;
  source: string;
  destinationCountry: string;
  equivalent: string;
  dosage: string;
  matchScore: number;
};

export type TimelineItem = {
  id: string;
  label: string;
  date: string;
  detail: string;
};

export type DashboardStat = {
  label: string;
  value: string;
  detail: string;
};

export type MedicationDraft = {
  query: string;
  country: string;
  selectedPresentationId: string;
  enteredName: string;
  doseText: string;
  frequencyText: string;
  indication: string;
};

function formatDate(value: string, locale: string) {
  return new Intl.DateTimeFormat(locale, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function formatMonthYear(value: string, locale: string) {
  return new Intl.DateTimeFormat(locale, {
    month: "long",
    year: "numeric",
  }).format(new Date(value));
}

export function buildStats({
  treatments,
  alerts,
  equivalents,
  countryCode,
}: {
  treatments: PatientMedication[];
  alerts: AlertItem[];
  equivalents: EquivalentItem[];
  countryCode: string | null;
}): DashboardStat[] {
  const activeTreatments = treatments.filter((item) => item.status === "active").length;

  return [
    {
      label: "Traitements actifs",
      value: String(activeTreatments),
      detail: `${treatments.length} traitement(s) enregistrés`,
    },
    {
      label: "Alertes majeures",
      value: String(alerts.filter((item) => item.severity !== "minor").length),
      detail: `${alerts.length} alerte(s) détectée(s)`,
    },
    {
      label: "Équivalents disponibles",
      value: String(equivalents.length),
      detail: "Résultats validés sur le corridor actif",
    },
    {
      label: "Passeport patient",
      value: treatments.length > 0 ? "Prêt" : "À créer",
      detail: countryCode ? `Pays principal : ${countryCode}` : "Ajoute un traitement pour l’activer",
    },
  ];
}

export function mapMedicationToTreatmentItem(medication: PatientMedication): TreatmentItem {
  const summary = medication.presentation_summary;
  return {
    id: medication.id,
    name: medication.entered_name,
    activeIngredient: summary?.active_ingredients.join(" + ") || "Principe actif non lié",
    schedule: medication.frequency_text || medication.dose_text || "À compléter",
    purpose: medication.indication || "Indication non renseignée",
    dosageForm: summary?.dosage_form || "Forme non liée",
    country: summary?.country_code || "N/A",
    status: medication.status === "active" ? "stable" : "attention",
  };
}

export function mapInteractionToAlertItem(match: InteractionCheckMatch): AlertItem {
  return {
    id: match.interaction_id,
    title: `${match.ingredient_a_name} + ${match.ingredient_b_name}`,
    severity: match.severity,
    summary: match.clinical_effect,
    action: match.recommendation,
  };
}

export function mapEquivalentToItem(
  sourceMedicationName: string,
  result: EquivalentPresentationSummary,
): EquivalentItem {
  return {
    id: `${sourceMedicationName}-${result.presentation_id}`,
    source: sourceMedicationName,
    destinationCountry: result.country_code,
    equivalent: result.brand_name,
    dosage: `${result.strength_text} · ${result.dosage_form}`,
    matchScore: 100,
  };
}

export function buildTimeline(user: AuthenticatedUser, medications: PatientMedication[], locale: string): TimelineItem[] {
  const baseItems = [
    {
      timestamp: user.created_at,
      id: "account-created",
      label: "Compte créé",
      date: formatDate(user.created_at, locale),
      detail: `Membre depuis ${formatMonthYear(user.created_at, locale)}.`,
    },
  ];

  for (const medication of medications.slice(0, 4)) {
    baseItems.push({
      timestamp: medication.created_at,
      id: medication.id,
      label: "Traitement ajouté",
      date: formatDate(medication.created_at, locale),
      detail: medication.entered_name,
    });
  }

  return baseItems
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .map(({ timestamp: _timestamp, ...item }) => item);
}
