# Guest-facing strings and feedback tags. Tag keys are stored in the DB, so never rename them.

TAGS = {
    "low": ["food_quality", "long_wait", "slow_service", "unfriendly_staff", "food_cold",
            "wrong_order", "cleanliness", "too_loud", "price_value"],
    "mid": ["tastier_food", "faster_service", "attentive_staff", "better_value", "warmer_food",
            "quieter_room", "cleaner_tables"],
    "high": ["delicious_food", "friendly_service", "quick_service", "great_atmosphere", "good_value",
             "great_drinks", "generous_portions", "spotless"],
}

def band(rating):
    return "low" if rating <= 2 else "mid" if rating == 3 else "high"

I18N = {
    "en": {
        "page_title": "Share your experience",
        "table": "Table", "today": "Today", "tonight": "Tonight",
        "q_today": "How was your visit today?", "q_tonight": "How was your visit tonight?",
        "sub": "Good or bad — an honest answer helps the kitchen and floor team most.",
        "tap": "Tap a star",
        "stars": ["Terrible", "Bad", "Okay", "Good", "Excellent"],
        "footer": "Anonymous · about 20 seconds · no login",
        "step": "Step 2 of 2 · optional", "back": "Back", "close": "Close",
        "h_low": "What went wrong?", "h_mid": "What would have made it a 5?", "h_high": "What stood out?",
        "txt_low": "What happened? (optional)", "ph_low": "e.g. Mains took 45 minutes and arrived lukewarm.",
        "txt_mid": "One thing we could do better? (optional)", "ph_mid": "e.g. Great food, but the room was very loud",
        "txt_high": "What should we keep doing? (optional)", "ph_high": "e.g. The schnitzel was perfect, ask for Anna",
        "contact_title": "Have the manager contact me",
        "contact_sub": "So we can make it right. Only used for this, then deleted.",
        "contact_name": "Your name (optional)", "contact_info": "Email or phone",
        "team_title": "Pass a thank-you to tonight’s team",
        "team_sub": "Shown to the kitchen and floor staff at the next briefing.",
        "send_only": "Send rating only", "send": "Send feedback",
        "anon": "Read by the owner. Staff never see who wrote it.",
        "rate_first": "Please choose a rating from 1 to 5.",
        "ty_title": "Thank you",
        "ty_high": "Glad you had a good night. Your feedback goes straight to the owner.",
        "ty_mid": "Thanks for being honest. Your feedback goes straight to the owner.",
        "ty_low": "Sorry it wasn’t right. The owner reads every message personally.",
        "ty_contact": "The manager will get in touch with you soon.",
        "share_title": "Share it publicly too?",
        "share_sub": "Other guests rely on honest reviews — good and bad. We’ll copy your text so you don’t have to retype it.",
        "share_btn": "Copy text & open Google", "share_btn_notext": "Open Google reviews",
        "done": "No thanks, I’m done", "done_msg": "All done — you can close this page.",
        "copied": "Text copied",
        "tags": {
            "food_quality": "Food quality", "long_wait": "Long wait", "slow_service": "Slow service",
            "unfriendly_staff": "Unfriendly staff", "food_cold": "Food was cold", "wrong_order": "Wrong order",
            "cleanliness": "Cleanliness", "too_loud": "Too loud", "price_value": "Price vs. value",
            "tastier_food": "Tastier food", "faster_service": "Faster service",
            "attentive_staff": "More attentive staff", "better_value": "Better value",
            "warmer_food": "Warmer food", "quieter_room": "Quieter room", "cleaner_tables": "Cleaner tables",
            "delicious_food": "Delicious food", "friendly_service": "Friendly service",
            "quick_service": "Quick service", "great_atmosphere": "Great atmosphere", "good_value": "Good value",
            "great_drinks": "Great drinks", "generous_portions": "Generous portions", "spotless": "Spotless",
        },
    },
    "de": {
        "page_title": "Teilen Sie Ihre Erfahrung",
        "table": "Tisch", "today": "Heute", "tonight": "Heute Abend",
        "q_today": "Wie war Ihr Besuch heute?", "q_tonight": "Wie war Ihr Besuch heute Abend?",
        "sub": "Ob gut oder schlecht – eine ehrliche Antwort hilft Küche und Service am meisten.",
        "tap": "Tippen Sie auf einen Stern",
        "stars": ["Sehr schlecht", "Schlecht", "Okay", "Gut", "Ausgezeichnet"],
        "footer": "Anonym · ca. 20 Sekunden · ohne Anmeldung",
        "step": "Schritt 2 von 2 · optional", "back": "Zurück", "close": "Schließen",
        "h_low": "Was ist schiefgelaufen?", "h_mid": "Was hätte daraus eine 5 gemacht?",
        "h_high": "Was hat Ihnen besonders gefallen?",
        "txt_low": "Was ist passiert? (optional)", "ph_low": "z. B. Die Hauptspeise kam nach 45 Minuten und war lauwarm.",
        "txt_mid": "Was könnten wir besser machen? (optional)", "ph_mid": "z. B. Tolles Essen, aber es war sehr laut",
        "txt_high": "Was sollen wir beibehalten? (optional)", "ph_high": "z. B. Das Schnitzel war perfekt, Anna war großartig",
        "contact_title": "Der Manager soll mich kontaktieren",
        "contact_sub": "Damit wir es wiedergutmachen können. Nur dafür verwendet, danach gelöscht.",
        "contact_name": "Ihr Name (optional)", "contact_info": "E-Mail oder Telefon",
        "team_title": "Ein Dankeschön an das heutige Team",
        "team_sub": "Wird Küche und Service bei der nächsten Besprechung gezeigt.",
        "send_only": "Nur Bewertung senden", "send": "Feedback senden",
        "anon": "Liest nur der Inhaber. Das Personal sieht nie, wer es geschrieben hat.",
        "rate_first": "Bitte wählen Sie eine Bewertung von 1 bis 5.",
        "ty_title": "Danke",
        "ty_high": "Schön, dass es Ihnen gefallen hat. Ihr Feedback geht direkt an den Inhaber.",
        "ty_mid": "Danke für Ihre Ehrlichkeit. Ihr Feedback geht direkt an den Inhaber.",
        "ty_low": "Es tut uns leid, dass es nicht gepasst hat. Der Inhaber liest jede Nachricht persönlich.",
        "ty_contact": "Der Manager meldet sich in Kürze bei Ihnen.",
        "share_title": "Auch öffentlich teilen?",
        "share_sub": "Andere Gäste verlassen sich auf ehrliche Bewertungen – gute wie schlechte. Wir kopieren Ihren Text, damit Sie ihn nicht neu tippen müssen.",
        "share_btn": "Text kopieren & Google öffnen", "share_btn_notext": "Google-Bewertungen öffnen",
        "done": "Nein danke, fertig", "done_msg": "Fertig – Sie können diese Seite jetzt schließen.",
        "copied": "Text kopiert",
        "tags": {
            "food_quality": "Qualität des Essens", "long_wait": "Lange Wartezeit", "slow_service": "Langsamer Service",
            "unfriendly_staff": "Unfreundliches Personal", "food_cold": "Essen war kalt",
            "wrong_order": "Falsche Bestellung", "cleanliness": "Sauberkeit", "too_loud": "Zu laut",
            "price_value": "Preis-Leistung", "tastier_food": "Besseres Essen", "faster_service": "Schnellerer Service",
            "attentive_staff": "Aufmerksameres Personal", "better_value": "Bessere Preis-Leistung",
            "warmer_food": "Wärmeres Essen", "quieter_room": "Ruhigerer Raum", "cleaner_tables": "Sauberere Tische",
            "delicious_food": "Köstliches Essen", "friendly_service": "Freundlicher Service",
            "quick_service": "Schneller Service", "great_atmosphere": "Tolle Atmosphäre",
            "good_value": "Gute Preis-Leistung", "great_drinks": "Tolle Getränke",
            "generous_portions": "Großzügige Portionen", "spotless": "Blitzsauber",
        },
    },
}

def pick_lang(request):
    lang = request.query_params.get("lang")
    if lang in I18N:
        request.session["lang"] = lang
        return lang
    if request.session.get("lang") in I18N:
        return request.session["lang"]
    accept = request.headers.get("accept-language", "").lower()
    return "de" if accept.startswith("de") else "en"
