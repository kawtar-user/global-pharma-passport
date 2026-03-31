"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { getDictionary, Locale } from "@/lib/i18n";
import { trackEvent } from "@/lib/analytics";
import { ApiError, login } from "@/lib/api";
import { setAccessToken } from "@/lib/session";

const loginCopy: Record<
  Locale,
  {
    emailPlaceholder: string;
    passwordPlaceholder: string;
    helper: string;
    secureNote: string;
    submit: string;
    loading: string;
    invalidEmail: string;
    invalidPassword: string;
    genericError: string;
    sessionReady: string;
    verificationPending: string;
  }
> = {
  fr: {
    emailPlaceholder: "patient@example.com",
    passwordPlaceholder: "Minimum 8 caractères",
    helper: "Connecte-toi avec ton compte patient pour retrouver tes traitements, alertes et équivalents.",
    secureNote: "Connexion sécurisée au backend patient",
    submit: "Entrer dans mon espace",
    loading: "Connexion en cours...",
    invalidEmail: "Ajoute une adresse email valide pour continuer.",
    invalidPassword: "Le mot de passe doit contenir au moins 8 caractères.",
    genericError: "Impossible de continuer pour le moment. Réessaie dans quelques secondes.",
    sessionReady: "Connexion réussie. Chargement de ton espace patient...",
    verificationPending:
      "Connexion réussie. L'email reste à confirmer, mais l'accès beta est temporairement autorisé.",
  },
  en: {
    emailPlaceholder: "patient@example.com",
    passwordPlaceholder: "At least 8 characters",
    helper: "Sign in with your patient account to access treatments, alerts and equivalents.",
    secureNote: "Secure sign-in to the patient backend",
    submit: "Open my workspace",
    loading: "Signing in...",
    invalidEmail: "Enter a valid email address to continue.",
    invalidPassword: "Your password must be at least 8 characters long.",
    genericError: "We could not continue right now. Please try again in a few seconds.",
    sessionReady: "Signed in successfully. Loading your patient workspace...",
    verificationPending:
      "Signed in successfully. The email still needs confirmation, but beta access is temporarily allowed.",
  },
  ar: {
    emailPlaceholder: "patient@example.com",
    passwordPlaceholder: "8 أحرف على الأقل",
    helper: "سجل الدخول بحسابك للوصول إلى العلاجات والتنبيهات والبدائل الدولية.",
    secureNote: "دخول آمن إلى الواجهة الخلفية للمريض",
    submit: "الدخول إلى مساحتي",
    loading: "جار تسجيل الدخول...",
    invalidEmail: "أدخل بريدا إلكترونيا صحيحا للمتابعة.",
    invalidPassword: "يجب أن تحتوي كلمة المرور على 8 أحرف على الأقل.",
    genericError: "تعذر المتابعة حاليا. حاول مرة أخرى بعد قليل.",
    sessionReady: "تم تسجيل الدخول بنجاح. جار تحميل مساحتك الطبية...",
    verificationPending:
      "تم تسجيل الدخول بنجاح. ما زال البريد يحتاج إلى تأكيد، لكن الوصول التجريبي مسموح مؤقتا.",
  },
};

export function LoginForm({ locale }: { locale: Locale }) {
  const router = useRouter();
  const dict = getDictionary(locale);
  const copy = loginCopy[locale];
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!email.includes("@")) {
      setError(copy.invalidEmail);
      return;
    }

    if (password.trim().length < 8) {
      setError(copy.invalidPassword);
      return;
    }

    try {
      setIsSubmitting(true);
      const response = await login({ email, password });
      setAccessToken(response.access_token);
      void trackEvent({
        eventName: "login_submitted",
        locale,
        properties: { screen: "login" },
      });
      setSuccess(response.requires_verification ? copy.verificationPending : copy.sessionReady);
      router.push(`/${locale}/dashboard`);
    } catch (error) {
      setError(error instanceof ApiError ? error.message : copy.genericError);
      setIsSubmitting(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <label className="field">
        <span>{dict.auth.email}</span>
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder={copy.emailPlaceholder}
          autoComplete="email"
          aria-invalid={Boolean(error)}
        />
      </label>

      <label className="field">
        <span>{dict.auth.password}</span>
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder={copy.passwordPlaceholder}
          autoComplete="current-password"
          aria-invalid={Boolean(error)}
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

      <div className="auth-links">
        <span>{copy.secureNote}</span>
        <Link href={`/${locale}/signup`}>{dict.auth.signupAction}</Link>
      </div>
    </form>
  );
}
