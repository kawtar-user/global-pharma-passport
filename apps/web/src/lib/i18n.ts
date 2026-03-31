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
    signup: string;
    login: string;
    benefits: [string, string, string];
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
  workspace: {
    summary: string;
    summaryTitle: string;
    summarySubtitle: string;
    treatmentsTitle: string;
    treatmentsSubtitle: string;
    equivalentsTitle: string;
    equivalentsSubtitle: string;
    addTreatmentShortcut: string;
    compareEquivalentShortcut: string;
    passportShortcut: string;
    summaryAddTreatmentBody: string;
    summaryCompareBody: string;
    summaryPassportBody: string;
    passportCardTitle: string;
    activeTreatmentsTitle: string;
    addMedicationHelp: string;
    corridorLabel: string;
    equivalentsEmptyTitle: string;
    equivalentsEmptyBody: string;
    equivalentsResultsTitle: string;
    sourceTreatmentsTitle: string;
    alertsTitle: string;
  };
};

export const dictionaries: Record<Locale, Dictionary> = {
  fr: {
    marketing: {
      eyebrow: "Global Pharma Passport",
      title: "Retrouvez et partagez votre traitement entre le Maroc et la France.",
      subtitle:
        "Global Pharma Passport vous aide a enregistrer vos medicaments, retrouver les equivalents dans l'autre pays et generer un passeport patient simple avant de voyager.",
      signup: "Creer un compte",
      login: "Se connecter",
      benefits: [
        "Retrouvez vos medicaments et leurs equivalents pays.",
        "Comprenez les interactions majeures en langage simple.",
        "Partagez un passeport patient clair en quelques secondes.",
      ],
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
    workspace: {
      summary: "Resume",
      summaryTitle: "Resume patient",
      summarySubtitle: "Ajoute, compare et partage sans te perdre dans un grand dashboard.",
      treatmentsTitle: "Traitements",
      treatmentsSubtitle: "Ajoute un traitement reel, verifie-le et retrouve-le facilement.",
      equivalentsTitle: "Equivalents internationaux",
      equivalentsSubtitle: "Compare tes traitements sur le corridor Maroc-France a partir des donnees reelles du catalogue.",
      addTreatmentShortcut: "Ajouter un traitement",
      compareEquivalentShortcut: "Comparer un equivalent",
      passportShortcut: "Ouvrir le passeport",
      summaryAddTreatmentBody: "Ajoute un traitement clair et relie au catalogue pour activer alertes, equivalents et passeport.",
      summaryCompareBody: "Vois immediatement si un equivalent existe dans l'autre pays et pourquoi il est propose.",
      summaryPassportBody: "Genere un passeport lisible, partageable et utile en situation reelle.",
      passportCardTitle: "Passeport patient",
      activeTreatmentsTitle: "Traitements actifs",
      addMedicationHelp: "Recherche d'abord un medicament du catalogue, puis selectionne la bonne presentation avant de l'ajouter au passeport.",
      corridorLabel: "Corridor actif",
      equivalentsEmptyTitle: "Aucun traitement compare pour le moment",
      equivalentsEmptyBody: "Ajoute d'abord un traitement lie au catalogue pour calculer les equivalences entre le Maroc et la France.",
      equivalentsResultsTitle: "Equivalents trouves",
      sourceTreatmentsTitle: "Traitements sources",
      alertsTitle: "Alertes majeures",
    },
  },
  en: {
    marketing: {
      eyebrow: "Global Pharma Passport",
      title: "Understand and share your treatment between Morocco and France.",
      subtitle:
        "Global Pharma Passport helps you save your medications, find equivalents across countries, and generate a simple patient passport before you travel.",
      signup: "Create account",
      login: "Log in",
      benefits: [
        "Find your medications and country equivalents quickly.",
        "Review major interactions in simple language.",
        "Share a clear patient passport in seconds.",
      ],
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
    workspace: {
      summary: "Summary",
      summaryTitle: "Patient summary",
      summarySubtitle: "Add, compare and share without getting lost in a large dashboard.",
      treatmentsTitle: "Treatments",
      treatmentsSubtitle: "Add a real treatment, verify it and find it quickly.",
      equivalentsTitle: "International equivalents",
      equivalentsSubtitle: "Compare your treatments on the Morocco-France corridor using real catalog data.",
      addTreatmentShortcut: "Add a treatment",
      compareEquivalentShortcut: "Compare an equivalent",
      passportShortcut: "Open passport",
      summaryAddTreatmentBody: "Add a catalog-linked treatment to activate alerts, equivalents and the passport.",
      summaryCompareBody: "See immediately whether an equivalent exists in the other country and why it is suggested.",
      summaryPassportBody: "Generate a readable, shareable passport that is useful in real situations.",
      passportCardTitle: "Patient passport",
      activeTreatmentsTitle: "Active treatments",
      addMedicationHelp: "Search the catalog first, then select the right presentation before adding it to the passport.",
      corridorLabel: "Active corridor",
      equivalentsEmptyTitle: "No treatment ready for comparison yet",
      equivalentsEmptyBody: "Add a catalog-linked treatment first to calculate equivalents between Morocco and France.",
      equivalentsResultsTitle: "Found equivalents",
      sourceTreatmentsTitle: "Source treatments",
      alertsTitle: "Major alerts",
    },
  },
  ar: {
    marketing: {
      eyebrow: "Global Pharma Passport",
      title: "افهم علاجك وشاركه بين المغرب وفرنسا.",
      subtitle:
        "يساعدك Global Pharma Passport على حفظ ادويتك، العثور على البدائل بين البلدين، وانشاء جواز مريض بسيط قبل السفر.",
      signup: "انشاء حساب",
      login: "تسجيل الدخول",
      benefits: [
        "اعثر بسرعة على دوائك وبدائله حسب الدولة.",
        "افهم التداخلات الدوائية المهمة بلغة بسيطة.",
        "شارك جواز مريض واضحا خلال ثوان.",
      ],
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
    workspace: {
      summary: "الملخص",
      summaryTitle: "ملخص المريض",
      summarySubtitle: "اضف وقارن وشارك دون الضياع داخل لوحة كبيرة ومعقدة.",
      treatmentsTitle: "العلاجات",
      treatmentsSubtitle: "اضف علاجا حقيقيا وتحقق منه واعثر عليه بسرعة.",
      equivalentsTitle: "البدائل الدولية",
      equivalentsSubtitle: "قارن علاجاتك على ممر المغرب-فرنسا بالاعتماد على بيانات الدليل الفعلية.",
      addTreatmentShortcut: "اضافة علاج",
      compareEquivalentShortcut: "مقارنة بديل",
      passportShortcut: "فتح الجواز",
      summaryAddTreatmentBody: "اضف علاجا مرتبطا بالدليل لتفعيل التنبيهات والبدائل والجواز الطبي.",
      summaryCompareBody: "اعرف فورا هل يوجد بديل في البلد الآخر ولماذا تم اقتراحه.",
      summaryPassportBody: "انشئ جوازا واضحا وقابلا للمشاركة ومفيدا في الاستخدام الحقيقي.",
      passportCardTitle: "جواز المريض",
      activeTreatmentsTitle: "العلاجات النشطة",
      addMedicationHelp: "ابحث أولا في دليل الادوية ثم اختر التركيبة الصحيحة قبل اضافتها الى الجواز.",
      corridorLabel: "الممر النشط",
      equivalentsEmptyTitle: "لا يوجد علاج جاهز للمقارنة بعد",
      equivalentsEmptyBody: "اضف اولا علاجا مرتبطا بالدليل لحساب البدائل بين المغرب وفرنسا.",
      equivalentsResultsTitle: "البدائل المتاحة",
      sourceTreatmentsTitle: "العلاجات المصدر",
      alertsTitle: "التنبيهات المهمة",
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
