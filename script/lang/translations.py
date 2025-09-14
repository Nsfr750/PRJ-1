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
            "close": "Close"
        },
        "menu": {
            "file": "File",
            "new": "New",
            "open": "Open",
            "save": "Save",
            "save_as": "Save As...",
            "exit": "Exit",
            "edit": "Edit",
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
            "project_browser": "Project Browser"
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
            "description": "A simple ProjectBrowser",
            "version": "Version: {version}",
            "author": "© {year} Nsfr750 - All rights reserved",
            "license": "License: GPLv3",
            "github": "GitHub Repository",
            "close": "Close"
        },
        "help": {
            "title": "Help",
            "error_loading": "Could not load help documentation\n\nPlease visit the GitHub repository for documentation",
            "getting_started": "Getting Started",
            "welcome": "Welcome."
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
            "close": "Chiudi"
        },
        "menu": {
            "file": "File",
            "new": "Nuovo",
            "open": "Apri",
            "save": "Salva",
            "save_as": "Salva con nome...",
            "exit": "Esci",
            "edit": "Modifica",
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
            "project_browser": "Browser Progetti"
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
            "description": "Un semplice Browser per i Progetti",
            "version": "Versione: {version}",
            "author": "© {year} Nsfr750 - Tutti i diritti riservati",
            "license": "Licenza: GPLv3",
            "github": "Repository GitHub",
            "close": "Chiudi"
        },
        "help": {
            "title": "Aiuto",
            "error_loading": "Impossibile caricare la documentazione\n\nVisita il repository GitHub per la documentazione",
            "getting_started": "Per Iniziare",
            "welcome": "Benvenuto!"
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
