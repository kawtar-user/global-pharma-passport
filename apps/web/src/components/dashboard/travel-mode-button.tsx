"use client";

import type { Locale } from "@/lib/i18n";
import { trackEvent } from "@/lib/analytics";

export function TravelModeButton({
  label,
  enabledLabel,
  locale,
  helperText,
  enabledHelperText,
  enabled,
  isPremium,
  onToggle,
  onUpgrade,
}: {
  label: string;
  enabledLabel: string;
  helperText: string;
  enabledHelperText: string;
  locale: Locale;
  enabled: boolean;
  isPremium: boolean;
  onToggle: (value: boolean) => void;
  onUpgrade: () => void;
}) {
  const upgradeMode = !isPremium;

  return (
    <div className={`travel-mode-button${enabled ? " is-enabled" : ""}${upgradeMode ? " is-locked" : ""}`}>
      <button
        type="button"
        className="travel-mode-button__action"
        aria-pressed={enabled}
        onClick={() => {
          if (upgradeMode) {
            onUpgrade();
            return;
          }
          const nextValue = !enabled;
          onToggle(nextValue);
          void trackEvent({
            eventName: nextValue ? "travel_mode_enabled" : "travel_mode_disabled",
            locale,
            properties: { state: nextValue },
          });
        }}
      >
        <span className="travel-mode-button__dot" />
        {upgradeMode ? "Mode voyage Premium" : enabled ? enabledLabel : label}
      </button>
      <p className="travel-mode-button__hint">
        {upgradeMode
          ? "Active Premium pour préparer un passeport complet, partager facilement et garder tes équivalents sans limite."
          : enabled
            ? enabledHelperText
            : helperText}
      </p>
    </div>
  );
}
