"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type { FormEvent } from "react";
import { getDictionary, Locale } from "@/lib/i18n";
import { trackEvent } from "@/lib/analytics";
import { ApiError, register } from "@/lib/api";
import { setAccessToken } from "@/lib/session";

const signupCopy: Record<
  Locale,
  {
    fullNamePlaceholder: string;
    emailPlaceholder: string;
    passwordPlaceholder: string;
    helper: string;
    submit: string;
    loading: string;
    invalidName: string;
    invalidEmail: string;
    invalidPassword: string;
    weakPassword: string;
    genericError: string;
    success: string;
  }
> = {
  fr: {
    fullNamePlaceholder: "Kawtar El Idrissi",
    emailPlaceholder: "kawtar@example.com",
    passwordPlaceholder: "Minimum 10 caractères, avec majuscule, chiffre et symbole",
    helper: "Commence simplement. Tu pourras ajouter tes traitements et activer le mode voyage après inscription.",
    submit: "Créer mon compte",
    loading: "Création du compte...",
    invalidName: "Ajoute ton nom complet pour personnaliser ton passeport médical.",
    invalidEmail: "Ajoute une adresse email valide.",
    invalidPassword: "Choisis un mot de passe d'au moins 10 caractères.",
    weakPassword: "Le mot de passe doit inclure une majuscule, une minuscule, un chiffre et un caractère spécial.",
    genericError: "Le compte n'a pas pu être créé pour le moment. Réessaie dans quelques secondes.",
    success: "Compte créé. Redirection vers ton tableau de bord...",
  },
  en: {
    fullNamePlaceholder: "Kawtar El Idrissi",
    emailPlaceholder: "kawtar@example.com",
    passwordPlaceholder: "At least 10 characters, with uppercase, digit and symbol",
    helper: "Start simple. You can add treatments and enable travel mode right after signup.",
    submit: "Create my account",
    loading: "Creating account...",
    invalidName: "Add your full name to personalize your medical passport.",
    invalidEmail: "Enter a valid email address.",
    invalidPassword: "Choose a password with at least 10 characters.",
    weakPassword: "Password must include uppercase, lowercase, digit and special character.",
    genericError: "Your account could not be created right now. Please try again in a few seconds.",
    success: "Account created. Redirecting to your dashboard...",
  },
  ar: {
    fullNamePlaceholder: "كوثر الإدريسي",
    emailPlaceholder: "kawtar@example.com",
    passwordPlaceholder: "10 أحرف على الأقل مع حرف كبير ورقم ورمز",
    helper: "ابدأ ببساطة. يمكنك إضافة العلاجات وتفعيل وضع السفر مباشرة بعد التسجيل.",
    submit: "إنشاء حسابي",
    loading: "جار إنشاء الحساب...",
    invalidName: "أدخل اسمك الكامل لتخصيص جوازك الطبي.",
    invalidEmail: "أدخل بريدا إلكترونيا صحيحا.",
    invalidPassword: "اختر كلمة مرور من 10 أحرف على الأقل.",
    weakPassword: "يجب أن تحتوي كلمة المرور على حرف كبير وحرف صغير ورقم ورمز خاص.",
    genericError: "تعذر إنشاء الحساب حاليا. حاول مرة أخرى بعد قليل.",
    success: "تم إنشاء الحساب. جار التحويل إلى لوحة المتابعة...",
  },
};

export function SignupForm({ locale }: { locale: Locale }) {
  const router = useRouter();
  const dict = getDictionary(locale);
  const copy = signupCopy[locale];
  const [form, setForm] = useState({
    fullName: "",
    email: "",
    country: "MA",
    password: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function updateField(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (form.fullName.trim().length < 2) {
      setError(copy.invalidName);
      return;
    }

    if (!form.email.includes("@")) {
      setError(copy.invalidEmail);
      return;
    }

    if (form.password.trim().length < 10) {
      setError(copy.invalidPassword);
      return;
    }

    if (
      !/[A-Z]/.test(form.password) ||
      !/[a-z]/.test(form.password) ||
      !/[0-9]/.test(form.password) ||
      !/[^A-Za-z0-9]/.test(form.password)
    ) {
      setError(copy.weakPassword);
      return;
    }

    try {
      setIsSubmitting(true);
      const response = await register({
        email: form.email,
        password: form.password,
        full_name: form.fullName,
        preferred_language: locale,
        country_code: form.country,
      });
      setAccessToken(response.access_token);
      void trackEvent({
        eventName: "signup_submitted",
        locale,
        countryCode: form.country,
        properties: { screen: "signup" },
      });
      setSuccess(copy.success);
      router.push(`/${locale}/dashboard`);
    } catch (error) {
      setError(error instanceof ApiError ? error.message : copy.genericError);
      setIsSubmitting(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <label className="field">
        <span>{dict.auth.fullName}</span>
        <input
          type="text"
          value={form.fullName}
          onChange={(event) => updateField("fullName", event.target.value)}
          placeholder={copy.fullNamePlaceholder}
          autoComplete="name"
        />
      </label>

      <label className="field">
        <span>{dict.auth.email}</span>
        <input
          type="email"
          value={form.email}
          onChange={(event) => updateField("email", event.target.value)}
          placeholder={copy.emailPlaceholder}
          autoComplete="email"
        />
      </label>

      <label className="field">
        <span>{dict.auth.country}</span>
        <select value={form.country} onChange={(event) => updateField("country", event.target.value)}>
          <option value="MA">Maroc</option>
          <option value="FR">France</option>
        </select>
      </label>

      <label className="field">
        <span>{dict.auth.password}</span>
        <input
          type="password"
          value={form.password}
          onChange={(event) => updateField("password", event.target.value)}
          placeholder={copy.passwordPlaceholder}
          autoComplete="new-password"
        />
      </label>

      {error ? (
        <p className="form-feedback form-feedback--error" role="alert">
          {error}
        </p>
      ) : null}

      {success ? <p className="form-feedback form-feedback--success">{success}</p> : null}

      <p className="form-note">{copy.helper}</p>

      <button type="submit" className="primary-button auth-submit" disabled={isSubmitting}>
        {isSubmitting ? copy.loading : copy.submit}
      </button>
    </form>
  );
}
