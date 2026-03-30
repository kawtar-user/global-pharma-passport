"use client";

import type { Locale } from "@/lib/i18n";

type OnboardingCardProps = {
  locale: Locale;
  medicationAdded: boolean;
  travelModeEnabled: boolean;
};

const onboardingCopy: Record<
  Locale,
  {
    eyebrow: string;
    title: string;
    subtitle: string;
    complete: string;
    pending: string;
    steps: [string, string, string];
  }
> = {
  fr: {
    eyebrow: "Premiers pas",
    title: "Configuration rapide pour être prêt avant le voyage",
    subtitle: "Complète ces étapes pour obtenir un espace patient vraiment utile dès aujourd'hui.",
    complete: "Terminé",
    pending: "À faire",
    steps: [
      "Compte sécurisé créé",
      "Ajouter un traitement principal",
      "Activer le mode voyage",
    ],
  },
  en: {
    eyebrow: "First steps",
    title: "Quick setup to be ready before traveling",
    subtitle: "Complete these steps to make your patient workspace useful from day one.",
    complete: "Done",
    pending: "To do",
    steps: [
      "Secure account created",
      "Add a primary treatment",
      "Enable travel mode",
    ],
  },
  ar: {
    eyebrow: "الخطوات الأولى",
    title: "إعداد سريع لتكون جاهزا قبل السفر",
    subtitle: "أكمل هذه الخطوات ليصبح ملفك الطبي مفيدا من أول استخدام.",
    complete: "مكتمل",
    pending: "قيد الإنجاز",
    steps: [
      "تم إنشاء حساب آمن",
      "إضافة العلاج الرئيسي",
      "تفعيل وضع السفر",
    ],
  },
};

export function OnboardingCard({
  locale,
  medicationAdded,
  travelModeEnabled,
}: OnboardingCardProps) {
  const copy = onboardingCopy[locale];
  const items = [
    { label: copy.steps[0], done: true },
    { label: copy.steps[1], done: medicationAdded },
    { label: copy.steps[2], done: travelModeEnabled },
  ];
  const completedSteps = items.filter((item) => item.done).length;

  return (
    <section className="onboarding-card" aria-label={copy.title}>
      <div className="onboarding-card__header">
        <div>
          <p className="section-card__eyebrow">{copy.eyebrow}</p>
          <h2>{copy.title}</h2>
          <p>{copy.subtitle}</p>
        </div>
        <div className="onboarding-card__progress">
          <strong>
            {completedSteps}/{items.length}
          </strong>
          <span>{copy.complete}</span>
        </div>
      </div>

      <div className="onboarding-card__steps">
        {items.map((item) => (
          <article key={item.label} className={`onboarding-step${item.done ? " is-done" : ""}`}>
            <span className="onboarding-step__icon" aria-hidden="true">
              {item.done ? "✓" : "•"}
            </span>
            <div>
              <strong>{item.label}</strong>
              <p>{item.done ? copy.complete : copy.pending}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
