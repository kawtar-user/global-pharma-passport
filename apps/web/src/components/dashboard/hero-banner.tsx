type HeroBannerProps = {
  homeCountry: string;
  treatmentCount: number;
  targetCountry: string;
  isPremium: boolean;
  onUpgrade: () => void;
};

export function HeroBanner({
  homeCountry,
  treatmentCount,
  targetCountry,
  isPremium,
  onUpgrade,
}: HeroBannerProps) {
  return (
    <section className="hero-banner">
      <div className="hero-banner__content">
        <p className="hero-banner__eyebrow">Résumé clinique du jour</p>
        <h3>Ton passeport patient centralise maintenant ton traitement réel entre {homeCountry} et {targetCountry}.</h3>
        <p>
          Traitements, alertes majeures et équivalents validés sont prêts à être consultés et partagés pour voyager plus sereinement.
        </p>
        <div className="hero-banner__value-strip">
          <span className="value-pill">{treatmentCount > 0 ? "Passeport prêt à être enrichi" : "Ajoute un premier traitement pour activer ton passeport"}</span>
          <span className="value-pill">{isPremium ? "Premium actif : mode voyage complet" : "Free : 3 traitements et 1 équivalent par recherche"}</span>
        </div>
        {!isPremium ? (
          <div className="hero-banner__cta">
            <p>Premium débloque les traitements illimités, les équivalents sans limite et le mode voyage complet.</p>
            <button type="button" className="secondary-button" onClick={onUpgrade}>
              Passer en Premium
            </button>
          </div>
        ) : null}
      </div>

      <div className="hero-banner__metrics">
        <div className="metric-chip">
          <span>Pays de référence</span>
          <strong>{homeCountry}</strong>
        </div>
        <div className="metric-chip">
          <span>Traitements liés</span>
          <strong>{treatmentCount}</strong>
        </div>
        <div className="metric-chip">
          <span>Passeport</span>
          <strong>{treatmentCount > 0 ? "Prêt" : "À compléter"}</strong>
        </div>
      </div>
    </section>
  );
}
