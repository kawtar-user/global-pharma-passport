import { TreatmentsPageClient } from "@/components/workspace/treatments-page-client";
import { defaultLocale, isValidLocale } from "@/lib/i18n";

export default function TreatmentsPage({ params }: { params: { locale: string } }) {
  const locale = isValidLocale(params.locale) ? params.locale : defaultLocale;
  return <TreatmentsPageClient locale={locale} />;
}
