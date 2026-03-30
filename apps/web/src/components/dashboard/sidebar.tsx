const navigationItems = [
  { key: "overview", active: true },
  { key: "medications" },
  { key: "interactions" },
  { key: "equivalents" },
  { key: "travelPassport" },
  { key: "documents" },
];

type SidebarLabels = {
  overview: string;
  medications: string;
  interactions: string;
  equivalents: string;
  travelPassport: string;
  documents: string;
  travelMode: string;
  travelText: string;
  travelCta: string;
  patientDashboard: string;
};

export function Sidebar({
  labels,
}: {
  labels: SidebarLabels;
}) {
  return (
    <aside className="sidebar">
      <div className="brand-block">
        <div className="brand-block__badge">GPP</div>
        <div>
          <p className="brand-block__eyebrow">Global Pharma Passport</p>
          <h1>{labels.patientDashboard}</h1>
        </div>
      </div>

      <nav className="sidebar__nav" aria-label="Navigation principale">
        {navigationItems.map((item) => (
          <button
            key={item.key}
            type="button"
            className={`sidebar__nav-item${item.active ? " is-active" : ""}`}
          >
            <span>{labels[item.key]}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar__cta">
        <p className="sidebar__cta-label">{labels.travelMode}</p>
        <p className="sidebar__cta-text">{labels.travelText}</p>
        <button type="button" className="primary-button">
          {labels.travelCta}
        </button>
      </div>
    </aside>
  );
}
