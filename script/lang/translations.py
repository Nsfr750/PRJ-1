"""
Translations
Contains all text strings in all supported languages.
"""

TRANSLATIONS = {
    'en': {
        "app": {
            "title": "Project Browser",
            "loading": "Loading...",
            "error": "Error",
            "success": "Success",
            "warning": "Warning",
            "info": "Information",
            "confirm": "Confirm",
            "yes": "Yes",
            "no": "No",
            "cancel": "Cancel",
            "ok": "OK",
            "save": "Save",
            "open": "Open",
            "close": "Close",
            "ready": "Ready",
            "confirm_exit": "Confirm Exit",
            "confirm_exit_text": "Are you sure you want to exit?",
            "log_viewer_error": "Failed to open log viewer"
        },
        "dependencies": {
            "stats": "Total: {total} | Outdated: {outdated} | Vulnerabilities: {vuln}"
        },
        "menu": {
            "file": "File",
            "new": "New",
            "open": "Open",
            "save": "Save",
            "save_as": "Save As...",
            "exit": "Exit",
            "edit": "Edit",
            "undo": "Undo",
            "redo": "Redo",
            "cut": "Cut",
            "copy": "Copy",
            "paste": "Paste",
            "delete": "Delete",
            "select_all": "Select All",
            "view": "View",
            "zoom_in": "Zoom In",
            "zoom_out": "Zoom Out",
            "reset_zoom": "Reset Zoom",
            "help": "Help",
            "about": "About",
            "language": "Language",
            "english": "English",
            "italian": "Italiano",
            "theme": "Theme",
            "dark": "Dark",
            "light": "Light",
            "system": "System",
            "tools": "Tools",
            "project_browser": "Project Browser",
            "view_logs": "View Logs",
            "check_updates": "Check for Updates",
            "documentation": "Documentation (Wiki)",
            "sponsor": "Sponsor"
        },
        "log_viewer": {
            "title": "Log Viewer",
            "refresh": "&Refresh",
            "clear": "&Clear Log",
            "save_as": "&Save As...",
            "no_logs": "No log files found.",
            "select_file": "Select log file to view:",
            "clear_confirm": "Are you sure you want to clear the log?",
            "save_success": "Log saved successfully!",
            "save_error": "Error saving log!"
        },
        "about": {
            "title": "About",
            "description": "A comprehensive project management tool helps you discover, organize, and manage your development projects with ease.",
            "version": "Version: {version}",
            "author": " Nsfr750 - All rights reserved",
            "license": "License: GPLv3",
            "github": "GitHub Repository",
            "close": "Close"
        },
        "advanced_search": {
            "title": "Advanced Project Search",
            "tabs": {
                "basic": "Basic",
                "advanced": "Advanced Filters",
                "date": "Date Filters"
            },
            "buttons": {
                "search": "Search",
                "clear": "Clear"
            },
            "basic": {
                "name": "Project Name",
                "name_placeholder": "Enter project name (supports wildcards: *, ?)",
                "exact_match": "Exact match",
                "case_sensitive": "Case sensitive",
                "language": "Programming Language",
                "any_language": "Any Language",
                "category": "Category",
                "any_category": "Any Category",
                "tags": "Tags",
                "tags_placeholder": "Enter tags (comma-separated, supports AND/OR)",
                "match_all_tags": "Match all tags (AND)"
            },
            "advanced": {
                "file_types": "File Types",
                "file_types_placeholder": "Enter file extensions (comma-separated, e.g., .py,.js,.cpp)",
                "match_any_file_type": "Match any file type",
                "project_size": "Project Size",
                "min_size": "Min size (KB):",
                "max_size": "Max size (KB):",
                "project_properties": "Project Properties",
                "has_git_repo": "Has Git repository",
                "is_favorite": "Is favorite",
                "has_notes": "Has notes"
            },
            "date": {
                "last_modified": "Last Modified",
                "created_date": "Created Date",
                "from": "From:",
                "to": "To:",
                "quick_presets": "Quick Presets",
                "today": "Today",
                "this_week": "This Week",
                "this_month": "This Month",
                "this_year": "This Year"
            }
        },
        "help": {
            "title": "Help - Project Browser",
            "header_title": "Project Browser - Help",
            "search_label": "Search:",
            "search_placeholder": "Type to search help topics...",
            "buttons": {
                "back": "← Back",
                "forward": "Forward →",
                "home": "🏠 Home",
                "close": "Close"
            },
            "nav": {
                "documentation": "Documentation",
                "topics": "Topics",
                "external_links": "External Links",
                "github_wiki": "GitHub Wiki",
                "report_issue": "Report Issue",
                "discussions": "Discussions",
                "release_notes": "Release Notes"
            },
            "tabs": {
                "help": "Help",
                "examples": "Examples",
                "api": "API Reference",
                "faq": "FAQ"
            },
            "error": {
                "no_docs_dir": "Documentation directory not found"
            },
            "error_loading": "Could not load help documentation\n\nPlease visit the GitHub repository for documentation",
            "getting_started": "Getting Started",
            "welcome": "Welcome!"
        },
        "sponsor": {
            "window_title": "Support Development",
            "title": "Support",
            "message": "If you find this application useful, please consider supporting its development.\n\nYour support helps cover hosting costs and encourages further development.",
            "buttons": {
                "github_sponsors": "GitHub Sponsors",
                "discord": "Join Discord",
                "patreon": "Become a Patron",
                "paypal": "Donate with PayPal",
                "donate_paypal": "Donate with PayPal",
                "copy_monero": "Copy Monero Address",
                "copied": "Copied!"
            },
            "monero": {
                "label": "Monero:"
            },
            "qr_tooltip": "Scan to donate XMR",
            "ways_to_support": "Ways to Support:",
            "other_ways": {
                "title": "Other Ways to Help:",
                "star": "Star the project on",
                "report": "Report bugs and suggest features",
                "share": "Share with others who might find it useful",
                "patreon": "Join on"
            }
        },
        "log_viewer": {
            "title": "Log Viewer",
            "select_file": "Select Log File:",
            "refresh": "&Refresh",
            "filter_by_type": "Filter by Type:",
            "filter_by_level": "Filter by Level:",
            "search": "Search:",
            "search_placeholder": "Search in logs...",
            "clear": "&Clear Log",
            "delete": "&Delete Log",
            "export": "&Export Log",
            "close": "&Close",
            "error": "Error",
            "success": "Success",
            "confirm_clear": "Confirm Clear",
            "clear_confirm": "Are you sure you want to clear all log files? This cannot be undone.",
            "clear_success": "All log files have been cleared.",
            "confirm_delete": "Confirm Delete",
            "delete_confirm": "Are you sure you want to delete {filename}?",
            "delete_success": "The log file has been deleted.",
            "export_log": "Export Log"
        },
        "project_browser": {
            "title": "Project Browser",
            "maximize": "Maximize",
            "restore": "Restore",
            "ready_scan": "Ready - Click 'Start Scan' to begin scanning projects",
            "scan_directory": "Scan Directory",
            "current_directory": "Current Directory:",
            "browse": "Browse...",
            "search_filter": "Search & Filter",
            "search": "Search:",
            "search_placeholder": "Search projects...",
            "language": "Language:",
            "category": "Category:",
            "tags": "Tags:",
            "tags_placeholder": "Filter by tags (comma-separated)...",
            "favorites": "Favorites:",
            "all": "All",
            "favorites_only": "Favorites Only",
            "non_favorites_only": "Non-Favorites Only",
            "recent_projects": "Recent Projects",
            "start_scan": "▶ Start Scan",
            "stop_scan": "⏹ Stop Scan",
            "export": "📊 Export",
            "dashboard": "📈 Dashboard",
            "advanced_search": "🔍 Advanced Search",
            "select_all": "☑ Select All",
            "select_none": "☐ Select None",
            "open_selected": "📂 Open Selected",
            "toggle_favorite": "⭐ Toggle Favorite",
            "add_tags": "🏷️ Add Tags",
            "set_category": "📁 Set Category"
        }
    },
    'it': {
        "app": {
            "title": "Project Browser",
            "loading": "Caricamento...",
            "error": "Errore",
            "success": "Operazione completata",
            "warning": "Avviso",
            "info": "Informazione",
            "confirm": "Conferma",
            "yes": "Sì",
            "no": "No",
            "cancel": "Annulla",
            "ok": "OK",
            "save": "Salva",
            "open": "Apri",
            "close": "Chiudi",
            "ready": "Pronto",
            "confirm_exit": "Conferma Uscita",
            "confirm_exit_text": "Sei sicuro di voler uscire?",
            "log_viewer_error": "Impossibile aprire il visualizzatore di log"
        },
        "dependencies": {
            "stats": "Totale: {total} | Obsoleti: {outdated} | Vulnerabilità: {vuln}"
        },
        "menu": {
            "file": "File",
            "new": "Nuovo",
            "open": "Apri",
            "save": "Salva",
            "save_as": "Salva con nome...",
            "exit": "Esci",
            "edit": "Modifica",
            "undo": "Annulla",
            "redo": "Ripeti",
            "cut": "Taglia",
            "copy": "Copia",
            "paste": "Incolla",
            "delete": "Elimina",
            "select_all": "Seleziona tutto",
            "view": "Visualizza",
            "zoom_in": "Ingrandisci",
            "zoom_out": "Riduci",
            "reset_zoom": "Reimposta zoom",
            "help": "Aiuto",
            "about": "Informazioni",
            "language": "Lingua",
            "english": "Inglese",
            "italian": "Italiano",
            "theme": "Tema",
            "dark": "Scuro",
            "light": "Chiaro",
            "system": "Sistema",
            "tools": "Strumenti",
            "project_browser": "Browser Progetti",
            "view_logs": "Visualizza Log",
            "check_updates": "Controlla Aggiornamenti",
            "documentation": "Documentazione (Wiki)",
            "sponsor": "Sponsor"
        },
        "log_viewer": {
            "title": "Visualizzatore Log",
            "refresh": "&Aggiorna",
            "clear": "&Pulisci Log",
            "save_as": "&Salva con nome...",
            "no_logs": "Nessun file di log trovato.",
            "select_file": "Seleziona il file di log da visualizzare:",
            "clear_confirm": "Sei sicuro di voler cancellare il log?",
            "save_success": "Log salvato con successo!",
            "save_error": "Errore nel salvataggio del log!"
        },
        "about": {
            "title": "Informazioni",
            "description": "Uno strumento completo per la gestione dei progetti ti aiuta a individuare, organizzare e gestire con facilità i tuoi progetti di sviluppo.",
            "version": "Versione: {version}",
            "author": "© {year} Nsfr750 - Tutti i diritti riservati",
            "license": "Licenza: GPLv3",
            "github": "Repository GitHub",
            "close": "Chiudi"
        },
        "advanced_search": {
            "title": "Ricerca Avanzata Progetti",
            "tabs": {
                "basic": "Base",
                "advanced": "Filtri Avanzati",
                "date": "Filtri Data"
            },
            "buttons": {
                "search": "Cerca",
                "clear": "Cancella"
            },
            "basic": {
                "name": "Nome Progetto",
                "name_placeholder": "Inserisci nome progetto (supporta wildcard: *, ?)",
                "exact_match": "Corrispondenza esatta",
                "case_sensitive": "Sensibile a maiuscole",
                "language": "Linguaggio Programmazione",
                "any_language": "Qualsiasi Linguaggio",
                "category": "Categoria",
                "any_category": "Qualsiasi Categoria",
                "tags": "Tag",
                "tags_placeholder": "Inserisci tag (separati da virgola, supporta AND/OR)",
                "match_all_tags": "Corrispondi tutti i tag (AND)"
            },
            "advanced": {
                "file_types": "Tipi File",
                "file_types_placeholder": "Inserisci estensioni file (separate da virgola, es. .py,.js,.cpp)",
                "match_any_file_type": "Corrispondi qualsiasi tipo file",
                "project_size": "Dimensione Progetto",
                "min_size": "Dimensione min (KB):",
                "max_size": "Dimensione max (KB):",
                "project_properties": "Proprietà Progetto",
                "has_git_repo": "Ha repository Git",
                "is_favorite": "È preferito",
                "has_notes": "Ha note"
            },
            "date": {
                "last_modified": "Ultima Modifica",
                "created_date": "Data Creazione",
                "from": "Da:",
                "to": "A:",
                "quick_presets": "Preimpostazioni Rapide",
                "today": "Oggi",
                "this_week": "Questa Settimana",
                "this_month": "Questo Mese",
                "this_year": "Quest'Anno"
            }
        },
        "help": {
            "title": "Aiuto - Project Browser",
            "header_title": "Project Browser - Aiuto",
            "search_label": "Cerca:",
            "search_placeholder": "Digita per cercare argomenti di aiuto...",
            "buttons": {
                "back": "← Indietro",
                "forward": "Avanti →",
                "home": "🏠 Home",
                "close": "Chiudi"
            },
            "nav": {
                "documentation": "Documentazione",
                "topics": "Argomenti",
                "external_links": "Link Esterni",
                "github_wiki": "Wiki GitHub",
                "report_issue": "Segnala Problema",
                "discussions": "Discussioni",
                "release_notes": "Note di Rilascio"
            },
            "tabs": {
                "help": "Aiuto",
                "examples": "Esempi",
                "api": "Riferimento API",
                "faq": "FAQ"
            },
            "error": {
                "no_docs_dir": "Directory documentazione non trovata"
            },
            "error_loading": "Impossibile caricare la documentazione\n\nVisita il repository GitHub per la documentazione",
            "getting_started": "Per Iniziare",
            "welcome": "Benvenuto!"
        },
        "sponsor": {
            "window_title": "Supporta Sviluppo",
            "title": "Supporta",
            "message": "Se trovi questa applicazione utile, considera di supportarne lo sviluppo.\n\nIl tuo supporto aiuta a coprire i costi di hosting e incoraggia ulteriore sviluppo.",
            "buttons": {
                "github_sponsors": "GitHub Sponsors",
                "discord": "Unisciti a Discord",
                "patreon": "Diventa un Patron",
                "paypal": "Dona con PayPal",
                "donate_paypal": "Dona con PayPal",
                "copy_monero": "Copia Indirizzo Monero",
                "copied": "Copiato!"
            },
            "monero": {
                "label": "Monero:"
            },
            "qr_tooltip": "Scansiona per donare XMR",
            "ways_to_support": "Modi per Supportare:",
            "other_ways": {
                "title": "Altri Modi per Aiutare:",
                "star": "Dai una stella al progetto su",
                "report": "Segnala bug e suggerisci funzionalità",
                "share": "Condividi con altri che potrebbero trovarlo utile",
                "patreon": "Unisciti su"
            }
        },
        "log_viewer": {
            "title": "Visualizzatore Log",
            "select_file": "Seleziona File Log:",
            "refresh": "&Aggiorna",
            "filter_by_type": "Filtra per Tipo:",
            "filter_by_level": "Filtra per Livello:",
            "search": "Cerca:",
            "search_placeholder": "Cerca nei log...",
            "clear": "&Cancella Log",
            "delete": "&Elimina Log",
            "export": "&Esporta Log",
            "close": "&Chiudi",
            "error": "Errore",
            "success": "Successo",
            "confirm_clear": "Conferma Cancellazione",
            "clear_confirm": "Sei sicuro di voler cancellare tutti i file di log? Questa operazione non può essere annullata.",
            "clear_success": "Tutti i file di log sono stati cancellati.",
            "confirm_delete": "Conferma Eliminazione",
            "delete_confirm": "Sei sicuro di voler eliminare {filename}?",
            "delete_success": "Il file di log è stato eliminato.",
            "export_log": "Esporta Log"
        },
        "project_browser": {
            "title": "Browser Progetti",
            "maximize": "Massimizza",
            "restore": "Ripristina",
            "ready_scan": "Pronto - Fai clic su 'Avvia Scansione' per iniziare la scansione dei progetti",
            "scan_directory": "Scansione Directory",
            "current_directory": "Directory Corrente:",
            "browse": "Sfoglia...",
            "search_filter": "Cerca & Filtra",
            "search": "Cerca:",
            "search_placeholder": "Cerca progetti...",
            "language": "Linguaggio:",
            "category": "Categoria:",
            "tags": "Tag:",
            "tags_placeholder": "Filtra per tag (separati da virgola)...",
            "favorites": "Preferiti:",
            "all": "Tutti",
            "favorites_only": "Solo Preferiti",
            "non_favorites_only": "Solo Non Preferiti",
            "recent_projects": "Progetti Recenti",
            "start_scan": "▶ Avvia Scansione",
            "stop_scan": "⏹ Ferma Scansione",
            "export": "📊 Esporta",
            "dashboard": "📈 Dashboard",
            "advanced_search": "🔍 Ricerca Avanzata",
            "select_all": "☑ Seleziona Tutto",
            "select_none": "☐ Deseleziona Tutto",
            "open_selected": "📂 Apri Selezionati",
            "toggle_favorite": "⭐ Toggle Preferito",
            "add_tags": "🏷️ Aggiungi Tag",
            "set_category": "📁 Imposta Categoria"
        }
    }
}

def get_translation(lang_code, key, default=None):
    """
    Get a translation for the given language code and key.
    
    Args:
        lang_code: Language code (e.g., 'en', 'it')
        key: Dot-separated key path (e.g., 'app.title')
        default: Default value to return if key not found
    
    Returns:
        The translated string or the default value if not found
    """
    if lang_code not in TRANSLATIONS:
        lang_code = 'en'  # Fallback to English
    
    parts = key.split('.')
    result = TRANSLATIONS[lang_code]
    
    try:
        for part in parts:
            result = result[part]
        return result
    except (KeyError, TypeError):
        return default if default is not None else key
