import re
import os
import time
import sqlite3
from datetime import datetime, date
from io import BytesIO

import pandas as pd
import streamlit as st
from fpdf import FPDF

from audio_utils import transcribe_with_whisper, save_audio_file
from storage_utils import upload_file_to_r2
from summarizer import extractive_summary
from auth import init_users, authenticate, list_users, add_user, delete_user, set_password

st.set_page_config(
    page_title="Medical Consultation Summary",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Translations ───────────────────────────────────────────────────────────────
T = {
    "de": {
        "app_title": "Gesprächsdokumentation",
        "login_title": "Anmelden",
        "username": "Benutzername",
        "password": "Passwort",
        "login_btn": "Anmelden",
        "login_error": "Ungültige Anmeldedaten",
        "logout": "Abmelden",
        "logged_as": "Angemeldet als",
        "tab_consult": "Patientengespräch",
        "tab_users": "Benutzerverwaltung",
        "patient_section": "Patientendaten",
        "name_hint": "Name eingeben — Vorschläge erscheinen automatisch",
        "name_ph": "Vor- und Nachname",
        "suggestions": "Vorschläge",
        "dob": "Geburtsdatum",
        "gender": "Geschlecht",
        "height": "Grösse (cm)",
        "weight": "Gewicht (kg)",
        "therapy_start": "Therapiebeginn",
        "duration": "Dauer (Monate)",
        "allergies": "Bekannte Allergie?",
        "diagnoses": "Diagnosen",
        "diagnoses_ph": "Relevante Diagnosen...",
        "followup": "Kontrolltermine",
        "fw_4": "4 Wochen",
        "fw_12": "12 Wochen",
        "comment": "Kommentar",
        "save_patient": "Patientendaten speichern",
        "saved_ok": "Patientendaten gespeichert!",
        "name_required": "Bitte Patientennamen eingeben!",
        "recordings_section": "Gesprächsaufnahmen",
        "rec_label": "Aufnahme starten",
        "processing": "Verarbeite Aufnahme...",
        "summary_section": "Zusammenfassung",
        "transcript_section": "Transkript",
        "show_transcript": "Vollständiges Transkript anzeigen",
        "audio_section": "Audioaufnahme",
        "dl_pdf": "PDF Herunterladen",
        "save_pdf": "PDF speichern",
        "add_another": "Weiteres Gespräch aufnehmen",
        "prev_convs": "Frühere Gespräche",
        "no_convs": "Noch keine Gespräche gespeichert.",
        "conv_from": "Gespräch vom",
        "mic_hint": "Klicken Sie auf das Mikrofon, um die Aufnahme zu starten",
        "users_section": "Benutzerverwaltung",
        "add_user_header": "Neuen Benutzer anlegen",
        "is_admin": "Administrator",
        "add_btn": "Hinzufügen",
        "user_added": "Benutzer hinzugefügt!",
        "user_exists": "Benutzername bereits vergeben.",
        "existing_users": "Vorhandene Benutzer",
        "admin_only": "Nur Administratoren haben Zugang zu diesem Bereich.",
        "saved_at": "Gespeichert",
        "gender_m": "M",
        "gender_f": "W",
        "lang_label": "Sprache",
        "pw_change": "Passwort ändern",
        "pw_new": "Neues Passwort",
        "pw_save": "Speichern",
        "pw_cancel": "Abbrechen",
        "pw_saved": "Passwort gespeichert",
        "toggle_admin": "Admin",
    },
    "en": {
        "app_title": "Consultation Documentation",
        "login_title": "Sign In",
        "username": "Username",
        "password": "Password",
        "login_btn": "Sign In",
        "login_error": "Invalid credentials",
        "logout": "Logout",
        "logged_as": "Signed in as",
        "tab_consult": "Patient Consultation",
        "tab_users": "User Management",
        "patient_section": "Patient Data",
        "name_hint": "Enter name — suggestions appear automatically",
        "name_ph": "First and last name",
        "suggestions": "Suggestions",
        "dob": "Date of Birth",
        "gender": "Gender",
        "height": "Height (cm)",
        "weight": "Weight (kg)",
        "therapy_start": "Therapy Start",
        "duration": "Duration (Months)",
        "allergies": "Known Allergies?",
        "diagnoses": "Diagnoses",
        "diagnoses_ph": "Relevant diagnoses...",
        "followup": "Follow-up Appointments",
        "fw_4": "4 Weeks",
        "fw_12": "12 Weeks",
        "comment": "Comment",
        "save_patient": "Save Patient Data",
        "saved_ok": "Patient data saved!",
        "name_required": "Please enter a patient name!",
        "recordings_section": "Conversation Recordings",
        "rec_label": "Start Recording",
        "processing": "Processing recording...",
        "summary_section": "Summary",
        "transcript_section": "Transcript",
        "show_transcript": "Show full transcript",
        "audio_section": "Audio Recording",
        "dl_pdf": "Download PDF",
        "save_pdf": "Save PDF",
        "add_another": "Record Another Conversation",
        "prev_convs": "Previous Conversations",
        "no_convs": "No conversations saved yet.",
        "conv_from": "Conversation from",
        "mic_hint": "Click the microphone to start recording",
        "users_section": "User Management",
        "add_user_header": "Add New User",
        "is_admin": "Administrator",
        "add_btn": "Add",
        "user_added": "User added!",
        "user_exists": "Username already taken.",
        "existing_users": "Existing Users",
        "admin_only": "Only administrators have access to this area.",
        "saved_at": "Saved",
        "gender_m": "M",
        "gender_f": "F",
        "lang_label": "Language",
        "pw_change": "Change Password",
        "pw_new": "New Password",
        "pw_save": "Save",
        "pw_cancel": "Cancel",
        "pw_saved": "Password saved",
        "toggle_admin": "Admin",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "de")
    return T.get(lang, T["de"]).get(key, key)


# ── Database ───────────────────────────────────────────────────────────────────
DB_PATH = "app.db"


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_database():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT UNIQUE,
            geburtsdatum DATE,
            geschlecht TEXT,
            groesse INTEGER,
            gewicht INTEGER,
            therapiebeginn DATE,
            dauer INTEGER,
            allergie TEXT,
            diagnosen TEXT,
            kontrolltermin_4 BOOLEAN,
            kontrolltermin_12 BOOLEAN,
            kontrolltermin_kommentar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            summary TEXT,
            transcript TEXT,
            audio_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()
    conn2 = get_conn()
    init_users(conn2)
    conn2.close()


init_database()


def fetch_patient_names(conn):
    try:
        return pd.read_sql("SELECT patient_name FROM patients ORDER BY patient_name", conn)[
            "patient_name"
        ].tolist()
    except Exception:
        return []


def load_patient_data(conn, patient_name: str) -> dict:
    try:
        df = pd.read_sql(
            "SELECT * FROM patients WHERE patient_name=?", conn, params=(patient_name,)
        )
        return df.iloc[0].to_dict() if not df.empty else {}
    except Exception:
        return {}


def load_conversations(conn, patient_id: int) -> pd.DataFrame:
    return pd.read_sql(
        "SELECT id, summary, transcript, audio_path, created_at FROM conversations "
        "WHERE patient_id=? ORDER BY created_at DESC",
        conn,
        params=(patient_id,),
    )


def _logo_html(width: int = 160) -> str:
    for _fname, _mime in [("clinic_logo.svg", "image/svg+xml"), ("clinic_logo.png", "image/png")]:
        if os.path.exists(_fname):
            import base64 as _b64
            with open(_fname, "rb") as _f:
                _data = _b64.b64encode(_f.read()).decode()
            return (
                f'<a href="https://revitaclinic.de" target="_blank" rel="noopener">'
                f'<img src="data:{_mime};base64,{_data}" style="max-width:{width}px;cursor:pointer;">'
                f'</a>'
            )
    return ""


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ").strip()


_PDF_CHAR_MAP = {
    "—": "-", "–": "-",          # em dash, en dash
    "‘": "'", "’": "'",          # curly single quotes
    "“": '"', "”": '"',          # curly double quotes
    "…": "...",                        # ellipsis
    "•": "-", "·": "-",          # bullet, middle dot
    "′": "'", "″": '"',          # prime, double prime
    "×": "x", "÷": "/",         # multiply, divide
    "’": "'",
}


def _sanitize_pdf(text: str) -> str:
    """Replace characters outside Latin-1 so Helvetica can render them."""
    for char, rep in _PDF_CHAR_MAP.items():
        text = text.replace(char, rep)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def make_pdf(patient_name: str, summary: str, transcript: str, lang: str) -> bytes:
    pdf = FPDF()
    pdf.set_margins(18, 18, 18)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    title = _sanitize_pdf(T[lang]["app_title"])
    pdf.set_font("Helvetica", "B", 13)
    pdf.multi_cell(0, 8, title, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, _sanitize_pdf(f"Patient: {patient_name}"))
    pdf.multi_cell(0, 6, datetime.now().strftime("%d.%m.%Y  %H:%M"))
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 11)
    pdf.multi_cell(0, 7, _sanitize_pdf(T[lang]["summary_section"]))
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, _sanitize_pdf(strip_html(summary)) or "-")
    pdf.ln(5)

    if transcript:
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, _sanitize_pdf(T[lang]["transcript_section"]))
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, _sanitize_pdf(strip_html(transcript)))

    return bytes(pdf.output())


# ── CSS ────────────────────────────────────────────────────────────────────────
PRIMARY = "rgb(38, 96, 65)"
st.markdown(
    f"""
<style>
/* Buttons */
.stButton > button {{
    background-color: {PRIMARY} !important;
    color: white !important;
    border: 1px solid rgb(30,76,52) !important;
    border-radius: 4px !important;
}}
.stButton > button:hover {{
    background-color: rgb(30,76,52) !important;
    color: white !important;
}}
.stButton > button[kind="secondary"] {{
    background-color: #f0f2f6 !important;
    color: {PRIMARY} !important;
    border: 1px solid {PRIMARY} !important;
}}
/* Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 0 !important; width: 100% !important; }}
.stTabs [data-baseweb="tab"] {{
    flex: 1 !important; height: 46px; background-color: #f0f2f6;
    border-radius: 4px 4px 0 0; color: {PRIMARY};
    text-align: center !important; justify-content: center !important;
}}
.stTabs [aria-selected="true"] {{ background-color: {PRIMARY} !important; color: white !important; }}
/* Section headers */
.sec-header {{
    background-color: {PRIMARY}; color: white;
    padding: 0.5rem 1rem; border-radius: 4px;
    margin: 1rem 0 0.75rem 0; font-weight: 600;
}}
/* Focus rings */
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {PRIMARY} !important;
    box-shadow: 0 0 0 0.2rem rgba(38,96,65,0.2) !important;
}}
hr {{ margin: 6px 0 !important; }}
/* Conversation cards */
.conv-card {{
    border: 1px solid #e0e0e0; border-radius: 6px;
    padding: 0.75rem 1rem; margin: 0.5rem 0;
    background: #fafafa;
}}
</style>
""",
    unsafe_allow_html=True,
)

# ── Session state defaults ─────────────────────────────────────────────────────
_defaults = {
    "lang": "de",
    "authenticated": False,
    "username": "",
    "is_admin": False,
    "patient_data": {},
    "last_loaded_patient": None,
    "current_patient_input": "",
    "clicked_suggestion": None,
    "display_patient_name": "",
    "just_loaded_patient": False,
    "recorded_data": None,
    "last_processed_audio": None,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Language selector (always visible, before auth) ────────────────────────────
_, _lc2 = st.columns([8, 1])
with _lc2:
    _lang_choice = st.radio(
        "Language",
        ["DE", "EN"],
        index=0 if st.session_state.lang == "de" else 1,
        horizontal=True,
        label_visibility="collapsed",
        key="_lang_sel",
    )
    _new_lang = "de" if _lang_choice == "DE" else "en"
    if _new_lang != st.session_state.lang:
        st.session_state.lang = _new_lang
        st.rerun()

# ── Login screen ───────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    st.markdown("<br>", unsafe_allow_html=True)
    _, _mc, _ = st.columns([1, 1.1, 1])
    with _mc:
        _login_logo = _logo_html(120)
        if _login_logo:
            st.markdown(_login_logo, unsafe_allow_html=True)
        st.markdown(f"### {t('app_title')}")
        st.markdown("---")
        _uname = st.text_input(t("username"), key="_login_u")
        _pw = st.text_input(t("password"), type="password", key="_login_p")
        if st.button(t("login_btn"), use_container_width=True, type="primary"):
            _conn = get_conn()
            _user = authenticate(_conn, _uname, _pw)
            _conn.close()
            if _user:
                _saved_lang = st.session_state.get("lang", "de")
                for _k in list(st.session_state.keys()):
                    del st.session_state[_k]
                st.session_state.lang = _saved_lang
                st.session_state.authenticated = True
                st.session_state.username = _user[1]
                st.session_state.is_admin = bool(_user[2])
                st.rerun()
            else:
                st.error(t("login_error"))
    st.stop()

# ── Recording announcement JS (injected once per session) ─────────────────────
_ann_text = "Aufnahme läuft" if st.session_state.lang == "de" else "Recording in progress"
_ann_lang = "de-DE" if st.session_state.lang == "de" else "en-US"
_js = (
    f"if(!window._rAS){{window._rAS=true;var _rs=false;"
    f"function _ann(){{if('speechSynthesis' in window){{"
    f"window.speechSynthesis.cancel();"
    f"var u=new SpeechSynthesisUtterance('{_ann_text}');"
    f"u.lang='{_ann_lang}';"
    f"window.speechSynthesis.speak(u);}}}}"
    f"new MutationObserver(function(){{"
    f"document.querySelectorAll('button[aria-label]').forEach(function(b){{"
    f"if(!b._rl){{b._rl=1;b.addEventListener('click',function(){{"
    f"setTimeout(function(){{var l=(b.getAttribute('aria-label')||'').toLowerCase();"
    f"if(l.includes('stop')&&!_rs){{_rs=1;_ann();}}else if(!l.includes('stop')){{_rs=0;}}"
    f"}},250);}});}}}});}}).observe(document.body,{{childList:true,subtree:true}});}}"
)
st.markdown(
    f'<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"'
    f' onload="{_js}" style="display:none;position:absolute">',
    unsafe_allow_html=True,
)

# ── Header ─────────────────────────────────────────────────────────────────────
_h1, _h2, _h3 = st.columns([1, 3, 1.6])
with _h1:
    _logo = _logo_html(160)
    if _logo:
        st.markdown(_logo, unsafe_allow_html=True)
with _h2:
    st.markdown(
        f"<h2 style='text-align:center;margin:0;color:#1a1a1a;'>{t('app_title')}</h2>",
        unsafe_allow_html=True,
    )
with _h3:
    st.markdown(
        f"""<div style='text-align:right;font-size:13px;line-height:1.5;color:#444;'>
        Clausewitzstr. 2<br>
        10629 Berlin-Charlottenburg<br>
        +49 30 6633110<br>
        info@revitaclinic.de<br>
        www.revitaclinic.de
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='text-align:right;font-size:11px;color:#777;margin-top:4px;'>"
        f"{t('logged_as')}: <b>{st.session_state.username}</b></div>",
        unsafe_allow_html=True,
    )
    if st.button(t("logout"), key="_logout", type="secondary"):
        for _k in list(st.session_state.keys()):
            del st.session_state[_k]
        st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ── Main tabs ──────────────────────────────────────────────────────────────────
_tab_consult, _tab_users = st.tabs([t("tab_consult"), t("tab_users")])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Patient consultation
# ══════════════════════════════════════════════════════════════════════════════
with _tab_consult:

    # ── Patient data section ──────────────────────────────────────────────────
    st.markdown(f'<div class="sec-header">{t("patient_section")}</div>', unsafe_allow_html=True)

    # Autocomplete name input
    _conn = get_conn()
    _patient_names = fetch_patient_names(_conn)
    _conn.close()

    if st.session_state.clicked_suggestion:
        _name = st.session_state.clicked_suggestion
        _conn = get_conn()
        _pd = load_patient_data(_conn, _name)
        _conn.close()
        if _pd:
            st.session_state.patient_data = _pd
            st.session_state.last_loaded_patient = _name
            st.session_state.display_patient_name = _name
            st.session_state.just_loaded_patient = True
        st.session_state.clicked_suggestion = None
        st.rerun()

    _display_val = st.session_state.display_patient_name or st.session_state.patient_data.get("patient_name", "")
    _typed = st.text_input(
        t("name_hint"),
        value=_display_val,
        placeholder=t("name_ph"),
        key="_name_input",
    )

    if _typed != st.session_state.current_patient_input:
        st.session_state.current_patient_input = _typed
        if st.session_state.last_loaded_patient and _typed and _typed not in _patient_names:
            st.session_state.patient_data = {}
            st.session_state.recorded_data = None
            st.session_state.last_loaded_patient = None
            st.session_state.display_patient_name = ""
            st.session_state.just_loaded_patient = False
            st.rerun()

    st.session_state.display_patient_name = _typed

    _suggestions = [n for n in _patient_names if _typed and _typed.lower() in n.lower()]
    if _typed and _suggestions and not st.session_state.just_loaded_patient:
        st.write(f"**{t('suggestions')}:**")
        for _sn in _suggestions[:7]:
            if st.button(_sn, key=f"_sug_{_sn}"):
                st.session_state.clicked_suggestion = _sn
                st.rerun()

    _patient_name_input = _typed
    if (
        _patient_name_input
        and _patient_name_input in _patient_names
        and _patient_name_input != st.session_state.last_loaded_patient
        and not st.session_state.just_loaded_patient
    ):
        _conn = get_conn()
        _pd = load_patient_data(_conn, _patient_name_input)
        _conn.close()
        if _pd:
            st.session_state.patient_data = _pd
            st.session_state.last_loaded_patient = _patient_name_input
            st.session_state.display_patient_name = _patient_name_input
            st.session_state.just_loaded_patient = True
            st.rerun()

    if st.session_state.just_loaded_patient:
        st.session_state.just_loaded_patient = False

    pdata = st.session_state.patient_data or {}

    # ── Parse stored dates ────────────────────────────────────────────────────
    def _parse_date(val):
        if isinstance(val, str):
            try:
                return datetime.strptime(val, "%Y-%m-%d").date()
            except Exception:
                return None
        return val if isinstance(val, date) else None

    _dob_default = _parse_date(pdata.get("geburtsdatum"))
    _ts_default = _parse_date(pdata.get("therapiebeginn"))
    _geschlecht_stored = pdata.get("geschlecht", "M")
    _groesse_stored = pdata.get("groesse")
    _gewicht_stored = pdata.get("gewicht")

    # ── Form fields ───────────────────────────────────────────────────────────
    _c1, _c2, _c3, _c4, _c5, _c6 = st.columns(6)

    with _c1:
        geburtsdatum = st.date_input(
            t("dob"),
            value=_dob_default,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD.MM.YYYY",
            key="_dob",
        )
    with _c2:
        _g_opts = [t("gender_m"), t("gender_f")]
        _g_idx = 1 if _geschlecht_stored in ("W", "F") else 0
        geschlecht = st.radio(t("gender"), _g_opts, horizontal=True, index=_g_idx, key="_gender")
    with _c3:
        groesse = st.number_input(
            t("height"),
            min_value=0,
            max_value=250,
            value=int(_groesse_stored) if _groesse_stored else None,
            placeholder="—",
            key="_groesse",
        )
    with _c4:
        gewicht = st.number_input(
            t("weight"),
            min_value=0,
            max_value=300,
            value=int(_gewicht_stored) if _gewicht_stored else None,
            placeholder="—",
            key="_gewicht",
        )
    with _c5:
        therapiebeginn = st.date_input(
            t("therapy_start"),
            value=_ts_default,
            format="DD.MM.YYYY",
            key="_ts",
        )
    with _c6:
        dauer = st.selectbox(
            t("duration"),
            list(range(1, 13)),
            index=int(pdata.get("dauer", 1)) - 1,
            key="_dauer",
        )

    allergie = st.text_input(t("allergies"), value=pdata.get("allergie", ""), key="_allergie")
    diagnosen = st.text_area(
        t("diagnoses"),
        value=pdata.get("diagnosen", ""),
        height=90,
        placeholder=t("diagnoses_ph"),
        key="_diagnosen",
    )

    # Follow-up
    st.markdown(f"#### <span style='color:{PRIMARY};'>{t('followup')}</span>", unsafe_allow_html=True)
    _fa, _fb = st.columns(2)
    with _fa:
        kt4 = st.checkbox(t("fw_4"), value=bool(pdata.get("kontrolltermin_4", False)), key="_kt4")
    with _fb:
        kt12 = st.checkbox(t("fw_12"), value=bool(pdata.get("kontrolltermin_12", False)), key="_kt12")
    kt_comment = st.text_input(t("comment"), value=pdata.get("kontrolltermin_kommentar", ""), key="_ktc")

    # Save button
    if st.button(t("save_patient"), type="primary"):
        if not _patient_name_input:
            st.error(t("name_required"))
        else:
            _conn = get_conn()
            _cur = _conn.cursor()
            _cur.execute("SELECT id FROM patients WHERE patient_name=?", (_patient_name_input,))
            _existing = _cur.fetchone()
            _vals_update = (
                geburtsdatum, geschlecht, groesse, gewicht,
                therapiebeginn, dauer, allergie, diagnosen,
                kt4, kt12, kt_comment, _patient_name_input,
            )
            _vals_insert = (
                _patient_name_input, geburtsdatum, geschlecht, groesse, gewicht,
                therapiebeginn, dauer, allergie, diagnosen, kt4, kt12, kt_comment,
            )
            if _existing:
                _cur.execute(
                    "UPDATE patients SET geburtsdatum=?,geschlecht=?,groesse=?,gewicht=?,"
                    "therapiebeginn=?,dauer=?,allergie=?,diagnosen=?,"
                    "kontrolltermin_4=?,kontrolltermin_12=?,kontrolltermin_kommentar=? WHERE patient_name=?",
                    _vals_update,
                )
            else:
                _cur.execute(
                    "INSERT INTO patients(patient_name,geburtsdatum,geschlecht,groesse,gewicht,"
                    "therapiebeginn,dauer,allergie,diagnosen,kontrolltermin_4,kontrolltermin_12,"
                    "kontrolltermin_kommentar) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    _vals_insert,
                )
            _conn.commit()
            _conn.close()
            st.session_state.patient_data = {
                "patient_name": _patient_name_input,
                "geburtsdatum": geburtsdatum, "geschlecht": geschlecht,
                "groesse": groesse, "gewicht": gewicht,
                "therapiebeginn": therapiebeginn, "dauer": dauer,
                "allergie": allergie, "diagnosen": diagnosen,
                "kontrolltermin_4": kt4, "kontrolltermin_12": kt12,
                "kontrolltermin_kommentar": kt_comment,
            }
            st.session_state.last_loaded_patient = _patient_name_input
            st.success(t("saved_ok"))
            time.sleep(0.8)
            st.rerun()

    # ── Recordings section ────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f'<div class="sec-header">{t("recordings_section")}</div>', unsafe_allow_html=True)

    _, _rc, _ = st.columns([1, 2, 1])
    with _rc:
        _whisper_lang = st.session_state.lang  # "de" or "en"
        audio_bytes = st.audio_input(t("rec_label"), key="_audio_rec")

        if audio_bytes and audio_bytes != st.session_state.last_processed_audio:
            st.session_state.last_processed_audio = audio_bytes
            with st.spinner(t("processing")):
                # Save audio locally
                try:
                    _audio_path = save_audio_file(audio_bytes)
                    try:
                        _remote = upload_file_to_r2(_audio_path)
                        if _remote:
                            _audio_path = _remote
                    except Exception:
                        pass
                except Exception as _e:
                    st.error(f"{t('recordings_section')}: {_e}")
                    _audio_path = None

                # Transcribe
                _transcript = ""
                try:
                    _transcript = transcribe_with_whisper(
                        audio_bytes, model_name="small", language=_whisper_lang
                    )
                except Exception as _e:
                    st.warning(f"Transkription: {_e}")

                # Summarize
                try:
                    _summary = extractive_summary(_transcript or "", top_k=6)
                    if not _summary:
                        _summary = (_transcript or "").strip()
                except Exception as _e:
                    st.warning(f"Zusammenfassung: {_e}")
                    _summary = (_transcript or "")[:1000]

                st.session_state.recorded_data = {
                    "summary": _summary,
                    "transcript": _transcript,
                    "audio_data": audio_bytes,
                    "audio_path": _audio_path,
                }

                # Persist to DB if patient is saved
                _pname = st.session_state.patient_data.get("patient_name")
                if _pname:
                    _conn = get_conn()
                    _cur = _conn.cursor()
                    _cur.execute("SELECT id FROM patients WHERE patient_name=?", (_pname,))
                    _row = _cur.fetchone()
                    if _row:
                        _cur.execute(
                            "INSERT INTO conversations(patient_id,summary,transcript,audio_path) VALUES(?,?,?,?)",
                            (_row[0], _summary, _transcript, _audio_path),
                        )
                        _conn.commit()
                    _conn.close()

            st.rerun()

        if not audio_bytes and st.session_state.recorded_data is None:
            st.markdown(
                f"<p style='text-align:center;color:#888;margin-top:0.5rem;'>{t('mic_hint')}</p>",
                unsafe_allow_html=True,
            )

    # ── Latest recording results ──────────────────────────────────────────────
    if st.session_state.recorded_data:
        rd = st.session_state.recorded_data
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f"#### <span style='color:{PRIMARY};'>{t('summary_section')}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='background:#fff;padding:1.2rem;border:1px solid #ddd;"
            f"border-radius:6px;line-height:1.8;'>{rd['summary']}</div>",
            unsafe_allow_html=True,
        )

        # PDF download
        _lang_now = st.session_state.lang
        if st.button(t("dl_pdf"), type="primary", key="_pdf_btn"):
            try:
                _pdf_bytes = make_pdf(
                    _patient_name_input or "—",
                    rd["summary"],
                    rd.get("transcript", ""),
                    _lang_now,
                )
                st.download_button(
                    label=t("save_pdf"),
                    data=_pdf_bytes,
                    file_name=f"Zusammenfassung_{_patient_name_input or 'patient'}.pdf",
                    mime="application/pdf",
                    key="_pdf_dl",
                )
            except Exception as _e:
                st.error(f"PDF: {_e}")

        # Transcript
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f"#### <span style='color:{PRIMARY};'>{t('transcript_section')}</span>",
            unsafe_allow_html=True,
        )
        with st.expander(t("show_transcript")):
            st.markdown(
                f"<div style='background:#f8f8f8;padding:1rem;border-radius:4px;'>"
                f"<pre style='white-space:pre-wrap;font-family:monospace;margin:0;'>"
                f"{rd.get('transcript','')}</pre></div>",
                unsafe_allow_html=True,
            )

        # Audio playback
        if rd.get("audio_data"):
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(
                f"#### <span style='color:{PRIMARY};'>{t('audio_section')}</span>",
                unsafe_allow_html=True,
            )
            st.audio(rd["audio_data"])

        # Add another recording button
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button(f"+ {t('add_another')}", type="secondary", key="_add_another"):
            st.session_state.recorded_data = None
            st.session_state.last_processed_audio = None
            st.rerun()

    # ── Previous conversations ────────────────────────────────────────────────
    _pname = st.session_state.patient_data.get("patient_name")
    if _pname:
        _conn = get_conn()
        _cur2 = _conn.cursor()
        _cur2.execute("SELECT id FROM patients WHERE patient_name=?", (_pname,))
        _pid_row = _cur2.fetchone()
        if _pid_row:
            _convs = load_conversations(_conn, _pid_row[0])
        else:
            _convs = pd.DataFrame()
        _conn.close()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f"#### <span style='color:{PRIMARY};'>{t('prev_convs')}</span>",
            unsafe_allow_html=True,
        )

        if _convs.empty:
            st.caption(t("no_convs"))
        else:
            for _, _cv in _convs.iterrows():
                _dt = str(_cv["created_at"])[:16]
                with st.expander(f"{t('conv_from')} {_dt}"):
                    st.markdown(
                        f"<div style='background:#fff;padding:0.9rem;border:1px solid #e0e0e0;"
                        f"border-radius:6px;line-height:1.7;'>{_cv['summary'] or '—'}</div>",
                        unsafe_allow_html=True,
                    )
                    if _cv.get("transcript"):
                        _ts_exp = st.expander(t("show_transcript"), expanded=False)
                        with _ts_exp:
                            st.text(_cv["transcript"])
                    if _cv.get("audio_path") and os.path.exists(str(_cv["audio_path"])):
                        with open(_cv["audio_path"], "rb") as _af:
                            st.audio(_af.read())


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — User management (admin only)
# ══════════════════════════════════════════════════════════════════════════════
with _tab_users:
    if not st.session_state.is_admin:
        st.warning(t("admin_only"))
    else:
        st.markdown(f'<div class="sec-header">{t("add_user_header")}</div>', unsafe_allow_html=True)
        _ua, _ub, _uc = st.columns([2, 2, 1])
        with _ua:
            _new_uname = st.text_input(t("username"), key="_nu_name")
        with _ub:
            _new_pw = st.text_input(t("password"), type="password", key="_nu_pw")
        with _uc:
            _new_admin = st.checkbox(t("is_admin"), key="_nu_admin")

        if st.button(t("add_btn"), type="primary", key="_nu_add"):
            if _new_uname and _new_pw:
                _conn = get_conn()
                _ok = add_user(_conn, _new_uname, _new_pw, _new_admin)
                _conn.close()
                if _ok:
                    st.success(t("user_added"))
                else:
                    st.error(t("user_exists"))
            else:
                st.warning(t("name_required"))

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f'<div class="sec-header">{t("existing_users")}</div>', unsafe_allow_html=True)

        _conn = get_conn()
        _users_df = list_users(_conn)
        _conn.close()

        for _, _urow in _users_df.iterrows():
            _uid = int(_urow["id"])
            _uname_row = str(_urow["username"])
            _edit_key = f"_editing_{_uid}"
            if _edit_key not in st.session_state:
                st.session_state[_edit_key] = False

            with st.container(border=True):
                _uc1, _uc2, _uc3, _uc4, _uc5 = st.columns([2, 1, 2, 1, 1])
                with _uc1:
                    st.markdown(f"**{_uname_row}**")
                with _uc2:
                    _is_admin_row = bool(_urow["is_admin"])
                    st.caption("Admin" if _is_admin_row else "User")
                with _uc3:
                    st.caption(str(_urow["created_at"])[:16])
                with _uc4:
                    if st.button(t("pw_change"), key=f"_edit_btn_{_uid}", type="secondary"):
                        st.session_state[_edit_key] = not st.session_state[_edit_key]
                        st.rerun()
                with _uc5:
                    if _uname_row != "Mahri":
                        if st.button("Delete", key=f"_del_{_uid}", type="secondary"):
                            _conn = get_conn()
                            delete_user(_conn, _uid)
                            _conn.close()
                            st.rerun()

                if st.session_state[_edit_key]:
                    st.markdown("---")
                    _ep1, _ep2, _ep3 = st.columns([2, 2, 1])
                    with _ep1:
                        _new_pw_val = st.text_input(
                            t("pw_new"), type="password", key=f"_pw_{_uid}"
                        )
                    with _ep2:
                        _new_admin_val = st.checkbox(
                            t("toggle_admin"),
                            value=_is_admin_row,
                            key=f"_adm_{_uid}",
                            disabled=(_uname_row == "Mahri"),
                        )
                    with _ep3:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(t("pw_save"), key=f"_pw_save_{_uid}", type="primary"):
                            _conn = get_conn()
                            if _new_pw_val:
                                set_password(_conn, _uid, _new_pw_val)
                            if _uname_row != "Mahri":
                                _conn.execute(
                                    "UPDATE users SET is_admin=? WHERE id=?",
                                    (int(_new_admin_val), _uid),
                                )
                                _conn.commit()
                            _conn.close()
                            st.session_state[_edit_key] = False
                            st.success(t("pw_saved"))
                            time.sleep(0.6)
                            st.rerun()
