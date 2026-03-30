import { DashboardExperience } from "@/components/dashboard/dashboard-experience";
import { defaultLocale, isValidLocale } from "@/lib/i18n";

export default function DashboardPage({ params }: { params: { locale: string } }) {
  const locale = isValidLocale(params.locale) ? params.locale : defaultLocale;
  return <DashboardExperience locale={locale} />;
}
