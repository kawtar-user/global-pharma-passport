import Link from "next/link";
import { defaultLocale, getDictionary, isValidLocale } from "@/lib/i18n";

export default function LocalizedHomePage({ params }: { params: { locale: string } }) {
  const locale = isValidLocale(params.locale) ? params.locale : defaultLocale;
  const dict = getDictionary(locale);

  return (
    <main className="landing-shell">
      <div className="landing-card">
        <p className="landing-card__eyebrow">{dict.marketing.eyebrow}</p>
        <h1>{dict.marketing.title}</h1>
        <p>{dict.marketing.subtitle}</p>
        <div className="landing-benefits">
          {dict.marketing.benefits.map((benefit) => (
            <article key={benefit} className="landing-benefit">
              <strong>{benefit}</strong>
            </article>
          ))}
        </div>
        <div className="landing-actions">
          <Link href={`/${locale}/signup`} className="primary-button">
            {dict.marketing.signup}
          </Link>
          <Link href={`/${locale}/login`} className="secondary-button">
            {dict.marketing.login}
          </Link>
        </div>
      </div>
    </main>
  );
}
