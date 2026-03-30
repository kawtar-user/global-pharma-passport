type StatItem = {
  label: string;
  value: string;
  detail: string;
};

type StatsGridProps = {
  stats: StatItem[];
};

export function StatsGrid({ stats }: StatsGridProps) {
  return (
    <div className="stats-grid">
      {stats.map((stat) => (
        <article key={stat.label} className="stat-card">
          <p>{stat.label}</p>
          <strong>{stat.value}</strong>
          <span>{stat.detail}</span>
        </article>
      ))}
    </div>
  );
}
