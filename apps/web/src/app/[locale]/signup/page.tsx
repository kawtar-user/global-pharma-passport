import { AuthShell } from "@/components/auth/auth-shell";
import { SignupForm } from "@/components/auth/signup-form";
import { defaultLocale, getDictionary, isValidLocale } from "@/lib/i18n";

export default function SignupPage({ params }: { params: { locale: string } }) {
  const locale = isValidLocale(params.locale) ? params.locale : defaultLocale;
  const dict = getDictionary(locale);

  return (
    <AuthShell
      title={dict.auth.signupTitle}
      subtitle={dict.auth.signupSubtitle}
      alternateLabel={dict.auth.existingMember}
      alternateHref={`/${locale}/login`}
      alternateAction={dict.auth.signIn}
    >
      <SignupForm locale={locale} />
    </AuthShell>
  );
}
