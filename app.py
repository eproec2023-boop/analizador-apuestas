import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Pro Bet Analyzer 7.0 | Pre-Partido & Live Radar",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DISEÑO VISUAL PROFESIONAL (CSS PERSONALIZADO) ---
st.markdown("""
<style>
    .main-banner {
        background: linear-gradient(135deg, #18181b 0%, #27272a 60%, #ea580c 100%);
        padding: 24px 30px;
        border-radius: 14px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.12);
        border-left: 8px solid #ff6b00;
    }
    .main-banner h1 {
        color: #ffffff !important;
        margin: 0;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .main-banner p {
        color: #e4e4e7 !important;
        margin: 6px 0 0 0;
        font-size: 1.0rem;
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e4e4e7;
        border-top: 4px solid #ff6b00;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
    }
    button[data-baseweb="tab"] {
        font-size: 15px !important;
        font-weight: 700 !important;
    }
</style>

<div class="main-banner">
    <h1>🏆 PRO BET ANALYZER 7.0 <span style="color:#ff8c00;">| PRE-MATCH & LIVE RADAR</span></h1>
    <p>Motor Predictivo de Distribución de Poisson • Amortiguador Bayesiano • Mapa de Calor y Auditoría En Vivo (+EV) vs. Betano</p>
</div>
""", unsafe_allow_html=True)

# Función para colorear filas con Valor (+EV)
def resaltar_valor(fila):
    veredicto = str(fila.get("Veredicto", ""))
    if "✅" in veredicto or "🔥" in veredicto:
        return ['background-color: rgba(22, 163, 74, 0.15); font-weight: 600;'] * len(fila)
    return [''] * len(fila)

# Función para dibujar Cancha de Fútbol o Pista NHL con Mapa de Calor de Asedio en Vivo
def dibujar_cancha_calor(eq_loc, eq_vis, dom_loc, dom_vis, intensidad_loc, intensidad_vis, deporte="futbol"):
    bg_pitch = "linear-gradient(90deg, #14532d 0%, #166534 25%, #15803d 50%, #166534 75%, #14532d 100%)" if deporte == "futbol" else "linear-gradient(90deg, #e0f2fe 0%, #f0f9ff 50%, #e0f2fe 100%)"
    line_color = "rgba(255,255,255,0.65)" if deporte == "futbol" else "rgba(220,38,38,0.45)"
    text_color = "#ffffff" if deporte == "futbol" else "#0f172a"
    border_pitch = "#ffffff" if deporte == "futbol" else "#0284c7"

    op_loc = min(max(0.25 + (dom_loc / 100.0) * 0.65, 0.25), 0.88)
    op_vis = min(max(0.25 + (dom_vis / 100.0) * 0.65, 0.25), 0.88)
    rad_loc = int(90 + (intensidad_loc * 55))
    rad_vis = int(90 + (intensidad_vis * 55))

    html_code = f"""
    <div style="background:{bg_pitch}; border: 3px solid {border_pitch}; border-radius: 14px; height: 270px; position: relative; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,0.18); margin-bottom: 18px; font-family: sans-serif;">
        <!-- Línea central y círculo -->
        <div style="position:absolute; left:50%; top:0; bottom:0; width:3px; background:{line_color}; transform:translateX(-50%);"></div>
        <div style="position:absolute; left:50%; top:50%; width:84px; height:84px; border:3px solid {line_color}; border-radius:50%; transform:translate(-50%, -50%);"></div>
        <!-- Áreas -->
        <div style="position:absolute; left:0; top:22%; bottom:22%; width:15%; border-right:3px solid {line_color}; border-top:3px solid {line_color}; border-bottom:3px solid {line_color};"></div>
        <div style="position:absolute; right:0; top:22%; bottom:22%; width:15%; border-left:3px solid {line_color}; border-top:3px solid {line_color}; border-bottom:3px solid {line_color};"></div>

        <!-- Foco de Calor Ataque Local (Ataca de Izquierda a Derecha -> Zona Derecha) -->
        <div style="position:absolute; right:6%; top:50%; width:{rad_loc}px; height:{rad_loc}px; background:radial-gradient(circle, rgba(255,59,0,{op_loc}) 0%, rgba(255,145,0,{op_loc*0.6}) 45%, rgba(255,255,0,0) 75%); transform:translateY(-50%); border-radius:50%; pointer-events:none;"></div>
        <div style="position:absolute; right:22%; top:32%; width:{int(rad_loc*0.75)}px; height:{int(rad_loc*0.75)}px; background:radial-gradient(circle, rgba(255,115,0,{op_loc*0.8}) 0%, rgba(255,255,0,0) 70%); border-radius:50%; pointer-events:none;"></div>
        <div style="position:absolute; right:22%; top:68%; width:{int(rad_loc*0.75)}px; height:{int(rad_loc*0.75)}px; background:radial-gradient(circle, rgba(255,115,0,{op_loc*0.8}) 0%, rgba(255,255,0,0) 70%); border-radius:50%; pointer-events:none;"></div>

        <!-- Foco de Calor Ataque Visita (Ataca de Derecha a Izquierda -> Zona Izquierda) -->
        <div style="position:absolute; left:6%; top:50%; width:{rad_vis}px; height:{rad_vis}px; background:radial-gradient(circle, rgba(0,200,255,{op_vis}) 0%, rgba(0,110,255,{op_vis*0.6}) 45%, rgba(0,0,255,0) 75%); transform:translateY(-50%); border-radius:50%; pointer-events:none;"></div>
        <div style="position:absolute; left:22%; top:35%; width:{int(rad_vis*0.75)}px; height:{int(rad_vis*0.75)}px; background:radial-gradient(circle, rgba(56,189,248,{op_vis*0.8}) 0%, rgba(0,0,255,0) 70%); border-radius:50%; pointer-events:none;"></div>

        <!-- Etiquetas Superiores de Dominio Territorial -->
        <div style="position:absolute; left:16px; top:12px; background:rgba(15,23,42,0.82); color:#fff; padding:6px 12px; border-radius:8px; font-weight:700; font-size:13px; border-left: 4px solid #ff6b00;">
            🏠 {eq_loc} (Ataca ➔) | Presión: {dom_loc:.0f}%
        </div>
        <div style="position:absolute; right:16px; top:12px; background:rgba(15,23,42,0.82); color:#fff; padding:6px 12px; border-radius:8px; font-weight:700; font-size:13px; border-right: 4px solid #38bdf8;">
            Presión: {dom_vis:.0f}% | (⬅ Ataca) {eq_vis} ✈️
        </div>

        <!-- Leyenda Inferior -->
        <div style="position:absolute; left:50%; bottom:10px; transform:translateX(-50%); background:rgba(15,23,42,0.85); color:#f8fafc; padding:4px 16px; border-radius:20px; font-size:12px; font-weight:600; white-space:nowrap;">
            🔥 Rojo/Naranja: Zona de Asedio de {eq_loc} &nbsp;&nbsp;|&nbsp;&nbsp; ❄️ Azul Eléctrico: Zona de Asedio de {eq_vis}
        </div>
    </div>
    """
    return html_code

# --- SELECTOR MAESTRO DE DEPORTE ---
st.sidebar.markdown("### 🎯 Selector de Deporte")
deporte_activo = st.sidebar.radio(
    "Elige la disciplina a analizar:",
    ["⚽ Fútbol (11 Ligas Mundiales)", "🏒 NHL (Hockey sobre Hielo)"]
)
st.sidebar.markdown("---")

# ==============================================================================
# MÓDULO 1: FÚTBOL (11 LIGAS, REMATES, CÓRNERS, BAYESIANO + RADAR EN VIVO)
# ==============================================================================
LIGAS_EUROPA_CSV = {
    "🇮🇹 Serie A (Italia)": "https://www.football-data.co.uk/mmz4281/2627/I1.csv",
    "🇪🇸 LaLiga (España)": "https://www.football-data.co.uk/mmz4281/2627/SP1.csv",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)": "https://www.football-data.co.uk/mmz4281/2627/E0.csv",
    "🇩🇪 Bundesliga (Alemania)": "https://www.football-data.co.uk/mmz4281/2627/D1.csv",
    "🇫🇷 Ligue 1 (Francia)": "https://www.football-data.co.uk/mmz4281/2627/F1.csv",
    "🇵🇹 Primeira Liga (Portugal)": "https://www.football-data.co.uk/mmz4281/2627/P1.csv",
    "🇧🇪 Jupiler Pro League (Bélgica)": "https://www.football-data.co.uk/mmz4281/2627/B1.csv",
    "🇹🇷 Süper Lig (Turquía)": "https://www.football-data.co.uk/mmz4281/2627/T1.csv"
}

LIGAS_AMERICA = {
    "🇲🇽 Liga MX (México)": {
        "csv_extra": "https://www.football-data.co.uk/new/MEX.csv",
        "espn_code": "mex.1",
        "equipos_base": [
            "Club América", "Cruz Azul", "Toluca", "Tigres UANL", "Monterrey", 
            "Pumas UNAM", "Guadalajara", "Atlético San Luis", "Tijuana", "Atlas", 
            "León", "Juárez", "Necaxa", "Mazatlán FC", "Puebla", "Pachuca", "Querétaro", "Santos Laguna"
        ]
    },
    "🇺🇸 MLS (Estados Unidos)": {
        "csv_extra": "https://www.football-data.co.uk/new/USA.csv",
        "espn_code": "usa.1",
        "equipos_base": [
            "Inter Miami CF", "LA Galaxy", "LAFC", "Columbus Crew", "FC Cincinnati", 
            "Real Salt Lake", "Seattle Sounders FC", "Houston Dynamo FC", "Orlando City SC", 
            "Charlotte FC", "New York Red Bulls", "New York City FC", "Minnesota United FC", 
            "Vancouver Whitecaps", "Portland Timbers", "Colorado Rapids", "Atlanta United FC", "Austin FC"
        ]
    },
    "🇨🇴 Liga BetPlay (Colombia)": {
        "csv_extra": None,
        "espn_code": "col.1",
        "equipos_base": [
            "América de Cali", "Independiente Santa Fe", "Millonarios", "Atlético Nacional", 
            "Once Caldas", "Junior", "Deportes Tolima", "Deportivo Pasto", "Fortaleza CEIF", 
            "Independiente Medellín", "Atlético Bucaramanga", "Deportivo Pereira", 
            "Águilas Doradas", "La Equidad", "Patriotas Boyacá", "Alianza FC", 
            "Deportivo Cali", "Jaguares de Córdoba", "Boyacá Chicó", "Envigado"
        ]
    }
}

TODAS_LAS_LIGAS = list(LIGAS_EUROPA_CSV.keys()) + list(LIGAS_AMERICA.keys())

@st.cache_data(ttl=3600)
def cargar_europa_football_data(url):
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
        if len(df) < 5:
            raise ValueError("Pocos partidos, usar respaldo")
    except Exception:
        url_backup = url.replace("/2627/", "/2526/")
        df = pd.read_csv(url_backup)
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])

    equipos = sorted(df['HomeTeam'].unique())
    filas = []
    for eq in equipos:
        h = df[df['HomeTeam'] == eq]
        a = df[df['AwayTeam'] == eq]
        gf_h = float(h['FTHG'].mean()) if len(h) > 0 else 1.40
        gf_a = float(a['FTAG'].mean()) if len(a) > 0 else 1.15
        
        sh_h = float(h['HS'].dropna().mean()) if ('HS' in h and len(h['HS'].dropna()) > 0) else round(gf_h * 8.8, 1)
        sh_a = float(a['AS'].dropna().mean()) if ('AS' in a and len(a['AS'].dropna()) > 0) else round(gf_a * 8.5, 1)
        sot_h = float(h['HST'].dropna().mean()) if ('HST' in h and len(h['HST'].dropna()) > 0) else round(gf_h * 3.2, 1)
        sot_a = float(a['AST'].dropna().mean()) if ('AST' in a and len(a['AST'].dropna()) > 0) else round(gf_a * 3.0, 1)
        cor_h = float(h['HC'].dropna().mean()) if ('HC' in h and len(h['HC'].dropna()) > 0) else 5.4
        cor_a = float(a['AC'].dropna().mean()) if ('AC' in a and len(a['AC'].dropna()) > 0) else 4.4

        filas.append({
            'Equipo': eq,
            'PJ_Home': int(len(h)),
            'PJ_Away': int(len(a)),
            'GF_Home': gf_h,
            'GC_Home': float(h['FTAG'].mean()) if len(h) > 0 else 1.15,
            'GF_Away': gf_a,
            'GC_Away': float(a['FTHG'].mean()) if len(a) > 0 else 1.40,
            'Shots_Home': sh_h,
            'Shots_Away': sh_a,
            'SoT_Home': sot_h,
            'SoT_Away': sot_a,
            'Corners_Home': cor_h,
            'Corners_Away': cor_a
        })
    return pd.DataFrame(filas)

@st.cache_data(ttl=3600)
def cargar_america_datos(nombre_liga):
    info = LIGAS_AMERICA[nombre_liga]
    if info["csv_extra"]:
        try:
            df = pd.read_csv(info["csv_extra"])
            df = df.dropna(subset=['Home', 'Away', 'HG', 'AG']).tail(180)
            equipos = sorted(df['Home'].unique())
            filas = []
            for eq in equipos:
                h = df[df['Home'] == eq]
                a = df[df['Away'] == eq]
                gf_h = float(h['HG'].mean()) if len(h) > 0 else 1.45
                gf_a = float(a['AG'].mean()) if len(a) > 0 else 1.15
                filas.append({
                    'Equipo': eq,
                    'PJ_Home': int(len(h)),
                    'PJ_Away': int(len(a)),
                    'GF_Home': gf_h,
                    'GC_Home': float(h['AG'].mean()) if len(h) > 0 else 1.15,
                    'GF_Away': gf_a,
                    'GC_Away': float(a['HG'].mean()) if len(a) > 0 else 1.45,
                    'Shots_Home': round(gf_h * 8.5, 1),
                    'Shots_Away': round(gf_a * 8.5, 1),
                    'SoT_Home': round(gf_h * 3.1, 1),
                    'SoT_Away': round(gf_a * 3.1, 1),
                    'Corners_Home': 5.4,
                    'Corners_Away': 4.3
                })
            if len(filas) > 5:
                return pd.DataFrame(filas)
        except Exception:
            pass

    try:
        url_espn = f"https://site.api.espn.com/apis/v2/sports/soccer/{info['espn_code']}/standings"
        r = requests.get(url_espn, timeout=6).json()
        entries = r['children'][0]['standings']['entries']
        filas = []
        for item in entries:
            nombre = item['team']['displayName']
            stats = {s['name']: s['value'] for s in item['stats']}
            pj = max(int(stats.get('gamesPlayed', 10)), 1)
            gf = stats.get('pointsFor', 13) / pj
            gc = stats.get('pointsAgainst', 13) / pj
            filas.append({
                'Equipo': nombre,
                'PJ_Home': max(pj // 2, 1),
                'PJ_Away': max(pj // 2, 1),
                'GF_Home': round(gf * 1.15, 2),
                'GC_Home': round(gc * 0.85, 2),
                'GF_Away': round(gf * 0.85, 2),
                'GC_Away': round(gc * 1.15, 2),
                'Shots_Home': round(gf * 9.0, 1),
                'Shots_Away': round(gf * 7.5, 1),
                'SoT_Home': round(gf * 3.3, 1),
                'SoT_Away': round(gf * 2.7, 1),
                'Corners_Home': 5.3,
                'Corners_Away': 4.2
            })
        if len(filas) > 5:
            return pd.DataFrame(filas).sort_values('Equipo')
    except Exception:
        pass

    filas = []
    for eq in sorted(info["equipos_base"]):
        filas.append({
            'Equipo': eq, 'PJ_Home': 6, 'PJ_Away': 6,
            'GF_Home': 1.45, 'GC_Home': 1.05, 'GF_Away': 1.10, 'GC_Away': 1.40,
            'Shots_Home': 13.5, 'Shots_Away': 10.5, 'SoT_Home': 4.6, 'SoT_Away': 3.6,
            'Corners_Home': 5.4, 'Corners_Away': 4.3
        })
    return pd.DataFrame(filas)


# ==============================================================================
# MÓDULO 2: EXTRACCIÓN AUTOMÁTICA NHL (API OFICIAL NHL + ESPN BACKUP)
# ==============================================================================
EQUIPOS_NHL_BASE = [
    "Boston Bruins", "Florida Panthers", "Toronto Maple Leafs", "Tampa Bay Lightning",
    "New York Rangers", "Carolina Hurricanes", "New Jersey Devils", "New York Islanders",
    "Dallas Stars", "Colorado Avalanche", "Winnipeg Jets", "Nashville Predators",
    "Edmonton Oilers", "Vancouver Canucks", "Vegas Golden Knights", "Los Angeles Kings",
    "Minnesota Wild", "St. Louis Blues", "Utah Hockey Club", "Calgary Flames",
    "Washington Capitals", "Pittsburgh Penguins", "Philadelphia Flyers", "Columbus Blue Jackets",
    "Detroit Red Wings", "Buffalo Sabres", "Ottawa Senators", "Montreal Canadiens",
    "Seattle Kraken", "Anaheim Ducks", "Chicago Blackhawks", "San Jose Sharks"
]

@st.cache_data(ttl=3600)
def cargar_datos_nhl():
    try:
        r = requests.get("https://api-web.nhle.com/v1/standings/now", timeout=6).json()
        standings = r.get("standings", [])
        filas = []
        for t in standings:
            nombre = t.get("teamName", {}).get("default", "NHL Team")
            pj_h = max(int(t.get("homeGamesPlayed", 1)), 1)
            pj_a = max(int(t.get("roadGamesPlayed", 1)), 1)
            gf_h = float(t.get("homeGoalsFor", 3 * pj_h)) / pj_h
            gc_h = float(t.get("homeGoalsAgainst", 3 * pj_h)) / pj_h
            gf_a = float(t.get("roadGoalsFor", 3 * pj_a)) / pj_a
            gc_a = float(t.get("roadGoalsAgainst", 3 * pj_a)) / pj_a
            
            sog_h = round(np.clip(26.0 + (gf_h - 2.6) * 3.8, 24.0, 36.5), 1)
            sog_a = round(np.clip(25.0 + (gf_a - 2.5) * 3.8, 23.0, 35.5), 1)
            
            filas.append({
                "Equipo": nombre,
                "PJ_Home": pj_h,
                "PJ_Away": pj_a,
                "GF_Home": round(gf_h, 2),
                "GC_Home": round(gc_h, 2),
                "GF_Away": round(gf_a, 2),
                "GC_Away": round(gc_a, 2),
                "SOG_Home": sog_h,
                "SOG_Away": sog_a
            })
        if len(filas) >= 16:
            return pd.DataFrame(filas).sort_values("Equipo")
    except Exception:
        pass

    try:
        url_espn = "https://site.api.espn.com/apis/v2/sports/hockey/nhl/standings"
        r = requests.get(url_espn, timeout=6).json()
        filas = []
        for child in r.get("children", []):
            for item in child.get("standings", {}).get("entries", []):
                nombre = item["team"]["displayName"]
                stats = {s["name"]: s["value"] for s in item.get("stats", [])}
                pj = max(int(stats.get("gamesPlayed", 10)), 1)
                gf = float(stats.get("pointsFor", 31)) / pj
                gc = float(stats.get("pointsAgainst", 31)) / pj
                filas.append({
                    "Equipo": nombre,
                    "PJ_Home": max(pj // 2, 1),
                    "PJ_Away": max(pj // 2, 1),
                    "GF_Home": round(gf * 1.06, 2),
                    "GC_Home": round(gc * 0.94, 2),
                    "GF_Away": round(gf * 0.94, 2),
                    "GC_Away": round(gc * 1.06, 2),
                    "SOG_Home": round(gf * 9.8, 1),
                    "SOG_Away": round(gf * 9.4, 1)
                })
        if len(filas) >= 16:
            return pd.DataFrame(filas).sort_values("Equipo")
    except Exception:
        pass

    filas = []
    for eq in sorted(EQUIPOS_NHL_BASE):
        filas.append({
            "Equipo": eq, "PJ_Home": 8, "PJ_Away": 8,
            "GF_Home": 3.25, "GC_Home": 2.95, "GF_Away": 2.95, "GC_Away": 3.25,
            "SOG_Home": 31.2, "SOG_Away": 29.4
        })
    return pd.DataFrame(filas)


# ==============================================================================
# EJECUCIÓN SEGÚN EL DEPORTE SELECCIONADO
# ==============================================================================
if deporte_activo == "⚽ Fútbol (11 Ligas Mundiales)":
    st.sidebar.markdown("### 🏆 1. Competición y Encuentro")
    liga_elegida = st.sidebar.selectbox("Selecciona la Liga", TODAS_LAS_LIGAS)

    if liga_elegida in LIGAS_EUROPA_CSV:
        df_liga = cargar_europa_football_data(LIGAS_EUROPA_CSV[liga_elegida])
    else:
        df_liga = cargar_america_datos(liga_elegida)

    lista_equipos = df_liga['Equipo'].tolist()

    col_sb1, col_sb2 = st.sidebar.columns(2)
    equipo_local = col_sb1.selectbox("🏠 Local", lista_equipos, index=0)
    equipo_visita = col_sb2.selectbox("✈️ Visita", lista_equipos, index=1 if len(lista_equipos) > 1 else 0)

    usar_amortiguador = st.sidebar.checkbox(
        "🛡️ Amortiguador Bayesiano (< 6 PJ)", 
        value=True,
        help="Suaviza promedios extremos cuando un club lleva menos de 6 partidos de local o visitante, ponderándolos con la media de la liga."
    )

    row_loc = df_liga[df_liga['Equipo'] == equipo_local].iloc[0]
    row_vis = df_liga[df_liga['Equipo'] == equipo_visita].iloc[0]

    media_gf_home = float(df_liga['GF_Home'].mean())
    media_gc_home = float(df_liga['GC_Home'].mean())
    media_gf_away = float(df_liga['GF_Away'].mean())
    media_gc_away = float(df_liga['GC_Away'].mean())
    media_goles_liga = (media_gf_home + media_gf_away) / 2.0

    pj_loc = int(row_loc['PJ_Home'])
    pj_vis = int(row_vis['PJ_Away'])

    peso_loc = min(pj_loc / 6.0, 1.0) if usar_amortiguador else 1.0
    peso_vis = min(pj_vis / 6.0, 1.0) if usar_amortiguador else 1.0

    gf_loc_calc = (peso_loc * float(row_loc['GF_Home'])) + ((1.0 - peso_loc) * media_gf_home)
    gc_loc_calc = (peso_loc * float(row_loc['GC_Home'])) + ((1.0 - peso_loc) * media_gc_home)
    gf_vis_calc = (peso_vis * float(row_vis['GF_Away'])) + ((1.0 - peso_vis) * media_gf_away)
    gc_vis_calc = (peso_vis * float(row_vis['GC_Away'])) + ((1.0 - peso_vis) * media_gc_away)

    with st.sidebar.expander("⚙️ Auditoría / Ajuste Manual de Datos"):
        st.caption(f"Muestra: {equipo_local} ({pj_loc} PJ Casa) | {equipo_visita} ({pj_vis} PJ Visita)")
        xg_favor_local = st.number_input("Goles/xG a Favor (Local)", min_value=0.1, max_value=5.0, value=round(gf_loc_calc, 2), step=0.05)
        xg_contra_local = st.number_input("Goles/xG en Contra (Local)", min_value=0.1, max_value=5.0, value=round(gc_loc_calc, 2), step=0.05)
        xg_favor_visita = st.number_input("Goles/xG a Favor (Visita)", min_value=0.1, max_value=5.0, value=round(gf_vis_calc, 2), step=0.05)
        xg_contra_visita = st.number_input("Goles/xG en Contra (Visita)", min_value=0.1, max_value=5.0, value=round(gc_vis_calc, 2), step=0.05)
        promedio_liga = st.number_input("Promedio Goles de la Liga", min_value=0.5, max_value=3.0, value=round(media_goles_liga, 2), step=0.05)
        
        st.markdown("---")
        remates_local = st.number_input("Remates Totales (Local)", min_value=1.0, max_value=30.0, value=round(float(row_loc['Shots_Home']), 1), step=0.5)
        remates_visita = st.number_input("Remates Totales (Visita)", min_value=1.0, max_value=30.0, value=round(float(row_vis['Shots_Away']), 1), step=0.5)
        puerta_local = st.number_input("Remates a Puerta (Local)", min_value=0.5, max_value=15.0, value=round(float(row_loc['SoT_Home']), 1), step=0.1)
        puerta_visita = st.number_input("Remates a Puerta (Visita)", min_value=0.5, max_value=15.0, value=round(float(row_vis['SoT_Away']), 1), step=0.1)
        corners_local = st.number_input("Córners Promedio (Local)", min_value=0.5, max_value=15.0, value=round(float(row_loc['Corners_Home']), 1), step=0.1)
        corners_visita = st.number_input("Córners Promedio (Visita)", min_value=0.5, max_value=15.0, value=round(float(row_vis['Corners_Away']), 1), step=0.1)

    # MOTOR MATEMÁTICO POISSON FÚTBOL PRE-PARTIDO
    lam_loc = max((xg_favor_local * xg_contra_visita) / max(promedio_liga, 0.5), 0.1)
    lam_vis = max((xg_favor_visita * xg_contra_local) / max(promedio_liga, 0.5), 0.1)

    matriz_prob = np.zeros((8, 8))
    for i in range(8):
        for j in range(8):
            matriz_prob[i, j] = poisson.pmf(i, lam_loc) * poisson.pmf(j, lam_vis)

    prob_1 = float(np.sum(np.tril(matriz_prob, -1)))
    prob_x = float(np.sum(np.diag(matriz_prob)))
    prob_2 = float(np.sum(np.triu(matriz_prob, 1)))
    prob_under25 = float(matriz_prob[0,0] + matriz_prob[1,0] + matriz_prob[0,1] + matriz_prob[2,0] + matriz_prob[0,2] + matriz_prob[1,1])
    prob_over25 = 1.0 - prob_under25
    prob_btts_no = float(np.sum(matriz_prob[0, :]) + np.sum(matriz_prob[:, 0]) - matriz_prob[0, 0])
    prob_btts_si = 1.0 - prob_btts_no

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas en Betano (Goles)")
    margen = 1.055
    c_sug_1 = round(max(1.05, 1 / (max(prob_1, 0.05) * margen)), 2)
    c_sug_x = round(max(1.05, 1 / (max(prob_x, 0.05) * margen)), 2)
    c_sug_2 = round(max(1.05, 1 / (max(prob_2, 0.05) * margen)), 2)

    c_sb1, c_sb2, c_sb3 = st.sidebar.columns(3)
    cuota_1 = c_sb1.number_input("Local (1)", min_value=1.01, value=c_sug_1, step=0.05)
    cuota_x = c_sb2.number_input("Empate (X)", min_value=1.01, value=c_sug_x, step=0.05)
    cuota_2 = c_sb3.number_input("Visita (2)", min_value=1.01, value=c_sug_2, step=0.05)

    c_sb4, c_sb5 = st.sidebar.columns(2)
    cuota_over25 = c_sb4.number_input("Over 2.5 Goles", min_value=1.01, value=1.85, step=0.05)
    cuota_under25 = c_sb5.number_input("Under 2.5 Goles", min_value=1.01, value=1.95, step=0.05)

    c_sb6, c_sb7 = st.sidebar.columns(2)
    cuota_btts_si = c_sb6.number_input("Ambos Anotan SÍ", min_value=1.01, value=1.80, step=0.05)
    cuota_btts_no = c_sb7.number_input("Ambos Anotan NO", min_value=1.01, value=1.95, step=0.05)

    with st.sidebar.expander("📏 Cuotas y Líneas de Remates / Córners"):
        linea_remates = st.number_input("Línea Remates Totales", min_value=10.5, max_value=40.5, value=24.5, step=1.0)
        cuota_over_rem = st.number_input("Cuota Over Remates", min_value=1.01, value=1.85, step=0.05)
        
        linea_puerta = st.number_input("Línea Remates a Puerta", min_value=3.5, max_value=20.5, value=8.5, step=1.0)
        cuota_over_pue = st.number_input("Cuota Over a Puerta", min_value=1.01, value=1.85, step=0.05)
        
        linea_corners = st.number_input("Línea Córners Totales", min_value=4.5, max_value=20.5, value=9.5, step=1.0)
        cuota_over_cor = st.number_input("Cuota Over Córners", min_value=1.01, value=1.85, step=0.05)

    lam_remates = remates_local + remates_visita
    prob_over_remates = 1.0 - sum(poisson.pmf(k, lam_remates) for k in range(int(linea_remates) + 1))

    lam_puerta = puerta_local + puerta_visita
    prob_over_puerta = 1.0 - sum(poisson.pmf(k, lam_puerta) for k in range(int(linea_puerta) + 1))

    lam_corners = corners_local + corners_visita
    prob_over_corners = 1.0 - sum(poisson.pmf(k, lam_corners) for k in range(int(linea_corners) + 1))

    st.markdown(f"### 🏟️ {equipo_local} vs. {equipo_visita} <span style='font-size:16px; color:#71717a; font-weight:normal;'>({liga_elegida})</span>", unsafe_allow_html=True)

    if usar_amortiguador and (pj_loc < 6 or pj_vis < 6):
        st.caption(f"🛡️ **Amortiguador Bayesiano Activo:** Muestra ponderada con la media de la liga ({media_goles_liga:.2f} goles) por pocos partidos jugados ({equipo_local}: {pj_loc} PJ Casa | {equipo_visita}: {pj_vis} PJ Visita).")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("⚽ Proyección de Goles (xG)", f"{lam_loc:.2f} - {lam_vis:.2f}", f"Total esperado: {lam_loc+lam_vis:.2f} goles")
    k2.metric("🎯 Remates Totales Esp.", f"{lam_remates:.1f} tiros", f"{remates_local:.1f} Local + {remates_visita:.1f} Visita")
    k3.metric("🥅 Remates a Puerta Esp.", f"{lam_puerta:.1f} al arco", f"{puerta_local:.1f} Local + {puerta_visita:.1f} Visita")
    k4.metric("⛳ Córners Proyectados", f"{lam_corners:.1f} esquinas", f"{corners_local:.1f} Local + {corners_visita:.1f} Visita")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 1. Mercados de Goles y 1X2", 
        "⛳ 2. Mercados de Remates y Córners", 
        "🔢 3. Matriz Exacta de Poisson",
        "🔴 4. Radar En Vivo (In-Play)"
    ])

    with tab1:
        mercados_g = [
            (f"Gana {equipo_local} (1)", prob_1, cuota_1),
            ("Empate (X)", prob_x, cuota_x),
            (f"Gana {equipo_visita} (2)", prob_2, cuota_2),
            ("Más de 2.5 Goles (Over)", prob_over25, cuota_over25),
            ("Menos de 2.5 Goles (Under)", prob_under25, cuota_under25),
            ("Ambos Equipos Anotan - SÍ", prob_btts_si, cuota_btts_si),
            ("Ambos Equipos Anotan - NO", prob_btts_no, cuota_btts_no)
        ]
        filas_g = []
        for m, p, c in mercados_g:
            justa = 1 / p if p > 0 else 99.0
            edge = (p * c) - 1
            filas_g.append({
                "Mercado en Betano": m,
                "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Mínima Justa": f"{justa:.2f}",
                "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
            })
        df_g = pd.DataFrame(filas_g)
        st.dataframe(df_g.style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with tab2:
        mercados_e = [
            (f"Más de {linea_remates} Remates Totales (Over)", prob_over_remates, cuota_over_rem),
            (f"Menos de {linea_remates} Remates Totales (Under)", 1.0 - prob_over_remates, 1.85),
            (f"Más de {linea_puerta} Remates a Puerta (Over)", prob_over_puerta, cuota_over_pue),
            (f"Menos de {linea_puerta} Remates a Puerta (Under)", 1.0 - prob_over_puerta, 1.85),
            (f"Más de {linea_corners} Córners Totales (Over)", prob_over_corners, cuota_over_cor),
            (f"Menos de {linea_corners} Córners Totales (Under)", 1.0 - prob_over_corners, 1.85),
        ]
        filas_e = []
        for m, p, c in mercados_e:
            justa = 1 / p if p > 0 else 99.0
            edge = (p * c) - 1
            filas_e.append({
                "Mercado Especial": m,
                "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Mínima Justa": f"{justa:.2f}",
                "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
            })
        df_e = pd.DataFrame(filas_e)
        st.dataframe(df_e.style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with tab3:
        st.caption("Probabilidad matemática exacta para cada marcador final entre 0 y 5 goles por equipo:")
        df_matriz = pd.DataFrame(
            matriz_prob[:6, :6] * 100, 
            index=[f"🏠 {equipo_local} ({i})" for i in range(6)], 
            columns=[f"✈️ {equipo_visita} ({j})" for j in range(6)]
        )
        st.dataframe(df_matriz.style.format("{:.1f}%").background_gradient(cmap="YlOrBr"), use_container_width=True)

    with tab4:
        st.markdown("#### 🔴 Escáner Táctico de Presión y Recálculo de Poisson en Tiempo Real")
        st.caption("Ingresa los datos actuales del partido en vivo (Sofascore / Betano) para visualizar el mapa de calor de asedio y detectar cuotas desajustadas en los minutos restantes:")

        lc1, lc2, lc3, lc4 = st.columns(4)
        min_actual = lc1.slider("⏱️ Minuto Actual", min_value=1, max_value=90, value=60)
        goles_vivo_loc = lc2.number_input(f"⚽ Goles {equipo_local}", min_value=0, max_value=10, value=1)
        goles_vivo_vis = lc3.number_input(f"⚽ Goles {equipo_visita}", min_value=0, max_value=10, value=1)
        posesion_loc = lc4.slider(f"📊 Posesión {equipo_local} (%)", min_value=20, max_value=80, value=54)

        ls1, ls2, ls3, ls4 = st.columns(4)
        sot_vivo_loc = ls1.number_input(f"🥅 A Puerta {equipo_local} (En Vivo)", min_value=0, max_value=25, value=4)
        sot_vivo_vis = ls2.number_input(f"🥅 A Puerta {equipo_visita} (En Vivo)", min_value=0, max_value=25, value=2)
        cor_vivo_loc = ls3.number_input(f"⛳ Córners {equipo_local} (En Vivo)", min_value=0, max_value=25, value=5)
        cor_vivo_vis = ls4.number_input(f"⛳ Córners {equipo_visita} (En Vivo)", min_value=0, max_value=25, value=3)

        # Cálculo de Índice de Presión Ofensiva (Momentum)
        puntos_presion_loc = (sot_vivo_loc * 3.0) + (cor_vivo_loc * 1.2) + (posesion_loc * 0.12) + 0.5
        puntos_presion_vis = (sot_vivo_vis * 3.0) + (cor_vivo_vis * 1.2) + ((100 - posesion_loc) * 0.12) + 0.5
        dom_loc_pct = (puntos_presion_loc / (puntos_presion_loc + puntos_presion_vis)) * 100.0
        dom_vis_pct = 100.0 - dom_loc_pct

        # Ritmo real vs esperado en el minuto actual
        fraccion_jugada = max(min_actual / 94.0, 0.08)
        fraccion_restante = max((94.0 - min_actual) / 94.0, 0.03)

        ritmo_sot_loc = (sot_vivo_loc / fraccion_jugada) / max(puerta_local, 1.5)
        ritmo_sot_vis = (sot_vivo_vis / fraccion_jugada) / max(puerta_visita, 1.5)

        factor_ritmo_loc = np.clip(0.65 + 0.35 * ritmo_sot_loc, 0.65, 1.55)
        factor_ritmo_vis = np.clip(0.65 + 0.35 * ritmo_sot_vis, 0.65, 1.55)

        # Urgencia según marcador actual (Game State)
        urg_loc = 1.18 if goles_vivo_loc < goles_vivo_vis else (1.06 if goles_vivo_loc == goles_vivo_vis else 0.90)
        urg_vis = 1.18 if goles_vivo_vis < goles_vivo_loc else (1.06 if goles_vivo_loc == goles_vivo_vis else 0.90)

        lam_rest_loc = max(lam_loc * fraccion_restante * factor_ritmo_loc * urg_loc, 0.04)
        lam_rest_vis = max(lam_vis * fraccion_restante * factor_ritmo_vis * urg_vis, 0.04)
        lam_rest_total = lam_rest_loc + lam_rest_vis

        # Renderizar Cancha con Mapa de Calor
        st.markdown(dibujar_cancha_calor(equipo_local, equipo_visita, dom_loc_pct, dom_vis_pct, factor_ritmo_loc, factor_ritmo_vis, "futbol"), unsafe_allow_html=True)

        # Probabilidades Poisson del Tiempo Restante
        mat_rest = np.zeros((7, 7))
        for i in range(7):
            for j in range(7):
                mat_rest[i, j] = poisson.pmf(i, lam_rest_loc) * poisson.pmf(j, lam_rest_vis)

        p_1_mas_gol = 1.0 - poisson.pmf(0, lam_rest_total)
        p_2_mas_goles = 1.0 - (poisson.pmf(0, lam_rest_total) + poisson.pmf(1, lam_rest_total))
        p_prox_gol_loc = (lam_rest_loc / lam_rest_total) * p_1_mas_gol
        p_prox_gol_vis = (lam_rest_vis / lam_rest_total) * p_1_mas_gol

        # Probabilidad del resultado final partiendo del marcador actual
        p_final_1, p_final_x, p_final_2 = 0.0, 0.0, 0.0
        for i in range(7):
            for j in range(7):
                g_fin_l = goles_vivo_loc + i
                g_fin_v = goles_vivo_vis + j
                if g_fin_l > g_fin_v:
                    p_final_1 += mat_rest[i, j]
                elif g_fin_l == g_fin_v:
                    p_final_x += mat_rest[i, j]
                else:
                    p_final_2 += mat_rest[i, j]

        goles_actuales_tot = goles_vivo_loc + goles_vivo_vis
        linea_vivo_1 = goles_actuales_tot + 0.5
        linea_vivo_2 = goles_actuales_tot + 1.5

        st.markdown("##### 🟠 Introduce las Cuotas EN VIVO de Betano para auditar el valor:")
        q1, q2, q3, q4 = st.columns(4)
        c_vivo_1gol = q1.number_input(f"Cuota Más de {linea_vivo_1} Goles (+1 gol más)", min_value=1.01, value=round(max(1.08, 1/max(p_1_mas_gol*1.06, 0.05)), 2), step=0.05)
        c_vivo_prox_l = q2.number_input(f"Cuota Próximo Gol: {equipo_local}", min_value=1.01, value=round(max(1.10, 1/max(p_prox_gol_loc*1.06, 0.05)), 2), step=0.05)
        c_vivo_prox_v = q3.number_input(f"Cuota Próximo Gol: {equipo_visita}", min_value=1.01, value=round(max(1.10, 1/max(p_prox_gol_vis*1.06, 0.05)), 2), step=0.05)
        c_vivo_gana_l = q4.number_input(f"Cuota Gana {equipo_local} (En Vivo)", min_value=1.01, value=round(max(1.05, 1/max(p_final_1*1.06, 0.05)), 2), step=0.05)

        mercados_vivo = [
            (f"Más de {linea_vivo_1} Goles en el Partido (1+ gol en lo que resta)", p_1_mas_gol, c_vivo_1gol),
            (f"Más de {linea_vivo_2} Goles en el Partido (2+ goles en lo que resta)", p_2_mas_goles, round(max(1.20, 1/max(p_2_mas_goles*1.07, 0.04)), 2)),
            (f"Próximo Gol en Vivo: Anota {equipo_local}", p_prox_gol_loc, c_vivo_prox_l),
            (f"Próximo Gol en Vivo: Anota {equipo_visita}", p_prox_gol_vis, c_vivo_prox_v),
            (f"Resultado Final (Partiendo de {goles_vivo_loc}-{goles_vivo_vis}): Gana {equipo_local}", p_final_1, c_vivo_gana_l),
            (f"Resultado Final (Partiendo de {goles_vivo_loc}-{goles_vivo_vis}): Empate", p_final_x, round(max(1.10, 1/max(p_final_x*1.06, 0.05)), 2)),
            (f"Resultado Final (Partiendo de {goles_vivo_loc}-{goles_vivo_vis}): Gana {equipo_visita}", p_final_2, round(max(1.10, 1/max(p_final_2*1.06, 0.05)), 2))
        ]

        filas_vivo = []
        for m, p, c in mercados_vivo:
            justa = 1 / p if p > 0 else 99.0
            edge = (p * c) - 1
            filas_vivo.append({
                "Mercado En Vivo (In-Play)": m,
                "Prob. Tiempo Restante (%)": f"{p*100:.1f}%",
                "Cuota Justa En Vivo": f"{justa:.2f}",
                "Cuota Betano En Vivo": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "🔥 ENTRAR EN VIVO (+EV)" if edge > 0.04 else "❄️ Esperar / Sin valor"
            })
        df_vivo = pd.DataFrame(filas_vivo)
        st.dataframe(df_vivo.style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)


# ==============================================================================
# EJECUCIÓN MÓDULO 2: NHL (HOCKEY SOBRE HIELO - MULTI-MERCADOS + RADAR EN VIVO)
# ==============================================================================
else:
    st.sidebar.markdown("### 🏒 1. Selección de Partido NHL")
    df_nhl = cargar_datos_nhl()
    lista_nhl = df_nhl["Equipo"].tolist()

    col_nhl1, col_nhl2 = st.sidebar.columns(2)
    nhl_local = col_nhl1.selectbox("🏠 Local (Home)", lista_nhl, index=0)
    nhl_visita = col_nhl2.selectbox("✈️ Visita (Road)", lista_nhl, index=1 if len(lista_nhl) > 1 else 0)

    usar_bayes_nhl = st.sidebar.checkbox(
        "🛡️ Amortiguador Bayesiano NHL (< 8 PJ)", 
        value=True,
        help="Estabiliza promedios de goles en el arranque de temporada NHL ponderando con la media de la liga (~3.10 G/p)."
    )

    row_nhl_loc = df_nhl[df_nhl["Equipo"] == nhl_local].iloc[0]
    row_nhl_vis = df_nhl[df_nhl["Equipo"] == nhl_visita].iloc[0]

    media_gf_h_nhl = float(df_nhl["GF_Home"].mean())
    media_gc_h_nhl = float(df_nhl["GC_Home"].mean())
    media_gf_a_nhl = float(df_nhl["GF_Away"].mean())
    media_gc_a_nhl = float(df_nhl["GC_Away"].mean())
    media_liga_nhl = (media_gf_h_nhl + media_gf_a_nhl) / 2.0

    pj_nhl_loc = int(row_nhl_loc["PJ_Home"])
    pj_nhl_vis = int(row_nhl_vis["PJ_Away"])

    peso_nhl_loc = min(pj_nhl_loc / 8.0, 1.0) if usar_bayes_nhl else 1.0
    peso_nhl_vis = min(pj_nhl_vis / 8.0, 1.0) if usar_bayes_nhl else 1.0

    gf_nhl_loc_c = (peso_nhl_loc * float(row_nhl_loc["GF_Home"])) + ((1.0 - peso_nhl_loc) * media_gf_h_nhl)
    gc_nhl_loc_c = (peso_nhl_loc * float(row_nhl_loc["GC_Home"])) + ((1.0 - peso_nhl_loc) * media_gc_h_nhl)
    gf_nhl_vis_c = (peso_nhl_vis * float(row_nhl_vis["GF_Away"])) + ((1.0 - peso_nhl_vis) * media_gf_a_nhl)
    gc_nhl_vis_c = (peso_nhl_vis * float(row_nhl_vis["GC_Away"])) + ((1.0 - peso_nhl_vis) * media_gc_a_nhl)

    with st.sidebar.expander("⚙️ Auditoría / Ajuste Manual NHL (Goles y SOG)"):
        st.caption(f"Muestra API NHL: {nhl_local} ({pj_nhl_loc} PJ Casa) | {nhl_visita} ({pj_nhl_vis} PJ Ruta)")
        nhl_gf_loc = st.number_input("Goles a Favor Local (60m/OT)", min_value=0.5, max_value=7.0, value=round(gf_nhl_loc_c, 2), step=0.05)
        nhl_gc_loc = st.number_input("Goles en Contra Local", min_value=0.5, max_value=7.0, value=round(gc_nhl_loc_c, 2), step=0.05)
        nhl_gf_vis = st.number_input("Goles a Favor Visita (60m/OT)", min_value=0.5, max_value=7.0, value=round(gf_nhl_vis_c, 2), step=0.05)
        nhl_gc_vis = st.number_input("Goles en Contra Visita", min_value=0.5, max_value=7.0, value=round(gc_nhl_vis_c, 2), step=0.05)
        nhl_media = st.number_input("Promedio Goles NHL por Equipo", min_value=1.5, max_value=5.0, value=round(media_liga_nhl, 2), step=0.05)
        st.markdown("---")
        sog_loc_in = st.number_input("Disparos al Arco (SOG Local)", min_value=15.0, max_value=45.0, value=float(row_nhl_loc["SOG_Home"]), step=0.5)
        sog_vis_in = st.number_input("Disparos al Arco (SOG Visita)", min_value=15.0, max_value=45.0, value=float(row_nhl_vis["SOG_Away"]), step=0.5)

    # MOTOR MATEMÁTICO NHL PRE-PARTIDO
    lam_nhl_loc = max((nhl_gf_loc * nhl_gc_vis) / max(nhl_media, 1.0), 0.5)
    lam_nhl_vis = max((nhl_gf_vis * nhl_gc_loc) / max(nhl_media, 1.0), 0.5)
    lam_nhl_total = lam_nhl_loc + lam_nhl_vis

    max_g_nhl = 13
    mat_nhl = np.zeros((max_g_nhl, max_g_nhl))
    for i in range(max_g_nhl):
        for j in range(max_g_nhl):
            mat_nhl[i, j] = poisson.pmf(i, lam_nhl_loc) * poisson.pmf(j, lam_nhl_vis)

    p_reg_loc = float(np.sum(np.tril(mat_nhl, -1)))
    p_reg_emp = float(np.sum(np.diag(mat_nhl)))
    p_reg_vis = float(np.sum(np.triu(mat_nhl, 1)))

    ratio_ot_loc = lam_nhl_loc / (lam_nhl_loc + lam_nhl_vis)
    p_ml_loc = p_reg_loc + (p_reg_emp * ratio_ot_loc)
    p_ml_vis = p_reg_vis + (p_reg_emp * (1.0 - ratio_ot_loc))

    p_pl_loc_menos15 = float(np.sum(np.tril(mat_nhl, -2)))
    p_pl_vis_mas15 = 1.0 - p_pl_loc_menos15

    lam_1p_total = lam_nhl_total * 0.29
    p_1p_over15 = 1.0 - (poisson.pmf(0, lam_1p_total) + poisson.pmf(1, lam_1p_total))
    p_1p_under15 = 1.0 - p_1p_over15
    p_1p_btts = (1.0 - poisson.pmf(0, lam_nhl_loc * 0.29)) * (1.0 - poisson.pmf(0, lam_nhl_vis * 0.29))

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas NHL en Betano")
    margen_nhl = 1.05

    c_ml1, c_ml2 = st.sidebar.columns(2)
    cuota_ml_loc = c_ml1.number_input("Moneyline Local (Inc. OT)", min_value=1.01, value=round(1/(max(p_ml_loc, 0.05)*margen_nhl), 2), step=0.05)
    cuota_ml_vis = c_ml2.number_input("Moneyline Visita (Inc. OT)", min_value=1.01, value=round(1/(max(p_ml_vis, 0.05)*margen_nhl), 2), step=0.05)

    c_ot1, c_ot2 = st.sidebar.columns(2)
    linea_total_nhl = c_ot1.selectbox("Línea Goles Totales", [5.5, 6.0, 6.5], index=2)
    cuota_over_nhl = c_ot2.number_input(f"Cuota Over {linea_total_nhl}", min_value=1.01, value=1.88, step=0.05)
    cuota_under_nhl = st.sidebar.number_input(f"Cuota Under {linea_total_nhl}", min_value=1.01, value=1.92, step=0.05)

    with st.sidebar.expander("🏒 Cuotas Puck Line, 60 Min, 1er Período y SOG"):
        c_reg1, c_reg2, c_reg3 = st.columns(3)
        cuota_60_1 = c_reg1.number_input("1 (60 Min)", min_value=1.01, value=round(1/(max(p_reg_loc, 0.05)*1.06), 2), step=0.05)
        cuota_60_x = c_reg2.number_input("X (Empate 60')", min_value=1.01, value=4.20, step=0.10)
        cuota_60_2 = c_reg3.number_input("2 (60 Min)", min_value=1.01, value=round(1/(max(p_reg_vis, 0.05)*1.06), 2), step=0.05)
        
        st.markdown("---")
        cuota_pl_loc_m15 = st.number_input(f"{nhl_local} -1.5 (Puck Line)", min_value=1.01, value=2.45, step=0.05)
        cuota_pl_vis_p15 = st.number_input(f"{nhl_visita} +1.5 (Puck Line)", min_value=1.01, value=1.55, step=0.05)
        
        st.markdown("---")
        cuota_1p_o15 = st.number_input("Cuota 1er Período Over 1.5 Goles", min_value=1.01, value=1.82, step=0.05)
        cuota_tt_loc_o35 = st.number_input(f"Cuota {nhl_local} Over 3.5 Goles", min_value=1.01, value=2.15, step=0.05)
        cuota_tt_vis_o25 = st.number_input(f"Cuota {nhl_visita} Over 2.5 Goles", min_value=1.01, value=1.78, step=0.05)
        
        st.markdown("---")
        linea_sog_total = st.number_input("Línea Disparos a Puerta (SOG Total)", min_value=45.5, max_value=75.5, value=59.5, step=1.0)
        cuota_sog_over = st.number_input("Cuota Over SOG", min_value=1.01, value=1.87, step=0.05)

    p_over_total_nhl = 1.0 - sum(poisson.pmf(k, lam_nhl_total) for k in range(int(linea_total_nhl) + 1))
    p_under_total_nhl = 1.0 - p_over_total_nhl

    p_tt_loc_o35 = 1.0 - sum(poisson.pmf(k, lam_nhl_loc) for k in range(4))
    p_tt_vis_o25 = 1.0 - sum(poisson.pmf(k, lam_nhl_vis) for k in range(3))
    lam_sog_tot = sog_loc_in + sog_vis_in
    p_sog_over = 1.0 - sum(poisson.pmf(k, lam_sog_tot) for k in range(int(linea_sog_total) + 1))

    st.markdown(f"### 🧊 {nhl_local} vs. {nhl_visita} <span style='font-size:16px; color:#71717a; font-weight:normal;'>(NHL Hockey sobre Hielo)</span>", unsafe_allow_html=True)

    if usar_bayes_nhl and (pj_nhl_loc < 8 or pj_nhl_vis < 8):
        st.caption(f"🛡️ **Amortiguador Bayesiano NHL Activo:** Muestra ponderada con la media de la liga ({media_liga_nhl:.2f} G/p) por arranque de temporada ({nhl_local}: {pj_nhl_loc} PJ Casa | {nhl_visita}: {pj_nhl_vis} PJ Ruta).")

    nk1, nk2, nk3, nk4 = st.columns(4)
    nk1.metric("🏒 Goles Esperados (60m)", f"{lam_nhl_loc:.2f} - {lam_nhl_vis:.2f}", f"Total: {lam_nhl_total:.2f} goles")
    nk2.metric("🏆 Prob. Moneyline (Inc. OT)", f"{p_ml_loc*100:.1f}% vs {p_ml_vis*100:.1f}%", f"Prob. Prórroga (OT): {p_reg_emp*100:.1f}%")
    nk3.metric("⏱️ Proyección 1er Período", f"{lam_1p_total:.2f} goles (1P)", f"Over 1.5 (1P): {p_1p_over15*100:.1f}%")
    nk4.metric("🥅 Disparos al Arco (SOG)", f"{lam_sog_tot:.1f} tiros", f"{sog_loc_in:.1f} L + {sog_vis_in:.1f} V")

    st.markdown("<br>", unsafe_allow_html=True)

    ntab1, ntab2, ntab3, ntab4 = st.tabs([
        "🏆 1. Moneyline, 60 Minutos, Puck Line y Totales",
        "⏱️ 2. Team Totals, 1er Período y Disparos (SOG)",
        "🔢 3. Matriz de Marcador Exacto NHL",
        "🔴 4. Radar En Vivo NHL (In-Play)"
    ])

    with ntab1:
        mercados_nhl_1 = [
            (f"Moneyline: Gana {nhl_local} (Incluye OT/SO)", p_ml_loc, cuota_ml_loc),
            (f"Moneyline: Gana {nhl_visita} (Incluye OT/SO)", p_ml_vis, cuota_ml_vis),
            (f"Tiempo Reglamentario (60'): Gana {nhl_local} (1)", p_reg_loc, cuota_60_1),
            ("Tiempo Reglamentario (60'): Empate / Se va a Prórroga (X)", p_reg_emp, cuota_60_x),
            (f"Tiempo Reglamentario (60'): Gana {nhl_visita} (2)", p_reg_vis, cuota_60_2),
            (f"Más de {linea_total_nhl} Goles Totales (Over)", p_over_total_nhl, cuota_over_nhl),
            (f"Menos de {linea_total_nhl} Goles Totales (Under)", p_under_total_nhl, cuota_under_nhl),
            (f"Puck Line: {nhl_local} -1.5 (Gana por 2+ goles)", p_pl_loc_menos15, cuota_pl_loc_m15),
            (f"Puck Line: {nhl_visita} +1.5 (Gana o pierde por 1 gol)", p_pl_vis_mas15, cuota_pl_vis_p15)
        ]
        filas_nhl_1 = []
        for m, p, c in mercados_nhl_1:
            justa = 1 / p if p > 0 else 99.0
            edge = (p * c) - 1
            filas_nhl_1.append({
                "Mercado Principal NHL (Betano)": m,
                "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Mínima Justa": f"{justa:.2f}",
                "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
            })
        df_nhl_1 = pd.DataFrame(filas_nhl_1)
        st.dataframe(df_nhl_1.style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with ntab2:
        mercados_nhl_2 = [
            ("1er Período: Más de 1.5 Goles (Over 1.5 1P)", p_1p_over15, cuota_1p_o15),
            ("1er Período: Menos de 1.5 Goles (Under 1.5 1P)", p_1p_under15, 1.95),
            ("1er Período: Ambos Equipos Anotan en el 1P - SÍ", p_1p_btts, 2.75),
            (f"Total por Equipo: {nhl_local} Más de 3.5 Goles", p_tt_loc_o35, cuota_tt_loc_o35),
            (f"Total por Equipo: {nhl_visita} Más de 2.5 Goles", p_tt_vis_o25, cuota_tt_vis_o25),
            (f"Disparos a Puerta: Más de {linea_sog_total} Tiros (Over SOG)", p_sog_over, cuota_sog_over),
            (f"Disparos a Puerta: Menos de {linea_sog_total} Tiros (Under SOG)", 1.0 - p_sog_over, 1.87)
        ]
        filas_nhl_2 = []
        for m, p, c in mercados_nhl_2:
            justa = 1 / p if p > 0 else 99.0
            edge = (p * c) - 1
            filas_nhl_2.append({
                "Mercado Especial NHL": m,
                "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Mínima Justa": f"{justa:.2f}",
                "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
            })
        df_nhl_2 = pd.DataFrame(filas_nhl_2)
        st.dataframe(df_nhl_2.style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with ntab3:
        st.caption("Probabilidad matemática de marcador exacto en tiempo reglamentario (0 a 7 goles por equipo):")
        df_mat_nhl = pd.DataFrame(
            mat_nhl[:8, :8] * 100,
            index=[f"🏠 {nhl_local} ({i})" for i in range(8)],
            columns=[f"✈️ {nhl_visita} ({j})" for j in range(8)]
        )
        st.dataframe(df_mat_nhl.style.format("{:.1f}%").background_gradient(cmap="Blues"), use_container_width=True)

    with ntab4:
        st.markdown("#### 🔴 Escáner En Vivo NHL: Presión en Pista y Recálculo de Tiempo Restante")
        st.caption("Ingresa el minuto jugado (de 1 a 60), goles y disparos (SOG) en vivo para detectar valor en tiempo real:")

        nh1, nh2, nh3, nh4, nh5 = st.columns(5)
        min_nhl = nh1.slider("⏱️ Minuto Jugado (0-60')", min_value=1, max_value=59, value=35)
        g_nhl_loc_v = nh2.number_input(f"🏒 Goles {nhl_local}", min_value=0, max_value=12, value=2)
        g_nhl_vis_v = nh3.number_input(f"🏒 Goles {nhl_visita}", min_value=0, max_value=12, value=2)
        sog_nhl_loc_v = nh4.number_input(f"🥅 SOG {nhl_local}", min_value=0, max_value=60, value=20)
        sog_nhl_vis_v = nh5.number_input(f"🥅 SOG {nhl_visita}", min_value=0, max_value=60, value=16)

        dom_nhl_l = ((sog_nhl_loc_v + 1.0) / (sog_nhl_loc_v + sog_nhl_vis_v + 2.0)) * 100.0
        dom_nhl_v = 100.0 - dom_nhl_l

        frac_nhl_jug = max(min_nhl / 60.0, 0.08)
        frac_nhl_rest = max((60.0 - min_nhl) / 60.0, 0.03)

        ritmo_nhl_l = np.clip(0.65 + 0.35 * ((sog_nhl_loc_v / frac_nhl_jug) / max(sog_loc_in, 15.0)), 0.70, 1.45)
        ritmo_nhl_v = np.clip(0.65 + 0.35 * ((sog_nhl_vis_v / frac_nhl_jug) / max(sog_vis_in, 15.0)), 0.70, 1.45)

        # En los últimos 10 minutos, si un equipo pierde por 1 o 2 goles, saca al portero (Empty Net -> Mayor tasa de goles)
        factor_empty_net = 1.25 if (min_nhl >= 48 and abs(g_nhl_loc_v - g_nhl_vis_v) in [1, 2]) else 1.0

        lam_nhl_rest_l = max(lam_nhl_loc * frac_nhl_rest * ritmo_nhl_l * factor_empty_net, 0.05)
        lam_nhl_rest_v = max(lam_nhl_vis * frac_nhl_rest * ritmo_nhl_v * factor_empty_net, 0.05)
        lam_nhl_rest_tot = lam_nhl_rest_l + lam_nhl_rest_v

        st.markdown(dibujar_cancha_calor(nhl_local, nhl_visita, dom_nhl_l, dom_nhl_v, ritmo_nhl_l, ritmo_nhl_v, "nhl"), unsafe_allow_html=True)

        p_nhl_1mas = 1.0 - poisson.pmf(0, lam_nhl_rest_tot)
        p_nhl_2mas = 1.0 - (poisson.pmf(0, lam_nhl_rest_tot) + poisson.pmf(1, lam_nhl_rest_tot))

        mat_nhl_r = np.zeros((9, 9))
        p_nhl_f1, p_nhl_fx, p_nhl_f2 = 0.0, 0.0, 0.0
        for i in range(9):
            for j in range(9):
                prob_ij = poisson.pmf(i, lam_nhl_rest_l) * poisson.pmf(j, lam_nhl_rest_v)
                if (g_nhl_loc_v + i) > (g_nhl_vis_v + j):
                    p_nhl_f1 += prob_ij
                elif (g_nhl_loc_v + i) == (g_nhl_vis_v + j):
                    p_nhl_fx += prob_ij
                else:
                    p_nhl_f2 += prob_ij

        p_nhl_ml_vivo_l = p_nhl_f1 + (p_nhl_fx * ratio_ot_loc)
        p_nhl_ml_vivo_v = p_nhl_f2 + (p_nhl_fx * (1.0 - ratio_ot_loc))

        g_actual_nhl = g_nhl_loc_v + g_nhl_vis_v
        lin_nhl_v1 = g_actual_nhl + 0.5
        lin_nhl_v2 = g_actual_nhl + 1.5

        nq1, nq2, nq3 = st.columns(3)
        c_nhl_v_o1 = nq1.number_input(f"Cuota Más de {lin_nhl_v1} Goles (+1 gol)", min_value=1.01, value=round(max(1.06, 1/max(p_nhl_1mas*1.06, 0.05)), 2), step=0.05)
        c_nhl_v_o2 = nq2.number_input(f"Cuota Más de {lin_nhl_v2} Goles (+2 goles)", min_value=1.01, value=round(max(1.15, 1/max(p_nhl_2mas*1.06, 0.05)), 2), step=0.05)
        c_nhl_v_ml1 = nq3.number_input(f"Cuota Moneyline En Vivo {nhl_local}", min_value=1.01, value=round(max(1.05, 1/max(p_nhl_ml_vivo_l*1.06, 0.05)), 2), step=0.05)

        mercados_nhl_vivo = [
            (f"Más de {lin_nhl_v1} Goles en 60 Min (1+ gol adicional)", p_nhl_1mas, c_nhl_v_o1),
            (f"Más de {lin_nhl_v2} Goles en 60 Min (2+ goles adicionales)", p_nhl_2mas, c_nhl_v_o2),
            (f"Moneyline En Vivo (Inc. OT): Gana {nhl_local}", p_nhl_ml_vivo_l, c_nhl_v_ml1),
            (f"Moneyline En Vivo (Inc. OT): Gana {nhl_visita}", p_nhl_ml_vivo_v, round(max(1.05, 1/max(p_nhl_ml_vivo_v*1.06, 0.05)), 2)),
            (f"Empate en 60 Minutos (Se va a Overtime partiendo de {g_nhl_loc_v}-{g_nhl_vis_v})", p_nhl_fx, round(max(1.20, 1/max(p_nhl_fx*1.07, 0.04)), 2))
        ]

        filas_nhl_v = []
        for m, p, c in mercados_nhl_vivo:
            justa = 1 / p if p > 0 else 99.0
            edge = (p * c) - 1
            filas_nhl_v.append({
                "Mercado En Vivo NHL": m,
                "Prob. Tiempo Restante (%)": f"{p*100:.1f}%",
                "Cuota Justa En Vivo": f"{justa:.2f}",
                "Cuota Betano En Vivo": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "🔥 ENTRAR EN VIVO (+EV)" if edge > 0.04 else "❄️ Esperar / Sin valor"
            })
        df_nhl_v = pd.DataFrame(filas_nhl_v)
        st.dataframe(df_nhl_v.style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)
