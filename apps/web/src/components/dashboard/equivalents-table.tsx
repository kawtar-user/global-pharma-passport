import { EquivalentItem } from "@/lib/dashboard-data";

type EquivalentsTableProps = {
  items: EquivalentItem[];
  isPremium: boolean;
  notice?: string;
  onUpgrade: () => void;
};

export function EquivalentsTable({ items, isPremium, notice, onUpgrade }: EquivalentsTableProps) {
  if (items.length === 0) {
    return (
      <div className="stack-list">
        <p className="empty-state">{notice ?? "Aucun équivalent disponible pour les traitements liés au catalogue."}</p>
        {!isPremium ? (
          <div className="upsell-card upsell-card--inline">
            <div>
              <p className="upsell-card__eyebrow">Premium</p>
              <strong>Débloque plus d’équivalents et un usage voyage complet.</strong>
              <p>Idéal si tu compares plusieurs traitements entre le Maroc et la France.</p>
            </div>
            <button type="button" className="secondary-button" onClick={onUpgrade}>
              Voir l’offre Premium
            </button>
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <div className="stack-list">
      <p className="form-note">Équivalent trouvé : les correspondances affichées sont vérifiées sur DCI, dosage et forme.</p>
      <div className="equivalents-table">
        <div className="equivalents-table__head">
          <span>Médicament source</span>
          <span>Pays cible</span>
          <span>Équivalent</span>
          <span>Correspondance</span>
        </div>
        {items.map((item) => (
          <div key={item.id} className="equivalents-table__row">
            <div>
              <strong>{item.source}</strong>
              <p>{item.dosage}</p>
            </div>
            <span>{item.destinationCountry}</span>
            <div>
              <strong>{item.equivalent}</strong>
              <p>Vérifié sur DCI, dosage et forme</p>
            </div>
            <span className="match-score">{item.matchScore}%</span>
          </div>
        ))}
      </div>
      {!isPremium ? (
        <div className="upsell-card upsell-card--inline">
          <div>
            <p className="upsell-card__eyebrow">Free vs Premium</p>
            <strong>Free montre un résultat par recherche. Premium débloque toutes les correspondances utiles.</strong>
          </div>
          <button type="button" className="secondary-button" onClick={onUpgrade}>
            Débloquer tous les équivalents
          </button>
        </div>
      ) : null}
    </div>
  );
}
