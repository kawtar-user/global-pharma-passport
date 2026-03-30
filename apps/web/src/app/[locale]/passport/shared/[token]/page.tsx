import { SharedPassportPageClient } from "@/components/passport/shared-passport-page-client";
import { defaultLocale, isValidLocale } from "@/lib/i18n";

export default function SharedPassportPage({
  params,
}: {
  params: { locale: string; token: string };
}) {
  const locale = isValidLocale(params.locale) ? params.locale : defaultLocale;
  return <SharedPassportPageClient locale={locale} shareToken={params.token} />;
}
