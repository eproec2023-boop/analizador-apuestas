import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from scipy.stats import poisson, norm
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Pro Bet Analyzer 8.0 | Omni-Sports Quant Suite",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DISEÑO VISUAL EJECUTIVO (CSS PERSONALIZADO) ---
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
<h1>🏆 PRO BET ANALYZER 8.0 <span style="color:#ff8c00;">| OMNI-SPORTS QUANT SUITE</span></h1>
<p>Fútbol (19 Ligas) • NHL • NBA • NFL • MLB • Tenis (Filtro por Superficie) • Radar En Vivo (+EV) vs. Betano</p>
</div>
""", unsafe_allow_html=True)

# Función para colorear filas con Valor (+EV)
def resaltar_valor(fila):
    veredicto = str(fila.get("Veredicto", ""))
    if "✅" in veredicto or "🔥" in veredicto:
        return ['background-color: rgba(22, 163, 74, 0.15); font-weight: 600;'] * len(fila)
    return [''] * len(fila)

# Función para renderizar Cancha Interactiva y Mapa de Calor Multideporte
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

    html_code = f"""
<div style="background:{bg_pitch}; border: 3px solid {border_pitch}; border-radius: 14px; height: 260px; position: relative; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,0.18); font-family: system-ui, -apple-system, sans-serif;">
<div style="position:absolute; left:50%; top:0; bottom:0; width:3px; background:{line_color}; transform:translateX(-50%);"></div>
<div style="position:absolute; left:50%; top:50%; width:80px; height:80px; border:3px solid {line_color}; border-radius:50%; transform:translate(-50%, -50%);"></div>
<div style="position:absolute; left:0; top:22%; bottom:22%; width:15%; border-right:3px solid {line_color}; border-top:3px solid {line_color}; border-bottom:3px solid {line_color};"></div>
<div style="position:absolute; right:0; top:22%; bottom:22%; width:15%; border-left:3px solid {line_color}; border-top:3px solid {line_color}; border-bottom:3px solid {line_color};"></div>
<div style="position:absolute; right:5%; top:50%; width:{rad_loc}px; height:{rad_loc}px; background:radial-gradient(circle, rgba(255,59,0,{op_loc}) 0%, rgba(255,145,0,{op_loc*0.65}) 45%, rgba(255,255,0,0) 75%); transform:translateY(-50%); border-radius:50%; pointer-events:none;"></div>
<div style="position:absolute; right:20%; top:28%; width:{int(rad_loc*0.75)}px; height:{int(rad_loc*0.75)}px; background:radial-gradient(circle, rgba(255,115,0,{op_loc*0.8}) 0%, rgba(255,255,0,0) 70%); border-radius:50%; pointer-events:none;"></div>
<div style="position:absolute; left:5%; top:50%; width:{rad_vis}px; height:{rad_vis}px; background:radial-gradient(circle, rgba(0,200,255,{op_vis}) 0%, rgba(0,110,255,{op_vis*0.65}) 45%, rgba(0,0,255,0) 75%); transform:translateY(-50%); border-radius:50%; pointer-events:none;"></div>
<div style="position:absolute; left:20%; top:32%; width:{int(rad_vis*0.75)}px; height:{int(rad_vis*0.75)}px; background:radial-gradient(circle, rgba(56,189,248,{op_vis*0.8}) 0%, rgba(0,0,255,0) 70%); border-radius:50%; pointer-events:none;"></div>
<div style="position:absolute; left:16px; top:12px; background:rgba(15,23,42,0.85); color:#fff; padding:6px 12px; border-radius:8px; font-weight:700; font-size:13px; border-left: 4px solid #ff6b00;">
🏠 {eq_loc} (➔) | Dominio/Presión: {dom_loc:.0f}%
</div>
<div style="position:absolute; right:16px; top:12px; background:rgba(15,23,42,0.85); color:#fff; padding:6px 12px; border-radius:8px; font-weight:700; font-size:13px; border-right: 4px solid #38bdf8;">
Dominio/Presión: {dom_vis:.0f}% | (⬅) {eq_vis} ✈️
</div>
<div style="position:absolute; left:50%; bottom:10px; transform:translateX(-50%); background:rgba(15,23,42,0.88); color:#f8fafc; padding:5px 16px; border-radius:20px; font-size:12px; font-weight:600; white-space:nowrap;">
🔥 Foco Naranja: Ofensiva de {eq_loc} &nbsp;&nbsp;|&nbsp;&nbsp; ❄️ Foco Azul: Ofensiva de {eq_vis}
</div>
</div>
"""
    components.html(html_code, height=275)

# --- SELECTOR MAESTRO DE DEPORTE ---
st.sidebar.markdown("### 🎯 Selector Maestro de Deporte")
deporte_activo = st.sidebar.selectbox(
    "Elige la disciplina a analizar:",
    [
        "⚽ Fútbol (19 Ligas y Torneos UEFA)",
        "🎾 Tenis (ATP / WTA + Superficie)",
        "🏀 NBA (Basketball EE. UU.)",
        "🏈 NFL (Fútbol Americano EE. UU.)",
        "⚾ MLB (Béisbol EE. UU.)",
        "🏒 NHL (Hockey sobre Hielo)"
    ]
)
st.sidebar.markdown("---")

# ==============================================================================
# BASES DE DATOS Y FUNCIONES DE EXTRACCIÓN MULTIDEPORTE
# ==============================================================================

# 1. FÚTBOL: 8 LIGAS EUROPEAS CSV + 11 LIGAS/TORNEOS ESPN & EXTRA
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

LIGAS_GLOBAL_ESPN = {
    "🇪🇨 LigaPro (Ecuador)": {
        "csv_extra": None, "espn_code": "ecu.1",
        "equipos_base": [
            "Barcelona SC", "Liga de Quito", "Independiente del Valle", "Emelec", "El Nacional",
            "Universidad Católica (ECU)", "Aucas", "Delfín", "Deportivo Cuenca", "Macará",
            "Orense", "Mushuc Runa", "Técnico Universitario", "Libertad (ECU)", "Imbabura", "Cumbayá"
        ]
    },
    "🇦🇷 Liga Profesional (Argentina)": {
        "csv_extra": "https://www.football-data.co.uk/new/ARG.csv", "espn_code": "arg.1",
        "equipos_base": [
            "River Plate", "Boca Juniors", "Racing Club", "Independiente", "San Lorenzo",
            "Vélez Sarsfield", "Talleres (C)", "Estudiantes LP", "Huracán", "Lanús",
            "Godoy Cruz", "Rosario Central", "Newell's Old Boys", "Argentinos Juniors",
            "Belgrano", "Unión", "Platense", "Defensa y Justicia", "Instituto", "Banfield"
        ]
    },
    "🇧🇷 Brasileirão Serie A (Brasil)": {
        "csv_extra": "https://www.football-data.co.uk/new/BRA.csv", "espn_code": "bra.1",
        "equipos_base": [
            "Flamengo", "Palmeiras", "Botafogo", "Fortaleza", "Internacional", "São Paulo",
            "Corinthians", "Bahia", "Cruzeiro", "Vasco da Gama", "Atlético Mineiro", "Grêmio",
            "Fluminense", "Vitória", "Athletico Paranaense", "Juventude", "Bragantino", "Criciúma"
        ]
    },
    "🇸🇦 Saudi Pro League (Arabia Saudita)": {
        "csv_extra": None, "espn_code": "sau.1",
        "equipos_base": [
            "Al Hilal", "Al Nassr", "Al Ittihad", "Al Ahli", "Al Taawoun", "Al Shabab",
            "Al Ettifaq", "Al Fateh", "Al Qadsiah", "Damac", "Al Riyadh", "Al Khaleej",
            "Al Raed", "Al Fayha", "Al Wehda", "Al Orobah", "Al Kholood", "Al Okhdood"
        ]
    },
    "🏆 UEFA Champions League": {
        "csv_extra": None, "espn_code": "uefa.champions",
        "equipos_base": [
            "Real Madrid", "Manchester City", "Bayern Munich", "Liverpool", "Barcelona",
            "Inter Milan", "Arsenal", "Paris Saint-Germain", "Bayer Leverkusen", "Borussia Dortmund",
            "Atlético Madrid", "Atalanta", "Juventus", "AC Milan", "Benfica", "Sporting CP",
            "Aston Villa", "AS Monaco", "Brest", "Feyenoord", "PSV Eindhoven", "Club Brugge"
        ]
    },
    "🏆 UEFA Europa League": {
        "csv_extra": None, "espn_code": "uefa.europa",
        "equipos_base": [
            "Lazio", "Athletic Club", "Tottenham Hotspur", "Manchester United", "Eintracht Frankfurt",
            "Lyon", "Olympiacos", "Galatasaray", "Fenerbahçe", "Ajax", "Real Sociedad", "AS Roma",
            "FC Porto", "AZ Alkmaar", "Rangers", "Braga", "Union Saint-Gilloise", "PAOK"
        ]
    },
    "🏆 UEFA Conference League": {
        "csv_extra": None, "espn_code": "uefa.europa.conf",
        "equipos_base": [
            "Chelsea", "Fiorentina", "Real Betis", "Heidenheim", " Vitória de Guimarães",
            "Gent", "Copenhagen", "Legia Warsaw", "Panathinaikos", "Rapid Wien",
            "APOEL", "Hearts", "Jagiellonia", "Cercle Brugge", "Lugano", "Olimpija Ljubljana"
        ]
    },
    "🌍 UEFA Nations League": {
        "csv_extra": None, "espn_code": "uefa.nations",
        "equipos_base": [
            "España", "Francia", "Alemania", "Portugal", "Italia", "Países Bajos", "Inglaterra",
            "Croacia", "Bélgica", "Dinamarca", "Suiza", "Austria", "Turquía", "Ucrania",
            "Serbia", "Polonia", "Escocia", "Hungría", "Grecia", "Noruega", "Suecia"
        ]
    },
    "🇲🇽 Liga MX (México)": {
        "csv_extra": "https://www.football-data.co.uk/new/MEX.csv", "espn_code": "mex.1",
        "equipos_base": [
            "Club América", "Cruz Azul", "Toluca", "Tigres UANL", "Monterrey", 
            "Pumas UNAM", "Guadalajara", "Atlético San Luis", "Tijuana", "Atlas", 
            "León", "Juárez", "Necaxa", "Mazatlán FC", "Puebla", "Pachuca", "Querétaro", "Santos Laguna"
        ]
    },
    "🇺🇸 MLS (Estados Unidos)": {
        "csv_extra": "https://www.football-data.co.uk/new/USA.csv", "espn_code": "usa.1",
        "equipos_base": [
            "Inter Miami CF", "LA Galaxy", "LAFC", "Columbus Crew", "FC Cincinnati", 
            "Real Salt Lake", "Seattle Sounders FC", "Houston Dynamo FC", "Orlando City SC", 
            "Charlotte FC", "New York Red Bulls", "New York City FC", "Minnesota United FC", 
            "Vancouver Whitecaps", "Portland Timbers", "Colorado Rapids", "Atlanta United FC", "Austin FC"
        ]
    },
    "🇨🇴 Liga BetPlay (Colombia)": {
        "csv_extra": None, "espn_code": "col.1",
        "equipos_base": [
            "América de Cali", "Independiente Santa Fe", "Millonarios", "Atlético Nacional", 
            "Once Caldas", "Junior", "Deportes Tolima", "Deportivo Pasto", "Fortaleza CEIF", 
            "Independiente Medellín", "Atlético Bucaramanga", "Deportivo Pereira", 
            "Águilas Doradas", "La Equidad", "Patriotas Boyacá", "Alianza FC", 
            "Deportivo Cali", "Jaguares de Córdoba", "Boyacá Chicó", "Envigado"
        ]
    }
}

TODAS_LAS_LIGAS_FUTBOL = list(LIGAS_EUROPA_CSV.keys()) + list(LIGAS_GLOBAL_ESPN.keys())

@st.cache_data(ttl=3600)
def cargar_europa_football_data(url):
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
        if len(df) < 5:
            raise ValueError("Pocos partidos")
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
            'Equipo': eq, 'PJ_Home': int(len(h)), 'PJ_Away': int(len(a)),
            'GF_Home': gf_h, 'GC_Home': float(h['FTAG'].mean()) if len(h) > 0 else 1.15,
            'GF_Away': gf_a, 'GC_Away': float(a['FTHG'].mean()) if len(a) > 0 else 1.40,
            'Shots_Home': sh_h, 'Shots_Away': sh_a, 'SoT_Home': sot_h, 'SoT_Away': sot_a,
            'Corners_Home': cor_h, 'Corners_Away': cor_a
        })
    return pd.DataFrame(filas)

@st.cache_data(ttl=3600)
def cargar_global_futbol_datos(nombre_liga):
    info = LIGAS_GLOBAL_ESPN[nombre_liga]
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
                    'Equipo': eq, 'PJ_Home': int(len(h)), 'PJ_Away': int(len(a)),
                    'GF_Home': gf_h, 'GC_Home': float(h['AG'].mean()) if len(h) > 0 else 1.15,
                    'GF_Away': gf_a, 'GC_Away': float(a['HG'].mean()) if len(a) > 0 else 1.45,
                    'Shots_Home': round(gf_h * 8.5, 1), 'Shots_Away': round(gf_a * 8.5, 1),
                    'SoT_Home': round(gf_h * 3.1, 1), 'SoT_Away': round(gf_a * 3.1, 1),
                    'Corners_Home': 5.4, 'Corners_Away': 4.3
                })
            if len(filas) > 5:
                return pd.DataFrame(filas)
        except Exception:
            pass

    try:
        url_espn = f"https://site.api.espn.com/apis/v2/sports/soccer/{info['espn_code']}/standings"
        r = requests.get(url_espn, timeout=6).json()
        filas = []
        for child in r.get('children', []):
            for item in child.get('standings', {}).get('entries', []):
                nombre = item['team']['displayName']
                stats = {s['name']: s['value'] for s in item.get('stats', [])}
                pj = max(int(stats.get('gamesPlayed', 8)), 1)
                gf = float(stats.get('pointsFor', 11)) / pj
                gc = float(stats.get('pointsAgainst', 11)) / pj
                filas.append({
                    'Equipo': nombre,
                    'PJ_Home': max(pj // 2, 1), 'PJ_Away': max(pj // 2, 1),
                    'GF_Home': round(gf * 1.14, 2), 'GC_Home': round(gc * 0.86, 2),
                    'GF_Away': round(gf * 0.86, 2), 'GC_Away': round(gc * 1.14, 2),
                    'Shots_Home': round(gf * 8.8, 1), 'Shots_Away': round(gf * 7.5, 1),
                    'SoT_Home': round(gf * 3.2, 1), 'SoT_Away': round(gf * 2.7, 1),
                    'Corners_Home': 5.3, 'Corners_Away': 4.3
                })
        if len(filas) > 5:
            return pd.DataFrame(filas).drop_duplicates(subset=['Equipo']).sort_values('Equipo')
    except Exception:
        pass

    filas = []
    for eq in sorted(info["equipos_base"]):
        filas.append({
            'Equipo': eq, 'PJ_Home': 6, 'PJ_Away': 6,
            'GF_Home': 1.48, 'GC_Home': 1.05, 'GF_Away': 1.12, 'GC_Away': 1.38,
            'Shots_Home': 13.5, 'Shots_Away': 10.6, 'SoT_Home': 4.6, 'SoT_Away': 3.6,
            'Corners_Home': 5.4, 'Corners_Away': 4.3
        })
    return pd.DataFrame(filas)

# 2. NHL BASE Y API
EQUIPOS_NHL_BASE = [
    "Boston Bruins", "Florida Panthers", "Toronto Maple Leafs", "Tampa Bay Lightning",
    "New York Rangers", "Carolina Hurricanes", "New Jersey Devils", "New York Islanders",
    "Dallas Stars", "Colorado Avalanche", "Winnipeg Jets", "Nashville Predators",
    "Edmonton Oilers", "Vancouver Canucks", "Vegas Golden Knights", "Los Angeles Kings",
    "Minnesota Wild", "St. Louis Blues", "Utah Mammoth", "Calgary Flames",
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
                "Equipo": nombre, "PJ_Home": pj_h, "PJ_Away": pj_a,
                "GF_Home": round(gf_h, 2), "GC_Home": round(gc_h, 2),
                "GF_Away": round(gf_a, 2), "GC_Away": round(gc_a, 2),
                "SOG_Home": sog_h, "SOG_Away": sog_a
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

# 3. NBA, NFL Y MLB (EXTRACCIÓN API ESPN + RESPALDO OFICIAL)
EQUIPOS_NBA_BASE = [
    "Boston Celtics", "Oklahoma City Thunder", "Denver Nuggets", "Minnesota Timberwolves",
    "Dallas Mavericks", "New York Knicks", "Milwaukee Bucks", "Philadelphia 76ers",
    "Cleveland Cavaliers", "Indiana Pacers", "Orlando Magic", "Phoenix Suns",
    "Los Angeles Lakers", "Golden State Warriors", "Sacramento Kings", "LA Clippers",
    "Miami Heat", "New Orleans Pelicans", "Houston Rockets", "Memphis Grizzlies",
    "San Antonio Spurs", "Atlanta Hawks", "Chicago Bulls", "Toronto Raptors",
    "Brooklyn Nets", "Utah Jazz", "Portland Trail Blazers", "Charlotte Hornets",
    "Detroit Pistons", "Washington Wizards"
]

EQUIPOS_NFL_BASE = [
    "Kansas City Chiefs", "San Francisco 49ers", "Baltimore Ravens", "Detroit Lions",
    "Buffalo Bills", "Philadelphia Eagles", "Green Bay Packers", "Houston Texans",
    "Dallas Cowboys", "Cincinnati Bengals", "Miami Dolphins", "Los Angeles Rams",
    "Pittsburgh Steelers", "Minnesota Vikings", "Atlanta Falcons", "Washington Commanders",
    "Tampa Bay Buccaneers", "Seattle Seahawks", "Chicago Bears", "New York Jets",
    "Jacksonville Jaguars", "Cleveland Browns", "Indianapolis Colts", "Los Angeles Chargers",
    "New Orleans Saints", "Arizona Cardinals", "Denver Broncos", "Las Vegas Raiders",
    "New England Patriots", "New York Giants", "Tennessee Titans", "Carolina Panthers"
]

EQUIPOS_MLB_BASE = [
    "Los Angeles Dodgers", "New York Yankees", "Philadelphia Phillies", "Baltimore Orioles",
    "Atlanta Braves", "Cleveland Guardians", "Milwaukee Brewers", "San Diego Padres",
    "Houston Astros", "New York Mets", "Arizona Diamondbacks", "Kansas City Royals",
    "Detroit Tigers", "Minnesota Twins", "Seattle Mariners", "Boston Red Sox",
    "Chicago Cubs", "St. Louis Cardinals", "San Francisco Giants", "Tampa Bay Rays",
    "Texas Rangers", "Toronto Blue Jays", "Cincinnati Reds", "Pittsburgh Pirates",
    "Athletics", "Washington Nationals", "Los Angeles Angels", "Miami Marlins",
    "Colorado Rockies", "Chicago White Sox"
]

@st.cache_data(ttl=3600)
def cargar_datos_usa_sport(sport_path, league_code, base_list, default_pf, default_pa):
    try:
        url = f"https://site.api.espn.com/apis/v2/sports/{sport_path}/{league_code}/standings"
        r = requests.get(url, timeout=6).json()
        filas = []
        for child in r.get("children", []):
            for item in child.get("standings", {}).get("entries", []):
                nombre = item["team"]["displayName"]
                stats = {s["name"]: s["value"] for s in item.get("stats", [])}
                pj = max(int(stats.get("gamesPlayed", stats.get("wins", 5) + stats.get("losses", 5))), 1)
                pf_tot = float(stats.get("pointsFor", default_pf * pj))
                pa_tot = float(stats.get("pointsAgainst", default_pa * pj))
                pf = pf_tot / pj if pf_tot > 25 else default_pf
                pa = pa_tot / pj if pa_tot > 25 else default_pa
                filas.append({
                    "Equipo": nombre, "PJ": pj,
                    "PF_Home": round(pf * 1.02, 2), "PA_Home": round(pa * 0.98, 2),
                    "PF_Away": round(pf * 0.98, 2), "PA_Away": round(pa * 1.02, 2)
                })
        if len(filas) >= 15:
            return pd.DataFrame(filas).drop_duplicates(subset=["Equipo"]).sort_values("Equipo")
    except Exception:
        pass
    filas = []
    for eq in sorted(base_list):
        filas.append({
            "Equipo": eq, "PJ": 12,
            "PF_Home": round(default_pf * 1.02, 2), "PA_Home": round(default_pa * 0.98, 2),
            "PF_Away": round(default_pf * 0.98, 2), "PA_Away": round(default_pa * 1.02, 2)
        })
    return pd.DataFrame(filas)

# 4. BASE DE DATOS DE TENIS (ATP & WTA CON ESTADÍSTICAS POR SUPERFICIE)
TENISTAS_DATA = {
    "ATP (Masculino)": {
        "Jannik Sinner": {"Hard_Hold": 90.5, "Hard_Brk": 28.5, "Clay_Hold": 85.0, "Clay_Brk": 27.0, "Grass_Hold": 91.0, "Grass_Brk": 24.0, "Aces": 8.5},
        "Carlos Alcaraz": {"Hard_Hold": 86.5, "Hard_Brk": 30.5, "Clay_Hold": 87.5, "Clay_Brk": 34.0, "Grass_Hold": 89.5, "Grass_Brk": 28.5, "Aces": 6.2},
        "Alexander Zverev": {"Hard_Hold": 88.5, "Hard_Brk": 24.5, "Clay_Hold": 86.5, "Clay_Brk": 27.5, "Grass_Hold": 89.0, "Grass_Brk": 20.5, "Aces": 10.4},
        "Novak Djokovic": {"Hard_Hold": 88.0, "Hard_Brk": 29.5, "Clay_Hold": 85.5, "Clay_Brk": 31.0, "Grass_Hold": 90.5, "Grass_Brk": 27.0, "Aces": 7.5},
        "Daniil Medvedev": {"Hard_Hold": 86.0, "Hard_Brk": 29.0, "Clay_Hold": 79.5, "Clay_Brk": 24.5, "Grass_Hold": 86.5, "Grass_Brk": 23.0, "Aces": 8.8},
        "Taylor Fritz": {"Hard_Hold": 89.0, "Hard_Brk": 22.5, "Clay_Hold": 82.5, "Clay_Brk": 22.0, "Grass_Hold": 91.5, "Grass_Brk": 20.0, "Aces": 11.8},
        "Casper Ruud": {"Hard_Hold": 82.5, "Hard_Brk": 21.5, "Clay_Hold": 86.0, "Clay_Brk": 29.5, "Grass_Hold": 78.0, "Grass_Brk": 17.5, "Aces": 5.8},
        "Andrey Rublev": {"Hard_Hold": 85.5, "Hard_Brk": 24.0, "Clay_Hold": 83.5, "Clay_Brk": 26.0, "Grass_Hold": 86.0, "Grass_Brk": 21.0, "Aces": 8.4},
        "Alex de Minaur": {"Hard_Hold": 83.0, "Hard_Brk": 29.5, "Clay_Hold": 78.5, "Clay_Brk": 27.5, "Grass_Hold": 85.5, "Grass_Brk": 26.5, "Aces": 4.9},
        "Grigor Dimitrov": {"Hard_Hold": 86.0, "Hard_Brk": 23.0, "Clay_Hold": 81.5, "Clay_Brk": 23.5, "Grass_Hold": 88.0, "Grass_Brk": 21.5, "Aces": 8.9},
        "Stefanos Tsitsipas": {"Hard_Hold": 86.0, "Hard_Brk": 21.5, "Clay_Hold": 86.5, "Clay_Brk": 27.0, "Grass_Hold": 85.0, "Grass_Brk": 18.5, "Aces": 8.2},
        "Tommy Paul": {"Hard_Hold": 83.5, "Hard_Brk": 26.5, "Clay_Hold": 80.0, "Clay_Brk": 26.0, "Grass_Hold": 86.0, "Grass_Brk": 24.5, "Aces": 6.4},
        "Holger Rune": {"Hard_Hold": 84.0, "Hard_Brk": 24.0, "Clay_Hold": 83.5, "Clay_Brk": 27.0, "Grass_Hold": 85.0, "Grass_Brk": 21.5, "Aces": 6.8},
        "Hubert Hurkacz": {"Hard_Hold": 89.5, "Hard_Brk": 19.5, "Clay_Hold": 84.0, "Clay_Brk": 20.0, "Grass_Hold": 93.0, "Grass_Brk": 19.0, "Aces": 14.2},
        "Ben Shelton": {"Hard_Hold": 88.5, "Hard_Brk": 19.5, "Clay_Hold": 81.0, "Clay_Brk": 19.0, "Grass_Hold": 90.0, "Grass_Brk": 18.0, "Aces": 12.6},
        "Jack Draper": {"Hard_Hold": 86.5, "Hard_Brk": 25.5, "Clay_Hold": 80.5, "Clay_Brk": 23.5, "Grass_Hold": 89.5, "Grass_Brk": 23.5, "Aces": 9.8},
        "Lorenzo Musetti": {"Hard_Hold": 80.5, "Hard_Brk": 22.5, "Clay_Hold": 83.5, "Clay_Brk": 28.0, "Grass_Hold": 85.5, "Grass_Brk": 23.0, "Aces": 5.2},
        "Francisco Cerúndolo": {"Hard_Hold": 78.5, "Hard_Brk": 24.5, "Clay_Hold": 81.5, "Clay_Brk": 30.5, "Grass_Hold": 79.0, "Grass_Brk": 21.0, "Aces": 4.8}
    },
    "WTA (Femenino)": {
        "Aryna Sabalenka": {"Hard_Hold": 81.5, "Hard_Brk": 38.5, "Clay_Hold": 79.5, "Clay_Brk": 40.0, "Grass_Hold": 83.5, "Grass_Brk": 35.0, "Aces": 6.8},
        "Iga Swiatek": {"Hard_Hold": 80.5, "Hard_Brk": 44.5, "Clay_Hold": 83.5, "Clay_Brk": 49.5, "Grass_Hold": 79.0, "Grass_Brk": 38.0, "Aces": 3.2},
        "Coco Gauff": {"Hard_Hold": 75.5, "Hard_Brk": 41.5, "Clay_Hold": 76.0, "Clay_Brk": 43.5, "Grass_Hold": 77.5, "Grass_Brk": 37.5, "Aces": 4.5},
        "Jessica Pegula": {"Hard_Hold": 76.5, "Hard_Brk": 40.0, "Clay_Hold": 73.5, "Clay_Brk": 39.5, "Grass_Hold": 78.0, "Grass_Brk": 36.0, "Aces": 3.6},
        "Elena Rybakina": {"Hard_Hold": 82.5, "Hard_Brk": 34.5, "Clay_Hold": 78.5, "Clay_Brk": 35.5, "Grass_Hold": 85.5, "Grass_Brk": 34.0, "Aces": 8.4},
        "Jasmine Paolini": {"Hard_Hold": 71.5, "Hard_Brk": 39.5, "Clay_Hold": 73.5, "Clay_Brk": 42.5, "Grass_Hold": 74.0, "Grass_Brk": 37.0, "Aces": 2.1},
        "Qinwen Zheng": {"Hard_Hold": 79.5, "Hard_Brk": 35.5, "Clay_Hold": 78.0, "Clay_Brk": 38.0, "Grass_Hold": 77.0, "Grass_Brk": 31.0, "Aces": 7.6},
        "Emma Navarro": {"Hard_Hold": 73.0, "Hard_Brk": 40.5, "Clay_Hold": 72.5, "Clay_Brk": 41.5, "Grass_Hold": 75.5, "Grass_Brk": 38.0, "Aces": 2.4},
        "Paula Badosa": {"Hard_Hold": 76.0, "Hard_Brk": 37.0, "Clay_Hold": 75.5, "Clay_Brk": 39.0, "Grass_Hold": 78.5, "Grass_Brk": 34.5, "Aces": 5.1},
        "Mirra Andreeva": {"Hard_Hold": 73.5, "Hard_Brk": 41.0, "Clay_Hold": 75.0, "Clay_Brk": 43.5, "Grass_Hold": 74.0, "Grass_Brk": 37.0, "Aces": 3.4}
    }
}


# ==============================================================================
# 1. EJECUCIÓN MÓDULO FÚTBOL (19 COMPETICIONES + RADAR EN VIVO)
# ==============================================================================
if deporte_activo.startswith("⚽"):
    st.sidebar.markdown("### 🏆 1. Competición y Encuentro")
    liga_elegida = st.sidebar.selectbox("Selecciona la Liga / Torneo", TODAS_LAS_LIGAS_FUTBOL)

    if liga_elegida in LIGAS_EUROPA_CSV:
        df_liga = cargar_europa_football_data(LIGAS_EUROPA_CSV[liga_elegida])
    else:
        df_liga = cargar_global_futbol_datos(liga_elegida)

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

    k_fut = f"{liga_elegida}_{equipo_local}_{equipo_visita}_{usar_amortiguador}"

    with st.sidebar.expander("⚙️ Auditoría / Ajuste Manual de Datos"):
        st.caption(f"Muestra: {equipo_local} ({pj_loc} PJ Casa) | {equipo_visita} ({pj_vis} PJ Visita)")
        xg_favor_local = st.number_input("Goles/xG a Favor (Local)", min_value=0.1, max_value=5.0, value=round(gf_loc_calc, 2), step=0.05, key=f"f1_{k_fut}")
        xg_contra_local = st.number_input("Goles/xG en Contra (Local)", min_value=0.1, max_value=5.0, value=round(gc_loc_calc, 2), step=0.05, key=f"f2_{k_fut}")
        xg_favor_visita = st.number_input("Goles/xG a Favor (Visita)", min_value=0.1, max_value=5.0, value=round(gf_vis_calc, 2), step=0.05, key=f"f3_{k_fut}")
        xg_contra_visita = st.number_input("Goles/xG en Contra (Visita)", min_value=0.1, max_value=5.0, value=round(gc_vis_calc, 2), step=0.05, key=f"f4_{k_fut}")
        promedio_liga = st.number_input("Promedio Goles de la Liga", min_value=0.5, max_value=3.0, value=round(media_goles_liga, 2), step=0.05, key=f"f5_{k_fut}")
        st.markdown("---")
        remates_local = st.number_input("Remates Totales (Local)", min_value=1.0, max_value=30.0, value=round(float(row_loc['Shots_Home']), 1), step=0.5, key=f"f6_{k_fut}")
        remates_visita = st.number_input("Remates Totales (Visita)", min_value=1.0, max_value=30.0, value=round(float(row_vis['Shots_Away']), 1), step=0.5, key=f"f7_{k_fut}")
        puerta_local = st.number_input("Remates a Puerta (Local)", min_value=0.5, max_value=15.0, value=round(float(row_loc['SoT_Home']), 1), step=0.1, key=f"f8_{k_fut}")
        puerta_visita = st.number_input("Remates a Puerta (Visita)", min_value=0.5, max_value=15.0, value=round(float(row_vis['SoT_Away']), 1), step=0.1, key=f"f9_{k_fut}")
        corners_local = st.number_input("Córners Promedio (Local)", min_value=0.5, max_value=15.0, value=round(float(row_loc['Corners_Home']), 1), step=0.1, key=f"f10_{k_fut}")
        corners_visita = st.number_input("Córners Promedio (Visita)", min_value=0.5, max_value=15.0, value=round(float(row_vis['Corners_Away']), 1), step=0.1, key=f"f11_{k_fut}")

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
    cuota_1 = c_sb1.number_input("Local (1)", min_value=1.01, value=c_sug_1, step=0.05, key=f"c1_{k_fut}")
    cuota_x = c_sb2.number_input("Empate (X)", min_value=1.01, value=c_sug_x, step=0.05, key=f"cx_{k_fut}")
    cuota_2 = c_sb3.number_input("Visita (2)", min_value=1.01, value=c_sug_2, step=0.05, key=f"c2_{k_fut}")

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

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("⚽ Proyección de Goles (xG)", f"{lam_loc:.2f} - {lam_vis:.2f}", f"Total esperado: {lam_loc+lam_vis:.2f} goles")
    k2.metric("🎯 Remates Totales Esp.", f"{lam_remates:.1f} tiros", f"{remates_local:.1f} L + {remates_visita:.1f} V")
    k3.metric("🥅 Remates a Puerta Esp.", f"{lam_puerta:.1f} al arco", f"{puerta_local:.1f} L + {puerta_visita:.1f} V")
    k4.metric("⛳ Córners Proyectados", f"{lam_corners:.1f} esquinas", f"{corners_local:.1f} L + {corners_visita:.1f} V")

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
                "Mercado en Betano": m, "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Mínima Justa": f"{justa:.2f}", "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
            })
        st.dataframe(pd.DataFrame(filas_g).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

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
                "Mercado Especial": m, "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Mínima Justa": f"{justa:.2f}", "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
            })
        st.dataframe(pd.DataFrame(filas_e).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with tab3:
        df_matriz = pd.DataFrame(
            matriz_prob[:6, :6] * 100, 
            index=[f"🏠 {equipo_local} ({i})" for i in range(6)], 
            columns=[f"✈️ {equipo_visita} ({j})" for j in range(6)]
        )
        st.dataframe(df_matriz.style.format("{:.1f}%").background_gradient(cmap="YlOrBr"), use_container_width=True)

    with tab4:
        lc1, lc2, lc3, lc4 = st.columns(4)
        min_actual = lc1.slider("⏱️ Minuto Actual", min_value=1, max_value=90, value=60)
        goles_vivo_loc = lc2.number_input(f"⚽ Goles {equipo_local}", min_value=0, max_value=10, value=0)
        goles_vivo_vis = lc3.number_input(f"⚽ Goles {equipo_visita}", min_value=0, max_value=10, value=0)
        posesion_loc = lc4.slider(f"📊 Posesión {equipo_local} (%)", min_value=20, max_value=80, value=54)

        ls1, ls2, ls3, ls4 = st.columns(4)
        sot_vivo_loc = ls1.number_input(f"🥅 A Puerta {equipo_local} (En Vivo)", min_value=0, max_value=25, value=4)
        sot_vivo_vis = ls2.number_input(f"🥅 A Puerta {equipo_visita} (En Vivo)", min_value=0, max_value=25, value=2)
        cor_vivo_loc = ls3.number_input(f"⛳ Córners {equipo_local} (En Vivo)", min_value=0, max_value=25, value=5)
        cor_vivo_vis = ls4.number_input(f"⛳ Córners {equipo_visita} (En Vivo)", min_value=0, max_value=25, value=3)

        puntos_presion_loc = (sot_vivo_loc * 3.0) + (cor_vivo_loc * 1.2) + (posesion_loc * 0.12) + 0.5
        puntos_presion_vis = (sot_vivo_vis * 3.0) + (cor_vivo_vis * 1.2) + ((100 - posesion_loc) * 0.12) + 0.5
        dom_loc_pct = (puntos_presion_loc / (puntos_presion_loc + puntos_presion_vis)) * 100.0
        dom_vis_pct = 100.0 - dom_loc_pct

        fraccion_jugada = max(min_actual / 94.0, 0.08)
        fraccion_restante = max((94.0 - min_actual) / 94.0, 0.03)
        factor_ritmo_loc = np.clip(0.65 + 0.35 * ((sot_vivo_loc / fraccion_jugada) / max(puerta_local, 1.5)), 0.65, 1.55)
        factor_ritmo_vis = np.clip(0.65 + 0.35 * ((sot_vivo_vis / fraccion_jugada) / max(puerta_visita, 1.5)), 0.65, 1.55)

        urg_loc = 1.18 if goles_vivo_loc < goles_vivo_vis else (1.06 if goles_vivo_loc == goles_vivo_vis else 0.90)
        urg_vis = 1.18 if goles_vivo_vis < goles_vivo_loc else (1.06 if goles_vivo_loc == goles_vivo_vis else 0.90)

        lam_rest_loc = max(lam_loc * fraccion_restante * factor_ritmo_loc * urg_loc, 0.04)
        lam_rest_vis = max(lam_vis * fraccion_restante * factor_ritmo_vis * urg_vis, 0.04)
        lam_rest_total = lam_rest_loc + lam_rest_vis

        mostrar_cancha_calor(equipo_local, equipo_visita, dom_loc_pct, dom_vis_pct, factor_ritmo_loc, factor_ritmo_vis, "futbol")

        p_1_mas_gol = 1.0 - poisson.pmf(0, lam_rest_total)
        p_2_mas_goles = 1.0 - (poisson.pmf(0, lam_rest_total) + poisson.pmf(1, lam_rest_total))
        p_prox_gol_loc = (lam_rest_loc / lam_rest_total) * p_1_mas_gol
        p_prox_gol_vis = (lam_rest_vis / lam_rest_total) * p_1_mas_gol

        p_final_1, p_final_x, p_final_2 = 0.0, 0.0, 0.0
        for i in range(7):
            for j in range(7):
                prob_ij = poisson.pmf(i, lam_rest_loc) * poisson.pmf(j, lam_rest_vis)
                if (goles_vivo_loc + i) > (goles_vivo_vis + j):
                    p_final_1 += prob_ij
                elif (goles_vivo_loc + i) == (goles_vivo_vis + j):
                    p_final_x += prob_ij
                else:
                    p_final_2 += prob_ij

        linea_vivo_1 = (goles_vivo_loc + goles_vivo_vis) + 0.5
        linea_vivo_2 = (goles_vivo_loc + goles_vivo_vis) + 1.5

        q1, q2, q3, q4 = st.columns(4)
        c_vivo_1gol = q1.number_input(f"Cuota Más de {linea_vivo_1} Goles", min_value=1.01, value=round(max(1.08, 1/max(p_1_mas_gol*1.06, 0.05)), 2), step=0.05)
        c_vivo_prox_l = q2.number_input(f"Cuota Próximo Gol: {equipo_local}", min_value=1.01, value=round(max(1.10, 1/max(p_prox_gol_loc*1.06, 0.05)), 2), step=0.05)
        c_vivo_prox_v = q3.number_input(f"Cuota Próximo Gol: {equipo_visita}", min_value=1.01, value=round(max(1.10, 1/max(p_prox_gol_vis*1.06, 0.05)), 2), step=0.05)
        c_vivo_gana_l = q4.number_input(f"Cuota Gana {equipo_local} (En Vivo)", min_value=1.01, value=round(max(1.05, 1/max(p_final_1*1.06, 0.05)), 2), step=0.05)

        mercados_vivo = [
            (f"Más de {linea_vivo_1} Goles en el Partido (+1 gol más)", p_1_mas_gol, c_vivo_1gol),
            (f"Más de {linea_vivo_2} Goles en el Partido (+2 goles más)", p_2_mas_goles, round(max(1.20, 1/max(p_2_mas_goles*1.07, 0.04)), 2)),
            (f"Próximo Gol en Vivo: Anota {equipo_local}", p_prox_gol_loc, c_vivo_prox_l),
            (f"Próximo Gol en Vivo: Anota {equipo_visita}", p_prox_gol_vis, c_vivo_prox_v),
            (f"Resultado Final ({goles_vivo_loc}-{goles_vivo_vis}): Gana {equipo_local}", p_final_1, c_vivo_gana_l)
        ]
        filas_vivo = []
        for m, p, c in mercados_vivo:
            justa = 1 / p if p > 0 else 99.0
            edge = (p * c) - 1
            filas_vivo.append({
                "Mercado En Vivo": m, "Prob. Restante (%)": f"{p*100:.1f}%",
                "Cuota Justa": f"{justa:.2f}", "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "🔥 ENTRAR EN VIVO (+EV)" if edge > 0.04 else "❄️ Esperar / Sin valor"
            })
        st.dataframe(pd.DataFrame(filas_vivo).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)


# ==============================================================================
# 2. EJECUCIÓN MÓDULO TENIS (ATP / WTA + FILTRO DE SUPERFICIE + EN VIVO)
# ==============================================================================
elif deporte_activo.startswith("🎾"):
    st.sidebar.markdown("### 🎾 1. Circuito, Superficie y Jugadores")
    circuito_tenis = st.sidebar.radio("Circuito:", ["ATP (Masculino)", "WTA (Femenino)"])
    superficie_tenis = st.sidebar.selectbox(
        "🌍 Superficie de la Cancha:",
        [
            "🟦 Cancha Dura (Hard Court - Outdoor)",
            "🟧 Polvo de Ladrillo / Arcilla (Clay)",
            "🟩 Césped (Grass - Wimbledon/Halle)",
            "🟪 Dura Techada (Indoor Hard - Rápida)"
        ]
    )
    formato_sets = st.sidebar.radio("Formato del Torneo:", ["Al mejor de 3 Sets (ATP/WTA Estándar)", "Al mejor de 5 Sets (Grand Slam ATP)"])

    jugadores_lista = sorted(list(TENISTAS_DATA[circuito_tenis].keys()))
    col_t1, col_t2 = st.sidebar.columns(2)
    jug_a = col_t1.selectbox("🎾 Jugador A", jugadores_lista, index=0)
    jug_b = col_t2.selectbox("🎾 Jugador B", jugadores_lista, index=1 if len(jugadores_lista) > 1 else 0)

    stats_a = TENISTAS_DATA[circuito_tenis][jug_a]
    stats_b = TENISTAS_DATA[circuito_tenis][jug_b]

    # Selección automática de métricas según la superficie elegida
    if "Arcilla" in superficie_tenis:
        hold_a_base, brk_a_base = stats_a["Clay_Hold"], stats_a["Clay_Brk"]
        hold_b_base, brk_b_base = stats_b["Clay_Hold"], stats_b["Clay_Brk"]
        factor_aces_sup = 0.72
        cancha_tipo = "tenis_clay"
    elif "Césped" in superficie_tenis:
        hold_a_base, brk_a_base = stats_a["Grass_Hold"], stats_a["Grass_Brk"]
        hold_b_base, brk_b_base = stats_b["Grass_Hold"], stats_b["Grass_Brk"]
        factor_aces_sup = 1.28
        cancha_tipo = "tenis_grass"
    elif "Indoor" in superficie_tenis:
        hold_a_base, brk_a_base = min(stats_a["Hard_Hold"] + 2.2, 95.0), max(stats_a["Hard_Brk"] - 1.8, 12.0)
        hold_b_base, brk_b_base = min(stats_b["Hard_Hold"] + 2.2, 95.0), max(stats_b["Hard_Brk"] - 1.8, 12.0)
        factor_aces_sup = 1.18
        cancha_tipo = "tenis_hard"
    else:
        hold_a_base, brk_a_base = stats_a["Hard_Hold"], stats_a["Hard_Brk"]
        hold_b_base, brk_b_base = stats_b["Hard_Hold"], stats_b["Hard_Brk"]
        factor_aces_sup = 1.00
        cancha_tipo = "tenis_hard"

    k_ten = f"{circuito_tenis}_{superficie_tenis}_{jug_a}_{jug_b}"
    with st.sidebar.expander("⚙️ Auditoría / Ajuste por Superficie (Hold % y Break %)"):
        st.caption("Porcentaje de juegos de saque ganados (Hold %) y quiebres logrados (Break %) en esta superficie:")
        hold_a = st.number_input(f"% Hold Saque {jug_a}", min_value=50.0, max_value=98.0, value=float(hold_a_base), step=0.5, key=f"th1_{k_ten}")
        brk_a = st.number_input(f"% Quiebre (Return) {jug_a}", min_value=10.0, max_value=60.0, value=float(brk_a_base), step=0.5, key=f"tb1_{k_ten}")
        hold_b = st.number_input(f"% Hold Saque {jug_b}", min_value=50.0, max_value=98.0, value=float(hold_b_base), step=0.5, key=f"th2_{k_ten}")
        brk_b = st.number_input(f"% Quiebre (Return) {jug_b}", min_value=10.0, max_value=60.0, value=float(brk_b_base), step=0.5, key=f"tb2_{k_ten}")

    # Modelo Matemático de Tenis (Fuerza combinada Servicio vs Resto en la superficie seleccionada)
    hold_efectivo_a = np.clip((hold_a + (100.0 - brk_b)) / 2.0, 52.0, 96.0)
    hold_efectivo_b = np.clip((hold_b + (100.0 - brk_a)) / 2.0, 52.0, 96.0)

    ventaja_neta_a = (hold_efectivo_a - hold_efectivo_b) / 100.0
    p_set_a = float(np.clip(0.50 + ventaja_neta_a * 1.95, 0.12, 0.88))
    p_set_b = 1.0 - p_set_a

    if "3 Sets" in formato_sets:
        p_2_0_a = p_set_a ** 2
        p_2_1_a = 2 * (p_set_a ** 2) * p_set_b
        p_gana_a = p_2_0_a + p_2_1_a
        p_0_2_b = p_set_b ** 2
        p_1_2_b = 2 * (p_set_b ** 2) * p_set_a
        p_gana_b = p_0_2_b + p_1_2_b
        sets_esperados = (2.0 * (p_2_0_a + p_0_2_b)) + (3.0 * (p_2_1_a + p_1_2_b))
    else:
        p_3_0_a = p_set_a ** 3
        p_3_1_a = 3 * (p_set_a ** 3) * p_set_b
        p_3_2_a = 6 * (p_set_a ** 3) * (p_set_b ** 2)
        p_gana_a = p_3_0_a + p_3_1_a + p_3_2_a
        p_gana_b = 1.0 - p_gana_a
        p_2_0_a = p_3_0_a
        p_0_2_b = p_set_b ** 3
        sets_esperados = 3.65

    # Juegos por set según dominancia del saque en la superficie
    media_hold_partido = (hold_efectivo_a + hold_efectivo_b) / 2.0
    juegos_por_set = 9.2 + ((media_hold_partido - 70.0) / 25.0) * 1.65
    juegos_totales_esp = round(juegos_por_set * sets_esperados, 1)
    prob_tiebreak = float(np.clip(((media_hold_partido - 65.0) / 30.0) * 0.52, 0.12, 0.68))
    aces_esp_total = round((stats_a["Aces"] + stats_b["Aces"]) * factor_aces_sup * (sets_esperados / 2.35), 1)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas Tenis en Betano")
    margen_t = 1.05
    ct1, ct2 = st.sidebar.columns(2)
    cuota_t_a = ct1.number_input(f"Gana {jug_a}", min_value=1.01, value=round(1/(max(p_gana_a, 0.05)*margen_t), 2), step=0.05, key=f"cta_{k_ten}")
    cuota_t_b = ct2.number_input(f"Gana {jug_b}", min_value=1.01, value=round(1/(max(p_gana_b, 0.05)*margen_t), 2), step=0.05, key=f"ctb_{k_ten}")

    linea_juegos = st.sidebar.number_input("Línea Total de Juegos (Ej. 21.5 / 22.5)", min_value=16.5, max_value=42.5, value=21.5 if circuito_tenis.startswith("WTA") else 22.5, step=0.5)
    cuota_over_j = st.sidebar.number_input(f"Cuota Más de {linea_juegos} Juegos", min_value=1.01, value=1.87, step=0.05)
    cuota_under_j = st.sidebar.number_input(f"Cuota Menos de {linea_juegos} Juegos", min_value=1.01, value=1.90, step=0.05)

    p_over_juegos = float(1.0 - norm.cdf(linea_juegos, loc=juegos_totales_esp, scale=3.4))
    p_under_juegos = 1.0 - p_over_juegos

    st.markdown(f"### 🎾 {jug_a} vs. {jug_b} <span style='font-size:16px; color:#71717a; font-weight:normal;'>({circuito_tenis} • {superficie_tenis})</span>", unsafe_allow_html=True)

    tk1, tk2, tk3, tk4 = st.columns(4)
    tk1.metric("🏆 Prob. Victoria", f"{p_gana_a*100:.1f}% vs {p_gana_b*100:.1f}%", f"1er Set {jug_a}: {p_set_a*100:.1f}%")
    tk2.metric("🎾 Total Juegos Proyectados", f"{juegos_totales_esp} juegos", f"Media Hold Superficie: {media_hold_partido:.1f}%")
    tk3.metric("🔥 Aces Esperados (Superficie)", f"{aces_esp_total} aces", f"Factor superficie: x{factor_aces_sup:.2f}")
    tk4.metric("🔢 Prob. Tie-Break en Partido", f"{prob_tiebreak*100:.1f}%", f"Sets esperados: {sets_esperados:.2f}")

    ttab1, ttab2 = st.tabs([
        "🎯 1. Ganador, Sets, Total de Juegos y Tie-Break",
        "🔴 2. Radar En Vivo Tenis (In-Play)"
    ])

    with ttab1:
        mercados_tenis = [
            (f"Moneyline: Gana {jug_a}", p_gana_a, cuota_t_a),
            (f"Moneyline: Gana {jug_b}", p_gana_b, cuota_t_b),
            (f"Ganador del 1er Set: {jug_a}", p_set_a, round(1/(max(p_set_a, 0.05)*1.05), 2)),
            (f"Ganador del 1er Set: {jug_b}", p_set_b, round(1/(max(p_set_b, 0.05)*1.05), 2)),
            (f"Hándicap de Sets: {jug_a} -1.5 Sets (Gana 2-0)", p_2_0_a, round(1/(max(p_2_0_a, 0.05)*1.06), 2)),
            (f"Hándicap de Sets: {jug_b} +1.5 Sets (Gana al menos 1 set)", 1.0 - p_2_0_a, round(1/(max(1.0 - p_2_0_a, 0.05)*1.06), 2)),
            (f"Total de Juegos: Más de {linea_juegos} Juegos (Over)", p_over_juegos, cuota_over_j),
            (f"Total de Juegos: Menos de {linea_juegos} Juegos (Under)", p_under_juegos, cuota_under_j),
            ("Habrá Tie-Break en el Partido - SÍ", prob_tiebreak, round(1/(max(prob_tiebreak, 0.05)*1.06), 2))
        ]
        filas_ten = []
        for m, p, c in mercados_tenis:
            justa = 1 / p if p > 0 else 99.0
            edge = (p * c) - 1
            filas_ten.append({
                "Mercado Tenis (Betano)": m, "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Justa": f"{justa:.2f}", "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
            })
        st.dataframe(pd.DataFrame(filas_ten).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with ttab2:
        mostrar_cancha_calor(jug_a, jug_b, hold_efectivo_a, hold_efectivo_b, hold_efectivo_a/80.0, hold_efectivo_b/80.0, cancha_tipo)
        tl1, tl2, tl3 = st.columns(3)
        sets_vivo_a = tl1.number_input(f"Sets Ganados {jug_a}", 0, 2, 0)
        sets_vivo_b = tl2.number_input(f"Sets Ganados {jug_b}", 0, 2, 0)
        cuota_vivo_ten_a = tl3.number_input(f"Cuota En Vivo Gana {jug_a}", 1.01, 20.0, round(1/max(p_gana_a, 0.05), 2), 0.05)

        if sets_vivo_a == 1 and sets_vivo_b == 0:
            p_vivo_a = p_set_a + (p_set_b * p_set_a)
        elif sets_vivo_a == 0 and sets_vivo_b == 1:
            p_vivo_a = p_set_a * p_set_a
        else:
            p_vivo_a = p_set_a
        edge_v_ten = (p_vivo_a * cuota_vivo_ten_a) - 1.0
        st.info(f"📊 **Probabilidad En Vivo de {jug_a}:** `{p_vivo_a*100:.1f}%` | **Cuota Justa:** `{1/p_vivo_a:.2f}` | **Edge:** `{edge_v_ten*100:+.2f}%` -> {'🔥 ENTRAR EN VIVO (+EV)' if edge_v_ten > 0.04 else '❄️ Esperar mejor cuota'}")


# ==============================================================================
# 3. EJECUCIÓN MÓDULO NBA (BASKETBALL EE. UU. + RADAR EN VIVO)
# ==============================================================================
elif deporte_activo.startswith("🏀"):
    st.sidebar.markdown("### 🏀 1. Selección de Partido NBA")
    df_nba = cargar_datos_usa_sport("basketball", "nba", EQUIPOS_NBA_BASE, 114.5, 114.5)
    lista_nba = df_nba["Equipo"].tolist()

    nb1, nb2 = st.sidebar.columns(2)
    nba_loc = nb1.selectbox("🏠 Local (Home)", lista_nba, index=0)
    nba_vis = nb2.selectbox("✈️ Visita (Road)", lista_nba, index=1 if len(lista_nba) > 1 else 0)

    r_nba_l = df_nba[df_nba["Equipo"] == nba_loc].iloc[0]
    r_nba_v = df_nba[df_nba["Equipo"] == nba_vis].iloc[0]
    media_nba = float(df_nba["PF_Home"].mean())

    k_nba = f"{nba_loc}_{nba_vis}"
    with st.sidebar.expander("⚙️ Auditoría / Ajuste Manual NBA (Puntos)"):
        pts_fav_l = st.number_input(f"Puntos a Favor {nba_loc}", 85.0, 140.0, float(r_nba_l["PF_Home"]), 0.5, key=f"nb1_{k_nba}")
        pts_con_l = st.number_input(f"Puntos en Contra {nba_loc}", 85.0, 140.0, float(r_nba_l["PA_Home"]), 0.5, key=f"nb2_{k_nba}")
        pts_fav_v = st.number_input(f"Puntos a Favor {nba_vis}", 85.0, 140.0, float(r_nba_v["PF_Away"]), 0.5, key=f"nb3_{k_nba}")
        pts_con_v = st.number_input(f"Puntos en Contra {nba_vis}", 85.0, 140.0, float(r_nba_v["PA_Away"]), 0.5, key=f"nb4_{k_nba}")

    # Proyección Gaussiana NBA (Incluye +2.2 pts de ventaja de cancha local)
    proy_nba_l = ((pts_fav_l + pts_con_v) / 2.0) + 1.1
    proy_nba_v = ((pts_fav_v + pts_con_l) / 2.0) - 1.1
    total_nba_esp = proy_nba_l + proy_nba_v
    margen_nba_esp = proy_nba_l - proy_nba_v  # Positivo = Local favorito

    # Desviación estándar histórica NBA: ~11.8 pts para margen, ~15.5 pts para totales
    p_nba_ml_l = float(1.0 - norm.cdf(0.0, loc=margen_nba_esp, scale=11.8))
    p_nba_ml_v = 1.0 - p_nba_ml_l

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Líneas y Cuotas NBA en Betano")
    spread_nba = st.sidebar.number_input(f"Línea Hándicap / Spread {nba_loc} (Ej. -4.5 o +3.5)", -25.5, 25.5, round(-margen_nba_esp * 2) / 2, 0.5, key=f"sp_{k_nba}")
    cuota_spread_l = st.sidebar.number_input(f"Cuota Spread {nba_loc} ({spread_nba:+.1f})", 1.01, 10.0, 1.90, 0.05)
    linea_tot_nba = st.sidebar.number_input("Línea Puntos Totales NBA", 180.5, 265.5, round(total_nba_esp * 2) / 2, 0.5, key=f"tot_{k_nba}")
    cuota_over_nba = st.sidebar.number_input(f"Cuota Over {linea_tot_nba} Pts", 1.01, 10.0, 1.90, 0.05)

    p_cubre_spread_l = float(1.0 - norm.cdf(-spread_nba, loc=margen_nba_esp, scale=11.8))
    p_over_nba = float(1.0 - norm.cdf(linea_tot_nba, loc=total_nba_esp, scale=15.5))
    proy_1q_total = total_nba_esp * 0.252

    st.markdown(f"### 🏀 {nba_loc} vs. {nba_vis} <span style='font-size:16px; color:#71717a; font-weight:normal;'>(NBA Basketball)</span>", unsafe_allow_html=True)
    bk1, bk2, bk3, bk4 = st.columns(4)
    bk1.metric("🏀 Marcador Proyectado", f"{proy_nba_l:.1f} - {proy_nba_v:.1f}", f"Total: {total_nba_esp:.1f} pts")
    bk2.metric("🏆 Prob. Moneyline", f"{p_nba_ml_l*100:.1f}% vs {p_nba_ml_v*100:.1f}%", f"Spread justo: {nba_loc} {-margen_nba_esp:+.1f}")
    bk3.metric("⏱️ Proyección 1er Cuarto (1Q)", f"{proy_1q_total:.1f} pts", f"{proy_nba_l*0.252:.1f} L - {proy_nba_v*0.252:.1f} V")
    bk4.metric("🎯 Prob. Cubrir Spread", f"{p_cubre_spread_l*100:.1f}%", f"Línea evaluada: {spread_nba:+.1f}")

    btab1, btab2 = st.tabs(["🎯 1. Moneyline, Spread, Totales y 1er Cuarto", "🔴 2. Radar En Vivo NBA (In-Play)"])
    with btab1:
        mercados_nba = [
            (f"Moneyline: Gana {nba_loc} (Incluye Prórroga)", p_nba_ml_l, round(1/(max(p_nba_ml_l, 0.05)*1.05), 2)),
            (f"Moneyline: Gana {nba_vis} (Incluye Prórroga)", p_nba_ml_v, round(1/(max(p_nba_ml_v, 0.05)*1.05), 2)),
            (f"Hándicap / Spread: {nba_loc} {spread_nba:+.1f} Puntos", p_cubre_spread_l, cuota_spread_l),
            (f"Hándicap / Spread: {nba_vis} {-spread_nba:+.1f} Puntos", 1.0 - p_cubre_spread_l, 1.90),
            (f"Puntos Totales: Más de {linea_tot_nba} Puntos (Over)", p_over_nba, cuota_over_nba),
            (f"Puntos Totales: Menos de {linea_tot_nba} Puntos (Under)", 1.0 - p_over_nba, 1.90),
            (f"Team Total: {nba_loc} Más de {round(proy_nba_l)-0.5} Puntos", 0.53, 1.88),
            (f"1er Cuarto (1Q): Más de {round(proy_1q_total)-0.5} Puntos", 0.54, 1.87)
        ]
        filas_nba = []
        for m, p, c in mercados_nba:
            justa = 1 / p if p > 0 else 99.0
            edge = (p * c) - 1
            filas_nba.append({
                "Mercado NBA (Betano)": m, "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Justa": f"{justa:.2f}", "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
            })
        st.dataframe(pd.DataFrame(filas_nba).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with btab2:
        mostrar_cancha_calor(nba_loc, nba_vis, p_nba_ml_l*100, p_nba_ml_v*100, 1.1, 1.0, "nba")
        bc1, bc2, bc3, bc4 = st.columns(4)
        min_nba_v = bc1.slider("⏱️ Minuto Jugado NBA (0-48')", 1, 47, 24)
        pts_v_l = bc2.number_input(f"Puntos En Vivo {nba_loc}", 0, 180, 56)
        pts_v_v = bc3.number_input(f"Puntos En Vivo {nba_vis}", 0, 180, 54)
        linea_v_nba = bc4.number_input("Línea Total En Vivo Betano", 170.5, 280.5, 224.5, 0.5)
        frac_rest_nba = (48.0 - min_nba_v) / 48.0
        tot_final_vivo_nba = (pts_v_l + pts_v_v) + (total_nba_esp * frac_rest_nba)
        p_over_v_nba = float(1.0 - norm.cdf(linea_v_nba, loc=tot_final_vivo_nba, scale=max(15.5 * np.sqrt(frac_rest_nba), 3.0)))
        st.info(f"🏀 **Proyección Final En Vivo:** `{tot_final_vivo_nba:.1f} Puntos` | **Prob. Over {linea_v_nba}:** `{p_over_v_nba*100:.1f}%` (Cuota Justa: `{1/max(p_over_v_nba,0.01):.2f}`) | **Prob. Under {linea_v_nba}:** `{(1-p_over_v_nba)*100:.1f}%` (Cuota Justa: `{1/max(1-p_over_v_nba,0.01):.2f}`)")


# ==============================================================================
# 4. EJECUCIÓN MÓDULO NFL (FÚTBOL AMERICANO EE. UU. + RADAR EN VIVO)
# ==============================================================================
elif deporte_activo.startswith("🏈"):
    st.sidebar.markdown("### 🏈 1. Selección de Partido NFL")
    df_nfl = cargar_datos_usa_sport("football", "nfl", EQUIPOS_NFL_BASE, 22.8, 22.8)
    lista_nfl = df_nfl["Equipo"].tolist()

    nf1, nf2 = st.sidebar.columns(2)
    nfl_loc = nf1.selectbox("🏠 Local (Home)", lista_nfl, index=0)
    nfl_vis = nf2.selectbox("✈️ Visita (Road)", lista_nfl, index=1 if len(lista_nfl) > 1 else 0)

    r_nfl_l = df_nfl[df_nfl["Equipo"] == nfl_loc].iloc[0]
    r_nfl_v = df_nfl[df_nfl["Equipo"] == nfl_vis].iloc[0]

    k_nfl = f"{nfl_loc}_{nfl_vis}"
    with st.sidebar.expander("⚙️ Auditoría / Ajuste Manual NFL (Puntos por Partido)"):
        nfl_pf_l = st.number_input(f"Puntos a Favor {nfl_loc}", 10.0, 42.0, float(r_nfl_l["PF_Home"]), 0.5, key=f"nf1_{k_nfl}")
        nfl_pa_l = st.number_input(f"Puntos en Contra {nfl_loc}", 10.0, 42.0, float(r_nfl_l["PA_Home"]), 0.5, key=f"nf2_{k_nfl}")
        nfl_pf_v = st.number_input(f"Puntos a Favor {nfl_vis}", 10.0, 42.0, float(r_nfl_v["PF_Away"]), 0.5, key=f"nf3_{k_nfl}")
        nfl_pa_v = st.number_input(f"Puntos en Contra {nfl_vis}", 10.0, 42.0, float(r_nfl_v["PA_Away"]), 0.5, key=f"nf4_{k_nfl}")

    proy_nfl_l = ((nfl_pf_l + nfl_pa_v) / 2.0) + 0.9
    proy_nfl_v = ((nfl_pf_v + nfl_pa_l) / 2.0) - 0.9
    tot_nfl_esp = proy_nfl_l + proy_nfl_v
    margen_nfl_esp = proy_nfl_l - proy_nfl_v

    # Desviación estándar NFL: 13.2 pts para margen, 13.5 pts para total
    p_nfl_ml_l = float(1.0 - norm.cdf(0.0, loc=margen_nfl_esp, scale=13.2))
    p_nfl_ml_v = 1.0 - p_nfl_ml_l
    tds_esp = tot_nfl_esp / 8.3

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Líneas y Cuotas NFL en Betano")
    spread_nfl = st.sidebar.number_input(f"Spread {nfl_loc} (Números clave: -3.0, -3.5, -7.0)", -21.5, 21.5, round(-margen_nfl_esp * 2) / 2, 0.5, key=f"spn_{k_nfl}")
    cuota_sp_nfl = st.sidebar.number_input(f"Cuota Spread {nfl_loc}", 1.01, 10.0, 1.90, 0.05)
    linea_tot_nfl = st.sidebar.number_input("Línea Total Puntos NFL", 30.5, 62.5, round(tot_nfl_esp * 2) / 2, 0.5, key=f"totn_{k_nfl}")
    cuota_ov_nfl = st.sidebar.number_input(f"Cuota Over {linea_tot_nfl}", 1.01, 10.0, 1.90, 0.05)

    p_cubre_nfl = float(1.0 - norm.cdf(-spread_nfl, loc=margen_nfl_esp, scale=13.2))
    p_over_nfl = float(1.0 - norm.cdf(linea_tot_nfl, loc=tot_nfl_esp, scale=13.5))
    p_td_over45 = 1.0 - sum(poisson.pmf(k, tds_esp) for k in range(5))

    st.markdown(f"### 🏈 {nfl_loc} vs. {nfl_vis} <span style='font-size:16px; color:#71717a; font-weight:normal;'>(NFL Fútbol Americano)</span>", unsafe_allow_html=True)
    fk1, fk2, fk3, fk4 = st.columns(4)
    fk1.metric("🏈 Marcador Proyectado", f"{proy_nfl_l:.1f} - {proy_nfl_v:.1f}", f"Total: {tot_nfl_esp:.1f} pts")
    fk2.metric("🏆 Prob. Moneyline", f"{p_nfl_ml_l*100:.1f}% vs {p_nfl_ml_v*100:.1f}%", f"Spread justo: {-margen_nfl_esp:+.1f}")
    fk3.metric("⏱️ Proyección 1ª Mitad (1H)", f"{tot_nfl_esp*0.50:.1f} pts (1H)", f"{proy_nfl_l*0.5:.1f} - {proy_nfl_v*0.5:.1f}")
    fk4.metric("🔥 Touchdowns Esperados", f"{tds_esp:.1f} TDs", f"Over 4.5 TDs: {p_td_over45*100:.1f}%")

    ftab1, ftab2 = st.tabs(["🎯 1. Moneyline, Spread, Totales, 1ª Mitad y Touchdowns", "🔴 2. Radar En Vivo NFL"])
    with ftab1:
        mercados_nfl = [
            (f"Moneyline: Gana {nfl_loc}", p_nfl_ml_l, round(1/(max(p_nfl_ml_l, 0.05)*1.05), 2)),
            (f"Moneyline: Gana {nfl_vis}", p_nfl_ml_v, round(1/(max(p_nfl_ml_v, 0.05)*1.05), 2)),
            (f"Spread / Hándicap: {nfl_loc} {spread_nfl:+.1f} Puntos", p_cubre_nfl, cuota_sp_nfl),
            (f"Spread / Hándicap: {nfl_vis} {-spread_nfl:+.1f} Puntos", 1.0 - p_cubre_nfl, 1.90),
            (f"Total Puntos: Más de {linea_tot_nfl} Puntos (Over)", p_over_nfl, cuota_ov_nfl),
            (f"Total Puntos: Menos de {linea_tot_nfl} Puntos (Under)", 1.0 - p_over_nfl, 1.90),
            ("Total Touchdowns del Partido: Más de 4.5 TDs", p_td_over45, 1.85)
        ]
        filas_nfl = []
        for m, p, c in mercados_nfl:
            justa = 1 / p if p > 0 else 99.0
            edge = (p * c) - 1
            filas_nfl.append({
                "Mercado NFL (Betano)": m, "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Justa": f"{justa:.2f}", "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
            })
        st.dataframe(pd.DataFrame(filas_nfl).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with ftab2:
        mostrar_cancha_calor(nfl_loc, nfl_vis, p_nfl_ml_l*100, p_nfl_ml_v*100, 1.1, 1.0, "nfl")


# ==============================================================================
# 5. EJECUCIÓN MÓDULO MLB (BÉISBOL EE. UU. + PITCHEO ABRIDOR + F5 & NRFI)
# ==============================================================================
elif deporte_activo.startswith("⚾"):
    st.sidebar.markdown("### ⚾ 1. Selección de Partido MLB y Pitcheo")
    df_mlb = cargar_datos_usa_sport("baseball", "mlb", EQUIPOS_MLB_BASE, 4.55, 4.55)
    lista_mlb = df_mlb["Equipo"].tolist()

    mb1, mb2 = st.sidebar.columns(2)
    mlb_loc = mb1.selectbox("🏠 Local (Home)", lista_mlb, index=0)
    mlb_vis = mb2.selectbox("✈️ Visita (Road)", lista_mlb, index=1 if len(lista_mlb) > 1 else 0)

    r_mlb_l = df_mlb[df_mlb["Equipo"] == mlb_loc].iloc[0]
    r_mlb_v = df_mlb[df_mlb["Equipo"] == mlb_vis].iloc[0]

    k_mlb = f"{mlb_loc}_{mlb_vis}"
    with st.sidebar.expander("⚙️ Ajuste de Carreras y ERA de Abridores (Pitchers)"):
        runs_f_l = st.number_input(f"Carreras a Favor {mlb_loc}", 2.0, 8.0, float(r_mlb_l["PF_Home"]), 0.1, key=f"m1_{k_mlb}")
        era_pitcher_l = st.number_input(f"ERA Lanzador Abridor {mlb_loc} (Media MLB ~4.15)", 1.50, 7.50, 3.85, 0.10, key=f"m2_{k_mlb}")
        runs_f_v = st.number_input(f"Carreras a Favor {mlb_vis}", 2.0, 8.0, float(r_mlb_v["PF_Away"]), 0.1, key=f"m3_{k_mlb}")
        era_pitcher_v = st.number_input(f"ERA Lanzador Abridor {mlb_vis} (Media MLB ~4.15)", 1.50, 7.50, 4.05, 0.10, key=f"m4_{k_mlb}")

    # Proyección de Carreras Poisson ponderando Ofensiva + Pitcheo Rival
    lam_mlb_l = max(runs_f_l * (era_pitcher_v / 4.15), 1.5)
    lam_mlb_v = max(runs_f_v * (era_pitcher_l / 4.15), 1.5)
    lam_mlb_tot = lam_mlb_l + lam_mlb_v

    mat_mlb = np.zeros((16, 16))
    for i in range(16):
        for j in range(16):
            mat_mlb[i, j] = poisson.pmf(i, lam_mlb_l) * poisson.pmf(j, lam_mlb_v)

    p_mlb_reg_l = float(np.sum(np.tril(mat_mlb, -1)))
    p_mlb_emp = float(np.sum(np.diag(mat_mlb)))
    p_mlb_reg_v = float(np.sum(np.triu(mat_mlb, 1)))

    # En MLB no hay empate final (Extra Innings)
    ratio_ei_l = lam_mlb_l / lam_mlb_tot
    p_mlb_ml_l = p_mlb_reg_l + (p_mlb_emp * ratio_ei_l)
    p_mlb_ml_v = p_mlb_reg_v + (p_mlb_emp * (1.0 - ratio_ei_l))

    # Run Line (-1.5 / +1.5)
    p_rl_l_m15 = float(np.sum(np.tril(mat_mlb, -2)))
    p_rl_v_p15 = 1.0 - p_rl_l_m15

    # Primeras 5 Entradas (F5 = 56% del total de carreras) y NRFI (1ª Entrada = 11.5% del total)
    lam_f5_tot = lam_mlb_tot * 0.56
    p_nrfi = float(poisson.pmf(0, lam_mlb_tot * 0.115))  # 0 carreras en el 1er Inning
    p_yrfi = 1.0 - p_nrfi

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas MLB en Betano")
    linea_runs_mlb = st.sidebar.selectbox("Línea Total de Carreras", [7.5, 8.0, 8.5, 9.0, 9.5], index=2)
    cuota_ov_mlb = st.sidebar.number_input(f"Cuota Más de {linea_runs_mlb} Carreras", 1.01, 10.0, 1.88, 0.05)
    cuota_nrfi = st.sidebar.number_input("Cuota NRFI (0 Carreras en 1ª Entrada)", 1.01, 10.0, 1.85, 0.05)

    p_over_mlb = 1.0 - sum(poisson.pmf(k, lam_mlb_tot) for k in range(int(linea_runs_mlb) + 1))

    st.markdown(f"### ⚾ {mlb_loc} vs. {mlb_vis} <span style='font-size:16px; color:#71717a; font-weight:normal;'>(MLB Béisbol)</span>", unsafe_allow_html=True)
    mk1, mk2, mk3, mk4 = st.columns(4)
    mk1.metric("⚾ Carreras Esperadas (9 Inn)", f"{lam_mlb_l:.2f} - {lam_mlb_v:.2f}", f"Total: {lam_mlb_tot:.2f} carreras")
    mk2.metric("🏆 Prob. Moneyline", f"{p_mlb_ml_l*100:.1f}% vs {p_mlb_ml_v*100:.1f}%", f"Run Line -1.5 L: {p_rl_l_m15*100:.1f}%")
    mk3.metric("5️⃣ Primeras 5 Entradas (F5)", f"{lam_f5_tot:.2f} carreras", f"{lam_mlb_l*0.56:.2f} L - {lam_mlb_v*0.56:.2f} V")
    mk4.metric("1️⃣ Prob. NRFI (1ª Entrada 0-0)", f"{p_nrfi*100:.1f}%", f"YRFI (Sí anotan 1ª): {p_yrfi*100:.1f}%")

    mtab1, mtab2 = st.tabs(["🎯 1. Moneyline, Run Line, Totales, F5 y NRFI/YRFI", "🔴 2. Radar En Vivo MLB"])
    with mtab1:
        mercados_mlb = [
            (f"Moneyline: Gana {mlb_loc} (Incluye Extra Innings)", p_mlb_ml_l, round(1/(max(p_mlb_ml_l, 0.05)*1.05), 2)),
            (f"Moneyline: Gana {mlb_vis} (Incluye Extra Innings)", p_mlb_ml_v, round(1/(max(p_mlb_ml_v, 0.05)*1.05), 2)),
            (f"Run Line: {mlb_loc} -1.5 Carreras", p_rl_l_m15, round(1/(max(p_rl_l_m15, 0.05)*1.06), 2)),
            (f"Run Line: {mlb_vis} +1.5 Carreras", p_rl_v_p15, round(1/(max(p_rl_v_p15, 0.05)*1.06), 2)),
            (f"Total de Carreras: Más de {linea_runs_mlb} Carreras (Over)", p_over_mlb, cuota_ov_mlb),
            (f"Total de Carreras: Menos de {linea_runs_mlb} Carreras (Under)", 1.0 - p_over_mlb, 1.90),
            ("1ª Entrada: NRFI (No habrá carrera en el 1er Inning)", p_nrfi, cuota_nrfi),
            ("1ª Entrada: YRFI (Sí habrá carrera en el 1er Inning)", p_yrfi, round(1/(max(p_yrfi, 0.05)*1.06), 2))
        ]
        filas_mlb = []
        for m, p, c in mercados_mlb:
            justa = 1 / p if p > 0 else 99.0
            edge = (p * c) - 1
            filas_mlb.append({
                "Mercado MLB (Betano)": m, "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Justa": f"{justa:.2f}", "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
            })
        st.dataframe(pd.DataFrame(filas_mlb).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with mtab2:
        mostrar_cancha_calor(mlb_loc, mlb_vis, p_mlb_ml_l*100, p_mlb_ml_v*100, 1.1, 1.0, "mlb")


# ==============================================================================
# 6. EJECUCIÓN MÓDULO NHL (100% INTACTO CON PUCK LINE, 60M, SOG Y RADAR EN VIVO)
# ==============================================================================
else:
    st.sidebar.markdown("### 🏒 1. Selección de Partido NHL")
    df_nhl = cargar_datos_nhl()
    lista_nhl = df_nhl["Equipo"].tolist()

    col_nhl1, col_nhl2 = st.sidebar.columns(2)
    nhl_local = col_nhl1.selectbox("🏠 Local (Home)", lista_nhl, index=0)
    nhl_visita = col_nhl2.selectbox("✈️ Visita (Road)", lista_nhl, index=1 if len(lista_nhl) > 1 else 0)

    usar_bayes_nhl = st.sidebar.checkbox("🛡️ Amortiguador Bayesiano NHL (< 8 PJ)", value=True)

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

    k_nhl = f"{nhl_local}_{nhl_visita}_{usar_bayes_nhl}"

    with st.sidebar.expander("⚙️ Auditoría / Ajuste Manual NHL (Goles y SOG)"):
        st.caption(f"Muestra API NHL: {nhl_local} ({pj_nhl_loc} PJ Casa) | {nhl_visita} ({pj_nhl_vis} PJ Ruta)")
        nhl_gf_loc = st.number_input("Goles a Favor Local (60m/OT)", min_value=0.5, max_value=7.0, value=round(gf_nhl_loc_c, 2), step=0.05, key=f"n1_{k_nhl}")
        nhl_gc_loc = st.number_input("Goles en Contra Local", min_value=0.5, max_value=7.0, value=round(gc_nhl_loc_c, 2), step=0.05, key=f"n2_{k_nhl}")
        nhl_gf_vis = st.number_input("Goles a Favor Visita (60m/OT)", min_value=0.5, max_value=7.0, value=round(gf_nhl_vis_c, 2), step=0.05, key=f"n3_{k_nhl}")
        nhl_gc_vis = st.number_input("Goles en Contra Visita", min_value=0.5, max_value=7.0, value=round(gc_nhl_vis_c, 2), step=0.05, key=f"n4_{k_nhl}")
        nhl_media = st.number_input("Promedio Goles NHL por Equipo", min_value=1.5, max_value=5.0, value=round(media_liga_nhl, 2), step=0.05, key=f"n5_{k_nhl}")
        st.markdown("---")
        sog_loc_in = st.number_input("Disparos al Arco (SOG Local)", min_value=15.0, max_value=45.0, value=float(row_nhl_loc["SOG_Home"]), step=0.5, key=f"n6_{k_nhl}")
        sog_vis_in = st.number_input("Disparos al Arco (SOG Visita)", min_value=15.0, max_value=45.0, value=float(row_nhl_vis["SOG_Away"]), step=0.5, key=f"n7_{k_nhl}")

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
    cuota_ml_loc = c_ml1.number_input("Moneyline Local (Inc. OT)", min_value=1.01, value=round(1/(max(p_ml_loc, 0.05)*margen_nhl), 2), step=0.05, key=f"cml1_{k_nhl}")
    cuota_ml_vis = c_ml2.number_input("Moneyline Visita (Inc. OT)", min_value=1.01, value=round(1/(max(p_ml_vis, 0.05)*margen_nhl), 2), step=0.05, key=f"cml2_{k_nhl}")

    c_ot1, c_ot2 = st.sidebar.columns(2)
    linea_total_nhl = c_ot1.selectbox("Línea Goles Totales", [5.5, 6.0, 6.5], index=2)
    cuota_over_nhl = c_ot2.number_input(f"Cuota Over {linea_total_nhl}", min_value=1.01, value=1.88, step=0.05)
    cuota_under_nhl = st.sidebar.number_input(f"Cuota Under {linea_total_nhl}", min_value=1.01, value=1.92, step=0.05)

    with st.sidebar.expander("🏒 Cuotas Puck Line, 60 Min, 1er Período y SOG"):
        c_reg1, c_reg2, c_reg3 = st.columns(3)
        cuota_60_1 = c_reg1.number_input("1 (60 Min)", min_value=1.01, value=round(1/(max(p_reg_loc, 0.05)*1.06), 2), step=0.05, key=f"c601_{k_nhl}")
        cuota_60_x = c_reg2.number_input("X (Empate 60')", min_value=1.01, value=4.20, step=0.10)
        cuota_60_2 = c_reg3.number_input("2 (60 Min)", min_value=1.01, value=round(1/(max(p_reg_vis, 0.05)*1.06), 2), step=0.05, key=f"c602_{k_nhl}")
        cuota_pl_loc_m15 = st.number_input(f"{nhl_local} -1.5 (Puck Line)", min_value=1.01, value=2.45, step=0.05)
        cuota_pl_vis_p15 = st.number_input(f"{nhl_visita} +1.5 (Puck Line)", min_value=1.01, value=1.55, step=0.05)
        cuota_1p_o15 = st.number_input("Cuota 1er Período Over 1.5 Goles", min_value=1.01, value=1.82, step=0.05)
        cuota_tt_loc_o35 = st.number_input(f"Cuota {nhl_local} Over 3.5 Goles", min_value=1.01, value=2.15, step=0.05)
        cuota_tt_vis_o25 = st.number_input(f"Cuota {nhl_visita} Over 2.5 Goles", min_value=1.01, value=1.78, step=0.05)
        linea_sog_total = st.number_input("Línea Disparos a Puerta (SOG Total)", min_value=45.5, max_value=75.5, value=59.5, step=1.0)
        cuota_sog_over = st.number_input("Cuota Over SOG", min_value=1.01, value=1.87, step=0.05)

    p_over_total_nhl = 1.0 - sum(poisson.pmf(k, lam_nhl_total) for k in range(int(linea_total_nhl) + 1))
    p_under_total_nhl = 1.0 - p_over_total_nhl
    p_tt_loc_o35 = 1.0 - sum(poisson.pmf(k, lam_nhl_loc) for k in range(4))
    p_tt_vis_o25 = 1.0 - sum(poisson.pmf(k, lam_nhl_vis) for k in range(3))
    lam_sog_tot = sog_loc_in + sog_vis_in
    p_sog_over = 1.0 - sum(poisson.pmf(k, lam_sog_tot) for k in range(int(linea_sog_total) + 1))

    st.markdown(f"### 🧊 {nhl_local} vs. {nhl_visita} <span style='font-size:16px; color:#71717a; font-weight:normal;'>(NHL Hockey sobre Hielo)</span>", unsafe_allow_html=True)

    nk1, nk2, nk3, nk4 = st.columns(4)
    nk1.metric("🏒 Goles Esperados (60m)", f"{lam_nhl_loc:.2f} - {lam_nhl_vis:.2f}", f"Total: {lam_nhl_total:.2f} goles")
    nk2.metric("🏆 Prob. Moneyline (Inc. OT)", f"{p_ml_loc*100:.1f}% vs {p_ml_vis*100:.1f}%", f"Prob. Prórroga (OT): {p_reg_emp*100:.1f}%")
    nk3.metric("⏱️ Proyección 1er Período", f"{lam_1p_total:.2f} goles (1P)", f"Over 1.5 (1P): {p_1p_over15*100:.1f}%")
    nk4.metric("🥅 Disparos al Arco (SOG)", f"{lam_sog_tot:.1f} tiros", f"{sog_loc_in:.1f} L + {sog_vis_in:.1f} V")

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
                "Mercado Principal NHL": m, "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Justa": f"{justa:.2f}", "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
            })
        st.dataframe(pd.DataFrame(filas_nhl_1).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

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
                "Mercado Especial NHL": m, "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Justa": f"{justa:.2f}", "Cuota Betano": f"{c:.2f}",
                "Edge / Ventaja (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
            })
        st.dataframe(pd.DataFrame(filas_nhl_2).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with ntab3:
        df_mat_nhl = pd.DataFrame(
            mat_nhl[:8, :8] * 100,
            index=[f"🏠 {nhl_local} ({i})" for i in range(8)],
            columns=[f"✈️ {nhl_visita} ({j})" for j in range(8)]
        )
        st.dataframe(df_mat_nhl.style.format("{:.1f}%").background_gradient(cmap="Blues"), use_container_width=True)

    with ntab4:
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

        mostrar_cancha_calor(nhl_local, nhl_visita, dom_nhl_l, dom_nhl_v, ritmo_nhl_l, ritmo_nhl_v, "nhl")
