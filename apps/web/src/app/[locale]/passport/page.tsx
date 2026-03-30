import { PassportPageClient } from "@/components/passport/passport-page-client";
import { defaultLocale, isValidLocale } from "@/lib/i18n";

export default function PassportPage({ params }: { params: { locale: string } }) {
  const locale = isValidLocale(params.locale) ? params.locale : defaultLocale;
  return <PassportPageClient locale={locale} />;
}
