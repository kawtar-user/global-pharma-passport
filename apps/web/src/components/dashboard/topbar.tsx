type TopbarProps = {
  name: string;
  memberSince: string;
  countryCode: string;
  preferredLanguage: string;
};

export function Topbar({ name, memberSince, countryCode, preferredLanguage }: TopbarProps) {
  return (
    <header className="topbar">
      <div>
        <p className="topbar__eyebrow">Tableau de bord patient</p>
        <h2>Bonjour {name}</h2>
        <p className="topbar__subtitle">
          Suivi centralisé des traitements, alertes pharmacologiques et préparation voyage.
        </p>
      </div>

      <div className="topbar__meta">
        <div>
          <span>Membre depuis</span>
          <strong>{memberSince}</strong>
        </div>
        <div>
          <span>Pays principal</span>
          <strong>{countryCode}</strong>
        </div>
        <div>
          <span>Langue préférée</span>
          <strong>{preferredLanguage.toUpperCase()}</strong>
        </div>
      </div>
    </header>
  );
}
