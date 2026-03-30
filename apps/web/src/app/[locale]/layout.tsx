import type { ReactNode } from "react";
import { defaultLocale, getDictionary, isValidLocale, localeDirection } from "@/lib/i18n";

export default function LocaleLayout({
  children,
  params,
}: Readonly<{ children: ReactNode; params: { locale: string } }>) {
  const locale = isValidLocale(params.locale) ? params.locale : defaultLocale;
  const direction = localeDirection[locale];
  const dictionary = getDictionary(locale);

  return (
    <div lang={locale} dir={direction} data-locale={locale}>
      <main aria-label={dictionary.dashboard.patientDashboard}>{children}</main>
    </div>
  );
}
