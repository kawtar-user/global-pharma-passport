import { EquivalentsPageClient } from "@/components/workspace/equivalents-page-client";
import { defaultLocale, isValidLocale } from "@/lib/i18n";

export default function EquivalentsPage({ params }: { params: { locale: string } }) {
  const locale = isValidLocale(params.locale) ? params.locale : defaultLocale;
  return <EquivalentsPageClient locale={locale} />;
}
