import { DashboardSummaryClient } from "@/components/workspace/dashboard-summary-client";
import { defaultLocale, isValidLocale } from "@/lib/i18n";

export default function DashboardPage({ params }: { params: { locale: string } }) {
  const locale = isValidLocale(params.locale) ? params.locale : defaultLocale;
  return <DashboardSummaryClient locale={locale} />;
}
