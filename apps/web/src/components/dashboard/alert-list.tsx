import { AlertItem } from "@/lib/dashboard-data";

type AlertListProps = {
  items: AlertItem[];
};

export function AlertList({ items }: AlertListProps) {
  if (items.length === 0) {
    return <p className="empty-state">Aucune interaction majeure détectée pour le moment.</p>;
  }

  return (
    <div className="stack-list">
      {items.map((item) => (
        <article key={item.id} className={`alert-card alert-card--${item.severity}`}>
          <div className="alert-card__header">
            <h3>{item.title}</h3>
            <span>{item.severity}</span>
          </div>
          <p>{item.summary}</p>
          <strong>{item.action}</strong>
        </article>
      ))}
    </div>
  );
}
