import Link from "next/link";
import { ReactNode } from "react";

type AuthShellProps = {
  title: string;
  subtitle: string;
  alternateLabel: string;
  alternateHref: string;
  alternateAction: string;
  children: ReactNode;
};

export function AuthShell({
  title,
  subtitle,
  alternateLabel,
  alternateHref,
  alternateAction,
  children,
}: AuthShellProps) {
  return (
    <main className="auth-shell">
      <section className="auth-panel auth-panel--brand">
        <div className="brand-block">
          <div className="brand-block__badge">GPP</div>
          <div>
            <p className="brand-block__eyebrow">Global Pharma Passport</p>
            <h1>Ton traitement reste compréhensible partout.</h1>
          </div>
        </div>

        <div className="auth-feature-list">
          <article>
            <strong>Profil médical voyage</strong>
            <p>Une carte internationale claire pour pharmacie, médecin ou proche de confiance.</p>
          </article>
          <article>
            <strong>Équivalents pays</strong>
            <p>Retrouve rapidement une alternative basée sur DCI, dosage et forme galénique.</p>
          </article>
          <article>
            <strong>Alertes pharmacologiques</strong>
            <p>Priorisation visuelle des interactions importantes avant le départ.</p>
          </article>
        </div>
      </section>

      <section className="auth-panel auth-panel--form">
        <div className="auth-copy">
          <p className="landing-card__eyebrow">Accès sécurisé</p>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>

        {children}

        <p className="auth-switch">
          {alternateLabel}{" "}
          <Link href={alternateHref}>
            {alternateAction}
          </Link>
        </p>
      </section>
    </main>
  );
}
