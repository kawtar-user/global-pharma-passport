export const locales = ["fr", "en", "ar"] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = "fr";

export const localeDirection: Record<Locale, "ltr" | "rtl"> = {
  fr: "ltr",
  en: "ltr",
  ar: "rtl",
};

type Dictionary = {
  marketing: {
    eyebrow: string;
    title: string;
    subtitle: string;
    login: string;
    signup: string;
  };
  auth: {
    secureAccess: string;
    loginTitle: string;
    loginSubtitle: string;
    signupTitle: string;
    signupSubtitle: string;
    noAccount: string;
    createAccess: string;
    existingMember: string;
    signIn: string;
    email: string;
    password: string;
    fullName: string;
    country: string;
    loginAction: string;
    signupAction: string;
  };
  dashboard: {
    patientDashboard: string;
    overview: string;
    medications: string;
    interactions: string;
    equivalents: string;
    travelPassport: string;
    documents: string;
    travelMode: string;
    travelModeEnabled: string;
    addMedication: string;
    activeTreatments: string;
    safety: string;
    international: string;
    travel: string;
    recentActivity: string;
    travelCta: string;
    travelText: string;
  };
};

export const dictionaries: Record<Locale, Dictionary> = {
  fr: {
    marketing: {
      eyebrow: "Global Pharma Passport",
      title: "Le passeport international du traitement medicamenteux.",
      subtitle:
        "Un espace patient simple, premium et medical pour se connecter, gerer ses traitements, comprendre les interactions et activer le mode voyage.",
      login: "Se connecter",
      signup: "Creer un compte",
    },
    auth: {
      secureAccess: "Acces securise",
      loginTitle: "Connexion patient",
      loginSubtitle:
        "Accede a tes traitements, alertes critiques et equivalents pays en un seul endroit.",
      signupTitle: "Creer un compte",
      signupSubtitle:
        "Prepare un profil medical international clair et partageable en quelques minutes.",
      noAccount: "Pas encore de compte ?",
      createAccess: "Creer mon acces",
      existingMember: "Deja membre ?",
      signIn: "Se connecter",
      email: "Email",
      password: "Mot de passe",
      fullName: "Nom complet",
      country: "Pays principal",
      loginAction: "Se connecter",
      signupAction: "Creer mon compte",
    },
    dashboard: {
      patientDashboard: "Tableau de bord patient",
      overview: "Vue d'ensemble",
      medications: "Mes traitements",
      interactions: "Interactions",
      equivalents: "Equivalents pays",
      travelPassport: "Passeport voyage",
      documents: "Documents",
      travelMode: "Mode voyage",
      travelModeEnabled: "Mode voyage active",
      addMedication: "Ajouter un medicament",
      activeTreatments: "Traitements actifs",
      safety: "Interactions et points d'attention",
      international: "Equivalents recommandes par pays",
      travel: "Carte medicale partageable",
      recentActivity: "Activite recente",
      travelCta: "Ouvrir le passeport",
      travelText:
        "Ton resume medical est pret a etre partage en francais, anglais et arabe.",
    },
  },
  en: {
    marketing: {
      eyebrow: "Global Pharma Passport",
      title: "The international passport for medication continuity.",
      subtitle:
        "A simple, premium medical workspace to sign in, manage treatments, review interactions and activate travel mode.",
      login: "Log in",
      signup: "Create account",
    },
    auth: {
      secureAccess: "Secure access",
      loginTitle: "Patient login",
      loginSubtitle:
        "Access your treatments, critical alerts and country equivalents in one place.",
      signupTitle: "Create an account",
      signupSubtitle:
        "Build a clear international medical profile in just a few minutes.",
      noAccount: "No account yet?",
      createAccess: "Create access",
      existingMember: "Already a member?",
      signIn: "Sign in",
      email: "Email",
      password: "Password",
      fullName: "Full name",
      country: "Primary country",
      loginAction: "Log in",
      signupAction: "Create my account",
    },
    dashboard: {
      patientDashboard: "Patient dashboard",
      overview: "Overview",
      medications: "My medications",
      interactions: "Interactions",
      equivalents: "Country equivalents",
      travelPassport: "Travel passport",
      documents: "Documents",
      travelMode: "Travel mode",
      travelModeEnabled: "Travel mode enabled",
      addMedication: "Add medication",
      activeTreatments: "Active treatments",
      safety: "Interactions and attention points",
      international: "Recommended equivalents by country",
      travel: "Shareable medical card",
      recentActivity: "Recent activity",
      travelCta: "Open passport",
      travelText:
        "Your medical summary is ready to share in French, English and Arabic.",
    },
  },
  ar: {
    marketing: {
      eyebrow: "Global Pharma Passport",
      title: "جواز دولي لاستمرارية العلاج الدوائي.",
      subtitle:
        "مساحة مريض بسيطة وراقية لمتابعة الادوية وفهم التداخلات وتفعيل وضع السفر.",
      login: "تسجيل الدخول",
      signup: "انشاء حساب",
    },
    auth: {
      secureAccess: "دخول آمن",
      loginTitle: "دخول المريض",
      loginSubtitle:
        "الوصول الى الادوية والتنبيهات المهمة والبدائل الدولية في مكان واحد.",
      signupTitle: "انشاء حساب",
      signupSubtitle:
        "انشئ ملفا طبيا دوليا واضحا وقابلا للمشاركة خلال دقائق.",
      noAccount: "ليس لديك حساب؟",
      createAccess: "انشاء الوصول",
      existingMember: "لديك حساب بالفعل؟",
      signIn: "تسجيل الدخول",
      email: "البريد الالكتروني",
      password: "كلمة المرور",
      fullName: "الاسم الكامل",
      country: "الدولة الرئيسية",
      loginAction: "تسجيل الدخول",
      signupAction: "انشاء الحساب",
    },
    dashboard: {
      patientDashboard: "لوحة المريض",
      overview: "نظرة عامة",
      medications: "ادويتي",
      interactions: "التداخلات",
      equivalents: "البدائل حسب الدولة",
      travelPassport: "جواز السفر الطبي",
      documents: "المستندات",
      travelMode: "وضع السفر",
      travelModeEnabled: "تم تفعيل وضع السفر",
      addMedication: "اضافة دواء",
      activeTreatments: "العلاجات النشطة",
      safety: "التداخلات ونقاط الانتباه",
      international: "بدائل موصى بها حسب الدولة",
      travel: "بطاقة طبية قابلة للمشاركة",
      recentActivity: "النشاط الاخير",
      travelCta: "فتح الجواز",
      travelText: "الملخص الطبي جاهز للمشاركة بالفرنسية والانجليزية والعربية.",
    },
  },
};

export function getDictionary(locale: string): Dictionary {
  const safeLocale = locales.includes(locale as Locale) ? (locale as Locale) : defaultLocale;
  return dictionaries[safeLocale];
}

export function isValidLocale(locale: string): locale is Locale {
  return locales.includes(locale as Locale);
}
