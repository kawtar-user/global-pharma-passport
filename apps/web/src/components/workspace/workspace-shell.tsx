"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import type { Locale } from "@/lib/i18n";
import { getDictionary } from "@/lib/i18n";

type WorkspaceShellProps = {
  locale: Locale;
  title: string;
  subtitle: string;
  actions?: ReactNode;
  notice?: ReactNode;
  children: ReactNode;
};

export function WorkspaceShell({ locale, title, subtitle, actions, notice, children }: WorkspaceShellProps) {
  const pathname = usePathname();
  const dictionary = getDictionary(locale);
  const items = [
    { href: `/${locale}/dashboard`, label: dictionary.workspace.summary },
    { href: `/${locale}/treatments`, label: dictionary.dashboard.medications },
    { href: `/${locale}/equivalents`, label: dictionary.dashboard.equivalents },
    { href: `/${locale}/passport`, label: dictionary.dashboard.travelPassport },
  ];

  return (
    <main className="workspace-shell">
      <header className="workspace-header">
        <div className="workspace-header__top">
          <Link href={`/${locale}/dashboard`} className="workspace-brand">
            <span className="workspace-brand__badge">GPP</span>
            <span>Global Pharma Passport</span>
          </Link>
          <nav className="workspace-nav" aria-label="Navigation principale">
            {items.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`workspace-nav__link${pathname === item.href ? " is-active" : ""}`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="workspace-header__body">
          <div>
            <p className="section-card__eyebrow">Poste de travail patient</p>
            <h1>{title}</h1>
            <p className="workspace-header__subtitle">{subtitle}</p>
            {notice ? <div className="workspace-header__notice">{notice}</div> : null}
          </div>
          {actions ? <div className="workspace-header__actions">{actions}</div> : null}
        </div>
      </header>

      <section className="workspace-content">{children}</section>
    </main>
  );
}
