import { TreatmentItem } from "@/lib/dashboard-data";

type TreatmentListProps = {
  items: TreatmentItem[];
  onDelete?: (item: TreatmentItem) => void;
  deletingId?: string | null;
};

export function TreatmentList({ items, onDelete, deletingId }: TreatmentListProps) {
  if (items.length === 0) {
    return <p className="empty-state">Aucun traitement enregistré pour le moment.</p>;
  }

  return (
    <div className="stack-list">
      {items.map((item) => (
        <article key={item.id} className="list-card">
          <div className="list-card__row">
            <div>
              <h3>{item.name}</h3>
              <p>{item.activeIngredient}</p>
            </div>
            <div className="list-card__actions">
              <span className={`status-pill status-pill--${item.status}`}>
                {item.status === "stable" ? "Stable" : "Surveillance"}
              </span>
              {onDelete ? (
                <button
                  type="button"
                  className="list-card__action-button"
                  onClick={() => onDelete(item)}
                  disabled={deletingId === item.id}
                >
                  {deletingId === item.id ? "Suppression..." : "Supprimer"}
                </button>
              ) : null}
            </div>
          </div>
          <dl className="list-card__meta">
            <div>
              <dt>Posologie</dt>
              <dd>{item.schedule}</dd>
            </div>
            <div>
              <dt>Indication</dt>
              <dd>{item.purpose}</dd>
            </div>
            <div>
              <dt>Forme</dt>
              <dd>{item.dosageForm}</dd>
            </div>
            <div>
              <dt>Pays source</dt>
              <dd>{item.country}</dd>
            </div>
          </dl>
        </article>
      ))}
    </div>
  );
}
