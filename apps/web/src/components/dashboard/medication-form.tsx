"use client";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import type { Locale } from "@/lib/i18n";
import { trackEvent } from "@/lib/analytics";
import { ApiError, createMyMedication, DrugProduct, listDrugProducts, PatientMedication } from "@/lib/api";
import { getAccessToken } from "@/lib/session";

type MedicationFormProps = {
  onMedicationCreated: (medication: PatientMedication) => void;
  locale: Locale;
  defaultCountry: string;
  currentMedicationCount: number;
  medicationLimit: number | null;
  isPremium: boolean;
  onUpgrade: () => void;
};

type MedicationDraft = {
  query: string;
  country: string;
  selectedPresentationId: string;
  enteredName: string;
  doseText: string;
  indication: string;
};

const initialState = (country: string): MedicationDraft => ({
  query: "",
  country: country === "FR" ? "FR" : "MA",
  selectedPresentationId: "",
  enteredName: "",
  doseText: "",
  indication: "",
});

type SearchResult = {
  presentationId: string;
  brandName: string;
  countryCode: string;
  strengthText: string;
  dosageForm: string;
  activeIngredients: string[];
};

type SelectedMedication = SearchResult;

function unique(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}

const medicationCopy: Record<
  Locale,
  {
    labels: {
      search: string;
      dosage: string;
      purpose: string;
      country: string;
      submit: string;
    };
    placeholders: {
      search: string;
      dosage: string;
      purpose: string;
    };
    hints: {
      search: string;
      country: string;
      dosage: string;
    };
    disclaimer: string;
    errors: {
      query: string;
      selection: string;
      dosage: string;
      purpose: string;
      session: string;
    };
    success: string;
    searchStates: {
      idle: string;
      loading: string;
      empty: string;
      submitting: string;
    };
  }
> = {
  fr: {
    labels: {
      search: "Rechercher un médicament",
      schedule: "Posologie",
      purpose: "Indication",
      country: "Pays",
      submit: "Ajouter au passeport",
    },
    placeholders: {
      search: "Ex. Doliprane, Glucophage, Coveram...",
      schedule: "1 comprimé matin et soir",
      purpose: "Diabète, tension, douleur...",
    },
    hints: {
      search: "Commence à taper le nom commercial ou le principe actif. Les suggestions arrivent automatiquement.",
      country: "Choisis le pays où ce médicament est actuellement utilisé.",
    },
    errors: {
      query: "Ajoute un nom de médicament pour lancer la recherche.",
      selection: "Sélectionne un médicament dans les résultats du catalogue.",
      schedule: "Ajoute une posologie simple et compréhensible.",
      purpose: "Ajoute à quoi sert ce traitement.",
      session: "Ta session a expiré. Reconnecte-toi pour ajouter un traitement.",
    },
    success: "Traitement ajouté. Ton passeport médical vient d'être mis à jour.",
    searchStates: {
      idle: "Recherche le médicament exact avant de l'ajouter.",
      loading: "Recherche dans le catalogue en cours...",
      empty: "Aucun résultat pour cette recherche dans le pays choisi.",
      submitting: "Ajout du traitement en cours...",
    },
  },
  en: {
    labels: {
      search: "Search medication",
      schedule: "Dosage",
      purpose: "Reason",
      country: "Country",
      submit: "Add to passport",
    },
    placeholders: {
      search: "e.g. Doliprane, Glucophage, Coveram...",
      schedule: "1 tablet morning and evening",
      purpose: "Diabetes, blood pressure, pain...",
    },
    hints: {
      search: "Start typing a brand or active ingredient. Suggestions load automatically.",
      country: "Choose the country where this medication is currently used.",
    },
    errors: {
      query: "Add a medication name to start the search.",
      selection: "Select one medication from the catalog results.",
      schedule: "Add a simple, easy-to-understand dosage.",
      purpose: "Add what this treatment is for.",
      session: "Your session expired. Sign in again to add a treatment.",
    },
    success: "Medication added. Your medical passport has been updated.",
    searchStates: {
      idle: "Search the exact medication before adding it.",
      loading: "Searching the catalog...",
      empty: "No result found for this search in the selected country.",
      submitting: "Adding medication...",
    },
  },
  ar: {
    labels: {
      search: "البحث عن دواء",
      schedule: "الجرعة",
      purpose: "سبب الاستخدام",
      country: "الدولة",
      submit: "إضافة إلى الجواز الطبي",
    },
    placeholders: {
      search: "مثال: Doliprane أو Glucophage أو Coveram",
      schedule: "قرص صباحا ومساء",
      purpose: "سكري، ضغط، ألم...",
    },
    hints: {
      search: "ابدأ بكتابة الاسم التجاري أو المادة الفعالة وستظهر الاقتراحات تلقائيا.",
      country: "اختر الدولة التي تستعمل فيها هذا الدواء حاليا.",
    },
    errors: {
      query: "أضف اسم الدواء لبدء البحث.",
      selection: "اختر دواء واحدا من نتائج الدليل.",
      schedule: "أضف جرعة واضحة وسهلة الفهم.",
      purpose: "أضف سبب استخدام هذا العلاج.",
      session: "انتهت الجلسة. سجل الدخول من جديد لإضافة علاج.",
    },
    success: "تمت إضافة العلاج وتحديث الجواز الطبي.",
    searchStates: {
      idle: "ابحث عن الدواء الصحيح قبل إضافته.",
      loading: "جار البحث في الدليل...",
      empty: "لا توجد نتيجة لهذا البحث في الدولة المختارة.",
      submitting: "جار إضافة العلاج...",
    },
  },
};

function flattenResults(products: DrugProduct[]): SearchResult[] {
  return products.flatMap((product) =>
    product.presentations.map((presentation) => ({
      presentationId: presentation.id,
      brandName: product.brand_name,
      countryCode: product.country_code,
      strengthText: presentation.strength_text,
      dosageForm: presentation.route || presentation.id,
      activeIngredients: unique(
        presentation.ingredients.map((item) => item.active_ingredient_name ?? item.active_ingredient_id),
      ),
    })),
  );
}

export function MedicationForm({
  onMedicationCreated,
  locale,
  defaultCountry,
  currentMedicationCount,
  medicationLimit,
  isPremium,
  onUpgrade,
}: MedicationFormProps) {
  const [form, setForm] = useState<MedicationDraft>(() => initialState(defaultCountry));
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [searchNotice, setSearchNotice] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [selectedMedication, setSelectedMedication] = useState<SelectedMedication | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const copy = medicationCopy[locale];
  const remainingMedicationSlots =
    medicationLimit === null ? null : Math.max(medicationLimit - currentMedicationCount, 0);

  function updateField(field: keyof MedicationDraft, value: string) {
    if (field === "query" || field === "country") {
      setSelectedMedication(null);
      setSearchNotice("");
    }
    setForm((current) => {
      const next = { ...current, [field]: value };
      if (field === "query" || field === "country") {
        next.selectedPresentationId = "";
        next.enteredName = "";
        next.doseText = "";
      }
      return next;
    });
  }

  async function searchCatalog(query: string, country: string, token: string) {
    const products = await listDrugProducts(query, country, token);
    if (products.length > 0) {
      return {
        results: flattenResults(products),
        notice: "",
      };
    }

    const corridorMatches = await listDrugProducts(query, null, token);
    const activeIngredientNames = unique(
      corridorMatches.flatMap((product) =>
        product.presentations.flatMap((presentation) =>
          presentation.ingredients.map((item) => item.active_ingredient_name),
        ),
      ),
    );

    if (activeIngredientNames.length > 0) {
      const ingredientMatches = await listDrugProducts(activeIngredientNames[0], country, token);
      if (ingredientMatches.length > 0) {
        return {
          results: flattenResults(ingredientMatches),
          notice: `Aucun résultat exact pour "${query}" dans ${country}. Voici les correspondances trouvées à partir du principe actif ${activeIngredientNames[0]}.`,
        };
      }
    }

    if (corridorMatches.length > 0) {
      return {
        results: flattenResults(corridorMatches),
        notice: "Aucun résultat exact dans le pays choisi. Voici les présentations trouvées sur le corridor Maroc-France.",
      };
    }

    return {
      results: [],
      notice: "Aucun résultat trouvé. Essaie le principe actif ou l'autre pays du corridor.",
    };
  }

  useEffect(() => {
    const normalizedQuery = form.query.trim();
    const token = getAccessToken();

    if (selectedMedication && normalizedQuery === `${selectedMedication.brandName} ${selectedMedication.strengthText}`) {
      setIsSearching(false);
      setSearchResults([]);
      return;
    }

    if (normalizedQuery.length < 2) {
      setSearchResults([]);
      setHasSearched(false);
      setIsSearching(false);
      setSearchNotice("");
      return;
    }

    if (!token) {
      setError(copy.errors.session);
      return;
    }

    let cancelled = false;
    setIsSearching(true);
    setHasSearched(true);
    setError("");
    setSuccess("");

    const timeoutId = window.setTimeout(async () => {
      try {
        const response = await searchCatalog(normalizedQuery, form.country, token);
        if (cancelled) {
          return;
        }
        setSearchResults(response.results);
        setSearchNotice(response.notice);
      } catch (searchError) {
        if (!cancelled) {
          setSearchResults([]);
          setError(searchError instanceof ApiError ? searchError.message : copy.searchStates.empty);
        }
      } finally {
        if (!cancelled) {
          setIsSearching(false);
        }
      }
    }, 300);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [form.query, form.country, selectedMedication, copy.errors.session, copy.searchStates.empty]);

  function handleSuggestionSelect(result: SearchResult) {
    setError("");
    setSuccess("");
    setSelectedMedication(result);
    setForm((current) => ({
      ...current,
      query: `${result.brandName} ${result.strengthText}`,
      selectedPresentationId: result.presentationId,
      enteredName: `${result.brandName} ${result.strengthText}`,
      doseText: result.strengthText,
    }));
    setSearchResults([]);
    setSearchNotice(`Sélectionné : ${result.brandName} ${result.strengthText} · ${result.countryCode}`);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setSearchNotice("");

    if (!form.selectedPresentationId) {
      setError(copy.errors.selection);
      return;
    }

    if (form.frequencyText.trim().length < 2) {
      setError(copy.errors.schedule);
      return;
    }

    if (form.indication.trim().length < 2) {
      setError(copy.errors.purpose);
      return;
    }

    try {
      setIsSubmitting(true);
      const token = getAccessToken();
      if (!token) {
        setError(copy.errors.session);
        return;
      }
      const medication = await createMyMedication(
        {
          drug_presentation_id: selectedMedication?.presentationId || form.selectedPresentationId,
          entered_name: selectedMedication ? `${selectedMedication.brandName} ${selectedMedication.strengthText}` : form.enteredName,
          dose_text: selectedMedication?.strengthText || form.doseText,
          frequency_text: form.frequencyText,
          indication: form.indication,
        },
        token,
      );
      void trackEvent({
        eventName: "medication_added",
        locale,
        countryCode: form.country,
        properties: { has_schedule: Boolean(form.frequencyText), has_purpose: Boolean(form.indication) },
      });
      onMedicationCreated(medication);
      setForm(initialState(defaultCountry));
      setSearchResults([]);
      setSelectedMedication(null);
      setHasSearched(false);
      setSuccess(copy.success);
    } catch (error) {
      setError(error instanceof ApiError ? error.message : copy.errors.session);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="medication-form" onSubmit={handleSubmit}>
      {!isPremium ? (
        <div className="upsell-card">
          <div>
            <p className="upsell-card__eyebrow">Offre actuelle</p>
            <strong>Free inclut {medicationLimit ?? 3} traitements et 1 équivalent par recherche.</strong>
            <p>
              {remainingMedicationSlots === 0
                ? "Tu as atteint la limite gratuite. Premium débloque les traitements illimités et le mode voyage complet."
                : `Il te reste ${remainingMedicationSlots} traitement(s) dans Free. Premium débloque tout le passeport sans limite.`}
            </p>
          </div>
          <button type="button" className="secondary-button" onClick={onUpgrade}>
            Passer en Premium
          </button>
        </div>
      ) : (
        <p className="form-note">Premium actif : ajoute tous tes traitements et enrichis ton passeport sans limite.</p>
      )}

      <div className="medication-form__grid">
        <label className="field">
          <span>{copy.labels.search}</span>
          <input
            type="text"
            value={form.query}
            onChange={(event) => updateField("query", event.target.value)}
            placeholder={copy.placeholders.search}
            required
            autoComplete="off"
          />
          <small className="field__hint">{copy.hints.search}</small>
        </label>

        <label className="field">
          <span>{copy.labels.country}</span>
          <select value={form.country} onChange={(event) => updateField("country", event.target.value)}>
            <option value="MA">MA</option>
            <option value="FR">FR</option>
          </select>
          <small className="field__hint">{copy.hints.country}</small>
        </label>

        <label className="field">
          <span>{copy.labels.schedule}</span>
          <input
            type="text"
            value={form.frequencyText}
            onChange={(event) => updateField("frequencyText", event.target.value)}
            placeholder={copy.placeholders.schedule}
            required
          />
        </label>

        <label className="field">
          <span>{copy.labels.purpose}</span>
          <input
            type="text"
            value={form.indication}
            onChange={(event) => updateField("indication", event.target.value)}
            placeholder={copy.placeholders.purpose}
            required
          />
        </label>
      </div>

      {isSearching ? <p className="form-note">{copy.searchStates.loading}</p> : null}

      {selectedMedication ? (
        <p className="form-feedback form-feedback--success">
          Sélectionné : {selectedMedication.brandName} {selectedMedication.strengthText} · {selectedMedication.countryCode}
        </p>
      ) : null}

      {searchResults.length > 0 ? (
        <div className="search-suggestions">
          {searchResults.map((result) => (
            <button
              key={result.presentationId}
              type="button"
              className="search-suggestion"
              onClick={() => handleSuggestionSelect(result)}
            >
              <strong>{result.brandName} {result.strengthText}</strong>
              <span>{result.countryCode} · {result.activeIngredients.join(" + ")}</span>
            </button>
          ))}
        </div>
      ) : null}

      {searchResults.length === 0 && hasSearched && !isSearching && !searchNotice ? (
        <p className="form-note">{hasSearched ? copy.searchStates.empty : copy.searchStates.idle}</p>
      ) : null}

      {searchNotice ? <p className="form-note">{searchNotice}</p> : null}

      {error ? (
        <p className="form-feedback form-feedback--error" role="alert">
          {error}
        </p>
      ) : null}

      {success ? <p className="form-feedback form-feedback--success">{success}</p> : null}

      <button
        type="submit"
        className="primary-button"
        disabled={
          isSubmitting ||
          !selectedMedication ||
          form.frequencyText.trim().length < 2 ||
          form.indication.trim().length < 2
        }
      >
        {isSubmitting ? copy.searchStates.submitting : copy.labels.submit}
      </button>
    </form>
  );
}
