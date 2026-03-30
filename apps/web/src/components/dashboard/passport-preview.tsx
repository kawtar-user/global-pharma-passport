import Link from "next/link";

type PassportPreviewProps = {
  medicationCount: number;
  preferredLanguage: string;
  countryCode: string;
  locale: string;
  majorInteractionCount: number;
  equivalentCount: number;
  isPremium: boolean;
  onUpgrade: () => void;
};

export function PassportPreview({
  medicationCount,
  preferredLanguage,
  countryCode,
  locale,
  majorInteractionCount,
  equivalentCount,
  isPremium,
  onUpgrade,
}: PassportPreviewProps) {
  const passportReady = medicationCount > 0;

  return (
    <div className="passport-preview">
      <div className="passport-preview__card">
        <div className="passport-preview__intro">
          <p className="passport-preview__eyebrow">Passeport patient</p>
          <h3>{passportReady ? "Passeport prêt à consulter et partager" : "Prépare ton passeport en ajoutant ton traitement"}</h3>
          <p className="passport-preview__subtitle">
            Une vue claire de tes médicaments, principes actifs, pays source et alertes majeures sur le corridor Maroc-France.
          </p>
        </div>

        <div className="passport-preview__grid">
          <div>
            <span>Traitements</span>
            <strong>{medicationCount} actif(s)</strong>
          </div>
          <div>
            <span>Interactions</span>
            <strong>{majorInteractionCount === 0 ? "Aucune majeure détectée" : `${majorInteractionCount} à surveiller`}</strong>
          </div>
          <div>
            <span>Pays principal</span>
            <strong>{countryCode}</strong>
          </div>
          <div>
            <span>Langue</span>
            <strong>{preferredLanguage.toUpperCase()}</strong>
          </div>
          <div>
            <span>Équivalents trouvés</span>
            <strong>{equivalentCount > 0 ? `${equivalentCount} disponible(s)` : "En attente"}</strong>
          </div>
          <div>
            <span>Partage</span>
            <strong>{passportReady ? "Lien prêt" : "S’active après ajout d’un traitement"}</strong>
          </div>
        </div>

        <div className="passport-preview__proofs">
          <span className="value-pill">{passportReady ? "Passeport prêt" : "Ajoute un traitement pour générer ton passeport"}</span>
          <span className="value-pill">{majorInteractionCount === 0 ? "Aucune interaction majeure détectée" : "Interactions majeures signalées clairement"}</span>
          {equivalentCount > 0 ? <span className="value-pill">Équivalent trouvé sur le corridor actif</span> : null}
        </div>
      </div>

      <div className="passport-preview__actions">
        <Link href={`/${locale}/passport`} className="primary-button">
          Ouvrir le passeport
        </Link>
        {!isPremium ? (
          <button type="button" className="secondary-button" onClick={onUpgrade}>
            Débloquer PDF + mode voyage
          </button>
        ) : null}
      </div>
    </div>
  );
}
