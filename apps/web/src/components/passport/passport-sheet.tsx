"use client";

import { useState } from "react";
import type { PassportSnapshot } from "@/lib/api";

type PassportSheetProps = {
  snapshot: PassportSnapshot;
  shareUrl?: string;
  isSharedView?: boolean;
};

export function PassportSheet({ snapshot, shareUrl, isSharedView = false }: PassportSheetProps) {
  const [copyFeedback, setCopyFeedback] = useState("");
  const canUseNativeShare = typeof navigator !== "undefined" && "share" in navigator;

  async function handleCopyLink() {
    if (!shareUrl || typeof navigator === "undefined" || !navigator.clipboard) {
      return;
    }
    await navigator.clipboard.writeText(shareUrl);
    setCopyFeedback("Lien copié");
    window.setTimeout(() => setCopyFeedback(""), 2000);
  }

  async function handleNativeShare() {
    if (!shareUrl || typeof navigator === "undefined" || !("share" in navigator)) {
      return;
    }
    await navigator.share({
      title: snapshot.title,
      text: `Passeport patient de ${snapshot.patient.full_name}`,
      url: shareUrl,
    });
  }

  function handlePrint() {
    if (typeof window === "undefined") {
      return;
    }
    window.print();
  }

  return (
    <main className="passport-sheet">
      <section className="passport-sheet__card">
        <div className="passport-sheet__header">
          <div>
            <p className="passport-sheet__eyebrow">Global Pharma Passport</p>
            <h1>{snapshot.patient.full_name}</h1>
            <p className="passport-sheet__subtitle">
              Passeport patient généré à partir des données réelles enregistrées dans l’application.
            </p>
          </div>
          <div className="passport-sheet__meta">
            <div>
              <span>Pays</span>
              <strong>{snapshot.patient.country_code ?? "N/A"}</strong>
            </div>
            <div>
              <span>Langue</span>
              <strong>{snapshot.patient.preferred_language.toUpperCase()}</strong>
            </div>
            <div>
              <span>Généré le</span>
              <strong>{new Date(snapshot.generated_at).toLocaleString()}</strong>
            </div>
          </div>
        </div>

        <div className="passport-preview__proofs">
          <span className="value-pill">{snapshot.medications.length > 0 ? "Passeport prêt" : "Ajoute un traitement pour compléter ce passeport"}</span>
          <span className="value-pill">
            {snapshot.major_interactions.length === 0
              ? "Aucune interaction majeure détectée"
              : `${snapshot.major_interactions.length} interaction(s) majeure(s) signalée(s)`}
          </span>
          <span className="value-pill">Corridor actif : Maroc ↔ France</span>
        </div>

        {!isSharedView && shareUrl ? (
          <div className="passport-sheet__share">
            <span>Lien de partage</span>
            <strong>{shareUrl}</strong>
            <div className="passport-sheet__actions print-hidden">
              <button type="button" className="primary-button" onClick={handleCopyLink}>
                Copier le lien
              </button>
              {canUseNativeShare ? (
                <button type="button" className="secondary-button" onClick={() => void handleNativeShare()}>
                  Partager
                </button>
              ) : null}
              <button type="button" className="secondary-button" onClick={handlePrint}>
                Export PDF simple
              </button>
            </div>
            {copyFeedback ? <p className="form-feedback form-feedback--success">{copyFeedback}</p> : null}
          </div>
        ) : null}

        <section className="passport-sheet__section">
          <h2>Traitements enregistrés</h2>
          {snapshot.medications.length === 0 ? (
            <p className="empty-state">Aucun traitement enregistré pour le moment.</p>
          ) : (
            <div className="passport-sheet__list">
              {snapshot.medications.map((item) => (
                <article key={item.medication_id} className="passport-medication">
                  <h3>{item.entered_name}</h3>
                  <p>{item.brand_name ?? "Présentation non liée au catalogue"}</p>
                  <dl>
                    <div>
                      <dt>Principes actifs</dt>
                      <dd>{item.active_ingredients.join(" + ") || "Non renseigné"}</dd>
                    </div>
                    <div>
                      <dt>Dosage</dt>
                      <dd>{item.dosage ?? "Non renseigné"}</dd>
                    </div>
                    <div>
                      <dt>Fréquence</dt>
                      <dd>{item.frequency ?? "Non renseignée"}</dd>
                    </div>
                    <div>
                      <dt>Pays</dt>
                      <dd>{item.country_code ?? "N/A"}</dd>
                    </div>
                  </dl>
                </article>
              ))}
            </div>
          )}
        </section>

        <section className="passport-sheet__section">
          <h2>Interactions majeures</h2>
          {snapshot.major_interactions.length === 0 ? (
            <p className="empty-state">Aucune interaction majeure détectée sur ce passeport.</p>
          ) : (
            <div className="passport-sheet__list">
              {snapshot.major_interactions.map((item) => (
                <article key={item.interaction_id} className="passport-alert">
                  <div className="passport-alert__header">
                    <h3>{item.title}</h3>
                    <span>{item.severity}</span>
                  </div>
                  <p>{item.clinical_effect}</p>
                  <strong>{item.recommendation}</strong>
                </article>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
