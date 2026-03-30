import { AuthShell } from "@/components/auth/auth-shell";
import { LoginForm } from "@/components/auth/login-form";
import { defaultLocale, getDictionary, isValidLocale } from "@/lib/i18n";

export default function LoginPage({ params }: { params: { locale: string } }) {
  const locale = isValidLocale(params.locale) ? params.locale : defaultLocale;
  const dict = getDictionary(locale);

  return (
    <AuthShell
      title={dict.auth.loginTitle}
      subtitle={dict.auth.loginSubtitle}
      alternateLabel={dict.auth.noAccount}
      alternateHref={`/${locale}/signup`}
      alternateAction={dict.auth.createAccess}
    >
      <LoginForm locale={locale} />
    </AuthShell>
  );
}
