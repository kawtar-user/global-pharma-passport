export type CountryConfig = {
  code: string;
  locale: string;
  currency: string;
  dateExample: string;
  decimalSeparator: "." | ",";
};

export const countryConfigs: Record<string, CountryConfig> = {
  MA: { code: "MA", locale: "fr-MA", currency: "MAD", dateExample: "29/03/2026", decimalSeparator: "," },
  FR: { code: "FR", locale: "fr-FR", currency: "EUR", dateExample: "29/03/2026", decimalSeparator: "," },
  GB: { code: "GB", locale: "en-GB", currency: "GBP", dateExample: "29/03/2026", decimalSeparator: "." },
  US: { code: "US", locale: "en-US", currency: "USD", dateExample: "03/29/2026", decimalSeparator: "." },
};

export function getCountryConfig(countryCode: string | undefined): CountryConfig {
  return countryConfigs[countryCode ?? "MA"] ?? countryConfigs.MA;
}
