import { TimelineItem } from "@/lib/dashboard-data";

type TimelineProps = {
  items: TimelineItem[];
};

export function Timeline({ items }: TimelineProps) {
  if (items.length === 0) {
    return <p className="empty-state">L’activité récente apparaîtra ici après les premières actions.</p>;
  }

  return (
    <div className="timeline">
      {items.map((item) => (
        <article key={item.id} className="timeline__item">
          <span className="timeline__dot" />
          <div>
            <p className="timeline__date">{item.date}</p>
            <h3>{item.label}</h3>
            <p>{item.detail}</p>
          </div>
        </article>
      ))}
    </div>
  );
}
