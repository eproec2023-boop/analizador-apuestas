import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from scipy.stats import poisson, norm
import requests
import urllib.parse
import io
import re
from datetime import datetime, timedelta, date

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Pro Bet Analyzer 17.2 | Bayesian Calibration & Universal Football Quant",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INICIALIZACIÓN DE BITÁCORA EN SESIÓN ---
COLS_BITACORA = [
    "ID", "Fecha", "Tipo Ticket", "Deporte Principal",
    "Partido 1", "Mercado 1", "Cuota 1",
    "Partido 2", "Mercado 2", "Cuota 2",
    "Partido 3", "Mercado 3", "Cuota 3",
    "Cuota Total", "Cuota Cierre", "CLV (%)",
    "Stake ($)", "Estado", "Monto Cash Out ($)", "Retorno ($)", "Beneficio Neto ($)"
]
if "bitacora_apuestas" not in st.session_state:
    st.session_state["bitacora_apuestas"] = pd.DataFrame(columns=COLS_BITACORA)

# --- ESTILOS CSS EJECUTIVOS Y ALTO CONTRASTE (PC & CELULARES) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    font-variant-numeric: tabular-nums;
}

.stApp {
    background-color: #09090b;
    color: #f4f4f5;
}

label, .stSelectbox label, .stNumberInput label, .stTextInput label, .stSlider label, .stRadio label, .stDateInput label {
    color: #f4f4f5 !important;
    font-weight: 700 !important;
}

div[data-baseweb="select"] > div, input[type="text"], input[type="number"], div[data-testid="stDateInput"] input {
    background-color: #ffffff !important;
    color: #111827 !important;
    font-weight: 700 !important;
}
div[data-baseweb="select"] span, div[data-baseweb="select"] div {
    color: #111827 !important;
}

section[data-testid="stSidebar"] {
    background-color: #121216;
    border-right: 1px solid rgba(255, 255, 255, 0.12);
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #f4f4f5 !important;
}
code {
    background-color: #27272a !important;
    color: #ff9e44 !important;
    padding: 2px 6px !important;
    border-radius: 5px !important;
    font-weight: 700 !important;
}

div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] strong {
    color: #111827 !important;
    font-weight: 600 !important;
}

.clasico-sidebar-box {
    background: linear-gradient(135deg, #2d1406 0%, #431a07 100%);
    border: 2px solid #ff6b00;
    border-left: 6px solid #ff8c00;
    border-radius: 12px;
    padding: 12px 14px;
    margin: 8px 0 12px 0;
    box-shadow: 0 6px 16px rgba(255, 107, 0, 0.25);
}
.clasico-sidebar-title {
    color: #ff9e44 !important;
    font-size: 0.74rem !important;
    font-weight: 800 !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 4px;
}
.clasico-sidebar-text {
    color: #ffffff !important;
    font-size: 0.96rem !important;
    font-weight: 800 !important;
    line-height: 1.3;
}

.main-banner {
    background: linear-gradient(135deg, #121216 0%, #1f1f24 55%, #ea580c 100%);
    padding: 18px 24px;
    border-radius: 16px;
    color: #ffffff;
    margin-bottom: 18px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.45);
    border: 1px solid rgba(255, 107, 0, 0.35);
    border-left: 8px solid #ff6b00;
}
.main-banner h1 {
    color: #ffffff !important;
    margin: 0;
    font-size: 1.80rem;
    font-weight: 900;
    letter-spacing: -0.5px;
}
.main-banner p {
    color: #e4e4e7 !important;
    margin: 5px 0 0 0;
    font-size: 0.88rem;
}

div[data-testid="stMetric"] {
    background: #18181b;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-top: 4px solid #ff6b00;
    padding: 14px 16px;
    border-radius: 14px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.35);
}
div[data-testid="stMetric"] label {
    color: #a1a1aa !important;
    font-weight: 700 !important;
    font-size: 0.76rem !important;
    text-transform: uppercase;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 1.40rem !important;
}

button[data-baseweb="tab"] {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #f4f4f5 !important;
}

.hero-matchup {
    background: linear-gradient(180deg, #18181b 0%, #111114 100%);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 18px;
    padding: 20px 22px;
    margin-bottom: 18px;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.55);
}
.hero-grid {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}
.hero-team {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    min-width: 0;
}
.hero-logo {
    width: 82px;
    height: 82px;
    object-fit: contain;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.65));
    margin-bottom: 8px;
}
.hero-photo {
    width: 88px;
    height: 88px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #ffffff;
    background: #18181b;
    box-shadow: 0 6px 14px rgba(0,0,0,0.5);
    margin-bottom: 8px;
}
.hero-team-name {
    font-size: 1.25rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.2;
    word-wrap: break-word;
}
.hero-badge-loc {
    background: rgba(255, 107, 0, 0.22);
    color: #ff9e44;
    border: 1px solid rgba(255, 107, 0, 0.45);
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    margin-top: 5px;
}
.hero-badge-vis {
    background: rgba(56, 189, 248, 0.20);
    color: #7dd3fc;
    border: 1px solid rgba(56, 189, 248, 0.40);
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    margin-top: 5px;
}
.hero-center {
    flex: 1.25;
    text-align: center;
    padding: 0 8px;
}
.hero-league-pill {
    background: rgba(255, 255, 255, 0.10);
    color: #f4f4f5;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 8px;
}
.hero-score {
    font-size: 2.35rem;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -1px;
    margin: 2px 0;
    white-space: nowrap;
}
.hero-sub {
    color: #d4d4d8;
    font-size: 0.82rem;
    font-weight: 600;
}
.prob-bar-wrap {
    margin-top: 14px;
    background: #27272a;
    border-radius: 999px;
    height: 12px;
    overflow: hidden;
    display: flex;
    border: 1px solid rgba(255,255,255,0.12);
}
.prob-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.76rem;
    font-weight: 700;
    margin-top: 6px;
    color: #e4e4e7;
    gap: 4px;
}

@media (max-width: 768px) {
    .main-banner { padding: 14px 16px; }
    .main-banner h1 { font-size: 1.30rem; }
    .main-banner p { font-size: 0.78rem; }
    .hero-matchup { padding: 14px 10px; }
    .hero-grid { gap: 6px; }
    .hero-logo { width: 56px; height: 56px; }
    .hero-photo { width: 62px; height: 62px; }
    .hero-team-name { font-size: 0.95rem; }
    .hero-score { font-size: 1.55rem; }
    .hero-sub { font-size: 0.72rem; }
    .hero-league-pill { font-size: 0.66rem; padding: 3px 8px; }
    .prob-labels { font-size: 0.68rem; }
    .clasico-sidebar-box { padding: 12px; }
    .clasico-sidebar-text { font-size: 0.92rem !important; }
    div[data-testid="stMetric"] { padding: 10px 12px; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { font-size: 1.18rem !important; }
}
</style>
<div class="main-banner">
<h1>🏆 PRO BET ANALYZER 17.2 <span style="color:#ff8c00;">| BAYESIAN CALIBRATED QUANT SUITE</span></h1>
<p>Calibración Bayesiana en Goles, Tiros, Arco y Córners (18 Ligas/UEFA) • Fuerza Rival Acotada • NHL SOG (Over), PIM & Puck Line</p>
</div>
""", unsafe_allow_html=True)

HEADERS_HTTP = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ==============================================================================
# CATÁLOGOS DE MERCADOS POR DEPORTE (SINCRONIZADOS CON LA BARRA LATERAL)
# ==============================================================================
MERCADOS_SISTEMA = {
    "⚽ Fútbol": [
        "1X2: Gana Local (1)",
        "1X2: Empate (X)",
        "1X2: Gana Visita (2)",
        "Goles: Más de 2.5 Goles (Over)",
        "Goles: Menos de 2.5 Goles (Under)",
        "Ambos Equipos Anotan (BTTS - SÍ)",
        "Ambos Equipos Anotan (BTTS - NO)",
        "Tiros Totales (Over)",
        "Tiros Totales (Under)",
        "Tiros al Arco / Puerta (Over)",
        "Tiros al Arco / Puerta (Under)",
        "Córners Partido Completo FT (Over)",
        "Córners Partido Completo FT (Under)",
        "Córners 1er Tiempo 1T (Over)",
        "Tarjetas Totales (Over)",
        "Tarjetas Totales (Under)"
    ],
    "🎾 Tenis (ATP / WTA)": [
        "Moneyline: Ganador(a) del Partido",
        "Ganador(a) 1er Set",
        "Total Juegos (Over)",
        "Total Juegos (Under)",
        "Total Aces en el Partido (Over)",
        "Total Aces en el Partido (Under)"
    ],
    "🏒 Hockey (NHL)": [
        "Moneyline NHL (Inc. Prórroga)",
        "Hándicap / Puck Line NHL",
        "Total Goles NHL (Over 5.5 / 6.0 / 6.5)",
        "Total Goles NHL (Under 5.5 / 6.0 / 6.5)",
        "Shots on Goal (SOG) Totales (Over)",
        "Shots on Goal (SOG) Equipo Local (Over)",
        "Minutos de Penalización (PIM) Totales (Over)",
        "Minutos de Penalización (PIM) Totales (Under)"
    ],
    "🏀 Basketball (NBA)": [
        "Moneyline NBA",
        "Hándicap / Spread NBA",
        "Total Puntos NBA (Over)",
        "Total Puntos NBA (Under)"
    ],
    "🏈 Fútbol Americano (NFL)": [
        "Moneyline NFL",
        "Hándicap / Spread NFL",
        "Total Puntos NFL (Over)",
        "Total Puntos NFL (Under)"
    ],
    "⚾ Béisbol (MLB)": [
        "Moneyline MLB",
        "Total Carreras MLB (Over)",
        "Total Carreras MLB (Under)"
    ]
}

# ==============================================================================
# EXTRACCIÓN EN VIVO DE TORNEOS UEFA CON BOXSCORE REAL (TIROS, CÓRNERS, TARJETAS)
# ==============================================================================
@st.cache_data(ttl=3600)
def obtener_telemetria_partido_espn(league_code, event_id):
    res = {
        "HS": np.nan, "HST": np.nan, "HC": np.nan, "HY": np.nan, "HR": np.nan,
        "AS": np.nan, "AST": np.nan, "AC": np.nan, "AY": np.nan, "AR": np.nan
    }
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/summary?event={event_id}"
        r = requests.get(url, headers=HEADERS_HTTP, timeout=5).json()
        teams_box = r.get("boxscore", {}).get("teams", [])
        for tb in teams_box:
            ha = tb.get("homeAway", "")
            pref = "H" if ha == "home" else ("A" if ha == "away" else "")
            if not pref:
                continue
            stats_map = {}
            for st_item in tb.get("statistics", []):
                nm = str(st_item.get("name", "")).lower()
                val_raw = st_item.get("displayValue", "0")
                try:
                    stats_map[nm] = float(val_raw)
                except Exception:
                    pass

            if "totalshots" in stats_map:
                res[f"{pref}S"] = int(stats_map["totalshots"])
            if "shotsontarget" in stats_map:
                res[f"{pref}ST"] = int(stats_map["shotsontarget"])
            if "woncorners" in stats_map:
                res[f"{pref}C"] = int(stats_map["woncorners"])
            if "yellowcards" in stats_map:
                res[f"{pref}Y"] = int(stats_map["yellowcards"])
            if "redcards" in stats_map:
                res[f"{pref}R"] = int(stats_map["redcards"])
    except Exception:
        pass
    return res

@st.cache_data(ttl=1800)
def cargar_datos_uefa_clubes_espn(league_code):
    eventos_unicos = {}
    equipos_activos = set()
    try:
        url_t = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/teams?limit=80"
        rt = requests.get(url_t, headers=HEADERS_HTTP, timeout=8).json()
        for sp in rt.get("sports", []):
            for lg in sp.get("leagues", []):
                for tw in lg.get("teams", []):
                    tm = tw.get("team", {})
                    nom = tm.get("displayName", "")
                    tid = str(tm.get("id", ""))
                    if nom:
                        equipos_activos.add(nom)
                    if tid:
                        url_sc = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/teams/{tid}/schedule"
                        rsc = requests.get(url_sc, headers=HEADERS_HTTP, timeout=6).json()
                        for ev in rsc.get("events", []):
                            comp = ev.get("competitions", [{}])[0]
                            if comp.get("status", {}).get("type", {}).get("completed", False):
                                comps = comp.get("competitors", [])
                                if len(comps) == 2:
                                    h_c = comps[0] if comps[0].get("homeAway") == "home" else comps[1]
                                    a_c = comps[1] if comps[0].get("homeAway") == "home" else comps[0]
                                    h_nom = h_c.get("team", {}).get("displayName", "")
                                    a_nom = a_c.get("team", {}).get("displayName", "")
                                    sc_h = h_c.get("score", 0)
                                    sc_a = a_c.get("score", 0)
                                    hg = int(float(sc_h.get("value", sc_h.get("displayValue", 0)))) if isinstance(sc_h, dict) else int(float(sc_h or 0))
                                    ag = int(float(sc_a.get("value", sc_a.get("displayValue", 0)))) if isinstance(sc_a, dict) else int(float(sc_a or 0))
                                    f_ev = ev.get("date", "")[:10]
                                    ev_id = str(ev.get("id", ""))
                                    if h_nom and a_nom and ev_id:
                                        equipos_activos.add(h_nom)
                                        equipos_activos.add(a_nom)
                                        if ev_id not in eventos_unicos:
                                            eventos_unicos[ev_id] = {
                                                "ev_id": ev_id,
                                                "Date": f_ev,
                                                "Tournament": league_code.upper(),
                                                "HomeTeam": h_nom,
                                                "AwayTeam": a_nom,
                                                "FTHG": hg,
                                                "FTAG": ag
                                            }
    except Exception:
        pass

    filas_partidos = []
    for ev_id, base_row in eventos_unicos.items():
        tel = obtener_telemetria_partido_espn(league_code, ev_id)
        fila_completa = {
            "Date": base_row["Date"],
            "Tournament": base_row["Tournament"],
            "HomeTeam": base_row["HomeTeam"],
            "AwayTeam": base_row["AwayTeam"],
            "FTHG": base_row["FTHG"],
            "FTAG": base_row["FTAG"],
            **tel
        }
        filas_partidos.append(fila_completa)

    df_uefa = pd.DataFrame(filas_partidos)
    if not df_uefa.empty:
        df_uefa = df_uefa.sort_values("Date").reset_index(drop=True)
    return df_uefa, sorted(list(equipos_activos))

def obtener_codigo_temporada_dinamico():
    hoy = datetime.utcnow()
    anio_ini = hoy.year if hoy.month >= 7 else hoy.year - 1
    anio_fin = anio_ini + 1
    return f"{str(anio_ini)[-2:]}{str(anio_fin)[-2:]}"

# ==============================================================================
# RECONSTRUCTOR DE TABLA DE POSICIONES Y DETECTOR DE RIESGO DE GOLEADA (BLOWOUT)
# ==============================================================================
def calcular_tabla_posiciones_csv(df_csv):
    if df_csv.empty:
        return pd.DataFrame(), {}
    equipos = sorted(list(set(df_csv['HomeTeam'].unique()).union(set(df_csv['AwayTeam'].unique()))))
    stats = {eq: {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "Pts": 0} for eq in equipos}

    for _, r in df_csv.iterrows():
        h, a = r['HomeTeam'], r['AwayTeam']
        hg, ag = int(r['FTHG']), int(r['FTAG'])
        stats[h]["PJ"] += 1
        stats[a]["PJ"] += 1
        stats[h]["GF"] += hg
        stats[h]["GC"] += ag
        stats[a]["GF"] += ag
        stats[a]["GC"] += hg
        if hg > ag:
            stats[h]["G"] += 1
            stats[h]["Pts"] += 3
            stats[a]["P"] += 1
        elif hg < ag:
            stats[a]["G"] += 1
            stats[a]["Pts"] += 3
            stats[h]["P"] += 1
        else:
            stats[h]["E"] += 1
            stats[a]["E"] += 1
            stats[h]["Pts"] += 1
            stats[a]["Pts"] += 1

    filas_tabla = []
    for eq, d in stats.items():
        dg = d["GF"] - d["GC"]
        ppp = round(d["Pts"] / max(d["PJ"], 1), 2)
        filas_tabla.append({
            "Equipo": eq, "PJ": d["PJ"], "G": d["G"], "E": d["E"], "P": d["P"],
            "GF": d["GF"], "GC": d["GC"], "DG": dg, "Pts": d["Pts"], "PPP": ppp
        })

    df_pos = pd.DataFrame(filas_tabla).sort_values(by=["Pts", "PPP", "DG", "GF"], ascending=False).reset_index(drop=True)
    df_pos.insert(0, "Pos", df_pos.index + 1)

    mapa_puestos = {}
    for _, row in df_pos.iterrows():
        mapa_puestos[row["Equipo"]] = {
            "pos": int(row["Pos"]),
            "pts": int(row["Pts"]),
            "pj": int(row["PJ"]),
            "dg": int(row["DG"]),
            "ppp": float(row["PPP"])
        }
    return df_pos, mapa_puestos

def evaluar_riesgo_goleada_corners(mat, pos_loc, pos_vis, total_equipos):
    prob_goleada_loc = 0.0
    prob_goleada_vis = 0.0
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if (i - j) >= 3:
                prob_goleada_loc += float(mat[i, j])
            elif (j - i) >= 3:
                prob_goleada_vis += float(mat[i, j])

    prob_goleada_max = max(prob_goleada_loc, prob_goleada_vis)
    brecha_puestos = abs(pos_loc - pos_vis)
    umbral_brecha = max(int(total_equipos * 0.45), 6)

    if (brecha_puestos >= umbral_brecha and prob_goleada_max >= 0.16) or (prob_goleada_max >= 0.24):
        factor_decay = 0.86
        quien_golea = "Local" if prob_goleada_loc >= prob_goleada_vis else "Visita"
        msg = (
            f"⚠️ Alerta Anti-Goleada Activa (Brecha #{pos_loc} vs #{pos_vis} | Prob. Goleada ≥3 goles: {prob_goleada_max*100:.1f}%): "
            f"Si {quien_golea} liquida el partido temprano (ej. 3-0 al min 60), el ritmo de córners en el 2T cae drásticamente. "
            f"Se aplicó un ajuste de -14% a los córners totales. Sugerencia táctica: Prioriza Córners 1er Tiempo (1T) o Cash Out al descanso."
        )
        return True, factor_decay, prob_goleada_max, msg

    return False, 1.00, prob_goleada_max, ""

# ==============================================================================
# DETECTOR AUTOMÁTICO DE CLÁSICOS, DERBIS Y RIVALIDADES DE ALTA FRICCIÓN
# ==============================================================================
CLASICOS_MUNDIALES = [
    ("real madrid", "barcelona", "El Clásico de España (+18% Fricción)"),
    ("real madrid", "ath madrid", "Derbi Madrileño (+18% Fricción)"),
    ("real madrid", "atletico", "Derbi Madrileño (+18% Fricción)"),
    ("barcelona", "espanol", "Derbi Barcelonés (+18% Fricción)"),
    ("betis", "sevilla", "El Gran Derbi Sevillano (+20% Fricción)"),
    ("ath bilbao", "sociedad", "Derbi Vasco (+18% Fricción)"),
    ("valencia", "villarreal", "Derbi de la Comunitat (+16% Fricción)"),
    ("arsenal", "tottenham", "North London Derby (+18% Fricción)"),
    ("liverpool", "man united", "Clásico de Inglaterra (+18% Fricción)"),
    ("liverpool", "manchester united", "Clásico de Inglaterra (+18% Fricción)"),
    ("liverpool", "everton", "Merseyside Derby (+18% Fricción)"),
    ("man city", "man united", "Manchester Derby (+16% Fricción)"),
    ("manchester city", "manchester united", "Manchester Derby (+16% Fricción)"),
    ("chelsea", "arsenal", "Derbi de Londres (+16% Fricción)"),
    ("chelsea", "tottenham", "Derbi de Londres (+18% Fricción)"),
    ("newcastle", "sunderland", "Tyne-Wear Derby (+20% Fricción)"),
    ("aston villa", "wolves", "West Midlands Derby (+16% Fricción)"),
    ("inter", "milan", "Derby della Madonnina (+18% Fricción)"),
    ("juventus", "inter", "Derby d'Italia (+18% Fricción)"),
    ("juventus", "torino", "Derby della Mole (+18% Fricción)"),
    ("roma", "lazio", "Derby della Capitale (+20% Fricción)"),
    ("napoli", "juventus", "Rivalidad Norte-Sur Italia (+16% Fricción)"),
    ("genoa", "sampdoria", "Derby della Lanterna (+18% Fricción)"),
    ("bayern", "dortmund", "Der Klassiker (+16% Fricción)"),
    ("dortmund", "schalke", "Revierderby (+20% Fricción)"),
    ("hamburg", "st pauli", "Derbi de Hamburgo (+20% Fricción)"),
    ("koln", "m'gladbach", "Derbi del Rin (+18% Fricción)"),
    ("paris sg", "marseille", "Le Classique Francia (+20% Fricción)"),
    ("paris saint-germain", "marseille", "Le Classique Francia (+20% Fricción)"),
    ("lyon", "st etienne", "Derby Rhône-Alpes (+20% Fricción)"),
    ("nice", "monaco", "Derby de la Côte d'Azur (+16% Fricción)"),
    ("ajax", "feyenoord", "De Klassieker Holanda (+20% Fricción)"),
    ("ajax", "psv", "De Topper Holanda (+16% Fricción)"),
    ("benfica", "porto", "O Clássico Portugal (+20% Fricción)"),
    ("benfica", "sp lisbon", "Dérbi de Lisboa (+18% Fricción)"),
    ("benfica", "sporting cp", "Dérbi de Lisboa (+18% Fricción)"),
    ("porto", "sp lisbon", "Clásico Portugal (+18% Fricción)"),
    ("celtic", "rangers", "Old Firm Derby (+22% Fricción)"),
    ("anderlecht", "club brugge", "De Topper Bélgica (+18% Fricción)"),
    ("standard", "anderlecht", "Clásico de Bélgica (+18% Fricción)"),
    ("galatasaray", "fenerbahce", "Clásico Intercontinental Estambul (+22% Fricción)"),
    ("galatasaray", "besiktas", "Derbi de Estambul (+20% Fricción)"),
    ("fenerbahce", "besiktas", "Derbi de Estambul (+20% Fricción)"),
    ("boca", "river", "Superclásico Argentino (+22% Fricción)"),
    ("racing", "independiente", "Clásico de Avellaneda (+20% Fricción)"),
    ("san lorenzo", "huracan", "Clásico Porteño (+18% Fricción)"),
    ("newell", "rosario", "Clásico Rosarino (+22% Fricción)"),
    ("flamengo", "fluminense", "Fla-Flu Carioca (+18% Fricción)"),
    ("flamengo", "vasco", "Clássico dos Milhões (+18% Fricción)"),
    ("corinthians", "palmeiras", "Derby Paulista (+20% Fricción)"),
    ("sao paulo", "corinthians", "Clássico Majestoso (+18% Fricción)"),
    ("gremio", "internacional", "Grenal Gaúcho (+22% Fricción)"),
    ("atletico-mg", "cruzeiro", "Clássico Mineiro (+20% Fricción)"),
    ("america", "guadalajara", "Clásico Nacional México (+18% Fricción)"),
    ("america", "cruz azul", "Clásico Joven México (+16% Fricción)"),
    ("america", "unam", "Clásico Capitalino (+18% Fricción)"),
    ("tigres", "monterrey", "Clásico Regiomontano (+20% Fricción)"),
    ("lafc", "la galaxy", "El Tráfico MLS (+18% Fricción)"),
    ("new york city", "new york red bulls", "Hudson River Derby (+18% Fricción)"),
    ("england", "germany", "Clásico Europeo Selecciones (+16% Fricción)"),
    ("france", "italy", "Derbi Transalpino (+16% Fricción)"),
    ("spain", "portugal", "Derbi Ibérico (+16% Fricción)"),
    ("netherlands", "germany", "Clásico del Rin Selecciones (+18% Fricción)"),
    ("netherlands", "belgium", "Derbi de los Países Bajos (+16% Fricción)"),
    ("serbia", "croatia", "Clásico Balcánico Alta Tensión (+22% Fricción)"),
    ("serbia", "albania", "Rivalidad Balcánica Alta Tensión (+22% Fricción)"),
    ("greece", "turkey", "Derbi del Egeo (+20% Fricción)")
]

def evaluar_clasico_y_friccion_h2h(eq_loc, eq_vis, df_csv, media_tarj_liga=4.0):
    l_low = eq_loc.lower().strip()
    v_low = eq_vis.lower().strip()

    for t1, t2, desc in CLASICOS_MUNDIALES:
        if (t1 in l_low and t2 in v_low) or (t2 in l_low and t1 in v_low):
            factor = 1.22 if "+22%" in desc else (1.20 if "+20%" in desc else (1.16 if "+16%" in desc else 1.18))
            return True, factor, f"🔥 {desc}"

    if not df_csv.empty and 'HY' in df_csv.columns and 'AY' in df_csv.columns:
        h2h = df_csv[
            ((df_csv['HomeTeam'] == eq_loc) & (df_csv['AwayTeam'] == eq_vis)) |
            ((df_csv['HomeTeam'] == eq_vis) & (df_csv['AwayTeam'] == eq_loc))
        ].dropna(subset=['HY', 'AY'])
        if len(h2h) >= 2:
            hr_h2h = h2h['HR'].fillna(0) if 'HR' in h2h.columns else 0
            ar_h2h = h2h['AR'].fillna(0) if 'AR' in h2h.columns else 0
            prom_h2h = float((h2h['HY'] + h2h['AY'] + hr_h2h + ar_h2h).mean())
            if prom_h2h >= (media_tarj_liga * 1.22):
                return True, 1.15, f"🔥 Rivalidad H2H Friccionada ({prom_h2h:.1f} tarj/PJ previos • +15%)"

    return False, 1.00, "Rivalidad Estándar (1.00x)"

# ==============================================================================
# UTILIDADES CUANTITATIVAS: CRITERIO DE KELLY, DIXON-COLES, B2B Y ESCUDOS
# ==============================================================================
def detectar_fatiga_back_to_back(df_partidos, col_fecha="Fecha"):
    if df_partidos.empty or col_fecha not in df_partidos.columns:
        return False, ""
    try:
        ult_str = str(df_partidos[col_fecha].iloc[-1])[:10]
        ult_dt = datetime.strptime(ult_str, "%Y-%m-%d").date()
        hoy_utc = datetime.utcnow().date()
        dias_diff = (hoy_utc - ult_dt).days
        if 0 <= dias_diff <= 1:
            return True, f"⚡ Back-to-Back Detectado (Jugó {ult_str})"
    except Exception:
        pass
    return False, ""

def calcular_kelly_stake(prob_real, cuota_betano, banca_actual, fraccion_kelly, min_prob_pct, min_edge_pct):
    edge = (prob_real * cuota_betano) - 1.0
    if (prob_real * 100.0) < min_prob_pct or (edge * 100.0) < min_edge_pct or cuota_betano <= 1.01:
        return 0.0, 0.0
    b = cuota_betano - 1.0
    q = 1.0 - prob_real
    kelly_puro = max(((b * prob_real) - q) / b, 0.0)
    stake_pct = min(kelly_puro * fraccion_kelly * 100.0, 15.0)
    monto_usd = round(banca_actual * (stake_pct / 100.0), 2)
    return round(stake_pct, 2), monto_usd

def aplicar_dixon_coles(mat, lam_loc, lam_vis, rho=-0.11):
    m = mat.copy()
    tau_00 = max(1.0 - (lam_loc * lam_vis * rho), 0.1)
    tau_10 = max(1.0 + (lam_vis * rho), 0.1)
    tau_01 = max(1.0 + (lam_loc * rho), 0.1)
    tau_11 = max(1.0 - rho, 0.1)
    m[0, 0] *= tau_00
    m[1, 0] *= tau_10
    m[0, 1] *= tau_01
    m[1, 1] *= tau_11
    suma = np.sum(m)
    if suma > 0:
        m = m / suma
    return m

def generar_escudo_svg_data_uri(nombre, color_hex="#ff6b00"):
    letras = "".join([w[0] for w in nombre.split()[:2]]).upper() if nombre else "EQ"
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="90" height="90" viewBox="0 0 90 90"><path d="M45 6 L78 20 V46 C78 66 63 80 45 86 C27 80 12 66 12 46 V20 Z" fill="#18181b" stroke="{color_hex}" stroke-width="4"/><text x="45" y="53" font-family="Arial, sans-serif" font-size="26" font-weight="bold" fill="#ffffff" text-anchor="middle">{letras}</text></svg>'
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)

def generar_avatar_tenista_svg(nombre, color_hex="#38bdf8"):
    letras = "".join([w[0] for w in nombre.split()[:2]]).upper() if nombre else "TN"
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96"><circle cx="48" cy="48" r="44" fill="#18181b" stroke="{color_hex}" stroke-width="4"/><text x="48" y="57" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="#ffffff" text-anchor="middle">{letras}</text></svg>'
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)

def buscar_logo_equipo(nombre_club, mapa_logos, color_fallback="#ff6b00"):
    fallback = generar_escudo_svg_data_uri(nombre_club, color_fallback)
    if not mapa_logos:
        return fallback, fallback
    n_low = nombre_club.lower().strip()
    if n_low in mapa_logos:
        return mapa_logos[n_low], fallback
    palabras = [w for w in re.sub(r'[^a-zA-Z\s]', '', n_low).split() if len(w) > 3 and w not in ["club", "real", "sport", "united", "city", "athletic", "atletico", "deportivo", "calcio"]]
    for k_map, url_logo in mapa_logos.items():
        if any(p in k_map for p in palabras):
            return url_logo, fallback
    return fallback, fallback

def renderizar_hero_card_deporte(eq_l, eq_v, logo_l, fb_l, logo_v, fb_v, liga_txt, marcador_txt, sub_txt, p_l, p_x, p_v, baja_l=0, baja_v=0, badge_extra="", sub_loc="🏠 LOCAL", sub_vis="✈️ VISITA"):
    baja_l_html = f'<span style="background:rgba(239,68,68,0.25);color:#fecaca;padding:2px 8px;border-radius:6px;font-size:0.70rem;margin-top:4px;">🏥 Bajas: -{baja_l}%</span>' if baja_l > 0 else ''
    baja_v_html = f'<span style="background:rgba(239,68,68,0.25);color:#fecaca;padding:2px 8px;border-radius:6px;font-size:0.70rem;margin-top:4px;">🏥 Bajas: -{baja_v}%</span>' if baja_v > 0 else ''
    extra_html = f'<div style="margin-top:6px;"><span style="background:rgba(234,88,12,0.35);color:#ffffff;border:1.5px solid #ff8c00;padding:4px 12px;border-radius:999px;font-size:0.76rem;font-weight:800;">{badge_extra}</span></div>' if badge_extra else ''

    if p_x is not None and p_x > 0.005:
        bar_html = f'<div class="prob-bar-wrap"><div style="width:{p_l*100:.1f}%; background:#ff6b00;"></div><div style="width:{p_x*100:.1f}%; background:#71717a;"></div><div style="width:{p_v*100:.1f}%; background:#38bdf8;"></div></div><div class="prob-labels"><span style="color:#ff9e44;">1: {p_l*100:.1f}%</span><span style="color:#d4d4d8;">X: {p_x*100:.1f}%</span><span style="color:#7dd3fc;">2: {p_v*100:.1f}%</span></div>'
    else:
        bar_html = f'<div class="prob-bar-wrap"><div style="width:{p_l*100:.1f}%; background:#ff6b00;"></div><div style="width:{p_v*100:.1f}%; background:#38bdf8;"></div></div><div class="prob-labels"><span style="color:#ff9e44;">{eq_l}: {p_l*100:.1f}%</span><span style="color:#7dd3fc;">{eq_v}: {p_v*100:.1f}%</span></div>'

    html_hero = (
        f'<div class="hero-matchup">'
        f'<div class="hero-grid">'
        f'<div class="hero-team">'
        f'<img src="{logo_l}" onerror="this.onerror=null;this.src=\'{fb_l}\';" class="hero-logo"/>'
        f'<div class="hero-team-name">{eq_l}</div>'
        f'<span class="hero-badge-loc">{sub_loc}</span>{baja_l_html}'
        f'</div>'
        f'<div class="hero-center">'
        f'<div class="hero-league-pill">{liga_txt}</div>'
        f'<div class="hero-score">{marcador_txt}</div>'
        f'<div class="hero-sub">{sub_txt}</div>'
        f'{extra_html}'
        f'{bar_html}'
        f'</div>'
        f'<div class="hero-team">'
        f'<img src="{logo_v}" onerror="this.onerror=null;this.src=\'{fb_v}\';" class="hero-logo"/>'
        f'<div class="hero-team-name">{eq_v}</div>'
        f'<span class="hero-badge-vis">{sub_vis}</span>{baja_v_html}'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html_hero, unsafe_allow_html=True)

def resaltar_valor(fila):
    veredicto = str(fila.get("Veredicto", ""))
    if "✅" in veredicto or "🔥" in veredicto:
        return ['background-color: #d1fae5; color: #065f46; font-weight: 800;'] * len(fila)
    if "⚠️" in veredicto:
        return ['background-color: #fef3c7; color: #92400e; font-weight: 700;'] * len(fila)
    return ['color: #18181b; font-weight: 500;'] * len(fila)

def mostrar_cancha_calor(eq_loc, eq_vis, dom_loc, dom_vis, intensidad_loc, intensidad_vis, deporte="futbol"):
    estilos = {
        "futbol": ("linear-gradient(90deg, #14532d 0%, #166534 25%, #15803d 50%, #166534 75%, #14532d 100%)", "rgba(255,255,255,0.65)", "#ffffff"),
        "nhl": ("linear-gradient(90deg, #e0f2fe 0%, #f0f9ff 50%, #e0f2fe 100%)", "rgba(220,38,38,0.45)", "#0284c7"),
        "nba": ("linear-gradient(90deg, #78350f 0%, #92400e 50%, #78350f 100%)", "rgba(255,255,255,0.70)", "#f59e0b"),
        "nfl": ("linear-gradient(90deg, #14532d 0%, #15803d 50%, #14532d 100%)", "rgba(255,255,255,0.75)", "#eab308"),
        "mlb": ("linear-gradient(90deg, #166534 0%, #92400e 50%, #166534 100%)", "rgba(255,255,255,0.70)", "#ffffff"),
        "tenis_hard": ("linear-gradient(90deg, #1e3a8a 0%, #2563eb 50%, #1e3a8a 100%)", "rgba(255,255,255,0.85)", "#60a5fa"),
        "tenis_clay": ("linear-gradient(90deg, #9a3412 0%, #c2410c 50%, #9a3412 100%)", "rgba(255,255,255,0.85)", "#fb923c"),
        "tenis_grass": ("linear-gradient(90deg, #14532d 0%, #16a34a 50%, #14532d 100%)", "rgba(255,255,255,0.85)", "#4ade80")
    }
    bg_pitch, line_color, border_pitch = estilos.get(deporte, estilos["futbol"])
    op_loc = min(max(0.28 + (dom_loc / 100.0) * 0.65, 0.28), 0.90)
    op_vis = min(max(0.28 + (dom_vis / 100.0) * 0.65, 0.28), 0.90)
    rad_loc = int(95 + (intensidad_loc * 55))
    rad_vis = int(95 + (intensidad_vis * 55))

    html_code = (
        f'<div style="background:{bg_pitch}; border: 3px solid {border_pitch}; border-radius: 14px; height: 240px; position: relative; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,0.35); font-family: system-ui, -apple-system, sans-serif;">'
        f'<div style="position:absolute; left:50%; top:0; bottom:0; width:3px; background:{line_color}; transform:translateX(-50%);"></div>'
        f'<div style="position:absolute; left:50%; top:50%; width:76px; height:76px; border:3px solid {line_color}; border-radius:50%; transform:translate(-50%, -50%);"></div>'
        f'<div style="position:absolute; left:0; top:22%; bottom:22%; width:15%; border-right:3px solid {line_color}; border-top:3px solid {line_color}; border-bottom:3px solid {line_color};"></div>'
        f'<div style="position:absolute; right:0; top:22%; bottom:22%; width:15%; border-left:3px solid {line_color}; border-top:3px solid {line_color}; border-bottom:3px solid {line_color};"></div>'
        f'<div style="position:absolute; right:5%; top:50%; width:{rad_loc}px; height:{rad_loc}px; background:radial-gradient(circle, rgba(255,59,0,{op_loc}) 0%, rgba(255,145,0,{op_loc*0.65}) 45%, rgba(255,255,0,0) 75%); transform:translateY(-50%); border-radius:50%; pointer-events:none;"></div>'
        f'<div style="position:absolute; left:5%; top:50%; width:{rad_vis}px; height:{rad_vis}px; background:radial-gradient(circle, rgba(0,200,255,{op_vis}) 0%, rgba(0,110,255,{op_vis*0.65}) 45%, rgba(0,0,255,0) 75%); transform:translateY(-50%); border-radius:50%; pointer-events:none;"></div>'
        f'<div style="position:absolute; left:10px; top:10px; background:rgba(15,23,42,0.90); color:#fff; padding:5px 10px; border-radius:8px; font-weight:700; font-size:12px; border-left: 4px solid #ff6b00;">🏠 {eq_loc}: {dom_loc:.0f}%</div>'
        f'<div style="position:absolute; right:10px; top:10px; background:rgba(15,23,42,0.90); color:#fff; padding:5px 10px; border-radius:8px; font-weight:700; font-size:12px; border-right: 4px solid #38bdf8;">{eq_vis}: {dom_vis:.0f}% ✈️</div>'
        f'</div>'
    )
    components.html(html_code, height=255)

def construir_tabla_mercados_kelly(lista_mercados, col_nombre, banca_act, frac_kelly, min_prob, min_edge):
    filas = []
    for m, p, c in lista_mercados:
        edge_pct = (p * c - 1.0) * 100.0
        prob_pct = p * 100.0
        stake_pct, monto_usd = calcular_kelly_stake(p, c, banca_act, frac_kelly, min_prob, min_edge)
        if stake_pct > 0:
            veredicto = "✅ APOSTAR (+EV)"
        elif edge_pct > 5.0:
            veredicto = "⚠️ Edge OK / Prob < Umbral"
        else:
            veredicto = "❌ Pasar"
        filas.append({
            col_nombre: m,
            "Prob. Real": round(prob_pct, 1),
            "Cuota Justa": f"{1/max(p, 0.01):.2f}",
            "Cuota Betano": f"{c:.2f}",
            "Edge (%)": f"{edge_pct:+.2f}%",
            "Kelly (%)": f"{stake_pct:.2f}%",
            "Apostar ($)": f"${monto_usd:.2f}",
            "Veredicto": veredicto
        })
    return pd.DataFrame(filas)

# ==============================================================================
# MOTOR DE INTELIGENCIA AUTOMÁTICA DE BAJAS, ÁRBITROS Y ESCUDOS (ESPN / NHL)
# ==============================================================================
ESPN_LEAGUE_MAP = {
    "🏆 UEFA Champions League": ("soccer", "uefa.champions"),
    "🥈 UEFA Europa League": ("soccer", "uefa.europa"),
    "🥉 UEFA Conference League": ("soccer", "uefa.europa.conf"),
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)": ("soccer", "eng.1"),
    "🇪🇸 LaLiga (España)": ("soccer", "esp.1"),
    "🇮🇹 Serie A (Italia)": ("soccer", "ita.1"),
    "🇩🇪 Bundesliga (Alemania)": ("soccer", "ger.1"),
    "🇫🇷 Ligue 1 (Francia)": ("soccer", "fra.1"),
    "🇳🇱 Eredivisie (Países Bajos)": ("soccer", "ned.1"),
    "🇵🇹 Primeira Liga (Portugal)": ("soccer", "por.1"),
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Premiership (Escocia)": ("soccer", "sco.1"),
    "🇧🇪 Jupiler Pro League (Bélgica)": ("soccer", "bel.1"),
    "🇹🇷 Süper Lig (Turquía)": ("soccer", "tur.1"),
    "🇺🇸 MLS (Estados Unidos)": ("soccer", "usa.1"),
    "🇧🇷 Brasileirão Serie A (Brasil)": ("soccer", "bra.1"),
    "🇦🇷 Liga Profesional (Argentina)": ("soccer", "arg.1"),
    "🇲🇽 Liga MX (México)": ("soccer", "mex.1"),
    "🌍 UEFA Nations League (Selecciones UEFA)": ("soccer", "uefa.nations")
}

TRADUCCION_ESTADO_LESION = {
    "Out": "🔴 Baja Confirmada (Out)",
    "Injured Reserve": "🔴 Reserva Lesionados (IR)",
    "Suspension": "🔴 Suspendido",
    "Doubtful": "🟠 Muy Dudoso (Doubtful)",
    "Questionable": "🟡 En Duda (Questionable)",
    "Day-To-Day": "🟡 Día a Día (Day-to-Day)",
    "Probable": "🟢 Probable"
}

@st.cache_data(ttl=1800)
def detectar_arbitro_asignado_espn(sport, league, eq_loc, eq_vis):
    if not sport or not league:
        return ""
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
        r = requests.get(url, headers=HEADERS_HTTP, timeout=6).json()
        claves = [w.lower() for w in (eq_loc.split() + eq_vis.split()) if len(w) > 3]
        for ev in r.get("events", []):
            nom_ev = ev.get("name", "").lower()
            if any(k in nom_ev for k in claves):
                comp = ev.get("competitions", [{}])[0]
                officials = comp.get("officials", [])
                if officials:
                    return str(officials[0].get("displayName", "")).strip()
    except Exception:
        pass
    return ""

@st.cache_data(ttl=3600)
def obtener_catalogo_equipos_y_logos_espn(sport, league):
    mapa_ids = {}
    mapa_logos = {}
    if not sport or not league:
        return mapa_ids, mapa_logos
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams?limit=120"
        r = requests.get(url, headers=HEADERS_HTTP, timeout=8).json()
        for sp in r.get("sports", []):
            for lg in sp.get("leagues", []):
                for t_wrap in lg.get("teams", []):
                    tm = t_wrap.get("team", {})
                    nombre = tm.get("displayName", "")
                    corto = tm.get("shortDisplayName", "")
                    tid = str(tm.get("id", ""))
                    logos = tm.get("logos", [])
                    logo_url = logos[0].get("href", "") if logos else tm.get("logo", "")
                    if nombre and tid:
                        mapa_ids[nombre] = tid
                    if logo_url:
                        if nombre:
                            mapa_logos[nombre.lower()] = logo_url
                        if corto:
                            mapa_logos[corto.lower()] = logo_url
    except Exception:
        pass
    return mapa_ids, mapa_logos

@st.cache_data(ttl=900)
def obtener_reporte_lesiones_espn(sport, league, eq_a, eq_b):
    filas_inj = []
    if not sport or not league:
        return pd.DataFrame()
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/injuries"
        r = requests.get(url, headers=HEADERS_HTTP, timeout=7).json()
        claves_a = [w.lower() for w in eq_a.split() if len(w) > 3] or [eq_a.lower()]
        claves_b = [w.lower() for w in eq_b.split() if len(w) > 3] or [eq_b.lower()]

        for block in r.get("injuries", []):
            tm_name = block.get("displayName", block.get("team", {}).get("displayName", ""))
            tm_low = tm_name.lower()
            pertenece_a = any(k in tm_low for k in claves_a)
            pertenece_b = any(k in tm_low for k in claves_b)
            if pertenece_a or pertenece_b:
                etiqueta_eq = eq_a if pertenece_a else eq_b
                for item in block.get("injuries", []):
                    ath = item.get("athlete", {})
                    jug = ath.get("displayName", "Jugador")
                    pos = ath.get("position", {}).get("abbreviation", "-")
                    est_raw = item.get("status", "Questionable")
                    est_esp = TRADUCCION_ESTADO_LESION.get(est_raw, f"🟡 {est_raw}")
                    det = item.get("shortComment", item.get("longComment", "Reporte médico activo"))

                    est_low = est_raw.lower()
                    if any(k in est_low for k in ["out", "injured", "ir", "suspen"]):
                        base_w = 3.0
                    elif "doubtful" in est_low:
                        base_w = 2.0
                    elif any(k in est_low for k in ["questionable", "day"]):
                        base_w = 1.0
                    else:
                        base_w = 0.0

                    pos_up = str(pos).upper()
                    if pos_up in ["QB"]:
                        base_w *= 4.5
                    elif pos_up in ["FW", "ST", "CF", "LW", "RW", "PG", "SG", "SF", "PF", "C", "P", "SP"]:
                        base_w *= 1.35

                    filas_inj.append({
                        "Equipo": etiqueta_eq,
                        "Jugador": jug,
                        "Posición": pos,
                        "Estado Médico": est_esp,
                        "Detalle / Parte Médico": str(det)[:110],
                        "_peso_auto": base_w
                    })
    except Exception:
        pass
    return pd.DataFrame(filas_inj)

@st.cache_data(ttl=900)
def obtener_noticias_relevantes_espn(sport, league, eq_a, eq_b):
    titulares = []
    if not sport or not league:
        return titulares
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/news?limit=40"
        r = requests.get(url, headers=HEADERS_HTTP, timeout=7).json()
        claves = [w.lower() for w in (eq_a.split() + eq_b.split()) if len(w) > 3]
        for art in r.get("articles", []):
            hl = art.get("headline", "")
            desc = art.get("description", "")
            texto_busq = f"{hl} {desc}".lower()
            if any(k in texto_busq for k in claves):
                fecha_n = art.get("published", "")[:10]
                titulares.append((fecha_n, hl, desc))
    except Exception:
        pass
    return titulares[:6]

def calcular_penalizacion_automatica(df_inj, noticias, eq_loc, eq_vis):
    raw_l, raw_v = 0.0, 0.0
    if not df_inj.empty and "_peso_auto" in df_inj.columns:
        raw_l += float(df_inj[df_inj["Equipo"] == eq_loc]["_peso_auto"].sum())
        raw_v += float(df_inj[df_inj["Equipo"] == eq_vis]["_peso_auto"].sum())

    palabras_alerta = ["injury", "injured", "out for", "ruled out", "sidelined", "lesion", "baja", "suspend", "miss"]
    claves_l = [w.lower() for w in eq_loc.split() if len(w) > 3]
    claves_v = [w.lower() for w in eq_vis.split() if len(w) > 3]
    for _, hl, desc in noticias:
        txt = f"{hl} {desc}".lower()
        if any(pa in txt for pa in palabras_alerta):
            if any(kl in txt for kl in claves_l):
                raw_l += 2.5
            if any(kv in txt for kv in claves_v):
                raw_v += 2.5

    pen_l = int(min(max(round(raw_l / 5.0) * 5, 0), 30))
    pen_v = int(min(max(round(raw_v / 5.0) * 5, 0), 30))
    return pen_l, pen_v

def renderizar_panel_bajas_y_factor(sport, league, eq_loc, eq_vis, key_prefix):
    df_inj = obtener_reporte_lesiones_espn(sport, league, eq_loc, eq_vis)
    noticias = obtener_noticias_relevantes_espn(sport, league, eq_loc, eq_vis)
    auto_pen_l, auto_pen_v = calcular_penalizacion_automatica(df_inj, noticias, eq_loc, eq_vis)

    with st.expander(f"🏥 INTELIGENCIA AUTOMÁTICA DE BAJAS, LESIONES Y NOTICIAS ({eq_loc} vs. {eq_vis})", expanded=(not df_inj.empty or auto_pen_l > 0 or auto_pen_v > 0)):
        if not df_inj.empty:
            st.warning(f"⚠️ Reporte Médico Oficial Detectado ({len(df_inj)} bajas/dudas en API ESPN) — Factor Auto-Calculado: {eq_loc} (-{auto_pen_l}%) | {eq_vis} (-{auto_pen_v}%)")
            cols_visibles = [c for c in df_inj.columns if not c.startswith("_")]
            st.dataframe(df_inj[cols_visibles].style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)
        else:
            st.info(f"ℹ️ Sin reporte médico activo en el feed público de ESPN para {eq_loc} vs. {eq_vis} (Factor Auto-Calculado: -{auto_pen_l}% / -{auto_pen_v}%).")

        if noticias:
            st.markdown("**🗞️ Últimas Noticias Relevantes Analizadas:**")
            for f_n, hl, desc in noticias:
                st.markdown(f"📰 **[{f_n}] {hl}** — _{desc[:140]}_")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏥 Factor de Incidencia (Auto)")
    st.sidebar.caption(f"🤖 Auto-detección: **{eq_loc} (-{auto_pen_l}%)** | **{eq_vis} (-{auto_pen_v}%)**")
    imp_loc = st.sidebar.slider(f"Penalización {eq_loc} (%)", 0, 30, auto_pen_l, 5, key=f"imp_l_{key_prefix}")
    imp_vis = st.sidebar.slider(f"Penalización {eq_vis} (%)", 0, 30, auto_pen_v, 5, key=f"imp_v_{key_prefix}")
    return 1.0 - (imp_loc / 100.0), 1.0 - (imp_vis / 100.0), imp_loc, imp_vis

# ==============================================================================
# FUNCIONES GLOBALES DE DATOS DEPORTIVOS (NATIONS LEAGUE, ESPN, NHL + PIM)
# ==============================================================================
SELECCIONES_UEFA = [
    "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus", "Belgium",
    "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark",
    "England", "Estonia", "Faroe Islands", "Finland", "France", "Georgia", "Germany",
    "Gibraltar", "Greece", "Hungary", "Iceland", "Israel", "Italy", "Kazakhstan",
    "Kosovo", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta", "Moldova",
    "Montenegro", "Netherlands", "North Macedonia", "Northern Ireland", "Norway",
    "Poland", "Portugal", "Republic of Ireland", "Romania", "San Marino", "Scotland",
    "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey",
    "Ukraine", "Wales"
]

@st.cache_data(ttl=1800)
def cargar_datos_nations_league():
    urls_int = [
        "https://cdn.jsdelivr.net/gh/martj42/international_results@master/results.csv",
        "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
    ]
    for u in urls_int:
        try:
            resp = requests.get(u, headers=HEADERS_HTTP, timeout=10)
            if resp.status_code == 200:
                df = pd.read_csv(io.StringIO(resp.text))
                df = df[df['date'] >= '2022-01-01'].copy()
                reemplazos = {"Czech Republic": "Czechia"}
                df['home_team'] = df['home_team'].replace(reemplazos)
                df['away_team'] = df['away_team'].replace(reemplazos)
                df = df[df['home_team'].isin(SELECCIONES_UEFA) & df['away_team'].isin(SELECCIONES_UEFA)]
                df = df.rename(columns={
                    'date': 'Date', 'home_team': 'HomeTeam', 'away_team': 'AwayTeam',
                    'home_score': 'FTHG', 'away_score': 'FTAG', 'tournament': 'Tournament'
                })
                df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
                df['FTHG'] = df['FTHG'].astype(int)
                df['FTAG'] = df['FTAG'].astype(int)
                if not df.empty:
                    return df
        except Exception:
            pass
    return pd.DataFrame()

@st.cache_data(ttl=900)
def extraer_ultimos_partidos_reales_espn(sport, league, team_id, nombre_equipo, n_partidos=5, condicion_filtro="ALL"):
    if not team_id:
        return pd.DataFrame()
    filas = []
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams/{team_id}/schedule"
        r = requests.get(url, headers=HEADERS_HTTP, timeout=8).json()
        for ev in r.get("events", []):
            comp = ev.get("competitions", [{}])[0]
            if comp.get("status", {}).get("type", {}).get("completed", False) is True:
                fecha_raw = ev.get("date", "")[:10]
                competidores = comp.get("competitors", [])
                if len(competidores) == 2:
                    yo, rival = None, None
                    for c in competidores:
                        c_id = str(c.get("team", {}).get("id", ""))
                        c_name = c.get("team", {}).get("displayName", "")
                        if c_id == str(team_id) or c_name == nombre_equipo:
                            yo = c
                        else:
                            rival = c
                    if yo and rival:
                        es_local = (yo.get("homeAway", "") == "home")
                        if condicion_filtro == "HOME" and not es_local:
                            continue
                        if condicion_filtro == "AWAY" and es_local:
                            continue

                        sc_yo_raw = yo.get("score", 0)
                        sc_riv_raw = rival.get("score", 0)
                        pts_yo = float(sc_yo_raw.get("value", sc_yo_raw.get("displayValue", 0))) if isinstance(sc_yo_raw, dict) else float(sc_yo_raw or 0)
                        pts_riv = float(sc_riv_raw.get("value", sc_riv_raw.get("displayValue", 0))) if isinstance(sc_riv_raw, dict) else float(sc_riv_raw or 0)
                        filas.append({
                            "Fecha": fecha_raw,
                            "Condición": "🏠 Casa" if es_local else "✈️ Ruta",
                            "Rival": rival.get("team", {}).get("displayName", "Rival"),
                            "Puntos/Carreras a Favor": int(pts_yo),
                            "Puntos/Carreras en Contra": int(pts_riv),
                            "Total Marcador": int(pts_yo + pts_riv),
                            "Resultado": "✅ Victoria" if pts_yo > pts_riv else ("❌ Derrota" if pts_yo < pts_riv else "🤝 Empate")
                        })
    except Exception:
        pass
    df_out = pd.DataFrame(filas)
    if not df_out.empty:
        df_out = df_out.sort_values("Fecha").tail(n_partidos)
    return df_out

@st.cache_data(ttl=1800)
def obtener_catalogo_equipos_nhl():
    mapa = {}
    mapa_logos = {}
    try:
        r = requests.get("https://api-web.nhle.com/v1/standings/now", headers=HEADERS_HTTP, timeout=8).json()
        for t in r.get("standings", []):
            nombre = t.get("teamName", {}).get("default", "")
            abbrev = t.get("teamAbbrev", {}).get("default", "")
            logo_url = t.get("teamLogo", "")
            if nombre and abbrev:
                mapa[nombre] = abbrev
                if logo_url:
                    mapa_logos[nombre.lower()] = logo_url
    except Exception:
        pass
    return mapa, mapa_logos

@st.cache_data(ttl=1200)
def obtener_boxscore_detallado_nhl(game_id):
    try:
        r = requests.get(f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore", headers=HEADERS_HTTP, timeout=5).json()
        h_tm = r.get("homeTeam", {})
        a_tm = r.get("awayTeam", {})
        h_sog = int(h_tm.get("sog", 0))
        a_sog = int(a_tm.get("sog", 0))
        h_pim = int(h_tm.get("pim", 0))
        a_pim = int(a_tm.get("pim", 0))
        return h_sog, a_sog, h_pim, a_pim
    except Exception:
        return 0, 0, 0, 0

@st.cache_data(ttl=900)
def extraer_ultimos_partidos_nhl_completo(abbrev, condicion="HOME", n_partidos=5):
    if not abbrev:
        return pd.DataFrame()
    filas = []
    try:
        r = requests.get(f"https://api-web.nhle.com/v1/club-schedule-season/{abbrev}/now", headers=HEADERS_HTTP, timeout=8).json()
        juegos_filtrados = []
        for g in r.get("games", []):
            if g.get("gameState") in ["OFF", "FINAL"]:
                h_ab = g.get("homeTeam", {}).get("abbrev", "")
                es_local = (h_ab == abbrev)
                if condicion == "HOME" and not es_local:
                    continue
                if condicion == "AWAY" and es_local:
                    continue
                juegos_filtrados.append(g)

        for g in juegos_filtrados[-n_partidos:]:
            gid = g.get("id")
            fecha = g.get("gameDate", "")
            h_tm = g.get("homeTeam", {})
            a_tm = g.get("awayTeam", {})
            h_ab = h_tm.get("abbrev", "")
            a_ab = a_tm.get("abbrev", "")
            h_sc = int(h_tm.get("score", 0))
            a_sc = int(a_tm.get("score", 0))
            es_local = (h_ab == abbrev)

            h_sog, a_sog, h_pim, a_pim = obtener_boxscore_detallado_nhl(gid) if gid else (0, 0, 0, 0)
            sog_favor = h_sog if es_local else a_sog
            sog_contra = a_sog if es_local else h_sog
            pim_propio = h_pim if es_local else a_pim
            pim_rival = a_pim if es_local else h_pim

            gf = h_sc if es_local else a_sc
            gc = a_sc if es_local else h_sc
            rival = a_ab if es_local else h_ab
            tipo_cierre = g.get("periodDescriptor", {}).get("periodType", "REG")
            cierre_lbl = "60' Reg." if tipo_cierre == "REG" else f"Prórroga ({tipo_cierre})"

            filas.append({
                "Fecha": fecha,
                "Condición": "🏠 Local" if es_local else "✈️ Visita",
                "Rival": rival,
                "Goles a Favor": gf,
                "Goles en Contra": gc,
                "Total Goles": gf + gc,
                "Tiros al Arco (SOG) Favor": sog_favor if sog_favor > 0 else np.nan,
                "Tiros al Arco (SOG) Contra": sog_contra if sog_contra > 0 else np.nan,
                "Total Tiros (SOG)": (sog_favor + sog_contra) if (sog_favor > 0 and sog_contra > 0) else np.nan,
                "Min. Penalización (PIM) Propios": pim_propio,
                "Min. Penalización (PIM) Rival": pim_rival,
                "Total Min. Penalización (PIM)": pim_propio + pim_rival,
                "Definición": cierre_lbl,
                "Resultado": "✅ Victoria" if gf > gc else "❌ Derrota"
            })
    except Exception:
        pass
    df_out = pd.DataFrame(filas)
    if not df_out.empty:
        df_out = df_out.sort_values("Fecha")
    return df_out

# ==============================================================================
# MOTOR DE TENIS CONECTADO EN VIVO A ESPN (SUPERFICIE 2X + DESGASTE + ACES)
# ==============================================================================
ACES_BASE_AUDITADOS = {
    "Jannik Sinner": 8.8, "Carlos Alcaraz": 6.4, "Alexander Zverev": 10.8, "Novak Djokovic": 7.6,
    "Daniil Medvedev": 8.9, "Taylor Fritz": 11.8, "Casper Ruud": 6.2, "Andrey Rublev": 9.1,
    "Alex de Minaur": 5.4, "Grigor Dimitrov": 8.7, "Stefanos Tsitsipas": 8.4, "Tommy Paul": 7.2,
    "Holger Rune": 7.5, "Hubert Hurkacz": 14.6, "Frances Tiafoe": 8.9, "Ben Shelton": 12.8,
    "Jack Draper": 9.6, "Ugo Humbert": 8.5, "Lorenzo Musetti": 5.8, "Arthur Fils": 7.9,
    "Sebastian Korda": 8.2, "Alexei Popyrin": 11.2, "Felix Auger-Aliassime": 10.9, "Karen Khachanov": 8.6,
    "Matteo Berrettini": 12.4, "Nicolas Jarry": 11.5, "Alexander Bublik": 13.4, "Reilly Opelka": 16.5,
    "Giovanni Mpetshi Perricard": 15.8, "Jakub Mensik": 10.2, "Tallon Griekspoor": 9.8,
    "Aryna Sabalenka": 6.9, "Iga Swiatek": 3.3, "Coco Gauff": 4.6, "Jessica Pegula": 4.2,
    "Elena Rybakina": 8.8, "Jasmine Paolini": 2.4, "Qinwen Zheng": 7.6, "Emma Navarro": 2.9,
    "Daria Kasatkina": 2.1, "Danielle Collins": 5.1, "Paula Badosa": 5.8, "Marta Kostyuk": 4.4,
    "Mirra Andreeva": 3.6, "Diana Shnaider": 3.8, "Anna Kalinskaya": 3.9, "Karolina Muchova": 4.7,
    "Donna Vekic": 5.9, "Beatriz Haddad Maia": 4.1, "Jelena Ostapenko": 4.8, "Elina Svitolina": 3.7,
    "Liudmila Samsonova": 6.8, "Ekaterina Alexandrova": 6.5, "Victoria Azarenka": 3.9,
    "Katie Boulter": 5.2, "Linda Noskova": 6.4, "Naomi Osaka": 7.8, "Clara Tauson": 6.2,
    "Caroline Garcia": 7.9, "Madison Keys": 6.1, "Amanda Anisimova": 4.9
}

@st.cache_data(ttl=1800)
def obtener_rankings_oficiales_espn_tenis(circuito):
    pref = "atp" if "ATP" in circuito else "wta"
    catalogo = {}
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/tennis/{pref}/rankings"
        r = requests.get(url, headers=HEADERS_HTTP, timeout=8).json()
        for rg in r.get("rankings", []):
            for item in rg.get("ranks", []):
                ath = item.get("athlete", {})
                nombre = ath.get("displayName", "").strip()
                aid = str(ath.get("id", ""))
                rk = int(item.get("current", 100))
                pts = float(item.get("points", 0))
                foto_api = ath.get("headshot", {}).get("href", "") if isinstance(ath.get("headshot"), dict) else ""
                foto_cdn = foto_api if foto_api else (f"https://a.espncdn.com/i/headshots/tennis/players/full/{aid}.png" if aid else "")
                if nombre:
                    catalogo[nombre] = {"id": aid, "rank": rk, "points": pts, "foto": foto_cdn}
    except Exception:
        pass
    return catalogo

@st.cache_data(ttl=3600)
def obtener_catalogo_maestro_entidades():
    catalogo = {}
    cod_temp = obtener_codigo_temporada_dinamico()
    urls_fut_cat = [
        f"https://www.football-data.co.uk/mmz4281/{cod_temp}/E0.csv",
        f"https://www.football-data.co.uk/mmz4281/{cod_temp}/SP1.csv",
        f"https://www.football-data.co.uk/mmz4281/{cod_temp}/I1.csv",
        f"https://www.football-data.co.uk/mmz4281/{cod_temp}/D1.csv",
        f"https://www.football-data.co.uk/mmz4281/{cod_temp}/F1.csv",
        f"https://www.football-data.co.uk/mmz4281/{cod_temp}/N1.csv",
        f"https://www.football-data.co.uk/mmz4281/{cod_temp}/P1.csv",
        f"https://www.football-data.co.uk/mmz4281/{cod_temp}/SC0.csv",
        f"https://www.football-data.co.uk/mmz4281/{cod_temp}/B1.csv",
        f"https://www.football-data.co.uk/mmz4281/{cod_temp}/T1.csv",
        "https://www.football-data.co.uk/new/USA.csv",
        "https://www.football-data.co.uk/new/BRA.csv",
        "https://www.football-data.co.uk/new/ARG.csv",
        "https://www.football-data.co.uk/new/MEX.csv"
    ]
    clubes_fut = set(SELECCIONES_UEFA)
    for u in urls_fut_cat:
        try:
            r = requests.get(u, headers=HEADERS_HTTP, timeout=5)
            if r.status_code == 200:
                df_t = pd.read_csv(io.StringIO(r.text))
                c_h = 'HomeTeam' if 'HomeTeam' in df_t.columns else ('Home' if 'Home' in df_t.columns else None)
                c_a = 'AwayTeam' if 'AwayTeam' in df_t.columns else ('Away' if 'Away' in df_t.columns else None)
                if c_h and c_a:
                    clubes_fut.update(df_t[c_h].dropna().astype(str).tolist())
                    clubes_fut.update(df_t[c_a].dropna().astype(str).tolist())
        except Exception:
            pass

    for lg_uefa in ["uefa.champions", "uefa.europa", "uefa.europa.conf"]:
        m_ids, _ = obtener_catalogo_equipos_y_logos_espn("soccer", lg_uefa)
        clubes_fut.update(m_ids.keys())

    catalogo["⚽ Fútbol"] = sorted(list(clubes_fut))

    cat_atp = obtener_rankings_oficiales_espn_tenis("ATP (Masculino)")
    cat_wta = obtener_rankings_oficiales_espn_tenis("WTA (Femenino)")
    tenistas_todos = sorted(list(set(list(cat_atp.keys()) + list(cat_wta.keys()) + list(ACES_BASE_AUDITADOS.keys()))))
    catalogo["🎾 Tenis (ATP / WTA)"] = tenistas_todos

    m_nhl, _ = obtener_catalogo_equipos_nhl()
    catalogo["🏒 Hockey (NHL)"] = sorted(list(m_nhl.keys())) if m_nhl else ["New York Rangers", "Boston Bruins", "Edmonton Oilers"]

    m_nba, _ = obtener_catalogo_equipos_y_logos_espn("basketball", "nba")
    catalogo["🏀 Basketball (NBA)"] = sorted(list(m_nba.keys())) if m_nba else ["Boston Celtics", "Denver Nuggets", "Los Angeles Lakers"]

    m_nfl, _ = obtener_catalogo_equipos_y_logos_espn("football", "nfl")
    catalogo["🏈 Fútbol Americano (NFL)"] = sorted(list(m_nfl.keys())) if m_nfl else ["Kansas City Chiefs", "Buffalo Bills", "San Francisco 49ers"]

    m_mlb, _ = obtener_catalogo_equipos_y_logos_espn("baseball", "mlb")
    catalogo["⚾ Béisbol (MLB)"] = sorted(list(m_mlb.keys())) if m_mlb else ["New York Yankees", "Los Angeles Dodgers", "Houston Astros"]

    return catalogo

def detectar_superficie_torneo(nombre_torneo):
    t = nombre_torneo.lower()
    if any(k in t for k in ["roland garros", "french open", "madrid", "rome", "roma", "monte carlo", "monte-carlo", "barcelona", "stuttgart", "charleston", "rio", "buenos aires", "santiago", "bogota", "hamburg", "gstaad", "bastad", "umag", "kitzbuhel", "geneva", "lyon", "strasbourg", "rabat", "palermo", "iasi", "budapest", "bucharest", "estoril", "munich"]):
        return "Clay"
    if any(k in t for k in ["wimbledon", "halle", "queen", "eastbourne", "s-hertogenbosch", "hertogenbosch", "mallorca", "berlin", "bad homburg", "nottingham", "birmingham", "newport"]):
        return "Grass"
    return "Hard"

@st.cache_data(ttl=1800)
def obtener_partidos_reales_espn_tenista(circuito, athlete_id, nombre_tenista):
    pref = "atp" if "ATP" in circuito else "wta"
    partidos = []
    try:
        fechas_consulta = []
        hoy = datetime.utcnow()
        for dias_atras in range(0, 300, 25):
            f_Fin = hoy - timedelta(days=dias_atras)
            f_Ini = f_Fin - timedelta(days=24)
            fechas_consulta.append(f"{f_Ini.strftime('%Y%m%d')}-{f_Fin.strftime('%Y%m%d')}")

        apellido_clave = nombre_tenista.split()[-1].lower()
        for rango_f in fechas_consulta[:8]:
            url_sb = f"https://site.api.espn.com/apis/site/v2/sports/tennis/{pref}/scoreboard?dates={rango_f}&limit=200"
            res_sb = requests.get(url_sb, headers=HEADERS_HTTP, timeout=6).json()
            for trn in res_sb.get("events", []):
                nom_torneo = trn.get("name", "Torneo Oficial")
                sup_torneo = detectar_superficie_torneo(nom_torneo)
                for grp in trn.get("grouping", []):
                    for comp in grp.get("competitions", []):
                        if comp.get("status", {}).get("type", {}).get("completed", False):
                            cs = comp.get("competitors", [])
                            if len(cs) == 2:
                                n0 = cs[0].get("athlete", {}).get("displayName", "")
                                n1 = cs[1].get("athlete", {}).get("displayName", "")
                                id0 = str(cs[0].get("athlete", {}).get("id", ""))
                                id1 = str(cs[1].get("athlete", {}).get("id", ""))
                                es_c0 = (id0 == str(athlete_id)) or (n0.lower() == nombre_tenista.lower()) or (apellido_clave in n0.lower() and n0[:1].lower() == nombre_tenista[:1].lower())
                                es_c1 = (id1 == str(athlete_id)) or (n1.lower() == nombre_tenista.lower()) or (apellido_clave in n1.lower() and n1[:1].lower() == nombre_tenista[:1].lower())
                                if es_c0 or es_c1:
                                    yo = cs[0] if es_c0 else cs[1]
                                    riv = cs[1] if es_c0 else cs[0]
                                    gano = bool(yo.get("winner", False))
                                    ls_yo = yo.get("linescores", [])
                                    ls_riv = riv.get("linescores", [])
                                    sets_str = []
                                    j_gan, j_per = 0, 0
                                    for s_idx in range(min(len(ls_yo), len(ls_riv))):
                                        v_y = int(float(ls_yo[s_idx].get("value", 0)))
                                        v_r = int(float(ls_riv[s_idx].get("value", 0)))
                                        sets_str.append(f"{v_y}-{v_r}")
                                        j_gan += v_y
                                        j_per += v_r
                                    marcador = ", ".join(sets_str) if sets_str else ("2-0" if gano else "0-2")
                                    fecha_p = comp.get("date", trn.get("date", ""))[:10]
                                    ronda = comp.get("type", {}).get("text", "-")
                                    partidos.append({
                                        "Fecha": fecha_p,
                                        "Torneo": nom_torneo,
                                        "Superficie": sup_torneo,
                                        "Ronda": ronda,
                                        "Rival": riv.get("athlete", {}).get("displayName", "Rival"),
                                        "Resultado": "✅ Victoria" if gano else "❌ Derrota",
                                        "Marcador": marcador,
                                        "J_Gan": j_gan,
                                        "J_Per": j_per,
                                        "Gano_Bool": gano
                                    })
    except Exception:
        pass

    df_p = pd.DataFrame(partidos)
    if not df_p.empty and "Fecha" in df_p.columns:
        df_p = df_p.drop_duplicates(subset=["Fecha", "Rival"]).sort_values("Fecha")
    return df_p

def calcular_perfil_superficie_real(df_partidos, rank_actual, circuito, nombre_tenista):
    es_atp = "ATP" in circuito
    r_clip = min(max(int(rank_actual), 1), 300)
    deg = np.log10(r_clip) / np.log10(300)

    if es_atp:
        h_hard_base = round(89.5 - (deg * 13.5), 1)
        b_hard_base = round(28.5 - (deg * 9.5), 1)
        aces_hard_default = round(max(9.4 - (deg * 3.8), 4.2), 1)
    else:
        h_hard_base = round(81.5 - (deg * 14.5), 1)
        b_hard_base = round(42.5 - (deg * 10.5), 1)
        aces_hard_default = round(max(5.4 - (deg * 2.4), 2.0), 1)

    aces_hard = ACES_BASE_AUDITADOS.get(nombre_tenista, aces_hard_default)
    win_base = round(float(np.clip(78.0 - (deg * 28.0), 42.0, 86.0)), 1)

    stats_sup = {
        "Hard": {"Hold": h_hard_base, "Break": b_hard_base, "G": 0, "P": 0, "WinPct": win_base, "Juegos_Prom": 22.4 if es_atp else 21.2, "Aces": round(aces_hard * 1.00, 1)},
        "Clay": {"Hold": round(h_hard_base - 3.2, 1), "Break": round(b_hard_base + 2.8, 1), "G": 0, "P": 0, "WinPct": round(win_base - 1.5, 1), "Juegos_Prom": 22.0 if es_atp else 20.8, "Aces": round(aces_hard * 0.72, 1)},
        "Grass": {"Hold": round(h_hard_base + 2.6, 1), "Break": round(b_hard_base - 3.0, 1), "G": 0, "P": 0, "WinPct": round(win_base + 1.0, 1), "Juegos_Prom": 23.4 if es_atp else 21.8, "Aces": round(aces_hard * 1.32, 1)}
    }

    if not df_partidos.empty and "Superficie" in df_partidos.columns:
        for sup_k in ["Hard", "Clay", "Grass"]:
            sub_s = df_partidos[df_partidos["Superficie"] == sup_k]
            if len(sub_s) > 0:
                g_s = int(sub_s["Gano_Bool"].sum())
                p_s = len(sub_s) - g_s
                wp_s = round((g_s / len(sub_s)) * 100.0, 1)
                jg_tot = float(sub_s["J_Gan"].sum())
                jp_tot = float(sub_s["J_Per"].sum())
                if (jg_tot + jp_tot) > 15:
                    ult_s = sub_s.tail(4)
                    jg_rec = float(ult_s["J_Gan"].sum())
                    jp_rec = float(ult_s["J_Per"].sum())
                    ratio_j = ((jg_tot + jg_rec) / max(jg_tot + jp_tot + jg_rec + jp_rec, 1.0))
                    ajuste = (ratio_j - 0.50) * 28.0
                    stats_sup[sup_k]["Hold"] = round(float(np.clip(stats_sup[sup_k]["Hold"] + ajuste, 58.0, 94.0)), 1)
                    stats_sup[sup_k]["Break"] = round(float(np.clip(stats_sup[sup_k]["Break"] + ajuste * 0.8, 15.0, 54.0)), 1)
                    stats_sup[sup_k]["Juegos_Prom"] = round(float((jg_tot + jp_tot) / len(sub_s)), 1)
                stats_sup[sup_k]["G"] = g_s
                stats_sup[sup_k]["P"] = p_s
                stats_sup[sup_k]["WinPct"] = wp_s

    return stats_sup

# ==============================================================================
# BARRA LATERAL: GESTIÓN DE BANCA (KELLY) Y SELECTOR MAESTRO DE DEPORTE
# ==============================================================================
st.sidebar.markdown("### 💰 Gestión de Banca (Criterio Kelly)")
banca_usuario = st.sidebar.number_input("Banca Actual ($ USD)", min_value=1.0, max_value=1000000.0, value=100.0, step=10.0)
col_k1, col_k2 = st.sidebar.columns(2)
kelly_opcion = col_k1.selectbox("Fracción Kelly", ["25% (Prudente)", "50% (Medio)", "15% (Conservador)"], index=0)
fraccion_kelly_val = 0.25 if "25%" in kelly_opcion else (0.50 if "50%" in kelly_opcion else 0.15)
min_prob_filtro = col_k2.number_input("Min Prob (%)", 50.0, 90.0, 65.0, 1.0)
min_edge_filtro = st.sidebar.slider("Edge Mínimo para Apostar (%)", 5.0, 25.0, 10.0, 1.0)
st.sidebar.markdown("---")

st.sidebar.markdown("### 🎯 Selector Maestro de Deporte")
opciones_deportes = [
    "⚽ Fútbol (18 Torneos: UEFA Champions/Europa/Conf + Ligas)",
    "🎾 Tenis (ATP / WTA Superficie 2x, Aces + Indoor/Altura)",
    "🏒 Hockey sobre Hielo (NHL - SOG Over, PIM + Hándicap Abierto)",
    "🏀 Basketball (NBA - Local/Visita, B2B + Spread)",
    "🏈 Fútbol Americano (NFL - Local/Visita, Clima + Spread)",
    "⚾ Béisbol (MLB - API ESPN + Escudos)"
]
deporte_activo = st.sidebar.selectbox("Elige la disciplina a analizar:", opciones_deportes, index=0)
st.sidebar.markdown("---")

# ==============================================================================
# BITÁCORA INTELIGENTE DE APUESTAS (FECHA + CASH OUT + GRÁFICOS DÍA/SEMANA/MES)
# ==============================================================================
def renderizar_selector_pata_bitacora(num_pata, catalogo_entidades, es_obligatorio=True):
    st.markdown(f"**{num_pata}️⃣ Selección {num_pata} {'(Obligatoria)' if es_obligatorio else ''}:**")
    c1, c2, c3, c4, c5, c6 = st.columns([1.15, 1.25, 1.25, 1.65, 0.85, 0.85])
    dep_sel = c1.selectbox("Deporte", list(MERCADOS_SISTEMA.keys()), key=f"bit_dep_{num_pata}")
    lista_ent = catalogo_entidades.get(dep_sel, ["Equipo / Jugador A", "Equipo / Jugador B"])
    idx_b_def = 1 if len(lista_ent) > 1 else 0
    ent_a = c2.selectbox("Local / Jugador A (Escribe para buscar)", lista_ent, index=0, key=f"bit_enta_{num_pata}")
    ent_b = c3.selectbox("Visita / Jugador B (Escribe para buscar)", lista_ent, index=idx_b_def, key=f"bit_entb_{num_pata}")
    merc_sel = c4.selectbox("Mercado del Sistema", MERCADOS_SISTEMA[dep_sel], key=f"bit_merc_{num_pata}")
    cuota_v = c5.number_input("Cuota", 1.01, 50.0, 1.80, 0.05, key=f"bit_cuo_{num_pata}")
    cierre_v = c6.number_input("Cierre", 1.01, 50.0, 1.72, 0.05, key=f"bit_cie_{num_pata}")
    partido_str = f"{ent_a} vs {ent_b}"
    return dep_sel, partido_str, merc_sel, cuota_v, cierre_v

with st.expander("📒 BITÁCORA INTELIGENTE DE APUESTAS (FECHA, CASH OUT Y RENDIMIENTO DÍA / SEMANA / MES)", expanded=False):
    catalogo_global = obtener_catalogo_maestro_entidades()
    df_bit = st.session_state["bitacora_apuestas"]

    st.markdown("**➕ Registrar Nueva Operación:**")
    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([1.0, 1.15, 0.95, 1.05, 0.95])
    fecha_ticket_reg = b_col1.date_input("📅 Fecha Apuesta", value=date.today(), key="bit_fecha_reg")
    tipo_apuesta_reg = b_col2.selectbox("Tipo de Ticket", ["Simple (1 Partido)", "Combinada (2 Partidos)", "Combinada (3 Partidos)"])
    stake_reg = b_col3.number_input("Stake ($ USD)", min_value=0.10, max_value=100000.0, value=round(max(banca_usuario * 0.05, 1.0), 2), step=1.0)
    estado_reg = b_col4.selectbox("Estado Ticket", ["⏳ Pendiente", "✅ Ganada", "❌ Perdida", "💰 Cash Out"])
    monto_cashout_reg = b_col5.number_input(
        "Monto Cash Out ($)",
        min_value=0.0, max_value=1000000.0,
        value=round(stake_reg * 1.25, 2) if "Cash Out" in estado_reg else 0.0,
        step=0.50,
        disabled=("Cash Out" not in estado_reg)
    )

    dep1, part1, merc1, cuota1_val, cierre1_val = renderizar_selector_pata_bitacora(1, catalogo_global, True)

    if "2 Partidos" in tipo_apuesta_reg or "3 Partidos" in tipo_apuesta_reg:
        dep2, part2, merc2, cuota2_val, cierre2_val = renderizar_selector_pata_bitacora(2, catalogo_global, False)
    else:
        dep2, part2, merc2, cuota2_val, cierre2_val = "-", "-", "-", 1.0, 1.0

    if "3 Partidos" in tipo_apuesta_reg:
        dep3, part3, merc3, cuota3_val, cierre3_val = renderizar_selector_pata_bitacora(3, catalogo_global, False)
    else:
        dep3, part3, merc3, cuota3_val, cierre3_val = "-", "-", "-", 1.0, 1.0

    cuota_total_ticket = round(cuota1_val * cuota2_val * cuota3_val, 2)
    cierre_total_ticket = round(cierre1_val * cierre2_val * cierre3_val, 2)
    clv_ticket = round(((cuota_total_ticket / max(cierre_total_ticket, 1.01)) - 1.0) * 100.0, 2)

    deps_usados = list(dict.fromkeys([d for d in [dep1, dep2, dep3] if d != "-"]))
    deporte_principal_str = deps_usados[0] if len(deps_usados) == 1 else "🔀 Mixto (" + " + ".join([d.split()[1] for d in deps_usados]) + ")"

    st.caption(f"📊 **Resumen Previo:** Fecha: **`{fecha_ticket_reg}`** | Disciplina: **`{deporte_principal_str}`** | Cuota Total: **`{cuota_total_ticket:.2f}`** | CLV: **`{clv_ticket:+.2f}%`** | Ganancia Potencial: **`+${stake_reg * (cuota_total_ticket - 1.0):.2f}`**")

    if st.button("💾 Guardar Apuesta en Bitácora", type="primary"):
        if "✅" in estado_reg:
            retorno_val = round(stake_reg * cuota_total_ticket, 2)
            neto_val = round(retorno_val - stake_reg, 2)
            co_val = 0.0
        elif "💰" in estado_reg:
            retorno_val = round(monto_cashout_reg, 2)
            neto_val = round(retorno_val - stake_reg, 2)
            co_val = round(monto_cashout_reg, 2)
        elif "❌" in estado_reg:
            retorno_val = 0.0
            neto_val = round(-stake_reg, 2)
            co_val = 0.0
        else:
            retorno_val = 0.0
            neto_val = 0.0
            co_val = 0.0

        nueva_fila = pd.DataFrame([{
            "ID": len(df_bit) + 1,
            "Fecha": fecha_ticket_reg.strftime("%Y-%m-%d"),
            "Tipo Ticket": tipo_apuesta_reg,
            "Deporte Principal": deporte_principal_str,
            "Partido 1": part1,
            "Mercado 1": merc1,
            "Cuota 1": cuota1_val,
            "Partido 2": part2,
            "Mercado 2": merc2,
            "Cuota 2": cuota2_val if cuota2_val > 1.0 else np.nan,
            "Partido 3": part3,
            "Mercado 3": merc3,
            "Cuota 3": cuota3_val if cuota3_val > 1.0 else np.nan,
            "Cuota Total": cuota_total_ticket,
            "Cuota Cierre": cierre_total_ticket,
            "CLV (%)": clv_ticket,
            "Stake ($)": stake_reg,
            "Estado": estado_reg,
            "Monto Cash Out ($)": co_val,
            "Retorno ($)": retorno_val,
            "Beneficio Neto ($)": neto_val
        }])
        st.session_state["bitacora_apuestas"] = pd.concat([df_bit, nueva_fila], ignore_index=True)
        st.success("✅ Ticket registrado correctamente en tu Bitácora.")

    df_bit_act = st.session_state["bitacora_apuestas"]
    if not df_bit_act.empty:
        st.markdown("---")
        pendientes_df = df_bit_act[df_bit_act["Estado"] == "⏳ Pendiente"]
        if not pendientes_df.empty:
            st.markdown("**⏱️ Cerrar / Liquidar Ticket Pendiente (Ganada, Perdida o Cash Out):**")
            u_c1, u_c2, u_c3, u_c4 = st.columns([2.0, 1.1, 1.0, 0.9])
            opciones_pend = [f"ID #{int(r['ID'])} | [{r['Fecha']}] {r['Partido 1']} - Stake ${r['Stake ($)']}" for _, r in pendientes_df.iterrows()]
            ticket_upd_sel = u_c1.selectbox("Selecciona Ticket Pendiente", opciones_pend, key="sel_upd_pend")
            nuevo_estado_upd = u_c2.selectbox("Resultado Final", ["✅ Ganada", "❌ Perdida", "💰 Cash Out"], key="est_upd_pend")
            monto_co_upd = u_c3.number_input(
                "Monto Cash Out ($)",
                min_value=0.0, max_value=1000000.0, value=0.0, step=0.50,
                disabled=("Cash Out" not in nuevo_estado_upd),
                key="co_upd_pend"
            )
            if u_c4.button("✅ Liquidar", key="btn_upd_pend"):
                id_target = int(ticket_upd_sel.split("|")[0].replace("ID #", "").strip())
                idx_row = df_bit_act[df_bit_act["ID"] == id_target].index[0]
                stk = float(df_bit_act.at[idx_row, "Stake ($)"])
                cuo = float(df_bit_act.at[idx_row, "Cuota Total"])
                df_bit_act.at[idx_row, "Estado"] = nuevo_estado_upd
                if "✅" in nuevo_estado_upd:
                    df_bit_act.at[idx_row, "Monto Cash Out ($)"] = 0.0
                    df_bit_act.at[idx_row, "Retorno ($)"] = round(stk * cuo, 2)
                    df_bit_act.at[idx_row, "Beneficio Neto ($)"] = round((stk * cuo) - stk, 2)
                elif "💰" in nuevo_estado_upd:
                    df_bit_act.at[idx_row, "Monto Cash Out ($)"] = round(monto_co_upd, 2)
                    df_bit_act.at[idx_row, "Retorno ($)"] = round(monto_co_upd, 2)
                    df_bit_act.at[idx_row, "Beneficio Neto ($)"] = round(monto_co_upd - stk, 2)
                else:
                    df_bit_act.at[idx_row, "Monto Cash Out ($)"] = 0.0
                    df_bit_act.at[idx_row, "Retorno ($)"] = 0.0
                    df_bit_act.at[idx_row, "Beneficio Neto ($)"] = round(-stk, 2)
                st.session_state["bitacora_apuestas"] = df_bit_act
                st.rerun()

        cerradas = df_bit_act[df_bit_act["Estado"].isin(["✅ Ganada", "❌ Perdida", "💰 Cash Out"])].copy()
        total_apostado = float(cerradas["Stake ($)"].sum()) if not cerradas.empty else 0.0
        beneficio_total = float(cerradas["Beneficio Neto ($)"].sum()) if not cerradas.empty else 0.0
        yield_pct = (beneficio_total / total_apostado * 100.0) if total_apostado > 0 else 0.0
        positivas_cnt = int(((cerradas["Estado"] == "✅ Ganada") | ((cerradas["Estado"] == "💰 Cash Out") & (cerradas["Beneficio Neto ($)"] > 0))).sum()) if not cerradas.empty else 0
        win_rate = (positivas_cnt / len(cerradas) * 100.0) if len(cerradas) > 0 else 0.0
        clv_medio = float(df_bit_act["CLV (%)"].mean())

        bm1, bm2, bm3, bm4 = st.columns(4)
        bm1.metric("💵 Beneficio Neto Global", f"${beneficio_total:+.2f}", f"Banca Actualizada: ${banca_usuario + beneficio_total:.2f}")
        bm2.metric("📈 Yield / ROI Global (%)", f"{yield_pct:+.2f}%", f"Volumen Cerrado: ${total_apostado:.2f}")
        bm3.metric("🎯 Tickets en Verde (%)", f"{win_rate:.1f}%", f"{positivas_cnt}/{len(cerradas)} tickets positivos")
        bm4.metric("⚡ CLV Promedio", f"{clv_medio:+.2f}%", "Ventaja vs cierre Betano")

        if not cerradas.empty:
            st.markdown("### 📈 Evolución Temporal de Rendimiento (Por Día, Semana y Mes)")
            cerradas["Fecha_dt"] = pd.to_datetime(cerradas["Fecha"], errors="coerce")
            cerradas = cerradas.dropna(subset=["Fecha_dt"]).sort_values("Fecha_dt")

            granularidad = st.radio(
                "Selecciona la vista temporal:",
                ["📅 Por Día", "📆 Por Semana", "🗓️ Por Mes"],
                horizontal=True,
                key="rad_gran_bit"
            )
            if "Día" in granularidad:
                cerradas["Período"] = cerradas["Fecha_dt"].dt.strftime("%Y-%m-%d")
            elif "Semana" in granularidad:
                cerradas["Período"] = cerradas["Fecha_dt"].dt.to_period("W").apply(lambda p: f"Sem {p.start_time.strftime('%Y-%m-%d')}")
            else:
                cerradas["Período"] = cerradas["Fecha_dt"].dt.strftime("%Y-%m")

            df_temp = cerradas.groupby("Período", sort=True).agg(
                Tickets=("ID", "count"),
                Positivos=("Beneficio Neto ($)", lambda x: int((x > 0).sum())),
                Invertido=("Stake ($)", "sum"),
                Retorno=("Retorno ($)", "sum"),
                Beneficio_Neto=("Beneficio Neto ($)", "sum")
            ).reset_index()

            df_temp["Acierto (%)"] = (df_temp["Positivos"] / df_temp["Tickets"] * 100.0).round(1)
            df_temp["Yield (%)"] = (df_temp["Beneficio_Neto"] / df_temp["Invertido"].replace(0, np.nan) * 100.0).fillna(0.0).round(2)
            df_temp["Beneficio Acumulado ($)"] = df_temp["Beneficio_Neto"].cumsum().round(2)
            df_temp["Banca Evolución ($)"] = (banca_usuario + df_temp["Beneficio Acumulado ($)"]).round(2)
            df_temp["Invertido ($)"] = df_temp["Invertido"].round(2)
            df_temp["Retorno ($)"] = df_temp["Retorno"].round(2)
            df_temp["Beneficio Neto ($)"] = df_temp["Beneficio_Neto"].round(2)
            df_temp["Veredicto"] = df_temp["Beneficio Neto ($)"].apply(lambda v: "✅ POSITIVO" if v > 0 else ("⚠️ Negativo" if v < 0 else "Neutro"))

            g_col1, g_col2 = st.columns(2)
            with g_col1:
                st.markdown(f"**📊 Beneficio Neto por Período ({granularidad}):**")
                st.bar_chart(df_temp.set_index("Período")["Beneficio Neto ($)"], color="#ff6b00", height=260)
            with g_col2:
                st.markdown(f"**📈 Curva de Evolución de Banca ({granularidad}):**")
                st.line_chart(df_temp.set_index("Período")["Banca Evolución ($)"], color="#22c55e", height=260)

            cols_temp_ver = ["Período", "Tickets", "Positivos", "Acierto (%)", "Invertido ($)", "Retorno ($)", "Beneficio Neto ($)", "Yield (%)", "Banca Evolución ($)", "Veredicto"]
            st.dataframe(df_temp[cols_temp_ver].style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

            st.markdown("### 📊 Rentabilidad Acumulada por Mercado y por Deporte")
            res_mercados = cerradas.groupby("Mercado 1").agg(
                Tickets=("ID", "count"),
                Positivos=("Beneficio Neto ($)", lambda x: int((x > 0).sum())),
                Invertido_USD=("Stake ($)", "sum"),
                Beneficio_USD=("Beneficio Neto ($)", "sum"),
                CLV_Prom=("CLV (%)", "mean")
            ).reset_index()
            res_mercados["Acierto (%)"] = (res_mercados["Positivos"] / res_mercados["Tickets"] * 100.0).round(1)
            res_mercados["Yield / ROI (%)"] = (res_mercados["Beneficio_USD"] / res_mercados["Invertido_USD"].replace(0, np.nan) * 100.0).fillna(0.0).round(2)
            res_mercados["Invertido ($)"] = res_mercados["Invertido_USD"].round(2)
            res_mercados["Beneficio Neto ($)"] = res_mercados["Beneficio_USD"].round(2)
            res_mercados["CLV (%)"] = res_mercados["CLV_Prom"].round(2)
            res_mercados["Veredicto"] = res_mercados["Beneficio Neto ($)"].apply(lambda v: "✅ RENTABLE (+EV)" if v > 0 else ("⚠️ En Ajuste" if v < 0 else "Neutro"))
            res_mercados = res_mercados.sort_values(by=["Beneficio Neto ($)", "Yield / ROI (%)"], ascending=False)

            mejor_merc = res_mercados.iloc[0]
            if mejor_merc["Beneficio Neto ($)"] > 0:
                st.success(f"🏆 **Tu Mercado Más Rentable:** `{mejor_merc['Mercado 1']}` con **`+${mejor_merc['Beneficio Neto ($)']:.2f}`** netos (**Yield: `{mejor_merc['Yield / ROI (%)']:+.2f}%`** | Acierto: **`{mejor_merc['Acierto (%)']}%`**).")

            cols_merc_ver = ["Mercado 1", "Tickets", "Positivos", "Acierto (%)", "Invertido ($)", "Beneficio Neto ($)", "Yield / ROI (%)", "CLV (%)", "Veredicto"]
            st.dataframe(res_mercados[cols_merc_ver].rename(columns={"Mercado 1": "Mercado Operado"}).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

            res_dep = cerradas.groupby("Deporte Principal").agg(
                Tickets=("ID", "count"),
                Positivos=("Beneficio Neto ($)", lambda x: int((x > 0).sum())),
                Invertido_USD=("Stake ($)", "sum"),
                Beneficio_USD=("Beneficio Neto ($)", "sum")
            ).reset_index()
            res_dep["Acierto (%)"] = (res_dep["Positivos"] / res_dep["Tickets"] * 100.0).round(1)
            res_dep["Yield / ROI (%)"] = (res_dep["Beneficio_USD"] / res_dep["Invertido_USD"].replace(0, np.nan) * 100.0).fillna(0.0).round(2)
            res_dep["Invertido ($)"] = res_dep["Invertido_USD"].round(2)
            res_dep["Beneficio Neto ($)"] = res_dep["Beneficio_USD"].round(2)
            res_dep["Veredicto"] = res_dep["Beneficio Neto ($)"].apply(lambda v: "✅ RENTABLE (+EV)" if v > 0 else "⚠️ En Ajuste")
            st.markdown("**🏅 Rendimiento por Disciplina Deportiva:**")
            st.dataframe(res_dep[["Deporte Principal", "Tickets", "Positivos", "Acierto (%)", "Invertido ($)", "Beneficio Neto ($)", "Yield / ROI (%)", "Veredicto"]].style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

        st.markdown("**📋 Historial Completo de Tickets Registrados:**")
        st.dataframe(df_bit_act, use_container_width=True, hide_index=True)
        csv_export = df_bit_act.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar Bitácora Completa en CSV / Excel", data=csv_export, file_name="bitacora_pro_bet_analyzer.csv", mime="text/csv")

# ==============================================================================
# 1. MÓDULO FÚTBOL (CALIBRACIÓN BAYESIANA UNIVERSAL + SOS ACOTADO + UEFA REAL)
# ==============================================================================
if deporte_activo.startswith("⚽"):
    st.sidebar.markdown("### 🏆 1. Competición y Equipos")
    cod_temp_act = obtener_codigo_temporada_dinamico()
    LIGAS_FUT = {
        "🏆 UEFA Champions League": "UEFA_CHAMPIONS",
        "🥈 UEFA Europa League": "UEFA_EUROPA",
        "🥉 UEFA Conference League": "UEFA_CONFERENCE",
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)": f"https://www.football-data.co.uk/mmz4281/{cod_temp_act}/E0.csv",
        "🇪🇸 LaLiga (España)": f"https://www.football-data.co.uk/mmz4281/{cod_temp_act}/SP1.csv",
        "🇮🇹 Serie A (Italia)": f"https://www.football-data.co.uk/mmz4281/{cod_temp_act}/I1.csv",
        "🇩🇪 Bundesliga (Alemania)": f"https://www.football-data.co.uk/mmz4281/{cod_temp_act}/D1.csv",
        "🇫🇷 Ligue 1 (Francia)": f"https://www.football-data.co.uk/mmz4281/{cod_temp_act}/F1.csv",
        "🇳🇱 Eredivisie (Países Bajos)": f"https://www.football-data.co.uk/mmz4281/{cod_temp_act}/N1.csv",
        "🇵🇹 Primeira Liga (Portugal)": f"https://www.football-data.co.uk/mmz4281/{cod_temp_act}/P1.csv",
        "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Premiership (Escocia)": f"https://www.football-data.co.uk/mmz4281/{cod_temp_act}/SC0.csv",
        "🇧🇪 Jupiler Pro League (Bélgica)": f"https://www.football-data.co.uk/mmz4281/{cod_temp_act}/B1.csv",
        "🇹🇷 Süper Lig (Turquía)": f"https://www.football-data.co.uk/mmz4281/{cod_temp_act}/T1.csv",
        "🌍 UEFA Nations League (Selecciones UEFA)": "NATIONS_LEAGUE",
        "🇺🇸 MLS (Estados Unidos)": "https://www.football-data.co.uk/new/USA.csv",
        "🇧🇷 Brasileirão Serie A (Brasil)": "https://www.football-data.co.uk/new/BRA.csv",
        "🇦🇷 Liga Profesional (Argentina)": "https://www.football-data.co.uk/new/ARG.csv",
        "🇲🇽 Liga MX (México)": "https://www.football-data.co.uk/new/MEX.csv"
    }
    liga_sel = st.sidebar.selectbox("Selecciona la Liga / Torneo:", list(LIGAS_FUT.keys()))

    @st.cache_data(ttl=1800)
    def cargar_datos_futbol_real(codigo_o_url):
        if codigo_o_url == "NATIONS_LEAGUE":
            df_nl = cargar_datos_nations_league()
            eqs_nl = sorted(list(set(df_nl['HomeTeam'].unique()).union(set(df_nl['AwayTeam'].unique())))) if not df_nl.empty else []
            return df_nl, eqs_nl
        if codigo_o_url == "UEFA_CHAMPIONS":
            return cargar_datos_uefa_clubes_espn("uefa.champions")
        if codigo_o_url == "UEFA_EUROPA":
            return cargar_datos_uefa_clubes_espn("uefa.europa")
        if codigo_o_url == "UEFA_CONFERENCE":
            return cargar_datos_uefa_clubes_espn("uefa.europa.conf")

        try:
            resp = requests.get(codigo_o_url, headers=HEADERS_HTTP, timeout=10)
            df = pd.read_csv(io.StringIO(resp.text))
            if 'Home' in df.columns:
                df = df.rename(columns={'Home': 'HomeTeam', 'Away': 'AwayTeam', 'HG': 'FTHG', 'AG': 'FTAG'})
            df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
            if len(df) < 5 and "/2627/" in codigo_o_url:
                resp_b = requests.get(codigo_o_url.replace("/2627/", "/2526/"), headers=HEADERS_HTTP, timeout=10)
                df = pd.read_csv(io.StringIO(resp_b.text)).dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
            eqs_activos = sorted(list(set(df['HomeTeam'].unique()).union(set(df['AwayTeam'].unique()))))
            return df, eqs_activos
        except Exception:
            return pd.DataFrame(), []

    with st.spinner(f"Cargando telemetría oficial de {liga_sel}..."):
        df_csv, equipos_fut = cargar_datos_futbol_real(LIGAS_FUT[liga_sel])

    if df_csv.empty and not equipos_fut:
        st.error("No se pudo conectar al servidor de datos en este momento.")
        st.stop()

    df_tabla_pos, mapa_puestos_liga = calcular_tabla_posiciones_csv(df_csv)
    total_eq_liga = max(len(df_tabla_pos), 18)

    c1, c2 = st.sidebar.columns(2)
    eq_l = c1.selectbox("🏠 Local", equipos_fut, index=0)
    eq_v = c2.selectbox("✈️ Visita", equipos_fut, index=1 if len(equipos_fut) > 1 else 0)

    info_pos_l = mapa_puestos_liga.get(eq_l, {"pos": 10, "pts": 0, "pj": 0, "dg": 0})
    info_pos_v = mapa_puestos_liga.get(eq_v, {"pos": 10, "pts": 0, "pj": 0, "dg": 0})

    col_opt1, col_opt2 = st.sidebar.columns(2)
    # Activado por defecto en TODAS las ligas para calibrar muestras < 6 partidos
    usar_amortiguador = col_opt1.checkbox("🛡️ Bayes (< 6 PJ)", value=True)
    usar_sos = col_opt2.checkbox("⚖️ Fuerza Rival (SoS)", value=True)
    col_opt3, col_opt4 = st.sidebar.columns(2)
    usar_dc = col_opt3.checkbox("📐 Dixon-Coles", value=True)
    usar_blowout = col_opt4.checkbox("🛡️ Anti-Goleada Córners", value=True)

    espn_sp, espn_lg = ESPN_LEAGUE_MAP.get(liga_sel, ("soccer", "eng.1"))
    _, mapa_logos_fut = obtener_catalogo_equipos_y_logos_espn(espn_sp, espn_lg)
    logo_eq_l, fb_eq_l = buscar_logo_equipo(eq_l, mapa_logos_fut, "#ff6b00")
    logo_eq_v, fb_eq_v = buscar_logo_equipo(eq_v, mapa_logos_fut, "#38bdf8")

    media_tarj_base_liga = 4.0
    if 'HY' in df_csv.columns and 'AY' in df_csv.columns and not df_csv['HY'].dropna().empty:
        hr_all = df_csv['HR'].fillna(0) if 'HR' in df_csv.columns else 0
        ar_all = df_csv['AR'].fillna(0) if 'AR' in df_csv.columns else 0
        media_tarj_base_liga = max(float((df_csv['HY'] + df_csv['AY'] + hr_all + ar_all).dropna().mean()), 2.0)

    es_clasico, factor_clasico, etiqueta_clasico = evaluar_clasico_y_friccion_h2h(eq_l, eq_v, df_csv, media_tarj_base_liga)

    tiene_ref_csv = ('Referee' in df_csv.columns and 'HY' in df_csv.columns and not df_csv['Referee'].dropna().empty)
    mult_arbitro = 1.0
    info_arbitro_txt = "Estándar (1.00x)"
    df_refs_stats = pd.DataFrame()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟨 Rigurosidad Arbitral y Clásico")
    if es_clasico:
        st.sidebar.markdown(
            f'<div class="clasico-sidebar-box">'
            f'<div class="clasico-sidebar-title">⚡ Rivalidad Detectada</div>'
            f'<div class="clasico-sidebar-text">{etiqueta_clasico}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    if tiene_ref_csv:
        df_r_tmp = df_csv.dropna(subset=['Referee', 'HY', 'AY']).copy()
        df_r_tmp['HR_clean'] = df_r_tmp['HR'].fillna(0) if 'HR' in df_r_tmp.columns else 0
        df_r_tmp['AR_clean'] = df_r_tmp['AR'].fillna(0) if 'AR' in df_r_tmp.columns else 0
        df_r_tmp['Tot_Tarj'] = df_r_tmp['HY'] + df_r_tmp['AY'] + df_r_tmp['HR_clean'] + df_r_tmp['AR_clean']

        grp_ref = df_r_tmp.groupby('Referee').agg(
            Partidos=('Tot_Tarj', 'count'),
            Prom_Amarillas=('HY', lambda x: round((x.sum() + df_r_tmp.loc[x.index, 'AY'].sum()) / len(x), 2)),
            Prom_Rojas=('HR_clean', lambda x: round((x.sum() + df_r_tmp.loc[x.index, 'AR_clean'].sum()) / len(x), 2)),
            Prom_Total_Tarjetas=('Tot_Tarj', lambda x: round(x.mean(), 2))
        ).reset_index()
        grp_ref['Índice Rigor'] = (grp_ref['Prom_Total_Tarjetas'] / media_tarj_base_liga).round(2)
        df_refs_stats = grp_ref.sort_values('Partidos', ascending=False)

        lista_arbitros = ["Promedio Liga (Auto / Sin Asignar)"] + sorted(df_refs_stats['Referee'].tolist())
        arb_espn = detectar_arbitro_asignado_espn(espn_sp, espn_lg, eq_l, eq_v)
        idx_arb = 0
        if arb_espn:
            for i_a, nom_a in enumerate(lista_arbitros):
                if arb_espn.split()[-1].lower() in nom_a.lower():
                    idx_arb = i_a
                    break

        arb_sel = st.sidebar.selectbox("Árbitro Central (Historial CSV):", lista_arbitros, index=idx_arb)
        if arb_sel != "Promedio Liga (Auto / Sin Asignar)":
            fila_a = df_refs_stats[df_refs_stats['Referee'] == arb_sel].iloc[0]
            mult_arbitro = float(np.clip(fila_a['Índice Rigor'], 0.70, 1.40))
            info_arbitro_txt = f"{arb_sel} ({mult_arbitro:.2f}x)"
            st.sidebar.caption(f"📋 **{arb_sel}:** `{fila_a['Prom_Amarillas']}` amarillas y `{fila_a['Prom_Rojas']}` rojas/PJ en `{int(fila_a['Partidos'])}` juegos.")
    else:
        contexto_arb = st.sidebar.selectbox(
            "Perfil Arbitral Adicional:",
            ["Estándar (1.00x)", "Árbitro Permisivo (-15%)", "Árbitro Tarjetero (+15%)"]
        )
        if "Permisivo" in contexto_arb:
            mult_arbitro, info_arbitro_txt = 0.85, "Permisivo (0.85x)"
        elif "Tarjetero" in contexto_arb:
            mult_arbitro, info_arbitro_txt = 1.15, "Tarjetero (1.15x)"

    mult_disciplina_total = round(mult_arbitro * factor_clasico, 3)

    mult_bajas_l, mult_bajas_v, pct_baja_l, pct_baja_v = renderizar_panel_bajas_y_factor(espn_sp, espn_lg, eq_l, eq_v, f"fut_{eq_l}_{eq_v}")

    p_l = df_csv[df_csv['HomeTeam'] == eq_l].tail(5).copy() if not df_csv.empty else pd.DataFrame()
    p_v = df_csv[df_csv['AwayTeam'] == eq_v].tail(5).copy() if not df_csv.empty else pd.DataFrame()

    media_gf_liga_home = float(df_csv['FTHG'].mean()) if not df_csv.empty else 1.48
    media_gc_liga_home = float(df_csv['FTAG'].mean()) if not df_csv.empty else 1.22
    media_gf_liga_away = media_gc_liga_home
    media_gc_liga_away = media_gf_liga_home
    media_liga = max((media_gf_liga_home + media_gc_liga_home) / 2.0, 1.25)

    # Fuerza Rival (SoS) ACOTADA entre 0.78x y 1.28x para evitar explosiones en muestras cortas
    if usar_sos and not p_l.empty and not p_v.empty:
        ataque_liga = df_csv.groupby('HomeTeam')['FTHG'].mean().to_dict()
        defensa_liga = df_csv.groupby('AwayTeam')['FTHG'].mean().to_dict()

        gf_l_adj, gc_l_adj = [], []
        for _, r in p_l.iterrows():
            riv = r['AwayTeam']
            def_riv = max(defensa_liga.get(riv, media_gf_liga_home), 0.5)
            ata_riv = max(ataque_liga.get(riv, media_gc_liga_home), 0.5)
            mult_def_l = float(np.clip(media_gf_liga_home / def_riv, 0.78, 1.28))
            mult_ata_l = float(np.clip(media_gc_liga_home / ata_riv, 0.78, 1.28))
            gf_l_adj.append(float(r['FTHG']) * mult_def_l)
            gc_l_adj.append(float(r['FTAG']) * mult_ata_l)

        gf_v_adj, gc_v_adj = [], []
        for _, r in p_v.iterrows():
            riv = r['HomeTeam']
            def_riv = max(defensa_liga.get(riv, media_gf_liga_away), 0.5)
            ata_riv = max(ataque_liga.get(riv, media_gc_liga_away), 0.5)
            mult_def_v = float(np.clip(media_gf_liga_away / def_riv, 0.78, 1.28))
            mult_ata_v = float(np.clip(media_gc_liga_away / ata_riv, 0.78, 1.28))
            gf_v_adj.append(float(r['FTAG']) * mult_def_v)
            gc_v_adj.append(float(r['FTHG']) * mult_ata_v)

        gf_l_puro = float(np.mean(gf_l_adj))
        gc_l_puro = float(np.mean(gc_l_adj))
        gf_v_puro = float(np.mean(gf_v_adj))
        gc_v_puro = float(np.mean(gc_v_adj))
    else:
        gf_l_puro = float(p_l['FTHG'].mean()) if not p_l.empty else 1.45
        gc_l_puro = float(p_l['FTAG'].mean()) if not p_l.empty else 1.20
        gf_v_puro = float(p_v['FTAG'].mean()) if not p_v.empty else 1.20
        gc_v_puro = float(p_v['FTHG'].mean()) if not p_v.empty else 1.40

    pj_l, pj_v = len(p_l), len(p_v)
    peso_l = min(pj_l / 6.0, 1.0) if usar_amortiguador else 1.0
    peso_v = min(pj_v / 6.0, 1.0) if usar_amortiguador else 1.0

    gf_l = (peso_l * gf_l_puro) + ((1.0 - peso_l) * media_gf_liga_home)
    gc_l = (peso_l * gc_l_puro) + ((1.0 - peso_l) * media_gc_liga_home)
    gf_v = (peso_v * gf_v_puro) + ((1.0 - peso_v) * media_gf_liga_away)
    gc_v = (peso_v * gc_v_puro) + ((1.0 - peso_v) * media_gc_liga_away)

    gf_l = gf_l * mult_bajas_l
    gf_v = gf_v * mult_bajas_v

    lam_loc = max((gf_l * gc_v) / media_liga, 0.15)
    lam_vis = max((gf_v * gc_l) / media_liga, 0.12)
    mat_raw = np.zeros((9, 9))
    for i in range(9):
        for j in range(9):
            mat_raw[i, j] = poisson.pmf(i, lam_loc) * poisson.pmf(j, lam_vis)

    mat = aplicar_dixon_coles(mat_raw, lam_loc, lam_vis, rho=-0.11) if usar_dc else mat_raw

    hay_riesgo_goleada, factor_blowout_cor, prob_goleada_val, msg_goleada = evaluar_riesgo_goleada_corners(
        mat, info_pos_l["pos"], info_pos_v["pos"], total_eq_liga
    )
    if not usar_blowout:
        factor_blowout_cor = 1.00

    tiene_tiros_csv = ('HS' in df_csv.columns and not p_l.empty and not p_v.empty and not p_l['HS'].dropna().empty and not p_v['AS'].dropna().empty)
    tiene_tarjetas_csv = ('HY' in df_csv.columns and not p_l.empty and not p_v.empty and not p_l['HY'].dropna().empty and not p_v['AY'].dropna().empty)

    # Medias reales de la competición para Amortiguador Bayesiano en Tiros, Arco y Córners
    media_hs_liga = float(df_csv['HS'].dropna().mean()) if ('HS' in df_csv.columns and not df_csv['HS'].dropna().empty) else 13.0
    media_as_liga = float(df_csv['AS'].dropna().mean()) if ('AS' in df_csv.columns and not df_csv['AS'].dropna().empty) else 11.2
    media_hst_liga = float(df_csv['HST'].dropna().mean()) if ('HST' in df_csv.columns and not df_csv['HST'].dropna().empty) else 4.6
    media_ast_liga = float(df_csv['AST'].dropna().mean()) if ('AST' in df_csv.columns and not df_csv['AST'].dropna().empty) else 3.9
    media_hc_liga = float(df_csv['HC'].dropna().mean()) if ('HC' in df_csv.columns and not df_csv['HC'].dropna().empty) else 5.2
    media_ac_liga = float(df_csv['AC'].dropna().mean()) if ('AC' in df_csv.columns and not df_csv['AC'].dropna().empty) else 4.4

    sh_l_puro = float(p_l['HS'].dropna().mean()) if tiene_tiros_csv else round(9.5 + gf_l * 2.4, 1)
    sh_v_puro = float(p_v['AS'].dropna().mean()) if tiene_tiros_csv else round(8.5 + gf_v * 2.3, 1)
    sh_l = ((peso_l * sh_l_puro) + ((1.0 - peso_l) * media_hs_liga)) * (0.5 + 0.5 * mult_bajas_l)
    sh_v = ((peso_v * sh_v_puro) + ((1.0 - peso_v) * media_as_liga)) * (0.5 + 0.5 * mult_bajas_v)

    sot_l_puro = float(p_l['HST'].dropna().mean()) if tiene_tiros_csv else round(2.6 + gf_l * 1.25, 1)
    sot_v_puro = float(p_v['AST'].dropna().mean()) if tiene_tiros_csv else round(2.2 + gf_v * 1.2, 1)
    sot_l = ((peso_l * sot_l_puro) + ((1.0 - peso_l) * media_hst_liga)) * (0.5 + 0.5 * mult_bajas_l)
    sot_v = ((peso_v * sot_v_puro) + ((1.0 - peso_v) * media_ast_liga)) * (0.5 + 0.5 * mult_bajas_v)

    cor_l_puro = float(p_l['HC'].dropna().mean()) if tiene_tiros_csv else round(3.8 + gf_l * 0.68, 1)
    cor_v_puro = float(p_v['AC'].dropna().mean()) if tiene_tiros_csv else round(3.4 + gf_v * 0.62, 1)
    cor_l_raw = (peso_l * cor_l_puro) + ((1.0 - peso_l) * media_hc_liga)
    cor_v_raw = (peso_v * cor_v_puro) + ((1.0 - peso_v) * media_ac_liga)

    cor_l = cor_l_raw * factor_blowout_cor
    cor_v = cor_v_raw * factor_blowout_cor
    lam_cor_1t = (cor_l_raw + cor_v_raw) * 0.48

    if tiene_tarjetas_csv:
        hy_l_puro = float(p_l['HY'].fillna(0).mean())
        hr_l_puro = float(p_l['HR'].fillna(0).mean()) if 'HR' in p_l.columns else 0.0
        ay_v_puro = float(p_v['AY'].fillna(0).mean())
        ar_v_puro = float(p_v['AR'].fillna(0).mean()) if 'AR' in p_v.columns else 0.0
        hy_l = (peso_l * hy_l_puro) + ((1.0 - peso_l) * (media_tarj_base_liga * 0.46))
        ay_v = (peso_v * ay_v_puro) + ((1.0 - peso_v) * (media_tarj_base_liga * 0.52))
        hr_l = peso_l * hr_l_puro
        ar_v = peso_v * ar_v_puro
        tarj_tot_esp = round((hy_l + hr_l + ay_v + ar_v) * mult_disciplina_total, 2)
        pts_tarj_esp = round((hy_l + (2.0 * hr_l) + ay_v + (2.0 * ar_v)) * mult_disciplina_total, 2)
    else:
        hy_l, hr_l, ay_v, ar_v = 2.0, 0.1, 2.2, 0.1
        tarj_tot_esp = round(4.40 * mult_disciplina_total, 2)
        pts_tarj_esp = round(4.60 * mult_disciplina_total, 2)

    prob_1 = float(np.sum(np.tril(mat, -1)))
    prob_x = float(np.sum(np.diag(mat)))
    prob_2 = float(np.sum(np.triu(mat, 1)))
    prob_u25 = float(mat[0,0]+mat[1,0]+mat[0,1]+mat[2,0]+mat[0,2]+mat[1,1])
    prob_o25 = 1.0 - prob_u25
    prob_btts_no = float(np.sum(mat[0, :]) + np.sum(mat[:, 0]) - mat[0, 0])
    prob_btts_si = 1.0 - prob_btts_no

    badge_hero = etiqueta_clasico if es_clasico else (f"⚠️ Brecha Tabla #{info_pos_l['pos']} vs #{info_pos_v['pos']} (Riesgo Goleada {prob_goleada_val*100:.0f}%)" if hay_riesgo_goleada else "")

    renderizar_hero_card_deporte(
        eq_l, eq_v, logo_eq_l, fb_eq_l, logo_eq_v, fb_eq_v,
        liga_sel, f"{lam_loc:.2f}  —  {lam_vis:.2f}",
        f"Goles Esp. (xG): {lam_loc+lam_vis:.2f} • Bayes: {'ON' if usar_amortiguador else 'OFF'} • Dixon-Coles: {'ON' if usar_dc else 'OFF'}",
        prob_1, prob_x, prob_2, pct_baja_l, pct_baja_v,
        badge_extra=badge_hero,
        sub_loc=f"🏠 LOCAL • Puesto #{info_pos_l['pos']} ({info_pos_l['pts']} pts)",
        sub_vis=f"✈️ VISITA • Puesto #{info_pos_v['pos']} ({info_pos_v['pts']} pts)"
    )

    TRADUCCION_COLS_FUTBOL = {
        "Date": "Fecha", "Tournament": "Torneo", "Referee": "Árbitro", "HomeTeam": "Equipo Local", "AwayTeam": "Equipo Visita",
        "FTHG": "Goles Local (A Favor)", "FTAG": "Goles Visita (En Contra)",
        "HS": "Tiros Totales Local", "HST": "Tiros al Arco Local", "HC": "Córners Local",
        "HY": "Amarillas Local", "HR": "Rojas Local",
        "AS": "Tiros Totales Visita", "AST": "Tiros al Arco Visita", "AC": "Córners Visita",
        "AY": "Amarillas Visita", "AR": "Rojas Visita"
    }

    with st.expander(f"📋 TABLA DE AUDITORÍA: Clasificación, Partidos Reales, Árbitros y Córners ({eq_l} #{info_pos_l['pos']} vs {eq_v} #{info_pos_v['pos']})", expanded=False):
        if es_clasico:
            st.warning(f"Alerta de Rivalidad Detectada: {etiqueta_clasico} — El modelo multiplica automáticamente las tarjetas esperadas por {factor_clasico:.2f}x.")
        if hay_riesgo_goleada:
            st.warning(msg_goleada)
        if tiene_tiros_csv and tiene_tarjetas_csv:
            st.success(f"✅ Telemetría Completa Opta / ESPN: Goles, Tiros Totales, Tiros al Arco, Córners, Amarillas y Rojas 100% reales (Muestra: {pj_l} PJ Local + {pj_v} PJ Visita).")
        else:
            st.warning("⚠️ Liga de América / Selecciones: El registro oficial público contiene Goles Reales verificados partido a partido, pero no incluye conteos de Tiros ni Tarjetas.")

        if not p_l.empty:
            cols_l = [c for c in ['Date', 'Referee', 'Tournament', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HS', 'HST', 'HC', 'HY', 'HR'] if c in p_l.columns]
            st.markdown(f"**🏠 Últimos {len(p_l)} partidos de {eq_l} como LOCAL (Puesto #{info_pos_l['pos']}):**")
            st.dataframe(p_l[cols_l].rename(columns=TRADUCCION_COLS_FUTBOL), use_container_width=True, hide_index=True)

        if not p_v.empty:
            trad_vis = dict(TRADUCCION_COLS_FUTBOL)
            trad_vis["FTHG"] = "Goles Local (En Contra)"
            trad_vis["FTAG"] = "Goles Visita (A Favor)"
            cols_v = [c for c in ['Date', 'Referee', 'Tournament', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'AS', 'AST', 'AC', 'AY', 'AR'] if c in p_v.columns]
            st.markdown(f"**✈️ Últimos {len(p_v)} partidos de {eq_v} como VISITANTE (Puesto #{info_pos_v['pos']}):**")
            st.dataframe(p_v[cols_v].rename(columns=trad_vis), use_container_width=True, hide_index=True)

        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            if not df_tabla_pos.empty:
                st.markdown("**🏆 Tabla de Posiciones Reconstruida del Torneo:**")
                st.dataframe(df_tabla_pos, use_container_width=True, hide_index=True)
        with c_sub2:
            if not df_refs_stats.empty:
                st.markdown("**🟨 Rigurosidad Arbitral en la Liga (Datos Reales):**")
                st.dataframe(df_refs_stats.head(15), use_container_width=True, hide_index=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas en Betano (Goles & 1X2)")
    cb1, cb2, cb3 = st.sidebar.columns(3)
    cuota_1 = cb1.number_input("Local (1)", 1.01, 30.0, round(1/max(prob_1*1.05, 0.05), 2), 0.05)
    cuota_x = cb2.number_input("Empate (X)", 1.01, 30.0, round(1/max(prob_x*1.05, 0.05), 2), 0.05)
    cuota_2 = cb3.number_input("Visita (2)", 1.01, 30.0, round(1/max(prob_2*1.05, 0.05), 2), 0.05)

    cb4, cb5 = st.sidebar.columns(2)
    cuota_over25 = cb4.number_input("Over 2.5 Goles", 1.01, 20.0, 1.85, 0.05)
    cuota_under25 = cb5.number_input("Under 2.5 Goles", 1.01, 20.0, 1.95, 0.05)

    cb6, cb7 = st.sidebar.columns(2)
    cuota_btts_si = cb6.number_input("BTTS SÍ", 1.01, 20.0, 1.80, 0.05)
    cuota_btts_no = cb7.number_input("BTTS NO", 1.01, 20.0, 1.95, 0.05)

    with st.sidebar.expander("📏 Cuotas Tiros, Córners (FT/1T) y Tarjetas"):
        linea_remates = st.number_input("Línea Tiros Totales", 10.5, 40.5, 24.5, 1.0)
        cuota_over_rem = st.number_input("Cuota Over Tiros", 1.01, 15.0, 1.85, 0.05)
        linea_puerta = st.number_input("Línea Tiros al Arco", 3.5, 20.5, 8.5, 1.0)
        cuota_over_pue = st.number_input("Cuota Over al Arco", 1.01, 15.0, 1.85, 0.05)
        linea_corners = st.number_input("Línea Córners Totales (FT)", 4.5, 20.5, 8.5, 1.0)
        cuota_over_cor = st.number_input("Cuota Over Córners FT", 1.01, 15.0, 1.85, 0.05)
        linea_cor_1t = st.number_input("Línea Córners 1er Tiempo (1T)", 2.5, 8.5, 4.5, 1.0)
        cuota_over_cor_1t = st.number_input("Cuota Over Córners 1T", 1.01, 15.0, 1.90, 0.05)
        st.markdown("---")
        linea_tarjetas = st.number_input("🟨 Línea Tarjetas Totales", 1.5, 9.5, 4.5, 1.0)
        cuota_over_tarj = st.number_input("Cuota Over Tarjetas", 1.01, 15.0, 1.85, 0.05)
        cuota_under_tarj = st.number_input("Cuota Under Tarjetas", 1.01, 15.0, 1.90, 0.05)

    # Ensanchar dispersión (scale) cuando la muestra combinada es < 10 partidos para evitar sobreconfianza
    muestra_comb = min(pj_l + pj_v, 10)
    factor_incertidumbre = 1.0 + ((10 - muestra_comb) * 0.045)

    lam_rem = sh_l + sh_v
    p_ov_rem = float(1.0 - norm.cdf(linea_remates, loc=lam_rem, scale=5.2 * factor_incertidumbre))
    lam_pue = sot_l + sot_v
    p_ov_pue = float(1.0 - norm.cdf(linea_puerta, loc=lam_pue, scale=3.1 * factor_incertidumbre))
    lam_cor = cor_l + cor_v
    p_ov_cor = float(1.0 - norm.cdf(linea_corners, loc=lam_cor, scale=3.65 * factor_incertidumbre))
    p_ov_cor_1t = float(1.0 - norm.cdf(linea_cor_1t, loc=lam_cor_1t, scale=2.45 * factor_incertidumbre))
    p_ov_tarj = float(1.0 - sum(poisson.pmf(k, max(tarj_tot_esp, 0.5)) for k in range(int(linea_tarjetas) + 1)))
    p_un_tarj = 1.0 - p_ov_tarj

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("⚽ Goles Esp. (xG)", f"{lam_loc:.2f} - {lam_vis:.2f}", f"Total: {lam_loc+lam_vis:.2f}")
    k2.metric("🎯 Tiros Totales Esp.", f"{lam_rem:.1f} tiros", f"{sh_l:.1f} L + {sh_v:.1f} V")
    k3.metric("🥅 Tiros al Arco Esp.", f"{lam_pue:.1f} arco", f"{sot_l:.1f} L + {sot_v:.1f} V")
    k4.metric("⛳ Córners FT / 1T", f"{lam_cor:.1f} FT | {lam_cor_1t:.1f} 1T", "Anti-Goleada -14%" if (hay_riesgo_goleada and usar_blowout) else f"{cor_l:.1f} L + {cor_v:.1f} V")
    k5.metric("🟨 Tarjetas Esp.", f"{tarj_tot_esp:.1f} tarj.", f"Factor: {mult_disciplina_total:.2f}x {'(Clásico)' if es_clasico else ''}")

    CONFIG_BARRA_PROB = {"Prob. Real": st.column_config.ProgressColumn("Prob. Real (%)", format="%.1f%%", min_value=0, max_value=100)}

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 1. Goles y 1X2", "⛳ 2. Tiros y Córners (FT / 1T)", "🟨 3. Tarjetas (Árbitro/Clásico)",
        "🔢 4. Matriz Exacta", "🔴 5. Radar En Vivo"
    ])
    with tab1:
        m_g = [
            (f"Gana {eq_l} (1)", prob_1, cuota_1),
            ("Empate (X)", prob_x, cuota_x),
            (f"Gana {eq_v} (2)", prob_2, cuota_2),
            ("Más de 2.5 Goles (Over)", prob_o25, cuota_over25),
            ("Menos de 2.5 Goles (Under)", prob_u25, cuota_under25),
            ("Ambos Equipos Anotan - SÍ", prob_btts_si, cuota_btts_si),
            ("Ambos Equipos Anotan - NO", prob_btts_no, cuota_btts_no)
        ]
        df_t1 = construir_tabla_mercados_kelly(m_g, "Mercado", banca_usuario, fraccion_kelly_val, min_prob_filtro, min_edge_filtro)
        st.dataframe(df_t1.style.apply(resaltar_valor, axis=1), column_config=CONFIG_BARRA_PROB, use_container_width=True, hide_index=True)

    with tab2:
        if hay_riesgo_goleada and usar_blowout:
            st.warning(msg_goleada)
        m_e = [
            (f"⛳ 1er Tiempo: Más de {linea_cor_1t} Córners 1T (Over)", p_ov_cor_1t, cuota_over_cor_1t),
            (f"⛳ Partido Completo: Más de {linea_corners} Córners FT (Over)", p_ov_cor, cuota_over_cor),
            (f"⛳ Partido Completo: Menos de {linea_corners} Córners FT (Under)", 1.0 - p_ov_cor, 1.85),
            (f"🎯 Más de {linea_remates} Tiros Totales (Over)", p_ov_rem, cuota_over_rem),
            (f"🎯 Menos de {linea_remates} Tiros Totales (Under)", 1.0 - p_ov_rem, 1.85),
            (f"🥅 Más de {linea_puerta} Tiros al Arco (Over)", p_ov_pue, cuota_over_pue),
            (f"🥅 Menos de {linea_puerta} Tiros al Arco (Under)", 1.0 - p_ov_pue, 1.85)
        ]
        df_t2 = construir_tabla_mercados_kelly(m_e, "Mercado Especial", banca_usuario, fraccion_kelly_val, min_prob_filtro, min_edge_filtro)
        st.dataframe(df_t2.style.apply(resaltar_valor, axis=1), column_config=CONFIG_BARRA_PROB, use_container_width=True, hide_index=True)

    with tab3:
        if not tiene_tarjetas_csv:
            st.warning("⚠️ Esta competición no incluye columnas oficiales de tarjetas en el archivo. No se recomienda operar mercados de tarjetas aquí.")
        else:
            st.info(f"📊 Disciplina + Árbitro ({info_arbitro_txt}) + Rivalidad ({etiqueta_clasico}): {eq_l} ({hy_l:.1f} amarillas / {hr_l:.2f} rojas) + {eq_v} ({ay_v:.1f} amarillas / {ar_v:.2f} rojas) × {mult_disciplina_total:.2f}x = {tarj_tot_esp:.2f} tarjetas esperadas.")
            m_tarj = [
                (f"🟨 Más de {linea_tarjetas} Tarjetas Totales (Over)", p_ov_tarj, cuota_over_tarj),
                (f"🟨 Menos de {linea_tarjetas} Tarjetas Totales (Under)", p_un_tarj, cuota_under_tarj)
            ]
            df_t3 = construir_tabla_mercados_kelly(m_tarj, "Mercado de Tarjetas", banca_usuario, fraccion_kelly_val, min_prob_filtro, min_edge_filtro)
            st.dataframe(df_t3.style.apply(resaltar_valor, axis=1), column_config=CONFIG_BARRA_PROB, use_container_width=True, hide_index=True)

    with tab4:
        df_mat = pd.DataFrame(mat[:6, :6]*100, index=[f"🏠 {eq_l} ({i})" for i in range(6)], columns=[f"✈️ {eq_v} ({j})" for j in range(6)])
        st.dataframe(df_mat.style.format("{:.1f}%").background_gradient(cmap="YlOrBr"), use_container_width=True)

    with tab5:
        lc1, lc2, lc3, lc4 = st.columns(4)
        min_act = lc1.slider("⏱️ Minuto Actual", 1, 90, 60)
        g_loc_v = lc2.number_input(f"⚽ Goles {eq_l}", 0, 10, 0)
        g_vis_v = lc3.number_input(f"⚽ Goles {eq_v}", 0, 10, 0)
        pos_loc = lc4.slider(f"📊 Posesión {eq_l} (%)", 20, 80, 54)
        mostrar_cancha_calor(eq_l, eq_v, pos_loc, 100 - pos_loc, 1.1, 1.0, "futbol")
        frac_rest = max((94.0 - min_act) / 94.0, 0.04)
        lam_rest = (lam_loc + lam_vis) * frac_rest
        p_1_gol_mas = 1.0 - poisson.pmf(0, lam_rest)
        st.info(f"🔥 Probabilidad de +0.5 Goles Restantes: {p_1_gol_mas*100:.1f}% | Cuota Mínima Justa: {1/max(p_1_gol_mas, 0.01):.2f}")


# ==============================================================================
# 2. MÓDULO TENIS (SUPERFICIE 2X + DESGASTE TORNEO + INDOOR/ALTURA + ACES)
# ==============================================================================
elif deporte_activo.startswith("🎾"):
    st.sidebar.markdown("### 🎾 1. Circuito, Superficie y Tenistas")
    circuito = st.sidebar.radio("Circuito:", ["ATP (Masculino)", "WTA (Femenino)"])
    superficie_elegida = st.sidebar.selectbox(
        "🌍 Superficie de la Cancha:",
        [
            "🟦 Cancha Dura (Hard Court - Velocidad Media/Alta)",
            "🟧 Polvo de Ladrillo / Arcilla (Clay - Lenta • -28% Aces)",
            "🟩 Césped (Grass - Rápida • +32% Aces)"
        ]
    )
    condicion_pista = st.sidebar.selectbox(
        "🏟️ Condición Ambiental / Velocidad:",
        [
            "☀️ Outdoor Estándar (1.00x Aces)",
            "🏢 Indoor / Techado o Altura (+18% Aces)",
            "🌙 Pista Pesada / Nocturna (-12% Aces)"
        ]
    )
    mult_pista_aces = 1.18 if "Indoor" in condicion_pista else (0.88 if "Pesada" in condicion_pista else 1.00)
    formato_sets = st.sidebar.radio("Formato del Partido:", ["Al mejor de 3 Sets (Estándar)", "Al mejor de 5 Sets (Grand Slam)"])

    catalogo_espn_tenis = obtener_rankings_oficiales_espn_tenis(circuito)
    if not catalogo_espn_tenis:
        st.error("No se pudo conectar a la API Oficial de Rankings de ESPN Tenis.")
        st.stop()

    lista_tenistas = sorted(list(catalogo_espn_tenis.keys()), key=lambda x: catalogo_espn_tenis[x]["rank"])

    def_a = "Jannik Sinner" if "ATP" in circuito else "Marta Kostyuk"
    def_b = "Carlos Alcaraz" if "ATP" in circuito else "Jessica Pegula"
    idx_a = lista_tenistas.index(def_a) if def_a in lista_tenistas else 0
    idx_b = lista_tenistas.index(def_b) if def_b in lista_tenistas else (1 if len(lista_tenistas) > 1 else 0)

    col_t1, col_t2 = st.sidebar.columns(2)
    jug_a = col_t1.selectbox("🎾 Tenista A", lista_tenistas, index=idx_a)
    jug_b = col_t2.selectbox("🎾 Tenista B", lista_tenistas, index=idx_b)

    info_a = catalogo_espn_tenis[jug_a]
    info_b = catalogo_espn_tenis[jug_b]
    rank_a, pts_rank_a, foto_a = info_a["rank"], info_a["points"], info_a["foto"]
    rank_b, pts_rank_b, foto_b = info_b["rank"], info_b["points"], info_b["foto"]
    fb_foto_a = generar_avatar_tenista_svg(jug_a, "#ff6b00")
    fb_foto_b = generar_avatar_tenista_svg(jug_b, "#38bdf8")

    with st.spinner(f"Extrayendo historial oficial en vivo de ESPN para {jug_a} y {jug_b}..."):
        df_part_a = obtener_partidos_reales_espn_tenista(circuito, info_a["id"], jug_a)
        df_part_b = obtener_partidos_reales_espn_tenista(circuito, info_b["id"], jug_b)

    pref_t = "atp" if "ATP" in circuito else "wta"
    noticias_t = obtener_noticias_relevantes_espn("tennis", pref_t, jug_a, jug_b)
    auto_fat_a, auto_fat_b = calcular_penalizacion_automatica(pd.DataFrame(), noticias_t, jug_a, jug_b)

    b2b_ta, msg_b2b_ta = detectar_fatiga_back_to_back(df_part_a, "Fecha")
    b2b_tb, msg_b2b_tb = detectar_fatiga_back_to_back(df_part_b, "Fecha")
    if b2b_ta:
        auto_fat_a = min(auto_fat_a + 5, 25)
    if b2b_tb:
        auto_fat_b = min(auto_fat_b + 5, 25)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏥 Factor Físico / Desgaste Torneo")
    st.sidebar.caption(f"🤖 Auto-cálculo: **{jug_a} (-{auto_fat_a}%)** | **{jug_b} (-{auto_fat_b}%)**")
    fat_a = st.sidebar.slider(f"Penalización Físico {jug_a} (%)", 0, 25, min(auto_fat_a, 25), 5)
    fat_b = st.sidebar.slider(f"Penalización Físico {jug_b} (%)", 0, 25, min(auto_fat_b, 25), 5)

    sup_a = calcular_perfil_superficie_real(df_part_a, rank_a, circuito, jug_a)
    sup_b = calcular_perfil_superficie_real(df_part_b, rank_b, circuito, jug_b)

    if "Arcilla" in superficie_elegida:
        clave_sup, nombre_sup_corto, estilo_cancha = "Clay", "Arcilla (Clay)", "tenis_clay"
        bg_cancha_card = "linear-gradient(135deg, #431407 0%, #9a3412 50%, #c2410c 100%)"
        borde_cancha_card = "#fb923c"
    elif "Césped" in superficie_elegida:
        clave_sup, nombre_sup_corto, estilo_cancha = "Grass", "Césped (Grass)", "tenis_grass"
        bg_cancha_card = "linear-gradient(135deg, #052e16 0%, #15803d 50%, #166534 100%)"
        borde_cancha_card = "#4ade80"
    else:
        clave_sup, nombre_sup_corto, estilo_cancha = "Hard", "Cancha Dura (Hard)", "tenis_hard"
        bg_cancha_card = "linear-gradient(135deg, #0f172a 0%, #1d4ed8 50%, #0284c7 100%)"
        borde_cancha_card = "#60a5fa"

    hold_a_sup = sup_a[clave_sup]["Hold"] * (1.0 - (fat_a / 200.0))
    brk_a_sup = sup_a[clave_sup]["Break"] * (1.0 - (fat_a / 200.0))
    hold_b_sup = sup_b[clave_sup]["Hold"] * (1.0 - (fat_b / 200.0))
    brk_b_sup = sup_b[clave_sup]["Break"] * (1.0 - (fat_b / 200.0))

    hold_eff_a = (hold_a_sup + (100.0 - brk_b_sup)) / 2.0
    hold_eff_b = (hold_b_sup + (100.0 - brk_a_sup)) / 2.0
    bono_rank_a = (np.log10(max(rank_b, 1)) - np.log10(max(rank_a, 1))) * 4.8
    diff_efectivo = (hold_eff_a - hold_eff_b) + bono_rank_a

    p_set_a = float(np.clip(0.50 + (diff_efectivo / 100.0) * 2.25, 0.08, 0.92))
    p_set_b = 1.0 - p_set_a
    if "3 Sets" in formato_sets:
        p_gana_a = float((p_set_a ** 2) + 2.0 * (p_set_a ** 2) * p_set_b)
        sets_esp = 2.0 * ((p_set_a**2) + (p_set_b**2)) + 3.0 * (2.0 * p_set_a * p_set_b)
        factor_formato_aces = sets_esp / 2.38
    else:
        p_gana_a = float((p_set_a ** 3) + 3.0 * (p_set_a ** 3) * p_set_b + 6.0 * (p_set_a ** 3) * (p_set_b ** 2))
        sets_esp = 3.65
        factor_formato_aces = 1.48
    p_gana_b = 1.0 - p_gana_a

    juegos_totales_esp = round((sup_a[clave_sup]["Juegos_Prom"] + sup_b[clave_sup]["Juegos_Prom"]) / 2.0, 1)

    media_brk_circuito = 24.0 if "ATP" in circuito else 35.0
    ajuste_resto_vs_a = np.clip(1.0 + ((media_brk_circuito - brk_b_sup) / 100.0) * 1.15, 0.78, 1.25)
    ajuste_resto_vs_b = np.clip(1.0 + ((media_brk_circuito - brk_a_sup) / 100.0) * 1.15, 0.78, 1.25)

    aces_esp_a = round(sup_a[clave_sup]["Aces"] * ajuste_resto_vs_a * factor_formato_aces * mult_pista_aces * (1.0 - fat_a / 150.0), 1)
    aces_esp_b = round(sup_b[clave_sup]["Aces"] * ajuste_resto_vs_b * factor_formato_aces * mult_pista_aces * (1.0 - fat_b / 150.0), 1)
    aces_totales_esp = round(aces_esp_a + aces_esp_b, 1)

    favorito_nom = jug_a if p_gana_a >= p_gana_b else jug_b
    fav_cuota_justa = 1.0 / max(p_gana_a, p_gana_b)
    fav_rk = rank_a if p_gana_a >= p_gana_b else rank_b

    html_tenis_hero = (
        f'<div class="hero-matchup" style="background:{bg_cancha_card}; border: 2px solid {borde_cancha_card};">'
        f'<div class="hero-grid">'
        f'<div class="hero-team">'
        f'<img src="{foto_a}" onerror="this.onerror=null;this.src=\'{fb_foto_a}\';" class="hero-photo"/>'
        f'<div class="hero-team-name">{jug_a}</div>'
        f'<span style="background:rgba(0,0,0,0.50);color:#fff;padding:2px 10px;border-radius:999px;font-size:0.74rem;font-weight:700;margin-top:4px;">Rank #{rank_a} • {int(pts_rank_a)} pts</span>'
        f'</div>'
        f'<div class="hero-center">'
        f'<div class="hero-league-pill" style="background:rgba(0,0,0,0.50);">{circuito} • {nombre_sup_corto.upper()}</div>'
        f'<div class="hero-score">{p_gana_a*100:.1f}% — {p_gana_b*100:.1f}%</div>'
        f'<div class="hero-sub" style="color:#ffffff;">👑 Fav: <b>{favorito_nom}</b> (#{fav_rk}) • Justa: <b>{fav_cuota_justa:.2f}</b></div>'
        f'<div class="hero-sub" style="color:#f4f4f5;margin-top:3px;">🔥 Aces Esp: <b>{aces_totales_esp}</b> ({aces_esp_a}+{aces_esp_b}) • Juegos: <b>{juegos_totales_esp}</b></div>'
        f'<div class="prob-bar-wrap"><div style="width:{p_gana_a*100:.1f}%; background:#ff6b00;"></div><div style="width:{p_gana_b*100:.1f}%; background:#38bdf8;"></div></div>'
        f'</div>'
        f'<div class="hero-team">'
        f'<img src="{foto_b}" onerror="this.onerror=null;this.src=\'{fb_foto_b}\';" class="hero-photo"/>'
        f'<div class="hero-team-name">{jug_b}</div>'
        f'<span style="background:rgba(0,0,0,0.50);color:#fff;padding:2px 10px;border-radius:999px;font-size:0.74rem;font-weight:700;margin-top:4px;">Rank #{rank_b} • {int(pts_rank_b)} pts</span>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html_tenis_hero, unsafe_allow_html=True)

    with st.expander(f"📋 TABLA DE AUDITORÍA TENIS: Superficies (Peso 2x), Aces y Últimos Partidos ({jug_a} vs {jug_b})", expanded=False):
        if b2b_ta or b2b_tb:
            st.warning(f"Alerta de Fatiga Reciente: {jug_a if b2b_ta else ''} {msg_b2b_ta} | {jug_b if b2b_tb else ''} {msg_b2b_tb}")
        if noticias_t:
            st.markdown("**🗞️ Noticias Recientes en ESPN Tenis:**")
            for f_nt, hl_t, desc_t in noticias_t:
                st.markdown(f"📰 **[{f_nt}] {hl_t}** — _{desc_t[:140]}_")
        st.markdown("**🌍 1. Rendimiento y Aces Comparados por Tipo de Cancha (Dura vs. Arcilla vs. Césped):**")
        df_comparativa_canchas = pd.DataFrame([
            {
                "Tenista": jug_a,
                "Ranking ESPN": f"#{rank_a} ({int(pts_rank_a)} pts)",
                "🟦 Dura (Saque / Quiebre | %Vict)": f"{sup_a['Hard']['Hold']}% / {sup_a['Hard']['Break']}% ({sup_a['Hard']['WinPct']}%)",
                "🟧 Arcilla (Saque / Quiebre | %Vict)": f"{sup_a['Clay']['Hold']}% / {sup_a['Clay']['Break']}% ({sup_a['Clay']['WinPct']}%)",
                "🟩 Césped (Saque / Quiebre | %Vict)": f"{sup_a['Grass']['Hold']}% / {sup_a['Grass']['Break']}% ({sup_a['Grass']['WinPct']}%)",
                "🔥 Aces Base (Dura / Arcilla / Césped)": f"{sup_a['Hard']['Aces']} / {sup_a['Clay']['Aces']} / {sup_a['Grass']['Aces']}",
                f"🎯 Aces Hoy ({nombre_sup_corto})": f"{aces_esp_a} aces"
            },
            {
                "Tenista": jug_b,
                "Ranking ESPN": f"#{rank_b} ({int(pts_rank_b)} pts)",
                "🟦 Dura (Saque / Quiebre | %Vict)": f"{sup_b['Hard']['Hold']}% / {sup_b['Hard']['Break']}% ({sup_b['Hard']['WinPct']}%)",
                "🟧 Arcilla (Saque / Quiebre | %Vict)": f"{sup_b['Clay']['Hold']}% / {sup_b['Clay']['Break']}% ({sup_b['Clay']['WinPct']}%)",
                "🟩 Césped (Saque / Quiebre | %Vict)": f"{sup_b['Grass']['Hold']}% / {sup_b['Grass']['Break']}% ({sup_b['Grass']['WinPct']}%)",
                "🔥 Aces Base (Dura / Arcilla / Césped)": f"{sup_b['Hard']['Aces']} / {sup_b['Clay']['Aces']} / {sup_b['Grass']['Aces']}",
                f"🎯 Aces Hoy ({nombre_sup_corto})": f"{aces_esp_b} aces"
            }
        ])
        st.dataframe(df_comparativa_canchas, use_container_width=True, hide_index=True)

        c_aud1, c_aud2 = st.columns(2)
        cols_mostrar_t = ["Fecha", "Torneo", "Superficie", "Ronda", "Rival", "Resultado", "Marcador"]
        with c_aud1:
            st.markdown(f"**🎾 Últimos partidos registrados en ESPN para {jug_a} (#{rank_a}):**")
            if not df_part_a.empty:
                st.dataframe(df_part_a[cols_mostrar_t].iloc[::-1].head(8), use_container_width=True, hide_index=True)
        with c_aud2:
            st.markdown(f"**🎾 Últimos partidos registrados en ESPN para {jug_b} (#{rank_b}):**")
            if not df_part_b.empty:
                st.dataframe(df_part_b[cols_mostrar_t].iloc[::-1].head(8), use_container_width=True, hide_index=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas Betano Tenis")
    c_ta = st.sidebar.number_input(f"Gana {jug_a}", 1.01, 20.0, round(1/max(p_gana_a*1.05, 0.05), 2), 0.05)
    c_tb = st.sidebar.number_input(f"Gana {jug_b}", 1.01, 20.0, round(1/max(p_gana_b*1.05, 0.05), 2), 0.05)
    linea_j_ten = st.sidebar.number_input("Línea Total de Juegos", 16.5, 42.5, 21.5 if "WTA" in circuito else 22.5, 0.5)
    c_ov_j = st.sidebar.number_input(f"Cuota Más de {linea_j_ten} Juegos", 1.01, 15.0, 1.87, 0.05)
    c_un_j = st.sidebar.number_input(f"Cuota Menos de {linea_j_ten} Juegos", 1.01, 15.0, 1.90, 0.05)

    with st.sidebar.expander("🔥 Cuotas y Línea de Aces (Betano)", expanded=True):
        linea_aces_def = float(int(aces_totales_esp) + 0.5)
        linea_aces_ten = st.number_input("Línea Total de Aces en Betano", 2.5, 45.5, linea_aces_def, 1.0)
        c_ov_aces = st.number_input(f"Cuota Más de {linea_aces_ten} Aces (Over)", 1.01, 15.0, 1.85, 0.05)
        c_un_aces = st.number_input(f"Cuota Menos de {linea_aces_ten} Aces (Under)", 1.01, 15.0, 1.85, 0.05)

    p_over_juegos = float(1.0 - norm.cdf(linea_j_ten, loc=juegos_totales_esp, scale=3.4))
    sigma_aces = max(np.sqrt(aces_totales_esp * 1.35), 2.2)
    p_over_aces = float(1.0 - norm.cdf(linea_aces_ten, loc=aces_totales_esp, scale=sigma_aces))
    p_under_aces = 1.0 - p_over_aces

    tk1, tk2, tk3, tk4 = st.columns(4)
    tk1.metric("🏆 Prob. Victoria", f"{p_gana_a*100:.1f}% vs {p_gana_b*100:.1f}%", f"Favorito(a): {favorito_nom}")
    tk2.metric(f"🎾 Saque Efectivo ({nombre_sup_corto})", f"{hold_eff_a:.1f}% vs {hold_eff_b:.1f}%", f"1er Set {jug_a}: {p_set_a*100:.1f}%")
    tk3.metric("📏 Total Juegos Esperados", f"{juegos_totales_esp} juegos", f"Sets Esp.: {sets_esp:.2f}")
    tk4.metric(f"🔥 Aces Esperados ({nombre_sup_corto})", f"{aces_totales_esp} aces", f"{aces_esp_a} L + {aces_esp_b} V")

    CONFIG_BARRA_PROB = {"Prob. Real": st.column_config.ProgressColumn("Prob. Real (%)", format="%.1f%%", min_value=0, max_value=100)}
    tab1, tab2 = st.tabs(["🎯 1. Mercados Tenis y Aces (Betano)", "🔴 2. Radar En Vivo"])
    with tab1:
        m_t = [
            (f"Moneyline: Gana {jug_a} ({nombre_sup_corto})", p_gana_a, c_ta),
            (f"Moneyline: Gana {jug_b} ({nombre_sup_corto})", p_gana_b, c_tb),
            (f"Ganador(a) 1er Set: {jug_a}", p_set_a, round(1/max(p_set_a*1.05, 0.05), 2)),
            (f"Total Juegos: Más de {linea_j_ten} Juegos (Over)", p_over_juegos, c_ov_j),
            (f"Total Juegos: Menos de {linea_j_ten} Juegos (Under)", 1.0 - p_over_juegos, c_un_j),
            (f"Total Aces ({nombre_sup_corto}): Más de {linea_aces_ten} Aces (Over)", p_over_aces, c_ov_aces),
            (f"Total Aces ({nombre_sup_corto}): Menos de {linea_aces_ten} Aces (Under)", p_under_aces, c_un_aces)
        ]
        df_ten_m = construir_tabla_mercados_kelly(m_t, "Mercado", banca_usuario, fraccion_kelly_val, min_prob_filtro, min_edge_filtro)
        st.dataframe(df_ten_m.style.apply(resaltar_valor, axis=1), column_config=CONFIG_BARRA_PROB, use_container_width=True, hide_index=True)
    with tab2:
        mostrar_cancha_calor(jug_a, jug_b, hold_eff_a, hold_eff_b, 1.1, 1.0, estilo_cancha)


# ==============================================================================
# 3. MÓDULO HOCKEY SOBRE HIELO (NHL - SOLO OVER SOG + PIM + HÁNDICAP ABIERTO)
# ==============================================================================
elif deporte_activo.startswith("🏒"):
    st.sidebar.markdown("### 🏒 1. Equipos NHL")
    mapa_nhl, mapa_logos_nhl = obtener_catalogo_equipos_nhl()
    if not mapa_nhl:
        st.error("No se pudo conectar con la API Oficial de la NHL (api-web.nhle.com).")
        st.stop()

    lista_nhl = sorted(list(mapa_nhl.keys()))
    col_nhl1, col_nhl2 = st.sidebar.columns(2)
    nh_l = col_nhl1.selectbox("🏠 Local (Home)", lista_nhl, index=0)
    nh_v = col_nhl2.selectbox("✈️ Visita (Road)", lista_nhl, index=1 if len(lista_nhl) > 1 else 0)

    logo_nh_l, fb_nh_l = buscar_logo_equipo(nh_l, mapa_logos_nhl, "#ff6b00")
    logo_nh_v, fb_nh_v = buscar_logo_equipo(nh_v, mapa_logos_nhl, "#38bdf8")

    st.sidebar.markdown("### 🥅 Porteros Confirmados (Goalies)")
    g_col1, g_col2 = st.sidebar.columns(2)
    portero_l = g_col1.selectbox(f"Arco {nh_l[:12]}", ["Titular (1.00x)", "Suplente (+11% GC)"])
    portero_v = g_col2.selectbox(f"Arco {nh_v[:12]}", ["Titular (1.00x)", "Suplente (+11% GC)"])
    mult_portero_l = 1.11 if "Suplente" in portero_l else 1.00
    mult_portero_v = 1.11 if "Suplente" in portero_v else 1.00

    usar_bayes_nhl = st.sidebar.checkbox("🛡️ Amortiguador Bayesiano NHL (< 6 PJ)", value=False)
    mult_bajas_nl, mult_bajas_nv, pct_baja_nl, pct_baja_nv = renderizar_panel_bajas_y_factor("hockey", "nhl", nh_l, nh_v, f"nhl_{nh_l}_{nh_v}")

    with st.spinner(f"Extrayendo boxscores reales de goles, Tiros (SOG) y Penalizaciones (PIM) de {nh_l} y {nh_v}..."):
        df_nhl_l = extraer_ultimos_partidos_nhl_completo(mapa_nhl[nh_l], condicion="HOME", n_partidos=5)
        df_nhl_v = extraer_ultimos_partidos_nhl_completo(mapa_nhl[nh_v], condicion="AWAY", n_partidos=5)

    b2b_nl, msg_b2b_nl = detectar_fatiga_back_to_back(df_nhl_l, "Fecha")
    b2b_nv, msg_b2b_nv = detectar_fatiga_back_to_back(df_nhl_v, "Fecha")
    mult_b2b_of_l = 0.92 if b2b_nl else 1.00
    mult_b2b_of_v = 0.92 if b2b_nv else 1.00

    media_nhl_home, media_nhl_away, media_nhl_global = 3.18, 2.92, 3.05

    gf_l_puro = float(df_nhl_l["Goles a Favor"].mean()) if not df_nhl_l.empty else media_nhl_home
    gc_l_puro = float(df_nhl_l["Goles en Contra"].mean()) if not df_nhl_l.empty else media_nhl_away
    gf_v_puro = float(df_nhl_v["Goles a Favor"].mean()) if not df_nhl_v.empty else media_nhl_away
    gc_v_puro = float(df_nhl_v["Goles en Contra"].mean()) if not df_nhl_v.empty else media_nhl_home

    pj_nhl_l, pj_nhl_v = len(df_nhl_l), len(df_nhl_v)
    if usar_bayes_nhl:
        peso_nl = min(pj_nhl_l / 6.0, 1.0)
        peso_nv = min(pj_nhl_v / 6.0, 1.0)
        gf_nhl_l = (peso_nl * gf_l_puro) + ((1.0 - peso_nl) * media_nhl_home)
        gc_nhl_l = (peso_nl * gc_l_puro) + ((1.0 - peso_nl) * media_nhl_away)
        gf_nhl_v = (peso_nv * gf_v_puro) + ((1.0 - peso_nv) * media_nhl_away)
        gc_nhl_v = (peso_nv * gc_v_puro) + ((1.0 - peso_nv) * media_nhl_home)
    else:
        gf_nhl_l, gc_nhl_l, gf_nhl_v, gc_nhl_v = gf_l_puro, gc_l_puro, gf_v_puro, gc_v_puro

    gf_nhl_l = gf_nhl_l * mult_bajas_nl * mult_b2b_of_l
    gf_nhl_v = gf_nhl_v * mult_bajas_nv * mult_b2b_of_v
    gc_nhl_l = gc_nhl_l * mult_portero_l
    gc_nhl_v = gc_nhl_v * mult_portero_v

    sog_f_l = float(df_nhl_l["Tiros al Arco (SOG) Favor"].dropna().mean()) if ("Tiros al Arco (SOG) Favor" in df_nhl_l and not df_nhl_l["Tiros al Arco (SOG) Favor"].dropna().empty) else 29.5
    sog_c_l = float(df_nhl_l["Tiros al Arco (SOG) Contra"].dropna().mean()) if ("Tiros al Arco (SOG) Contra" in df_nhl_l and not df_nhl_l["Tiros al Arco (SOG) Contra"].dropna().empty) else 28.5
    sog_f_v = float(df_nhl_v["Tiros al Arco (SOG) Favor"].dropna().mean()) if ("Tiros al Arco (SOG) Favor" in df_nhl_v and not df_nhl_v["Tiros al Arco (SOG) Favor"].dropna().empty) else 28.0
    sog_c_v = float(df_nhl_v["Tiros al Arco (SOG) Contra"].dropna().mean()) if ("Tiros al Arco (SOG) Contra" in df_nhl_v and not df_nhl_v["Tiros al Arco (SOG) Contra"].dropna().empty) else 30.0

    sog_esp_loc = round(((sog_f_l + sog_c_v) / 2.0) * (0.6 + 0.4 * mult_bajas_nl) * (1.06 if b2b_nv else 1.0), 1)
    sog_esp_vis = round(((sog_f_v + sog_c_l) / 2.0) * (0.6 + 0.4 * mult_bajas_nv) * (1.06 if b2b_nl else 1.0), 1)
    sog_totales_esp = round(sog_esp_loc + sog_esp_vis, 1)

    pim_prop_l = float(df_nhl_l["Min. Penalización (PIM) Propios"].dropna().mean()) if ("Min. Penalización (PIM) Propios" in df_nhl_l and not df_nhl_l["Min. Penalización (PIM) Propios"].dropna().empty) else 8.0
    pim_riv_l = float(df_nhl_l["Min. Penalización (PIM) Rival"].dropna().mean()) if ("Min. Penalización (PIM) Rival" in df_nhl_l and not df_nhl_l["Min. Penalización (PIM) Rival"].dropna().empty) else 8.0
    pim_prop_v = float(df_nhl_v["Min. Penalización (PIM) Propios"].dropna().mean()) if ("Min. Penalización (PIM) Propios" in df_nhl_v and not df_nhl_v["Min. Penalización (PIM) Propios"].dropna().empty) else 8.5
    pim_riv_v = float(df_nhl_v["Min. Penalización (PIM) Rival"].dropna().mean()) if ("Min. Penalización (PIM) Rival" in df_nhl_v and not df_nhl_v["Min. Penalización (PIM) Rival"].dropna().empty) else 8.0

    pim_esp_loc = round((pim_prop_l + pim_riv_v) / 2.0, 1)
    pim_esp_vis = round((pim_prop_v + pim_riv_l) / 2.0, 1)
    pim_totales_esp = round(pim_esp_loc + pim_esp_vis, 1)

    lam_nhl_l = max((gf_nhl_l * gc_nhl_v) / media_nhl_global, 0.50)
    lam_nhl_v = max((gf_nhl_v * gc_nhl_l) / media_nhl_global, 0.50)
    tot_nhl = lam_nhl_l + lam_nhl_v
    diff_goles_nhl = lam_nhl_l - lam_nhl_v

    mat_n = np.zeros((13, 13))
    for i in range(13):
        for j in range(13):
            mat_n[i, j] = poisson.pmf(i, lam_nhl_l) * poisson.pmf(j, lam_nhl_v)
    p_reg_l = float(np.sum(np.tril(mat_n, -1)))
    p_emp = float(np.sum(np.diag(mat_n)))
    p_ml_l = p_reg_l + (p_emp * (lam_nhl_l / tot_nhl))
    p_ml_v = 1.0 - p_ml_l

    alertas_nhl = []
    if "Suplente" in portero_l:
        alertas_nhl.append(f"🥅 Suplente {nh_l}")
    if "Suplente" in portero_v:
        alertas_nhl.append(f"🥅 Suplente {nh_v}")
    if b2b_nl:
        alertas_nhl.append(f"⚡ B2B {nh_l}")
    if b2b_nv:
        alertas_nhl.append(f"⚡ B2B {nh_v}")

    renderizar_hero_card_deporte(
        nh_l, nh_v, logo_nh_l, fb_nh_l, logo_nh_v, fb_nh_v,
        "🏒 NHL HOCKEY • LOCAL VS. VISITA",
        f"{lam_nhl_l:.2f}  —  {lam_nhl_v:.2f}",
        f"Goles Esp.: {tot_nhl:.2f} • SOG Esp.: {sog_totales_esp} • Min. Penalización (PIM) Esp.: {pim_totales_esp} min",
        p_ml_l, None, p_ml_v, pct_baja_nl, pct_baja_nv,
        badge_extra=" | ".join(alertas_nhl)
    )

    with st.expander(f"📋 TABLA DE AUDITORÍA NHL: Goles, Tiros (SOG) y Minutos Penalización (PIM) Reales ({nh_l} vs {nh_v})", expanded=False):
        st.success("✅ Datos extraídos en vivo desde los Boxscores Oficiales de la NHL (`api-web.nhle.com`).")
        st.markdown(f"**🏠 Últimos {len(df_nhl_l)} partidos de {nh_l} en CASA (Prom. SOG: {sog_f_l:.1f} | Prom. PIM propios: {pim_prop_l:.1f} min):**")
        if not df_nhl_l.empty:
            st.dataframe(df_nhl_l, use_container_width=True, hide_index=True)

        st.markdown(f"**✈️ Últimos {len(df_nhl_v)} partidos de {nh_v} de VISITA (Prom. SOG: {sog_f_v:.1f} | Prom. PIM propios: {pim_prop_v:.1f} min):**")
        if not df_nhl_v.empty:
            st.dataframe(df_nhl_v, use_container_width=True, hide_index=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas Betano NHL (ML, Hándicap & Goles)")
    c_nh_l = st.sidebar.number_input(f"Moneyline {nh_l} (Inc. OT)", 1.01, 20.0, round(1/max(p_ml_l*1.05, 0.05), 2), 0.05)
    c_nh_v = st.sidebar.number_input(f"Moneyline {nh_v} (Inc. OT)", 1.01, 20.0, round(1/max(p_ml_v*1.05, 0.05), 2), 0.05)

    handicap_nhl_loc = st.sidebar.number_input(f"Hándicap / Puck Line {nh_l} (ej. -1.5, +1.5, -2.5)", -6.5, 6.5, -1.5 if diff_goles_nhl > 0.35 else 1.5, 0.5)
    c_hc_nhl_l = st.sidebar.number_input(f"Cuota {nh_l} ({handicap_nhl_loc:+.1f})", 1.01, 15.0, 2.25 if handicap_nhl_loc < 0 else 1.65, 0.05)
    c_hc_nhl_v = st.sidebar.number_input(f"Cuota {nh_v} ({-handicap_nhl_loc:+.1f})", 1.01, 15.0, 1.65 if handicap_nhl_loc < 0 else 2.25, 0.05)

    linea_nhl = st.sidebar.selectbox("Línea Goles Totales NHL", [5.5, 6.0, 6.5], index=2)
    c_ov_nhl = st.sidebar.number_input(f"Cuota Over {linea_nhl} Goles", 1.01, 15.0, 1.88, 0.05)
    c_un_nhl = st.sidebar.number_input(f"Cuota Under {linea_nhl} Goles", 1.01, 15.0, 1.92, 0.05)

    with st.sidebar.expander("🎯 Líneas Tiros (Solo Over) y Penalizaciones (PIM)", expanded=True):
        linea_sog_tot = st.number_input("Línea Tiros al Arco Totales (Over)", 40.5, 80.5, float(int(sog_totales_esp) + 0.5), 1.0)
        c_ov_sog = st.number_input(f"Cuota Over {linea_sog_tot} Tiros", 1.01, 15.0, 1.87, 0.05)
        linea_sog_loc = st.number_input(f"Línea Tiros {nh_l} Local (Over)", 18.5, 45.5, float(int(sog_esp_loc) + 0.5), 1.0)
        c_ov_sog_l = st.number_input(f"Cuota Over {linea_sog_loc} Tiros {nh_l}", 1.01, 15.0, 1.85, 0.05)
        st.markdown("---")
        linea_pim_tot = st.number_input("⏱️ Línea Minutos Penalización (PIM)", 4.5, 35.5, float(int(pim_totales_esp) + 0.5), 1.0)
        c_ov_pim = st.number_input(f"Cuota Over {linea_pim_tot} Min. PIM", 1.01, 15.0, 1.85, 0.05)
        c_un_pim = st.number_input(f"Cuota Under {linea_pim_tot} Min. PIM", 1.01, 15.0, 1.85, 0.05)

    p_hc_nhl_l = 0.0
    for i in range(13):
        for j in range(13):
            if i == j:
                p_ot_l = lam_nhl_l / max(tot_nhl, 0.1)
                if (1.0 + handicap_nhl_loc) > 0:
                    p_hc_nhl_l += float(mat_n[i, j]) * p_ot_l
                if (-1.0 + handicap_nhl_loc) > 0:
                    p_hc_nhl_l += float(mat_n[i, j]) * (1.0 - p_ot_l)
            else:
                if ((i - j) + handicap_nhl_loc) > 0:
                    p_hc_nhl_l += float(mat_n[i, j])
    p_hc_nhl_l = float(np.clip(p_hc_nhl_l, 0.02, 0.98))
    p_hc_nhl_v = 1.0 - p_hc_nhl_l

    p_ov_nhl = 1.0 - sum(poisson.pmf(k, tot_nhl) for k in range(int(linea_nhl) + 1))
    p_ov_sog_tot = float(1.0 - norm.cdf(linea_sog_tot, loc=sog_totales_esp, scale=6.8))
    p_ov_sog_l = float(1.0 - norm.cdf(linea_sog_loc, loc=sog_esp_loc, scale=4.8))
    p_ov_pim = float(1.0 - norm.cdf(linea_pim_tot, loc=pim_totales_esp, scale=4.6))
    p_un_pim = 1.0 - p_ov_pim

    nk1, nk2, nk3, nk4 = st.columns(4)
    nk1.metric("🏒 Goles Esp. (60m)", f"{lam_nhl_l:.2f} - {lam_nhl_v:.2f}", f"Total: {tot_nhl:.2f} goles")
    nk2.metric("⚖️ Hándicap NHL", f"{nh_l} {handicap_nhl_loc:+.1f}: {p_hc_nhl_l*100:.1f}%", f"ML: {p_ml_l*100:.1f}% vs {p_ml_v*100:.1f}%")
    nk3.metric("🎯 Tiros al Arco Esp.", f"{sog_totales_esp} tiros", f"{sog_esp_loc} L + {sog_esp_vis} V")
    nk4.metric("⏱️ Min. Penalización (PIM)", f"{pim_totales_esp} min", f"{pim_esp_loc} L + {pim_esp_vis} V")

    CONFIG_BARRA_PROB = {"Prob. Real": st.column_config.ProgressColumn("Prob. Real (%)", format="%.1f%%", min_value=0, max_value=100)}
    ntab1, ntab2, ntab3 = st.tabs(["🏆 1. Goles, ML y Hándicap", "🎯 2. Tiros (Over) & Penalizaciones (PIM)", "🔴 3. Radar En Vivo"])
    with ntab1:
        m_nhl = [
            (f"Moneyline: Gana {nh_l} (Inc. Prórroga)", p_ml_l, c_nh_l),
            (f"Moneyline: Gana {nh_v} (Inc. Prórroga)", p_ml_v, c_nh_v),
            (f"Hándicap / Puck Line: {nh_l} ({handicap_nhl_loc:+.1f})", p_hc_nhl_l, c_hc_nhl_l),
            (f"Hándicap / Puck Line: {nh_v} ({-handicap_nhl_loc:+.1f})", p_hc_nhl_v, c_hc_nhl_v),
            (f"Total: Más de {linea_nhl} Goles (Over)", p_ov_nhl, c_ov_nhl),
            (f"Total: Menos de {linea_nhl} Goles (Under)", 1.0 - p_ov_nhl, c_un_nhl)
        ]
        df_nh1 = construir_tabla_mercados_kelly(m_nhl, "Mercado NHL", banca_usuario, fraccion_kelly_val, min_prob_filtro, min_edge_filtro)
        st.dataframe(df_nh1.style.apply(resaltar_valor, axis=1), column_config=CONFIG_BARRA_PROB, use_container_width=True, hide_index=True)

    with ntab2:
        m_sog_pim = [
            (f"🎯 Más de {linea_sog_tot} Shots on Goal Totales (Over)", p_ov_sog_tot, c_ov_sog),
            (f"🎯 {nh_l}: Más de {linea_sog_loc} Shots on Goal (Over)", p_ov_sog_l, c_ov_sog_l),
            (f"⏱️ Más de {linea_pim_tot} Minutos de Penalización Totales (Over PIM)", p_ov_pim, c_ov_pim),
            (f"⏱️ Menos de {linea_pim_tot} Minutos de Penalización Totales (Under PIM)", p_un_pim, c_un_pim)
        ]
        df_nh2 = construir_tabla_mercados_kelly(m_sog_pim, "Mercado Tiros (Over) y Penalizaciones (PIM)", banca_usuario, fraccion_kelly_val, min_prob_filtro, min_edge_filtro)
        st.dataframe(df_nh2.style.apply(resaltar_valor, axis=1), column_config=CONFIG_BARRA_PROB, use_container_width=True, hide_index=True)

    with ntab3:
        mostrar_cancha_calor(nh_l, nh_v, p_ml_l*100, p_ml_v*100, 1.1, 1.0, "nhl")


# ==============================================================================
# 4. MÓDULO BALONCESTO (NBA - LOCAL VS VISITA + BACK-TO-BACK + SPREADS)
# ==============================================================================
elif deporte_activo.startswith("🏀"):
    st.sidebar.markdown("### 🏀 1. Equipos NBA")
    mapa_nba, mapa_logos_nba = obtener_catalogo_equipos_y_logos_espn("basketball", "nba")
    if not mapa_nba:
        st.error("No se pudo conectar con la API Oficial de ESPN para NBA.")
        st.stop()

    lista_nba = sorted(list(mapa_nba.keys()))
    c_nb1, c_nb2 = st.sidebar.columns(2)
    nb_l = c_nb1.selectbox("🏠 Local (Home)", lista_nba, index=0)
    nb_v = c_nb2.selectbox("✈️ Visita (Road)", lista_nba, index=1 if len(lista_nba) > 1 else 0)

    logo_nb_l, fb_nb_l = buscar_logo_equipo(nb_l, mapa_logos_nba, "#ff6b00")
    logo_nb_v, fb_nb_v = buscar_logo_equipo(nb_v, mapa_logos_nba, "#38bdf8")

    usar_bayes_nba = st.sidebar.checkbox("🛡️ Amortiguador Bayesiano NBA (< 6 PJ)", value=False)
    mult_bajas_nbl, mult_bajas_nbv, pct_b_nbl, pct_b_nbv = renderizar_panel_bajas_y_factor("basketball", "nba", nb_l, nb_v, f"nba_{nb_l}_{nb_v}")

    df_nba_l = extraer_ultimos_partidos_reales_espn("basketball", "nba", mapa_nba[nb_l], nb_l, n_partidos=5, condicion_filtro="HOME")
    df_nba_v = extraer_ultimos_partidos_reales_espn("basketball", "nba", mapa_nba[nb_v], nb_v, n_partidos=5, condicion_filtro="AWAY")

    b2b_nbl, msg_b2b_nbl = detectar_fatiga_back_to_back(df_nba_l, "Fecha")
    b2b_nbv, msg_b2b_nbv = detectar_fatiga_back_to_back(df_nba_v, "Fecha")
    pen_b2b_nba_l = -3.5 if b2b_nbl else 0.0
    pen_b2b_nba_v = -3.5 if b2b_nbv else 0.0

    media_nba_home, media_nba_away = 114.5, 111.5
    pf_l_puro = float(df_nba_l["Puntos/Carreras a Favor"].mean()) if not df_nba_l.empty else media_nba_home
    pa_l_puro = float(df_nba_l["Puntos/Carreras en Contra"].mean()) if not df_nba_l.empty else media_nba_away
    pf_v_puro = float(df_nba_v["Puntos/Carreras a Favor"].mean()) if not df_nba_v.empty else media_nba_away
    pa_v_puro = float(df_nba_v["Puntos/Carreras en Contra"].mean()) if not df_nba_v.empty else media_nba_home

    if usar_bayes_nba:
        w_nl = min(len(df_nba_l) / 6.0, 1.0)
        w_nv = min(len(df_nba_v) / 6.0, 1.0)
        pf_l = (w_nl * pf_l_puro) + ((1.0 - w_nl) * media_nba_home)
        pa_l = (w_nl * pa_l_puro) + ((1.0 - w_nl) * media_nba_away)
        pf_v = (w_nv * pf_v_puro) + ((1.0 - w_nv) * media_nba_away)
        pa_v = (w_nv * pa_v_puro) + ((1.0 - w_nv) * media_nba_home)
    else:
        pf_l, pa_l, pf_v, pa_v = pf_l_puro, pa_l_puro, pf_v_puro, pa_v_puro

    pf_l = (pf_l * mult_bajas_nbl) + pen_b2b_nba_l
    pf_v = (pf_v * mult_bajas_nbv) + pen_b2b_nba_v

    proy_l = (pf_l + pa_v) / 2.0
    proy_v = (pf_v + pa_l) / 2.0
    tot_nba = proy_l + proy_v
    spread_esp_nba = proy_l - proy_v
    p_ml_l = float(1.0 - norm.cdf(0.0, loc=spread_esp_nba, scale=11.8))
    p_ml_v = 1.0 - p_ml_l

    alertas_nba = []
    if b2b_nbl:
        alertas_nba.append(f"⚡ B2B {nb_l} (-3.5 pts)")
    if b2b_nbv:
        alertas_nba.append(f"⚡ B2B {nb_v} (-3.5 pts)")

    renderizar_hero_card_deporte(
        nb_l, nb_v, logo_nb_l, fb_nb_l, logo_nb_v, fb_nb_v,
        "🏀 NBA BASKETBALL • LOCAL VS. VISITA",
        f"{proy_l:.1f}  —  {proy_v:.1f}",
        f"Total Esperado: {tot_nba:.1f} pts • Spread Proyectado: {spread_esp_nba:+.1f}",
        p_ml_l, None, p_ml_v, pct_b_nbl, pct_b_nbv,
        badge_extra=" | ".join(alertas_nba)
    )

    with st.expander(f"📋 TABLA DE AUDITORÍA NBA: Últimos partidos reales de {nb_l} en CASA y {nb_v} de VISITA", expanded=False):
        st.success("✅ Datos extraídos en vivo desde ESPN Schedule filtrando estrictamente por Localía (`HOME`) y Gira (`AWAY`).")
        st.markdown(f"**🏠 Últimos {len(df_nba_l)} partidos de {nb_l} jugando en CASA (Local):**")
        if not df_nba_l.empty:
            st.dataframe(df_nba_l.rename(columns={"Puntos/Carreras a Favor": "Puntos Anotados", "Puntos/Carreras en Contra": "Puntos Recibidos", "Total Marcador": "Total Puntos"}), use_container_width=True, hide_index=True)
        st.markdown(f"**✈️ Últimos {len(df_nba_v)} partidos de {nb_v} jugando de GIRA (Visita):**")
        if not df_nba_v.empty:
            st.dataframe(df_nba_v.rename(columns={"Puntos/Carreras a Favor": "Puntos Anotados", "Puntos/Carreras en Contra": "Puntos Recibidos", "Total Marcador": "Total Puntos"}), use_container_width=True, hide_index=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas Betano NBA (ML, Spread & Total)")
    c_nba_l = st.sidebar.number_input(f"Moneyline Gana {nb_l}", 1.01, 25.0, round(1/max(p_ml_l*1.05, 0.05), 2), 0.05)
    c_nba_v = st.sidebar.number_input(f"Moneyline Gana {nb_v}", 1.01, 25.0, round(1/max(p_ml_v*1.05, 0.05), 2), 0.05)
    spread_linea_nba = st.sidebar.number_input(f"Hándicap / Spread {nb_l} (ej. -4.5 o +3.5)", -25.5, 25.5, round(-spread_esp_nba*2)/2, 0.5)
    c_sp_nba_l = st.sidebar.number_input(f"Cuota {nb_l} ({spread_linea_nba:+.1f})", 1.01, 15.0, 1.90, 0.05)
    c_sp_nba_v = st.sidebar.number_input(f"Cuota {nb_v} ({-spread_linea_nba:+.1f})", 1.01, 15.0, 1.90, 0.05)
    linea_nba = st.sidebar.number_input("Línea Total Puntos NBA", 180.5, 265.5, round(tot_nba*2)/2, 0.5)
    c_ov_nba = st.sidebar.number_input(f"Cuota Más de {linea_nba} (Over)", 1.01, 15.0, 1.90, 0.05)
    c_un_nba = st.sidebar.number_input(f"Cuota Menos de {linea_nba} (Under)", 1.01, 15.0, 1.90, 0.05)

    p_sp_nba_l = float(1.0 - norm.cdf(-spread_linea_nba, loc=spread_esp_nba, scale=11.8))
    p_sp_nba_v = 1.0 - p_sp_nba_l
    p_ov_nba = float(1.0 - norm.cdf(linea_nba, loc=tot_nba, scale=13.5))

    nk1, nk2, nk3, nk4 = st.columns(4)
    nk1.metric("🎯 Marcador Proyectado", f"{proy_l:.1f} - {proy_v:.1f}", f"Total: {tot_nba:.1f} pts")
    nk2.metric("🏆 Prob. Moneyline", f"{p_ml_l*100:.1f}% vs {p_ml_v*100:.1f}%")
    nk3.metric("⚖️ Hándicap (Spread)", f"{nb_l} {spread_linea_nba:+.1f}: {p_sp_nba_l*100:.1f}%", f"Diferencial Esp.: {spread_esp_nba:+.1f}")
    nk4.metric("📈 Prob. Over / Under", f"{p_ov_nba*100:.1f}% Over {linea_nba}", f"{(1-p_ov_nba)*100:.1f}% Under {linea_nba}")

    CONFIG_BARRA_PROB = {"Prob. Real": st.column_config.ProgressColumn("Prob. Real (%)", format="%.1f%%", min_value=0, max_value=100)}
    btab1, btab2 = st.tabs(["🎯 1. Mercados NBA (ML, Spread & Puntos)", "🔴 2. Radar En Vivo"])
    with btab1:
        m_nba = [
            (f"Moneyline: Gana {nb_l}", p_ml_l, c_nba_l),
            (f"Moneyline: Gana {nb_v}", p_ml_v, c_nba_v),
            (f"Hándicap: {nb_l} ({spread_linea_nba:+.1f})", p_sp_nba_l, c_sp_nba_l),
            (f"Hándicap: {nb_v} ({-spread_linea_nba:+.1f})", p_sp_nba_v, c_sp_nba_v),
            (f"Total: Más de {linea_nba} Puntos (Over)", p_ov_nba, c_ov_nba),
            (f"Total: Menos de {linea_nba} Puntos (Under)", 1.0 - p_ov_nba, c_un_nba)
        ]
        df_nba_m = construir_tabla_mercados_kelly(m_nba, "Mercado NBA", banca_usuario, fraccion_kelly_val, min_prob_filtro, min_edge_filtro)
        st.dataframe(df_nba_m.style.apply(resaltar_valor, axis=1), column_config=CONFIG_BARRA_PROB, use_container_width=True, hide_index=True)
    with btab2:
        mostrar_cancha_calor(nb_l, nb_v, p_ml_l*100, p_ml_v*100, 1.1, 1.0, "nba")


# ==============================================================================
# 5. MÓDULO FÚTBOL AMERICANO (NFL - LOCAL/VISITA + CLIMA + SPREAD + BAJAS)
# ==============================================================================
elif deporte_activo.startswith("🏈"):
    st.sidebar.markdown("### 🏈 1. Equipos NFL")
    mapa_nfl, mapa_logos_nfl = obtener_catalogo_equipos_y_logos_espn("football", "nfl")
    if not mapa_nfl:
        st.error("No se pudo conectar con la API Oficial de ESPN para NFL.")
        st.stop()

    lista_nfl = sorted(list(mapa_nfl.keys()))
    c_nf1, c_nf2 = st.sidebar.columns(2)
    nf_l = c_nf1.selectbox("🏠 Local (Home)", lista_nfl, index=0)
    nf_v = c_nf2.selectbox("✈️ Visita (Road)", lista_nfl, index=1 if len(lista_nfl) > 1 else 0)

    logo_nf_l, fb_nf_l = buscar_logo_equipo(nf_l, mapa_logos_nfl, "#ff6b00")
    logo_nf_v, fb_nf_v = buscar_logo_equipo(nf_v, mapa_logos_nfl, "#38bdf8")

    clima_nfl = st.sidebar.selectbox(
        "🌦️ Condición Climática / Estadio:",
        [
            "🏟️ Domo / Clima Normal (0.0 pts)",
            "💨 Viento Fuerte > 25 km/h o Lluvia (-4.5 pts)",
            "❄️ Nieve / Frío Extremo (-6.0 pts)"
        ]
    )
    ajuste_clima_nfl = -4.5 if "Viento" in clima_nfl else (-6.0 if "Nieve" in clima_nfl else 0.0)

    usar_bayes_nfl = st.sidebar.checkbox("🛡️ Amortiguador Bayesiano NFL (< 6 PJ)", value=True)
    mult_bajas_nfl_l, mult_bajas_nfl_v, pct_b_nfl_l, pct_b_nfl_v = renderizar_panel_bajas_y_factor("football", "nfl", nf_l, nf_v, f"nfl_{nf_l}_{nf_v}")

    df_nfl_l = extraer_ultimos_partidos_reales_espn("football", "nfl", mapa_nfl[nf_l], nf_l, n_partidos=5, condicion_filtro="HOME")
    df_nfl_v = extraer_ultimos_partidos_reales_espn("football", "nfl", mapa_nfl[nf_v], nf_v, n_partidos=5, condicion_filtro="AWAY")

    media_nfl_home, media_nfl_away = 23.4, 21.6

    pf_l_puro = float(df_nfl_l["Puntos/Carreras a Favor"].mean()) if not df_nfl_l.empty else media_nfl_home
    pa_l_puro = float(df_nfl_l["Puntos/Carreras en Contra"].mean()) if not df_nfl_l.empty else media_nfl_away
    pf_v_puro = float(df_nfl_v["Puntos/Carreras a Favor"].mean()) if not df_nfl_v.empty else media_nfl_away
    pa_v_puro = float(df_nfl_v["Puntos/Carreras en Contra"].mean()) if not df_nfl_v.empty else media_nfl_home

    pj_nf_l, pj_nf_v = len(df_nfl_l), len(df_nfl_v)
    if usar_bayes_nfl:
        peso_nfl_l = min(pj_nf_l / 6.0, 1.0)
        peso_nfl_v = min(pj_nf_v / 6.0, 1.0)
        pf_l = (peso_nfl_l * pf_l_puro) + ((1.0 - peso_nfl_l) * media_nfl_home)
        pa_l = (peso_nfl_l * pa_l_puro) + ((1.0 - peso_nfl_l) * media_nfl_away)
        pf_v = (peso_nfl_v * pf_v_puro) + ((1.0 - peso_nfl_v) * media_nfl_away)
        pa_v = (peso_nfl_v * pa_v_puro) + ((1.0 - peso_nfl_v) * media_nfl_home)
    else:
        pf_l, pa_l, pf_v, pa_v = pf_l_puro, pa_l_puro, pf_v_puro, pa_v_puro

    pf_l = (pf_l * mult_bajas_nfl_l) + (ajuste_clima_nfl / 2.0)
    pf_v = (pf_v * mult_bajas_nfl_v) + (ajuste_clima_nfl / 2.0)

    proy_l = max((pf_l + pa_v) / 2.0, 6.0)
    proy_v = max((pf_v + pa_l) / 2.0, 6.0)
    tot_nfl = proy_l + proy_v
    spread_esp_nfl = proy_l - proy_v
    p_ml_l = float(1.0 - norm.cdf(0.0, loc=spread_esp_nfl, scale=13.2))
    p_ml_v = 1.0 - p_ml_l

    renderizar_hero_card_deporte(
        nf_l, nf_v, logo_nf_l, fb_nf_l, logo_nf_v, fb_nf_v,
        "🏈 NFL FÚTBOL AMERICANO • LOCAL VS. VISITA",
        f"{proy_l:.1f}  —  {proy_v:.1f}",
        f"Total Esperado: {tot_nfl:.1f} puntos • Spread Proyectado: {spread_esp_nfl:+.1f}",
        p_ml_l, None, p_ml_v, pct_b_nfl_l, pct_b_nfl_v,
        badge_extra=f"🌦️ Ajuste Clima: {ajuste_clima_nfl:+.1f} pts" if ajuste_clima_nfl < 0 else ""
    )

    with st.expander(f"📋 TABLA DE AUDITORÍA NFL: Últimos partidos reales de {nf_l} como LOCAL y {nf_v} como VISITANTE", expanded=False):
        st.success("✅ Datos extraídos en vivo desde ESPN Schedule filtrando estrictamente por Localía (`HOME`) y Gira (`AWAY`).")
        st.markdown(f"**🏠 Últimos {len(df_nfl_l)} partidos de {nf_l} jugando en CASA (Local):**")
        if not df_nfl_l.empty:
            st.dataframe(df_nfl_l.rename(columns={"Puntos/Carreras a Favor": "Puntos Anotados", "Puntos/Carreras en Contra": "Puntos Recibidos", "Total Marcador": "Total Puntos"}), use_container_width=True, hide_index=True)
        st.markdown(f"**✈️ Últimos {len(df_nfl_v)} partidos de {nf_v} jugando de GIRA (Visita):**")
        if not df_nfl_v.empty:
            st.dataframe(df_nfl_v.rename(columns={"Puntos/Carreras a Favor": "Puntos Anotados", "Puntos/Carreras en Contra": "Puntos Recibidos", "Total Marcador": "Total Puntos"}), use_container_width=True, hide_index=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas Betano NFL (ML, Spread & Total)")
    c_nfl_l = st.sidebar.number_input(f"Moneyline Gana {nf_l}", 1.01, 25.0, round(1/max(p_ml_l*1.05, 0.05), 2), 0.05)
    c_nfl_v = st.sidebar.number_input(f"Moneyline Gana {nf_v}", 1.01, 25.0, round(1/max(p_ml_v*1.05, 0.05), 2), 0.05)
    spread_linea_nfl = st.sidebar.number_input(f"Hándicap / Spread {nf_l} (ej. -3.5 o +6.5)", -24.5, 24.5, round(-spread_esp_nfl*2)/2, 0.5)
    c_sp_nfl_l = st.sidebar.number_input(f"Cuota {nf_l} ({spread_linea_nfl:+.1f})", 1.01, 15.0, 1.90, 0.05)
    c_sp_nfl_v = st.sidebar.number_input(f"Cuota {nf_v} ({-spread_linea_nfl:+.1f})", 1.01, 15.0, 1.90, 0.05)
    linea_nfl = st.sidebar.number_input("Línea Puntos Totales NFL", 30.5, 68.5, round(tot_nfl*2)/2, 0.5)
    c_ov_nfl = st.sidebar.number_input(f"Cuota Más de {linea_nfl} (Over)", 1.01, 15.0, 1.90, 0.05)
    c_un_nfl = st.sidebar.number_input(f"Cuota Menos de {linea_nfl} (Under)", 1.01, 15.0, 1.90, 0.05)

    p_sp_nfl_l = float(1.0 - norm.cdf(-spread_linea_nfl, loc=spread_esp_nfl, scale=13.2))
    p_sp_nfl_v = 1.0 - p_sp_nfl_l
    p_ov_nfl = float(1.0 - norm.cdf(linea_nfl, loc=tot_nfl, scale=14.2))

    fk1, fk2, fk3, fk4 = st.columns(4)
    fk1.metric("🎯 Marcador Proyectado", f"{proy_l:.1f} - {proy_v:.1f}", f"Total: {tot_nfl:.1f} pts")
    fk2.metric("🏆 Prob. Moneyline", f"{p_ml_l*100:.1f}% vs {p_ml_v*100:.1f}%")
    fk3.metric("⚖️ Hándicap (Spread)", f"{nf_l} {spread_linea_nfl:+.1f}: {p_sp_nfl_l*100:.1f}%", f"Diferencial Esp.: {spread_esp_nfl:+.1f}")
    fk4.metric("📈 Prob. Over / Under", f"{p_ov_nfl*100:.1f}% Over {linea_nfl}", f"{(1-p_ov_nfl)*100:.1f}% Under {linea_nfl}")

    CONFIG_BARRA_PROB = {"Prob. Real": st.column_config.ProgressColumn("Prob. Real (%)", format="%.1f%%", min_value=0, max_value=100)}
    ftab1, ftab2 = st.tabs(["🎯 1. Mercados NFL (ML, Spread & Puntos)", "🔴 2. Radar En Vivo (In-Play)"])
    with ftab1:
        m_nfl = [
            (f"Moneyline: Gana {nf_l}", p_ml_l, c_nfl_l),
            (f"Moneyline: Gana {nf_v}", p_ml_v, c_nfl_v),
            (f"Hándicap: {nf_l} ({spread_linea_nfl:+.1f})", p_sp_nfl_l, c_sp_nfl_l),
            (f"Hándicap: {nf_v} ({-spread_linea_nfl:+.1f})", p_sp_nfl_v, c_sp_nfl_v),
            (f"Total: Más de {linea_nfl} Puntos (Over)", p_ov_nfl, c_ov_nfl),
            (f"Total: Menos de {linea_nfl} Puntos (Under)", 1.0 - p_ov_nfl, c_un_nfl)
        ]
        df_nfl_m = construir_tabla_mercados_kelly(m_nfl, "Mercado NFL", banca_usuario, fraccion_kelly_val, min_prob_filtro, min_edge_filtro)
        st.dataframe(df_nfl_m.style.apply(resaltar_valor, axis=1), column_config=CONFIG_BARRA_PROB, use_container_width=True, hide_index=True)
    with ftab2:
        mostrar_cancha_calor(nf_l, nf_v, p_ml_l*100, p_ml_v*100, 1.1, 1.0, "nfl")


# ==============================================================================
# 6. MÓDULO BÉISBOL (MLB - ESCUDOS OFICIALES, KELLY Y BAJAS AUTO)
# ==============================================================================
else:
    sport_p, league_c, nom_dep, sigma_m, cancha_k = "baseball", "mlb", "MLB Béisbol", 3.2, "mlb"

    st.sidebar.markdown(f"### 🏆 1. Equipos {nom_dep}")
    mapa_equipos_espn, mapa_logos_usa = obtener_catalogo_equipos_y_logos_espn(sport_p, league_c)
    if not mapa_equipos_espn:
        st.error(f"No se pudo conectar con el servidor en vivo de ESPN para {nom_dep}.")
        st.stop()

    lista_eq = sorted(list(mapa_equipos_espn.keys()))
    u_l = st.sidebar.selectbox("🏠 Local (Home)", lista_eq, index=0)
    u_v = st.sidebar.selectbox("✈️ Visita (Road)", lista_eq, index=1 if len(lista_eq) > 1 else 0)

    logo_u_l, fb_u_l = buscar_logo_equipo(u_l, mapa_logos_usa, "#ff6b00")
    logo_u_v, fb_u_v = buscar_logo_equipo(u_v, mapa_logos_usa, "#38bdf8")

    mult_bajas_ul, mult_bajas_uv, pct_b_ul, pct_b_uv = renderizar_panel_bajas_y_factor(sport_p, league_c, u_l, u_v, f"{league_c}_{u_l}_{u_v}")

    df_real_l = extraer_ultimos_partidos_reales_espn(sport_p, league_c, mapa_equipos_espn[u_l], u_l, n_partidos=8, condicion_filtro="ALL")
    df_real_v = extraer_ultimos_partidos_reales_espn(sport_p, league_c, mapa_equipos_espn[u_v], u_v, n_partidos=8, condicion_filtro="ALL")

    def_pts = 4.5
    pf_l = (float(df_real_l["Puntos/Carreras a Favor"].mean()) if not df_real_l.empty else def_pts) * mult_bajas_ul
    pa_l = float(df_real_l["Puntos/Carreras en Contra"].mean()) if not df_real_l.empty else def_pts
    pf_v = (float(df_real_v["Puntos/Carreras a Favor"].mean()) if not df_real_v.empty else def_pts) * mult_bajas_uv
    pa_v = float(df_real_v["Puntos/Carreras en Contra"].mean()) if not df_real_v.empty else def_pts

    proy_l = (pf_l + pa_v) / 2.0
    proy_v = (pf_v + pa_l) / 2.0
    tot_esp = proy_l + proy_v
    p_ml_l = float(1.0 - norm.cdf(0.0, loc=proy_l - proy_v, scale=sigma_m))
    p_ml_v = 1.0 - p_ml_l

    renderizar_hero_card_deporte(
        u_l, u_v, logo_u_l, fb_u_l, logo_u_v, fb_u_v,
        nom_dep.upper(),
        f"{proy_l:.1f}  —  {proy_v:.1f}",
        f"Total Esperado: {tot_esp:.1f} carreras",
        p_ml_l, None, p_ml_v, pct_b_ul, pct_b_uv
    )

    with st.expander(f"📋 TABLA DE AUDITORÍA {nom_dep}: Últimos partidos oficiales extraídos en vivo de ESPN ({u_l} vs {u_v})", expanded=False):
        st.success(f"✅ Datos de {nom_dep} extraídos 100% en tiempo real desde la API Oficial de ESPN (`site.api.espn.com`).")
        st.markdown(f"**🏠 Últimos {len(df_real_l)} partidos finalizados de {u_l}:**")
        if not df_real_l.empty:
            st.dataframe(df_real_l, use_container_width=True, hide_index=True)
        st.markdown(f"**✈️ Últimos {len(df_real_v)} partidos finalizados de {u_v}:**")
        if not df_real_v.empty:
            st.dataframe(df_real_v, use_container_width=True, hide_index=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 🟠 2. Cuotas Betano {nom_dep}")
    c_ul = st.sidebar.number_input(f"Gana {u_l}", 1.01, 25.0, round(1/max(p_ml_l*1.05, 0.05), 2), 0.05)
    c_uv = st.sidebar.number_input(f"Gana {u_v}", 1.01, 25.0, round(1/max(p_ml_v*1.05, 0.05), 2), 0.05)
    linea_u = st.sidebar.number_input("Línea Total Carreras", 3.5, 25.5, round(tot_esp*2)/2, 0.5)
    c_ov_u = st.sidebar.number_input(f"Cuota Over {linea_u}", 1.01, 15.0, 1.90, 0.05)
    c_un_u = st.sidebar.number_input(f"Cuota Under {linea_u}", 1.01, 15.0, 1.90, 0.05)

    p_ov_u = float(1.0 - norm.cdf(linea_u, loc=tot_esp, scale=sigma_m * 1.15))

    uk1, uk2, uk3 = st.columns(3)
    uk1.metric("🎯 Marcador Proyectado", f"{proy_l:.1f} - {proy_v:.1f}", f"Total Esperado: {tot_esp:.1f}")
    uk2.metric("🏆 Prob. Moneyline", f"{p_ml_l*100:.1f}% vs {p_ml_v*100:.1f}%")
    uk3.metric("📈 Prob. Over Línea", f"{p_ov_u*100:.1f}%", f"Línea: {linea_u}")

    CONFIG_BARRA_PROB = {"Prob. Real": st.column_config.ProgressColumn("Prob. Real (%)", format="%.1f%%", min_value=0, max_value=100)}
    utab1, utab2 = st.tabs(["🎯 1. Mercados Betano", "🔴 2. Radar En Vivo (In-Play)"])
    with utab1:
        m_u = [
            (f"Moneyline: Gana {u_l}", p_ml_l, c_ul),
            (f"Moneyline: Gana {u_v}", p_ml_v, c_uv),
            (f"Total: Más de {linea_u} (Over)", p_ov_u, c_ov_u),
            (f"Total: Menos de {linea_u} (Under)", 1.0 - p_ov_u, c_un_u)
        ]
        df_usa_m = construir_tabla_mercados_kelly(m_u, "Mercado", banca_usuario, fraccion_kelly_val, min_prob_filtro, min_edge_filtro)
        st.dataframe(df_usa_m.style.apply(resaltar_valor, axis=1), column_config=CONFIG_BARRA_PROB, use_container_width=True, hide_index=True)
    with utab2:
        mostrar_cancha_calor(u_l, u_v, p_ml_l*100, p_ml_v*100, 1.1, 1.0, cancha_k)
