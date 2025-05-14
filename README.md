# ISO 50001 Newsletter App

Eine lokale Desktop-Anwendung zur Verwaltung und automatisierten Erstellung von individualisierten Newslettern über regulatorische Änderungen im Bereich ISO 50001.

## ✨ Ziel der Anwendung

Diese Anwendung ersetzt eine Excel-basierte Lösung zur Information von Kunden über relevante Änderungen in ISO 50001. Sie erlaubt es, kundenindividuelle Newsletter auf Knopfdruck zu erzeugen und zu versenden – basierend auf gepflegten Kundenzuordnungen zu Themen-Kategorien.

---

## 🏗️ Architektur & Tech-Stack

- **Sprache:** Python 3.11
- **GUI:** PySide6 (Qt für Python)
- **Templating:** Jinja2
- **Datenbank:** SQLite
- **E-Mail-Versand:** SMTP (konfigurierbar)
- **Deployment:** Lokale `.exe` möglich (z. B. via PyInstaller)

---

## 🔐 Login-System

- Benutzer melden sich mit Username & Passwort an
- Aktuell kein Rollenmodell (optional erweiterbar)

---

## 📊 Hauptfunktionen

### Kundenverwaltung
- Mehrere E-Mail-Adressen pro Kunde
- Verwaltung über GUI + Dialog
- Kunden können aktiviert/deaktiviert werden

### Kategorien & Zuordnung (Matrix)
Zwei Ansichten zur Pflege der Kunden-Kategorie-Matrix:

1. **Kunden-View:** Zeigt Kategorien für ausgewählten Kunden
2. **Kategorien-View:** Zeigt Kunden für ausgewählte Kategorie

Beide Ansichten mit:
- Checkboxen zur Zuordnung
- Live-Speicherung in DB
- Live-Suchfeld zur Filterung

### Newsletter
- HTML-Vorlage mit Jinja2-Platzhaltern
- Versand via SMTP
- Template kann frei angepasst werden
- Testversand-Funktion integriert

---

## 🗃️ Datenbankstruktur

| Tabelle                  | Inhalt |
|--------------------------|--------|
| Users                    | Benutzerlogin |
| Customers                | Kundenstammdaten |
| CustomerEmails           | Beliebig viele E-Mails pro Kunde |
| Categories               | Themenkategorien |
| RegulatoryChanges        | Einzelne regulatorische Änderungen |
| CustomerCategoryMapping  | Zuordnung Kunde ↔ Kategorie |
| NewsletterDispatch       | Versandhistorie |
| AuditLog                 | Benutzeraktionen (optional) |

---

## 🔧 Konfiguration: `config.ini`

```ini
[APP]
db_path = data/iso_newsletter_app.db
template_path = templates/newsletter_template.html
log_file = logs/app.log

[SMTP]
host = smtp.firma.local
port = 587
username = newsletter@firma.de
password = geheim
use_tls = yes

[NEWSLETTER]
from_name = ISO 50001 Bot
from_email = newsletter@firma.de
subject_template = ISO 50001 Updates – {{quarter}} for {{customer_name}}
```

---

## 📁 Projektstruktur

```bash
iso_newsletter_app/
├── main.py
├── config.ini
├── requirements.txt
├── core/
│   ├── db.py
│   ├── email_sender.py
│   └── models.py
├── ui/
│   ├── login.py
│   ├── main_window.py
│   ├── email_dialog.py
│   └── category_matrix.py
├── templates/
│   └── newsletter_template.html
├── data/
│   └── iso_newsletter_app.db
└── logs/
    └── app.log
```

---

## 🚀 Entwicklung & Ausblick

| Thema                  | Status | Empfehlung |
|------------------------|--------|------------|
| Passwort-Hashing       | ❌     | bcrypt verwenden |
| Benutzerrollen         | ❌     | "admin", "editor" denkbar |
| Versandplanung         | 🔜     | Newsletter an alle |
| Empfangs-Tracking      | 🔜     | Open/Click Tracking über externen Anbieter |
| PDF-Generierung        | 🔜     | Optional für Audits |
| Live-Vorschau          | 🔜     | Newsletter pro Kunde anzeigen |

---

## 💬 Lizenz

Internes Projekt / Closed Source – Nutzung und Weitergabe nach Absprache.
