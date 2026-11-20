import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from scipy.stats import poisson, norm
import requests
import unicodedata
import io
import re
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Pro Bet Analyzer 13.0 | Deep Intelligence, Cards & SOG",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS ---
st.markdown("""
<style>
.main-banner {
    background: linear-gradient(135deg, #18181b 0%, #27272a 60%, #ea580c 100%);
    padding: 22px 28px;
    border-radius: 14px;
    color: #ffffff;
    margin-bottom: 22px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.12);
    border-left: 8px solid #ff6b00;
}
.main-banner h1 {
    color: #ffffff !important;
    margin: 0;
    font-size: 2.0rem;
    font-weight: 800;
    letter-spacing: -0.5px;
}
.main-banner p {
    color: #e4e4e7 !important;
    margin: 6px 0 0 0;
    font-size: 0.95rem;
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
.fav-banner {
    background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
    color: #f8fafc;
    padding: 14px 20px;
    border-radius: 10px;
    border-left: 6px solid #22c55e;
    margin-bottom: 16px;
    font-size: 0.96rem;
}
.injury-alert {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-left: 5px solid #dc2626;
    color: #7f1d1d;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 12px;
    font-size: 0.90rem;
}
</style>
<div class="main-banner">
<h1>🏆 PRO BET ANALYZER 13.0 <span style="color:#ff8c00;">| DEEP INTELLIGENCE, CARDS & SOG SUITE</span></h1>
<p>Factor de Incidencia por Bajas Clave en Todos los Deportes • Tarjetas Reales (HY/AY/HR/AR) en Fútbol • Shots on Goal (SOG) Reales en NHL</p>
</div>
""", unsafe_allow_html=True)

HEADERS_HTTP = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def resaltar_valor(fila):
    veredicto = str(fila.get("Veredicto", ""))
    if "✅" in veredicto or "🔥" in veredicto:
        return ['background-color: rgba(22, 163, 74, 0.15); font-weight: 600;'] * len(fila)
    return [''] * len(fila)

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
<div style="background:{bg_pitch}; border: 3px solid {border_pitch}; border-radius: 14px; height: 250px; position: relative; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,0.18); font-family: system-ui, -apple-system, sans-serif;">
<div style="position:absolute; left:50%; top:0; bottom:0; width:3px; background:{line_color}; transform:translateX(-50%);"></div>
<div style="position:absolute; left:50%; top:50%; width:80px; height:80px; border:3px solid {line_color}; border-radius:50%; transform:translate(-50%, -50%);"></div>
<div style="position:absolute; left:0; top:22%; bottom:22%; width:15%; border-right:3px solid {line_color}; border-top:3px solid {line_color}; border-bottom:3px solid {line_color};"></div>
<div style="position:absolute; right:0; top:22%; bottom:22%; width:15%; border-left:3px solid {line_color}; border-top:3px solid {line_color}; border-bottom:3px solid {line_color};"></div>
<div style="position:absolute; right:5%; top:50%; width:{rad_loc}px; height:{rad_loc}px; background:radial-gradient(circle, rgba(255,59,0,{op_loc}) 0%, rgba(255,145,0,{op_loc*0.65}) 45%, rgba(255,255,0,0) 75%); transform:translateY(-50%); border-radius:50%; pointer-events:none;"></div>
<div style="position:absolute; left:5%; top:50%; width:{rad_vis}px; height:{rad_vis}px; background:radial-gradient(circle, rgba(0,200,255,{op_vis}) 0%, rgba(0,110,255,{op_vis*0.65}) 45%, rgba(0,0,255,0) 75%); transform:translateY(-50%); border-radius:50%; pointer-events:none;"></div>
<div style="position:absolute; left:16px; top:12px; background:rgba(15,23,42,0.85); color:#fff; padding:6px 12px; border-radius:8px; font-weight:700; font-size:13px; border-left: 4px solid #ff6b00;">
🏠 {eq_loc} | Dominio: {dom_loc:.0f}%
</div>
<div style="position:absolute; right:16px; top:12px; background:rgba(15,23,42,0.85); color:#fff; padding:6px 12px; border-radius:8px; font-weight:700; font-size:13px; border-right: 4px solid #38bdf8;">
Dominio: {dom_vis:.0f}% | {eq_vis} ✈️
</div>
</div>
"""
    components.html(html_code, height=265)

# ==============================================================================
# MOTOR DE INTELIGENCIA DE NOTICIAS Y REPORTES DE LESIONES EN VIVO (ESPN API)
# ==============================================================================
ESPN_LEAGUE_MAP = {
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

@st.cache_data(ttl=900)
def obtener_reporte_lesiones_espn(sport, league, eq_a, eq_b):
    """Consulta en vivo /injuries de ESPN y filtra los lesionados/dudosos de ambos equipos."""
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
                    est = item.get("status", "Questionable")
                    det = item.get("shortComment", item.get("longComment", "Reporte médico activo"))
                    filas_inj.append({
                        "Equipo": etiqueta_eq,
                        "Jugador": jug,
                        "Pos.": pos,
                        "Estado": est,
                        "Detalle / Parte Médico": str(det)[:110]
                    })
    except Exception:
        pass
    return pd.DataFrame(filas_inj)

@st.cache_data(ttl=900)
def obtener_noticias_relevantes_espn(sport, league, eq_a, eq_b):
    """Extrae titulares recientes desde /news de ESPN filtrados por los protagonistas del partido."""
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
                titulares.append(f"📰 **[{fecha_n}] {hl}** — _{desc[:140]}_")
    except Exception:
        pass
    return titulares[:6]

def renderizar_panel_bajas_y_factor(sport, league, eq_loc, eq_vis, key_prefix):
    """Muestra el reporte médico en vivo y los controles de Factor de Incidencia por bajas."""
    df_inj = obtener_reporte_lesiones_espn(sport, league, eq_loc, eq_vis)
    noticias = obtener_noticias_relevantes_espn(sport, league, eq_loc, eq_vis)

    with st.expander(f"🏥 INTELIGENCIA DE BAJAS, LESIONES Y NOTICIAS EN VIVO ({eq_loc} vs. {eq_vis})", expanded=False):
        if not df_inj.empty:
            st.warning(f"⚠️ **Reporte Médico Oficial Detectado ({len(df_inj)} bajas/dudas registradas en API ESPN):**")
            st.dataframe(df_inj, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Sin listado detallado de lesionados en el feed público de ESPN para este cruce (puedes ajustar manualmente el Factor de Incidencia en la barra lateral si conoces una baja de última hora).")

        if noticias:
            st.markdown("**🗞️ Últimas Noticias Relevantes Detectadas:**")
            for n in noticias:
                st.markdown(n)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏥 Factor de Incidencia por Bajas")
    imp_loc = st.sidebar.slider(
        f"Penalización Ofensiva {eq_loc} (%)",
        min_value=0, max_value=30, value=0, step=5,
        help="Reduce la proyección ofensiva del equipo local si faltan figuras clave (ej. -10% delantero/QB estrella, -20% múltiples titulares).",
        key=f"imp_l_{key_prefix}"
    )
    imp_vis = st.sidebar.slider(
        f"Penalización Ofensiva {eq_vis} (%)",
        min_value=0, max_value=30, value=0, step=5,
        help="Reduce la proyección ofensiva del equipo visitante si faltan figuras clave.",
        key=f"imp_v_{key_prefix}"
    )
    return 1.0 - (imp_loc / 100.0), 1.0 - (imp_vis / 100.0), imp_loc, imp_vis

# ==============================================================================
# FUNCIONES GLOBALES DE DATOS DEPORTIVOS (NATIONS LEAGUE, ESPN, NHL)
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

@st.cache_data(ttl=1800)
def obtener_catalogo_equipos_espn(sport, league):
    mapa_ids = {}
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams?limit=100"
        r = requests.get(url, headers=HEADERS_HTTP, timeout=8).json()
        for sp in r.get("sports", []):
            for lg in sp.get("leagues", []):
                for t_wrap in lg.get("teams", []):
                    tm = t_wrap.get("team", {})
                    nombre = tm.get("displayName")
                    tid = str(tm.get("id", ""))
                    if nombre and tid:
                        mapa_ids[nombre] = tid
    except Exception:
        pass
    return mapa_ids

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
                            "Anotados": int(pts_yo),
                            "Recibidos": int(pts_riv),
                            "Total": int(pts_yo + pts_riv),
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
    try:
        r = requests.get("https://api-web.nhle.com/v1/standings/now", headers=HEADERS_HTTP, timeout=8).json()
        for t in r.get("standings", []):
            nombre = t.get("teamName", {}).get("default", "")
            abbrev = t.get("teamAbbrev", {}).get("default", "")
            if nombre and abbrev:
                mapa[nombre] = abbrev
    except Exception:
        pass
    return mapa

@st.cache_data(ttl=1200)
def obtener_sog_boxscore_nhl(game_id):
    """Consulta el boxscore oficial de un partido NHL para obtener los Shots on Goal (SOG) reales."""
    try:
        r = requests.get(f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore", headers=HEADERS_HTTP, timeout=5).json()
        h_sog = int(r.get("homeTeam", {}).get("sog", 0))
        a_sog = int(r.get("awayTeam", {}).get("sog", 0))
        return h_sog, a_sog
    except Exception:
        return 0, 0

@st.cache_data(ttl=900)
def extraer_ultimos_partidos_nhl_con_sog(abbrev, condicion="HOME", n_partidos=5):
    """
    Extrae los últimos N partidos reales como LOCAL ('HOME') o VISITANTE ('AWAY')
    desde api-web.nhle.com incluyendo Goles y Shots on Goal (SOG) reales de boxscore.
    """
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

            h_sog, a_sog = obtener_sog_boxscore_nhl(gid) if gid else (0, 0)
            sog_favor = h_sog if es_local else a_sog
            sog_contra = a_sog if es_local else h_sog

            gf = h_sc if es_local else a_sc
            gc = a_sc if es_local else h_sc
            rival = a_ab if es_local else h_ab
            tipo_cierre = g.get("periodDescriptor", {}).get("periodType", "REG")
            cierre_lbl = "60' Reg." if tipo_cierre == "REG" else f"Prórroga ({tipo_cierre})"

            filas.append({
                "Fecha": fecha,
                "Condición": "🏠 Local" if es_local else "✈️ Visita",
                "Rival": rival,
                "GF": gf,
                "GC": gc,
                "Total Goles": gf + gc,
                "SOG Favor": sog_favor if sog_favor > 0 else np.nan,
                "SOG Contra": sog_contra if sog_contra > 0 else np.nan,
                "Total SOG": (sog_favor + sog_contra) if (sog_favor > 0 and sog_contra > 0) else np.nan,
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
# MOTOR DE TENIS CONECTADO EN VIVO A ESPN + MODELO DE ACES POR SUPERFICIE
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
                if nombre:
                    catalogo[nombre] = {"id": aid, "rank": rk, "points": pts}
    except Exception:
        pass
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
                    ratio_j = jg_tot / (jg_tot + jp_tot)
                    ajuste = (ratio_j - 0.50) * 26.0
                    stats_sup[sup_k]["Hold"] = round(float(np.clip(stats_sup[sup_k]["Hold"] + ajuste, 58.0, 94.0)), 1)
                    stats_sup[sup_k]["Break"] = round(float(np.clip(stats_sup[sup_k]["Break"] + ajuste * 0.8, 15.0, 54.0)), 1)
                    stats_sup[sup_k]["Juegos_Prom"] = round(float((jg_tot + jp_tot) / len(sub_s)), 1)
                stats_sup[sup_k]["G"] = g_s
                stats_sup[sup_k]["P"] = p_s
                stats_sup[sup_k]["WinPct"] = wp_s

    return stats_sup

# --- SELECTOR MAESTRO DE DEPORTE ---
st.sidebar.markdown("### 🎯 Selector Maestro de Deporte")
opciones_deportes = [
    "⚽ Fútbol (15 Ligas + Tarjetas Reales + Bajas)",
    "🎾 Tenis (ATP / WTA Superficie, Aces + Estado Físico)",
    "🏒 Hockey sobre Hielo (NHL - Local/Visita, SOG + Bajas)",
    "🏈 Fútbol Americano (NFL - Local/Visita + Bajas)",
    "🏀 Basketball (NBA - API ESPN + Bajas)",
    "⚾ Béisbol (MLB - API ESPN + Bajas)"
]
deporte_activo = st.sidebar.selectbox("Elige la disciplina a analizar:", opciones_deportes, index=0)
st.sidebar.markdown("---")

# ==============================================================================
# 1. MÓDULO FÚTBOL (15 LIGAS + TARJETAS REALES HY/AY/HR/AR + INTELIGENCIA BAJAS)
# ==============================================================================
if deporte_activo.startswith("⚽"):
    st.sidebar.markdown("### 🏆 1. Competición y Equipos")
    LIGAS_FUT = {
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)": "https://www.football-data.co.uk/mmz4281/2627/E0.csv",
        "🇪🇸 LaLiga (España)": "https://www.football-data.co.uk/mmz4281/2627/SP1.csv",
        "🇮🇹 Serie A (Italia)": "https://www.football-data.co.uk/mmz4281/2627/I1.csv",
        "🇩🇪 Bundesliga (Alemania)": "https://www.football-data.co.uk/mmz4281/2627/D1.csv",
        "🇫🇷 Ligue 1 (Francia)": "https://www.football-data.co.uk/mmz4281/2627/F1.csv",
        "🇳🇱 Eredivisie (Países Bajos)": "https://www.football-data.co.uk/mmz4281/2627/N1.csv",
        "🇵🇹 Primeira Liga (Portugal)": "https://www.football-data.co.uk/mmz4281/2627/P1.csv",
        "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Premiership (Escocia)": "https://www.football-data.co.uk/mmz4281/2627/SC0.csv",
        "🇧🇪 Jupiler Pro League (Bélgica)": "https://www.football-data.co.uk/mmz4281/2627/B1.csv",
        "🇹🇷 Süper Lig (Turquía)": "https://www.football-data.co.uk/mmz4281/2627/T1.csv",
        "🌍 UEFA Nations League (Selecciones UEFA)": "NATIONS_LEAGUE",
        "🇺🇸 MLS (Estados Unidos)": "https://www.football-data.co.uk/new/USA.csv",
        "🇧🇷 Brasileirão Serie A (Brasil)": "https://www.football-data.co.uk/new/BRA.csv",
        "🇦🇷 Liga Profesional (Argentina)": "https://www.football-data.co.uk/new/ARG.csv",
        "🇲🇽 Liga MX (México)": "https://www.football-data.co.uk/new/MEX.csv"
    }
    liga_sel = st.sidebar.selectbox("Selecciona la Liga / Torneo:", list(LIGAS_FUT.keys()))

    @st.cache_data(ttl=1800)
    def cargar_datos_futbol_real(url):
        if url == "NATIONS_LEAGUE":
            return cargar_datos_nations_league()
        try:
            resp = requests.get(url, headers=HEADERS_HTTP, timeout=10)
            df = pd.read_csv(io.StringIO(resp.text))
            if 'Home' in df.columns:
                df = df.rename(columns={'Home': 'HomeTeam', 'Away': 'AwayTeam', 'HG': 'FTHG', 'AG': 'FTAG'})
            df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
            if len(df) < 5 and "/2627/" in url:
                resp_b = requests.get(url.replace("/2627/", "/2526/"), headers=HEADERS_HTTP, timeout=10)
                df = pd.read_csv(io.StringIO(resp_b.text)).dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
            return df
        except Exception:
            return pd.DataFrame()

    df_csv = cargar_datos_futbol_real(LIGAS_FUT[liga_sel])
    if df_csv.empty:
        st.error("No se pudo conectar al servidor de datos en este momento.")
        st.stop()

    equipos_fut = sorted(list(set(df_csv['HomeTeam'].unique()).union(set(df_csv['AwayTeam'].unique()))))
    c1, c2 = st.sidebar.columns(2)
    eq_l = c1.selectbox("🏠 Local", equipos_fut, index=0)
    eq_v = c2.selectbox("✈️ Visita", equipos_fut, index=1 if len(equipos_fut) > 1 else 0)

    usar_amortiguador = st.sidebar.checkbox("🛡️ Amortiguador Bayesiano (< 6 PJ)", value=False)

    # Panel de Inteligencia de Bajas y Factor de Incidencia
    espn_sp, espn_lg = ESPN_LEAGUE_MAP.get(liga_sel, ("soccer", "eng.1"))
    mult_bajas_l, mult_bajas_v, pct_baja_l, pct_baja_v = renderizar_panel_bajas_y_factor(espn_sp, espn_lg, eq_l, eq_v, f"fut_{eq_l}_{eq_v}")

    p_l = df_csv[df_csv['HomeTeam'] == eq_l].tail(5)
    p_v = df_csv[df_csv['AwayTeam'] == eq_v].tail(5)

    media_gf_liga_home = float(df_csv['FTHG'].mean()) if not df_csv.empty else 1.45
    media_gc_liga_home = float(df_csv['FTAG'].mean()) if not df_csv.empty else 1.20
    media_gf_liga_away = media_gc_liga_home
    media_gc_liga_away = media_gf_liga_home
    media_liga = max((media_gf_liga_home + media_gc_liga_home) / 2.0, 1.25)

    gf_l_puro = float(p_l['FTHG'].mean()) if not p_l.empty else 1.40
    gc_l_puro = float(p_l['FTAG'].mean()) if not p_l.empty else 1.20
    gf_v_puro = float(p_v['FTAG'].mean()) if not p_v.empty else 1.15
    gc_v_puro = float(p_v['FTHG'].mean()) if not p_v.empty else 1.40

    pj_l, pj_v = len(p_l), len(p_v)
    if usar_amortiguador:
        peso_l = min(pj_l / 6.0, 1.0)
        peso_v = min(pj_v / 6.0, 1.0)
        gf_l = (peso_l * gf_l_puro) + ((1.0 - peso_l) * media_gf_liga_home)
        gc_l = (peso_l * gc_l_puro) + ((1.0 - peso_l) * media_gc_liga_home)
        gf_v = (peso_v * gf_v_puro) + ((1.0 - peso_v) * media_gf_liga_away)
        gc_v = (peso_v * gc_v_puro) + ((1.0 - peso_v) * media_gc_liga_away)
    else:
        gf_l, gc_l, gf_v, gc_v = gf_l_puro, gc_l_puro, gf_v_puro, gc_v_puro

    # Aplicar Factor de Incidencia por Ausencia de Jugadores Clave
    gf_l = gf_l * mult_bajas_l
    gf_v = gf_v * mult_bajas_v

    tiene_tiros_csv = ('HS' in df_csv.columns and not p_l['HS'].dropna().empty and not p_v['AS'].dropna().empty)
    tiene_tarjetas_csv = ('HY' in df_csv.columns and not p_l['HY'].dropna().empty and not p_v['AY'].dropna().empty)

    sh_l = (float(p_l['HS'].mean()) if tiene_tiros_csv else round(9.5 + gf_l * 2.4, 1)) * (0.5 + 0.5 * mult_bajas_l)
    sh_v = (float(p_v['AS'].mean()) if tiene_tiros_csv else round(8.5 + gf_v * 2.3, 1)) * (0.5 + 0.5 * mult_bajas_v)
    sot_l = (float(p_l['HST'].mean()) if tiene_tiros_csv else round(2.6 + gf_l * 1.25, 1)) * (0.5 + 0.5 * mult_bajas_l)
    sot_v = (float(p_v['AST'].mean()) if tiene_tiros_csv else round(2.2 + gf_v * 1.2, 1)) * (0.5 + 0.5 * mult_bajas_v)
    cor_l = float(p_l['HC'].mean()) if tiene_tiros_csv else round(3.8 + gf_l * 0.68, 1)
    cor_v = float(p_v['AC'].mean()) if tiene_tiros_csv else round(3.4 + gf_v * 0.62, 1)

    # Cálculo real de Tarjetas (Amarillas HY/AY + Rojas HR/AR)
    if tiene_tarjetas_csv:
        hy_l = float(p_l['HY'].fillna(0).mean())
        hr_l = float(p_l['HR'].fillna(0).mean()) if 'HR' in p_l.columns else 0.0
        ay_v = float(p_v['AY'].fillna(0).mean())
        ar_v = float(p_v['AR'].fillna(0).mean()) if 'AR' in p_v.columns else 0.0
        # Tarjetas totales esperadas (Amarillas + Rojas) y Puntos por Tarjeta (Amarilla=1, Roja=2)
        tarj_tot_esp = round(hy_l + hr_l + ay_v + ar_v, 2)
        pts_tarj_esp = round(hy_l + (2.0 * hr_l) + ay_v + (2.0 * ar_v), 2)
    else:
        hy_l, hr_l, ay_v, ar_v = 2.0, 0.1, 2.2, 0.1
        tarj_tot_esp = 4.40
        pts_tarj_esp = 4.60

    with st.expander(f"📋 TABLA DE AUDITORÍA: Partidos reales, Remates, Córners y Tarjetas ({eq_l} vs {eq_v})", expanded=True):
        if tiene_tiros_csv and tiene_tarjetas_csv:
            st.success("✅ Telemetría Completa Opta / Football-Data: Goles (FTHG/FTAG), Remates (HS/AS), Puerta (HST/AST), Córners (HC/AC) y Tarjetas (HY/AY, HR/AR) 100% reales.")
        else:
            st.warning("⚠️ Liga de América / Selecciones: El CSV público contiene Goles Reales (FTHG/FTAG), pero no incluye conteos de Tiros ni Tarjetas.")
        if pct_baja_l > 0 or pct_baja_v > 0:
            st.markdown(f"<div class='injury-alert'>🏥 <b>Factor de Incidencia Aplicado:</b> {eq_l} (-{pct_baja_l}% potencia ofensiva) | {eq_v} (-{pct_baja_v}% potencia ofensiva).</div>", unsafe_allow_html=True)

        cols_l = [c for c in ['Date', 'Tournament', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HS', 'HST', 'HC', 'HY', 'HR'] if c in p_l.columns]
        st.markdown(f"**🏠 Últimos {len(p_l)} partidos de {eq_l} como LOCAL:**")
        st.dataframe(p_l[cols_l], use_container_width=True, hide_index=True)
        cols_v = [c for c in ['Date', 'Tournament', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'AS', 'AST', 'AC', 'AY', 'AR'] if c in p_v.columns]
        st.markdown(f"**✈️ Últimos {len(p_v)} partidos de {eq_v} como VISITANTE:**")
        st.dataframe(p_v[cols_v], use_container_width=True, hide_index=True)

    lam_loc = max((gf_l * gc_v) / media_liga, 0.15)
    lam_vis = max((gf_v * gc_l) / media_liga, 0.12)
    mat = np.zeros((9, 9))
    for i in range(9):
        for j in range(9):
            mat[i, j] = poisson.pmf(i, lam_loc) * poisson.pmf(j, lam_vis)

    prob_1 = float(np.sum(np.tril(mat, -1)))
    prob_x = float(np.sum(np.diag(mat)))
    prob_2 = float(np.sum(np.triu(mat, 1)))
    prob_u25 = float(mat[0,0]+mat[1,0]+mat[0,1]+mat[2,0]+mat[0,2]+mat[1,1])
    prob_o25 = 1.0 - prob_u25
    prob_btts_no = float(np.sum(mat[0, :]) + np.sum(mat[:, 0]) - mat[0, 0])
    prob_btts_si = 1.0 - prob_btts_no

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

    with st.sidebar.expander("📏 Cuotas Remates, Córners y Tarjetas"):
        linea_remates = st.number_input("Línea Remates Totales", 10.5, 40.5, 24.5, 1.0)
        cuota_over_rem = st.number_input("Cuota Over Remates", 1.01, 15.0, 1.85, 0.05)
        linea_puerta = st.number_input("Línea Remates a Puerta", 3.5, 20.5, 8.5, 1.0)
        cuota_over_pue = st.number_input("Cuota Over a Puerta", 1.01, 15.0, 1.85, 0.05)
        linea_corners = st.number_input("Línea Córners Totales", 4.5, 20.5, 8.5, 1.0)
        cuota_over_cor = st.number_input("Cuota Over Córners", 1.01, 15.0, 1.85, 0.05)
        st.markdown("---")
        linea_tarjetas = st.number_input("🟨 Línea Tarjetas Totales", 1.5, 9.5, 4.5, 1.0)
        cuota_over_tarj = st.number_input("Cuota Over Tarjetas", 1.01, 15.0, 1.85, 0.05)
        cuota_under_tarj = st.number_input("Cuota Under Tarjetas", 1.01, 15.0, 1.90, 0.05)

    lam_rem = sh_l + sh_v
    p_ov_rem = float(1.0 - norm.cdf(linea_remates, loc=lam_rem, scale=4.8))
    lam_pue = sot_l + sot_v
    p_ov_pue = float(1.0 - norm.cdf(linea_puerta, loc=lam_pue, scale=2.75))
    lam_cor = cor_l + cor_v
    p_ov_cor = float(1.0 - norm.cdf(linea_corners, loc=lam_cor, scale=3.35))

    # Probabilidad Poisson para Tarjetas Totales (disciplina real HY+HR+AY+AR)
    p_ov_tarj = float(1.0 - sum(poisson.pmf(k, max(tarj_tot_esp, 0.5)) for k in range(int(linea_tarjetas) + 1)))
    p_un_tarj = 1.0 - p_ov_tarj

    st.markdown(f"### 🏟️ {eq_l} vs. {eq_v} <span style='font-size:16px; color:#71717a;'>({liga_sel})</span>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("⚽ Goles Esp. (xG)", f"{lam_loc:.2f} - {lam_vis:.2f}", f"Total: {lam_loc+lam_vis:.2f}")
    k2.metric("🎯 Remates Esp.", f"{lam_rem:.1f} tiros", f"{sh_l:.1f} L + {sh_v:.1f} V")
    k3.metric("🥅 A Puerta Esp.", f"{lam_pue:.1f} arco", f"{sot_l:.1f} L + {sot_v:.1f} V")
    k4.metric("⛳ Córners Esp.", f"{lam_cor:.1f} esq.", f"{cor_l:.1f} L + {cor_v:.1f} V")
    k5.metric("🟨 Tarjetas Esp.", f"{tarj_tot_esp:.1f} tarj.", f"{hy_l+hr_l:.1f} L + {ay_v+ar_v:.1f} V" if tiene_tarjetas_csv else "Sin CSV Tarj.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 1. Goles y 1X2", "⛳ 2. Remates y Córners", "🟨 3. Tarjetas (Amarillas/Rojas)",
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
        filas = [{"Mercado": m, "Prob. Real (%)": f"{p*100:.1f}%", "Cuota Justa": f"{1/p:.2f}", "Cuota Betano": f"{c:.2f}", "Edge (%)": f"{(p*c-1)*100:+.2f}%", "Veredicto": "✅ APOSTAR (+EV)" if (p*c-1) > 0.05 else "❌ Pasar"} for m, p, c in m_g]
        st.dataframe(pd.DataFrame(filas).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with tab2:
        m_e = [
            (f"Más de {linea_remates} Remates Totales (Over)", p_ov_rem, cuota_over_rem),
            (f"Menos de {linea_remates} Remates Totales (Under)", 1.0 - p_ov_rem, 1.85),
            (f"Más de {linea_puerta} Remates a Puerta (Over)", p_ov_pue, cuota_over_pue),
            (f"Menos de {linea_puerta} Remates a Puerta (Under)", 1.0 - p_ov_pue, 1.85),
            (f"Más de {linea_corners} Córners Totales (Over)", p_ov_cor, cuota_over_cor),
            (f"Menos de {linea_corners} Córners Totales (Under)", 1.0 - p_ov_cor, 1.85)
        ]
        filas_e = [{"Mercado Especial": m, "Prob. Real (%)": f"{p*100:.1f}%", "Cuota Justa": f"{1/p:.2f}", "Cuota Betano": f"{c:.2f}", "Edge (%)": f"{(p*c-1)*100:+.2f}%", "Veredicto": "✅ APOSTAR (+EV)" if (p*c-1) > 0.05 else "❌ Pasar"} for m, p, c in m_e]
        st.dataframe(pd.DataFrame(filas_e).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with tab3:
        if not tiene_tarjetas_csv:
            st.warning("⚠️ Esta liga no incluye columnas oficiales de tarjetas (`HY`/`AY`) en el archivo CSV. No se recomienda operar mercados de tarjetas aquí.")
        else:
            st.info(f"📊 **Desglose Disciplinario Real (Últimos 5 PJ):** **{eq_l}** promedia `{hy_l:.1f}` amarillas y `{hr_l:.2f}` rojas en casa | **{eq_v}** promedia `{ay_v:.1f}` amarillas y `{ar_v:.2f}` rojas de visita (Puntos Tarjeta Esp.: `{pts_tarj_esp:.1f}`).")
            m_tarj = [
                (f"🟨 Más de {linea_tarjetas} Tarjetas Totales (Over)", p_ov_tarj, cuota_over_tarj),
                (f"🟨 Menos de {linea_tarjetas} Tarjetas Totales (Under)", p_un_tarj, cuota_under_tarj)
            ]
            filas_t = [{"Mercado de Tarjetas": m, "Prob. Real (%)": f"{p*100:.1f}%", "Cuota Justa": f"{1/p:.2f}", "Cuota Betano": f"{c:.2f}", "Edge (%)": f"{(p*c-1)*100:+.2f}%", "Veredicto": "✅ APOSTAR (+EV)" if (p*c-1) > 0.05 else "❌ Pasar"} for m, p, c in m_tarj]
            st.dataframe(pd.DataFrame(filas_t).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

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
        st.info(f"🔥 **Probabilidad de +0.5 Goles Restantes:** `{p_1_gol_mas*100:.1f}%` | **Cuota Mínima Justa:** `{1/max(p_1_gol_mas, 0.01):.2f}`")


# ==============================================================================
# 2. MÓDULO TENIS (SUPERFICIE, ACES + ESTADO FÍSICO Y NOTICIAS ESPN)
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

    # Calibración de Estado Físico / Fatiga / Molestias en Tenis
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏥 Estado Físico / Fatiga Reciente")
    fat_a = st.sidebar.slider(f"Penalización Físico/Fatiga {jug_a} (%)", 0, 25, 0, 5)
    fat_b = st.sidebar.slider(f"Penalización Físico/Fatiga {jug_b} (%)", 0, 25, 0, 5)

    info_a = catalogo_espn_tenis[jug_a]
    info_b = catalogo_espn_tenis[jug_b]
    rank_a, pts_rank_a = info_a["rank"], info_a["points"]
    rank_b, pts_rank_b = info_b["rank"], info_b["points"]

    pref_t = "atp" if "ATP" in circuito else "wta"
    noticias_t = obtener_noticias_relevantes_espn("tennis", pref_t, jug_a, jug_b)

    with st.spinner(f"Extrayendo historial oficial en vivo de ESPN para {jug_a} y {jug_b}..."):
        df_part_a = obtener_partidos_reales_espn_tenista(circuito, info_a["id"], jug_a)
        df_part_b = obtener_partidos_reales_espn_tenista(circuito, info_b["id"], jug_b)

    sup_a = calcular_perfil_superficie_real(df_part_a, rank_a, circuito, jug_a)
    sup_b = calcular_perfil_superficie_real(df_part_b, rank_b, circuito, jug_b)

    if "Arcilla" in superficie_elegida:
        clave_sup, nombre_sup_corto, estilo_cancha = "Clay", "Arcilla (Clay)", "tenis_clay"
    elif "Césped" in superficie_elegida:
        clave_sup, nombre_sup_corto, estilo_cancha = "Grass", "Césped (Grass)", "tenis_grass"
    else:
        clave_sup, nombre_sup_corto, estilo_cancha = "Hard", "Cancha Dura (Hard)", "tenis_hard"

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

    aces_esp_a = round(sup_a[clave_sup]["Aces"] * ajuste_resto_vs_a * factor_formato_aces * (1.0 - fat_a / 150.0), 1)
    aces_esp_b = round(sup_b[clave_sup]["Aces"] * ajuste_resto_vs_b * factor_formato_aces * (1.0 - fat_b / 150.0), 1)
    aces_totales_esp = round(aces_esp_a + aces_esp_b, 1)

    favorito_nom = jug_a if p_gana_a >= p_gana_b else jug_b
    fav_prob = max(p_gana_a, p_gana_b) * 100.0
    fav_cuota_justa = 1.0 / max(p_gana_a, p_gana_b)
    fav_rk = rank_a if p_gana_a >= p_gana_b else rank_b
    fav_sup_d = sup_a[clave_sup] if p_gana_a >= p_gana_b else sup_b[clave_sup]

    st.markdown(f"""
    <div class="fav-banner">
        👑 <b>FAVORITO(A) EN {nombre_sup_corto.upper()}: {favorito_nom} (Rank Oficial #{fav_rk} | {fav_prob:.1f}% Prob. Real | Cuota Justa: {fav_cuota_justa:.2f})</b><br>
        📌 En <b>{nombre_sup_corto}</b> presenta un <b>{fav_sup_d['WinPct']}% de efectividad</b> con <b>{fav_sup_d['Hold']}% Hold de Saque</b> • Proyección de Aces en {nombre_sup_corto}: <b>{aces_totales_esp} Aces totales ({aces_esp_a} {jug_a} + {aces_esp_b} {jug_b})</b>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(f"📋 TABLA DE AUDITORÍA TENIS: Superficies, Aces, Noticias y Últimos Partidos ({jug_a} vs {jug_b})", expanded=True):
        if noticias_t:
            st.markdown("**🗞️ Noticias Recientes en ESPN Tenis:**")
            for nt in noticias_t:
                st.markdown(nt)
        st.markdown("**🌍 1. Rendimiento y Aces Comparados por Tipo de Cancha (Dura vs. Arcilla vs. Césped):**")
        df_comparativa_canchas = pd.DataFrame([
            {
                "Tenista": jug_a,
                "Rank ESPN": f"#{rank_a} ({int(pts_rank_a)} pts)",
                "🟦 Dura (Hold / Break | %Vict)": f"{sup_a['Hard']['Hold']}% / {sup_a['Hard']['Break']}% ({sup_a['Hard']['WinPct']}%)",
                "🟧 Arcilla (Hold / Break | %Vict)": f"{sup_a['Clay']['Hold']}% / {sup_a['Clay']['Break']}% ({sup_a['Clay']['WinPct']}%)",
                "🟩 Césped (Hold / Break | %Vict)": f"{sup_a['Grass']['Hold']}% / {sup_a['Grass']['Break']}% ({sup_a['Grass']['WinPct']}%)",
                "🔥 Aces Base (Dura / Arcilla / Césped)": f"{sup_a['Hard']['Aces']} / {sup_a['Clay']['Aces']} / {sup_a['Grass']['Aces']}",
                f"🎯 Aces Hoy ({nombre_sup_corto})": f"{aces_esp_a} aces"
            },
            {
                "Tenista": jug_b,
                "Rank ESPN": f"#{rank_b} ({int(pts_rank_b)} pts)",
                "🟦 Dura (Hold / Break | %Vict)": f"{sup_b['Hard']['Hold']}% / {sup_b['Hard']['Break']}% ({sup_b['Hard']['WinPct']}%)",
                "🟧 Arcilla (Hold / Break | %Vict)": f"{sup_b['Clay']['Hold']}% / {sup_b['Clay']['Break']}% ({sup_b['Clay']['WinPct']}%)",
                "🟩 Césped (Hold / Break | %Vict)": f"{sup_b['Grass']['Hold']}% / {sup_b['Grass']['Break']}% ({sup_b['Grass']['WinPct']}%)",
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

    st.markdown(f"### 🎾 {jug_a} (#{rank_a}) vs. {jug_b} (#{rank_b}) <span style='font-size:16px; color:#71717a;'>({circuito} • {nombre_sup_corto})</span>", unsafe_allow_html=True)
    tk1, tk2, tk3, tk4 = st.columns(4)
    tk1.metric("🏆 Prob. Victoria", f"{p_gana_a*100:.1f}% vs {p_gana_b*100:.1f}%", f"Favorito(a): {favorito_nom}")
    tk2.metric(f"🎾 Hold Efectivo ({nombre_sup_corto})", f"{hold_eff_a:.1f}% vs {hold_eff_b:.1f}%", f"1er Set {jug_a}: {p_set_a*100:.1f}%")
    tk3.metric("📏 Total Juegos Esperados", f"{juegos_totales_esp} juegos", f"Sets Esp.: {sets_esp:.2f}")
    tk4.metric(f"🔥 Aces Esperados ({nombre_sup_corto})", f"{aces_totales_esp} aces", f"{aces_esp_a} L + {aces_esp_b} V")

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
        st.dataframe(pd.DataFrame([{"Mercado": m, "Prob. Real (%)": f"{p*100:.1f}%", "Cuota Justa": f"{1/p:.2f}", "Cuota Betano": f"{c:.2f}", "Edge (%)": f"{(p*c-1)*100:+.2f}%", "Veredicto": "✅ APOSTAR (+EV)" if (p*c-1)>0.05 else "❌ Pasar"} for m, p, c in m_t]).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)
    with tab2:
        mostrar_cancha_calor(jug_a, jug_b, hold_eff_a, hold_eff_b, 1.1, 1.0, estilo_cancha)


# ==============================================================================
# 3. MÓDULO HOCKEY SOBRE HIELO (NHL - LOCAL/VISITA + SHOTS ON GOAL + BAJAS)
# ==============================================================================
elif deporte_activo.startswith("🏒"):
    st.sidebar.markdown("### 🏒 1. Equipos NHL")
    mapa_nhl = obtener_catalogo_equipos_nhl()
    if not mapa_nhl:
        st.error("No se pudo conectar con la API Oficial de la NHL (api-web.nhle.com).")
        st.stop()

    lista_nhl = sorted(list(mapa_nhl.keys()))
    col_nhl1, col_nhl2 = st.sidebar.columns(2)
    nh_l = col_nhl1.selectbox("🏠 Local (Home)", lista_nhl, index=0)
    nh_v = col_nhl2.selectbox("✈️ Visita (Road)", lista_nhl, index=1 if len(lista_nhl) > 1 else 0)

    usar_bayes_nhl = st.sidebar.checkbox("🛡️ Amortiguador Bayesiano NHL (< 6 PJ)", value=False)
    mult_bajas_nl, mult_bajas_nv, pct_baja_nl, pct_baja_nv = renderizar_panel_bajas_y_factor("hockey", "nhl", nh_l, nh_v, f"nhl_{nh_l}_{nh_v}")

    with st.spinner(f"Extrayendo boxscores reales de goles y Shots on Goal (SOG) de {nh_l} y {nh_v}..."):
        df_nhl_l = extraer_ultimos_partidos_nhl_con_sog(mapa_nhl[nh_l], condicion="HOME", n_partidos=5)
        df_nhl_v = extraer_ultimos_partidos_nhl_con_sog(mapa_nhl[nh_v], condicion="AWAY", n_partidos=5)

    media_nhl_home, media_nhl_away, media_nhl_global = 3.18, 2.92, 3.05

    gf_l_puro = float(df_nhl_l["GF"].mean()) if not df_nhl_l.empty else media_nhl_home
    gc_l_puro = float(df_nhl_l["GC"].mean()) if not df_nhl_l.empty else media_nhl_away
    gf_v_puro = float(df_nhl_v["GF"].mean()) if not df_nhl_v.empty else media_nhl_away
    gc_v_puro = float(df_nhl_v["GC"].mean()) if not df_nhl_v.empty else media_nhl_home

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

    # Aplicar Factor de Incidencia por Ausencia de Jugadores Clave
    gf_nhl_l = gf_nhl_l * mult_bajas_nl
    gf_nhl_v = gf_nhl_v * mult_bajas_nv

    # Extraer promedios reales de Shots on Goal (SOG) desde los boxscores
    sog_f_l = float(df_nhl_l["SOG Favor"].dropna().mean()) if ("SOG Favor" in df_nhl_l and not df_nhl_l["SOG Favor"].dropna().empty) else 29.5
    sog_c_l = float(df_nhl_l["SOG Contra"].dropna().mean()) if ("SOG Contra" in df_nhl_l and not df_nhl_l["SOG Contra"].dropna().empty) else 28.5
    sog_f_v = float(df_nhl_v["SOG Favor"].dropna().mean()) if ("SOG Favor" in df_nhl_v and not df_nhl_v["SOG Favor"].dropna().empty) else 28.0
    sog_c_v = float(df_nhl_v["SOG Contra"].dropna().mean()) if ("SOG Contra" in df_nhl_v and not df_nhl_v["SOG Contra"].dropna().empty) else 30.0

    # Proyección cruzada de Shots on Goal (SOG) calibrada por ritmo y bajas
    sog_esp_loc = round(((sog_f_l + sog_c_v) / 2.0) * (0.6 + 0.4 * mult_bajas_nl), 1)
    sog_esp_vis = round(((sog_f_v + sog_c_l) / 2.0) * (0.6 + 0.4 * mult_bajas_nv), 1)
    sog_totales_esp = round(sog_esp_loc + sog_esp_vis, 1)

    with st.expander(f"📋 TABLA DE AUDITORÍA NHL: Goles y Shots on Goal (SOG) Reales ({nh_l} Local vs {nh_v} Visita)", expanded=True):
        st.success("✅ Datos extraídos en vivo desde los Boxscores Oficiales de `api-web.nhle.com` filtrados por Localía (`HOME`) y Gira (`AWAY`).")
        if pct_baja_nl > 0 or pct_baja_nv > 0:
            st.markdown(f"<div class='injury-alert'>🏥 <b>Factor de Incidencia NHL Aplicado:</b> {nh_l} (-{pct_baja_nl}%) | {nh_v} (-{pct_baja_nv}%).</div>", unsafe_allow_html=True)

        st.markdown(f"**🏠 Últimos {len(df_nhl_l)} partidos de {nh_l} en CASA (Prom. SOG: {sog_f_l:.1f} a favor / {sog_c_l:.1f} en contra):**")
        if not df_nhl_l.empty:
            st.dataframe(df_nhl_l, use_container_width=True, hide_index=True)

        st.markdown(f"**✈️ Últimos {len(df_nhl_v)} partidos de {nh_v} de VISITA (Prom. SOG: {sog_f_v:.1f} a favor / {sog_c_v:.1f} en contra):**")
        if not df_nhl_v.empty:
            st.dataframe(df_nhl_v, use_container_width=True, hide_index=True)

    lam_nhl_l = max((gf_nhl_l * gc_nhl_v) / media_nhl_global, 0.50)
    lam_nhl_v = max((gf_nhl_v * gc_nhl_l) / media_nhl_global, 0.50)
    tot_nhl = lam_nhl_l + lam_nhl_v

    mat_n = np.zeros((13, 13))
    for i in range(13):
        for j in range(13):
            mat_n[i, j] = poisson.pmf(i, lam_nhl_l) * poisson.pmf(j, lam_nhl_v)
    p_reg_l = float(np.sum(np.tril(mat_n, -1)))
    p_emp = float(np.sum(np.diag(mat_n)))
    p_ml_l = p_reg_l + (p_emp * (lam_nhl_l / tot_nhl))
    p_ml_v = 1.0 - p_ml_l

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas Betano NHL (Goles & SOG)")
    c_nh_l = st.sidebar.number_input(f"Moneyline {nh_l} (Inc. OT)", 1.01, 20.0, round(1/max(p_ml_l*1.05, 0.05), 2), 0.05)
    c_nh_v = st.sidebar.number_input(f"Moneyline {nh_v} (Inc. OT)", 1.01, 20.0, round(1/max(p_ml_v*1.05, 0.05), 2), 0.05)
    linea_nhl = st.sidebar.selectbox("Línea Goles Totales NHL", [5.5, 6.0, 6.5], index=2)
    c_ov_nhl = st.sidebar.number_input(f"Cuota Over {linea_nhl} Goles", 1.01, 15.0, 1.88, 0.05)
    c_un_nhl = st.sidebar.number_input(f"Cuota Under {linea_nhl} Goles", 1.01, 15.0, 1.92, 0.05)

    with st.sidebar.expander("🎯 Líneas y Cuotas Shots on Goal (SOG)", expanded=True):
        linea_sog_tot = st.number_input("Línea SOG Totales Partido", 40.5, 80.5, float(int(sog_totales_esp) + 0.5), 1.0)
        c_ov_sog = st.number_input(f"Cuota Over {linea_sog_tot} SOG", 1.01, 15.0, 1.87, 0.05)
        c_un_sog = st.number_input(f"Cuota Under {linea_sog_tot} SOG", 1.01, 15.0, 1.87, 0.05)
        linea_sog_loc = st.number_input(f"Línea SOG {nh_l} (Local)", 18.5, 45.5, float(int(sog_esp_loc) + 0.5), 1.0)
        c_ov_sog_l = st.number_input(f"Cuota Over {linea_sog_loc} SOG {nh_l}", 1.01, 15.0, 1.85, 0.05)

    p_ov_nhl = 1.0 - sum(poisson.pmf(k, tot_nhl) for k in range(int(linea_nhl) + 1))
    p_ov_sog_tot = float(1.0 - norm.cdf(linea_sog_tot, loc=sog_totales_esp, scale=6.8))
    p_ov_sog_l = float(1.0 - norm.cdf(linea_sog_loc, loc=sog_esp_loc, scale=4.8))

    st.markdown(f"### 🧊 {nh_l} vs. {nh_v} <span style='font-size:16px; color:#71717a;'>(NHL • Goles & Shots on Goal)</span>", unsafe_allow_html=True)
    nk1, nk2, nk3, nk4 = st.columns(4)
    nk1.metric("🏒 Goles Esp. (60m)", f"{lam_nhl_l:.2f} - {lam_nhl_v:.2f}", f"Total: {tot_nhl:.2f} goles")
    nk2.metric("🏆 Prob. Moneyline", f"{p_ml_l*100:.1f}% vs {p_ml_v*100:.1f}%", f"Empate 60': {p_emp*100:.1f}%")
    nk3.metric("🎯 Shots on Goal Esp.", f"{sog_totales_esp} SOG", f"{sog_esp_loc} L + {sog_esp_vis} V")
    nk4.metric("📈 Prob. Over Goles", f"{p_ov_nhl*100:.1f}% Over {linea_nhl}", f"{(1-p_ov_nhl)*100:.1f}% Under {linea_nhl}")

    ntab1, ntab2, ntab3 = st.tabs(["🏆 1. Mercados Goles & ML", "🎯 2. Shots on Goal (SOG)", "🔴 3. Radar En Vivo"])
    with ntab1:
        m_nhl = [
            (f"Moneyline: Gana {nh_l} (Inc. OT)", p_ml_l, c_nh_l),
            (f"Moneyline: Gana {nh_v} (Inc. OT)", p_ml_v, c_nh_v),
            (f"Total: Más de {linea_nhl} Goles (Over)", p_ov_nhl, c_ov_nhl),
            (f"Total: Menos de {linea_nhl} Goles (Under)", 1.0 - p_ov_nhl, c_un_nhl)
        ]
        st.dataframe(pd.DataFrame([{"Mercado NHL": m, "Prob. Real (%)": f"{p*100:.1f}%", "Cuota Justa": f"{1/p:.2f}", "Cuota Betano": f"{c:.2f}", "Edge (%)": f"{(p*c-1)*100:+.2f}%", "Veredicto": "✅ APOSTAR (+EV)" if (p*c-1)>0.05 else "❌ Pasar"} for m, p, c in m_nhl]).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with ntab2:
        m_sog = [
            (f"🎯 Más de {linea_sog_tot} Shots on Goal Totales (Over)", p_ov_sog_tot, c_ov_sog),
            (f"🎯 Menos de {linea_sog_tot} Shots on Goal Totales (Under)", 1.0 - p_ov_sog_tot, c_un_sog),
            (f"🎯 {nh_l}: Más de {linea_sog_loc} Shots on Goal (Over)", p_ov_sog_l, c_ov_sog_l),
            (f"🎯 {nh_l}: Menos de {linea_sog_loc} Shots on Goal (Under)", 1.0 - p_ov_sog_l, 1.85)
        ]
        st.dataframe(pd.DataFrame([{"Mercado Shots on Goal": m, "Prob. Real (%)": f"{p*100:.1f}%", "Cuota Justa": f"{1/p:.2f}", "Cuota Betano": f"{c:.2f}", "Edge (%)": f"{(p*c-1)*100:+.2f}%", "Veredicto": "✅ APOSTAR (+EV)" if (p*c-1)>0.05 else "❌ Pasar"} for m, p, c in m_sog]).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

    with ntab3:
        mostrar_cancha_calor(nh_l, nh_v, p_ml_l*100, p_ml_v*100, 1.1, 1.0, "nhl")


# ==============================================================================
# 4. MÓDULO FÚTBOL AMERICANO (NFL - LOCAL/VISITA + BAYESIANO + BAJAS)
# ==============================================================================
elif deporte_activo.startswith("🏈"):
    st.sidebar.markdown("### 🏈 1. Equipos NFL")
    mapa_nfl = obtener_catalogo_equipos_espn("football", "nfl")
    if not mapa_nfl:
        st.error("No se pudo conectar con la API Oficial de ESPN para NFL.")
        st.stop()

    lista_nfl = sorted(list(mapa_nfl.keys()))
    c_nf1, c_nf2 = st.sidebar.columns(2)
    nf_l = c_nf1.selectbox("🏠 Local (Home)", lista_nfl, index=0)
    nf_v = c_nf2.selectbox("✈️ Visita (Road)", lista_nfl, index=1 if len(lista_nfl) > 1 else 0)

    usar_bayes_nfl = st.sidebar.checkbox("🛡️ Amortiguador Bayesiano NFL (< 6 PJ)", value=True)
    mult_bajas_nfl_l, mult_bajas_nfl_v, pct_b_nfl_l, pct_b_nfl_v = renderizar_panel_bajas_y_factor("football", "nfl", nf_l, nf_v, f"nfl_{nf_l}_{nf_v}")

    df_nfl_l = extraer_ultimos_partidos_reales_espn("football", "nfl", mapa_nfl[nf_l], nf_l, n_partidos=5, condicion_filtro="HOME")
    df_nfl_v = extraer_ultimos_partidos_reales_espn("football", "nfl", mapa_nfl[nf_v], nf_v, n_partidos=5, condicion_filtro="AWAY")

    media_nfl_home, media_nfl_away = 23.4, 21.6

    pf_l_puro = float(df_nfl_l["Anotados"].mean()) if not df_nfl_l.empty else media_nfl_home
    pa_l_puro = float(df_nfl_l["Recibidos"].mean()) if not df_nfl_l.empty else media_nfl_away
    pf_v_puro = float(df_nfl_v["Anotados"].mean()) if not df_nfl_v.empty else media_nfl_away
    pa_v_puro = float(df_nfl_v["Recibidos"].mean()) if not df_nfl_v.empty else media_nfl_home

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

    pf_l = pf_l * mult_bajas_nfl_l
    pf_v = pf_v * mult_bajas_nfl_v

    with st.expander(f"📋 TABLA DE AUDITORÍA NFL: Últimos partidos reales de {nf_l} como LOCAL y {nf_v} como VISITANTE", expanded=True):
        st.success("✅ Datos extraídos en vivo desde ESPN Schedule filtrando estrictamente por Localía (`HOME`) y Gira (`AWAY`).")
        if pct_b_nfl_l > 0 or pct_b_nfl_v > 0:
            st.markdown(f"<div class='injury-alert'>🏥 <b>Factor de Incidencia NFL Aplicado:</b> {nf_l} (-{pct_b_nfl_l}%) | {nf_v} (-{pct_b_nfl_v}%).</div>", unsafe_allow_html=True)

        st.markdown(f"**🏠 Últimos {len(df_nfl_l)} partidos de {nf_l} jugando en CASA (Local):**")
        if not df_nfl_l.empty:
            st.dataframe(df_nfl_l, use_container_width=True, hide_index=True)
        st.markdown(f"**✈️ Últimos {len(df_nfl_v)} partidos de {nf_v} jugando de GIRA (Visita):**")
        if not df_nfl_v.empty:
            st.dataframe(df_nfl_v, use_container_width=True, hide_index=True)

    proy_l = (pf_l + pa_v) / 2.0
    proy_v = (pf_v + pa_l) / 2.0
    tot_nfl = proy_l + proy_v
    p_ml_l = float(1.0 - norm.cdf(0.0, loc=proy_l - proy_v, scale=13.2))
    p_ml_v = 1.0 - p_ml_l

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas Betano NFL")
    c_nfl_l = st.sidebar.number_input(f"Moneyline Gana {nf_l}", 1.01, 25.0, round(1/max(p_ml_l*1.05, 0.05), 2), 0.05)
    c_nfl_v = st.sidebar.number_input(f"Moneyline Gana {nf_v}", 1.01, 25.0, round(1/max(p_ml_v*1.05, 0.05), 2), 0.05)
    linea_nfl = st.sidebar.number_input("Línea Puntos Totales NFL", 30.5, 68.5, round(tot_nfl*2)/2, 0.5)
    c_ov_nfl = st.sidebar.number_input(f"Cuota Más de {linea_nfl} (Over)", 1.01, 15.0, 1.90, 0.05)
    c_un_nfl = st.sidebar.number_input(f"Cuota Menos de {linea_nfl} (Under)", 1.01, 15.0, 1.90, 0.05)

    p_ov_nfl = float(1.0 - norm.cdf(linea_nfl, loc=tot_nfl, scale=14.2))

    st.markdown(f"### 🏈 {nf_l} vs. {nf_v} <span style='font-size:16px; color:#71717a;'>(NFL • Auditoría Local vs. Visita)</span>", unsafe_allow_html=True)
    fk1, fk2, fk3 = st.columns(3)
    fk1.metric("🎯 Marcador Proyectado", f"{proy_l:.1f} - {proy_v:.1f}", f"Total Esperado: {tot_nfl:.1f} pts")
    fk2.metric("🏆 Prob. Moneyline", f"{p_ml_l*100:.1f}% vs {p_ml_v*100:.1f}%", f"Spread Esp.: {proy_l - proy_v:+.1f}")
    fk3.metric("📈 Prob. Over / Under", f"{p_ov_nfl*100:.1f}% Over {linea_nfl}", f"{(1-p_ov_nfl)*100:.1f}% Under {linea_nfl}")

    ftab1, ftab2 = st.tabs(["🎯 1. Mercados NFL (Betano)", "🔴 2. Radar En Vivo (In-Play)"])
    with ftab1:
        m_nfl = [
            (f"Moneyline: Gana {nf_l}", p_ml_l, c_nfl_l),
            (f"Moneyline: Gana {nf_v}", p_ml_v, c_nfl_v),
            (f"Total: Más de {linea_nfl} Puntos (Over)", p_ov_nfl, c_ov_nfl),
            (f"Total: Menos de {linea_nfl} Puntos (Under)", 1.0 - p_ov_nfl, c_un_nfl)
        ]
        st.dataframe(pd.DataFrame([{"Mercado NFL": m, "Prob. Real (%)": f"{p*100:.1f}%", "Cuota Justa": f"{1/p:.2f}", "Cuota Betano": f"{c:.2f}", "Edge (%)": f"{(p*c-1)*100:+.2f}%", "Veredicto": "✅ APOSTAR (+EV)" if (p*c-1)>0.05 else "❌ Pasar"} for m, p, c in m_nfl]).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)
    with ftab2:
        mostrar_cancha_calor(nf_l, nf_v, p_ml_l*100, p_ml_v*100, 1.1, 1.0, "nfl")


# ==============================================================================
# 5. MÓDULOS NBA (🏀) Y MLB (⚾) CON INTELIGENCIA DE BAJAS Y NOTICIAS
# ==============================================================================
else:
    if deporte_activo.startswith("🏀"):
        sport_p, league_c, nom_dep, sigma_m, cancha_k = "basketball", "nba", "NBA Basketball", 11.8, "nba"
    else:
        sport_p, league_c, nom_dep, sigma_m, cancha_k = "baseball", "mlb", "MLB Béisbol", 3.2, "mlb"

    st.sidebar.markdown(f"### 🏆 1. Equipos {nom_dep}")
    mapa_equipos_espn = obtener_catalogo_equipos_espn(sport_p, league_c)
    if not mapa_equipos_espn:
        st.error(f"No se pudo conectar con el servidor en vivo de ESPN para {nom_dep}.")
        st.stop()

    lista_eq = sorted(list(mapa_equipos_espn.keys()))
    u_l = st.sidebar.selectbox("🏠 Local (Home)", lista_eq, index=0)
    u_v = st.sidebar.selectbox("✈️ Visita (Road)", lista_eq, index=1 if len(lista_eq) > 1 else 0)

    mult_bajas_ul, mult_bajas_uv, pct_b_ul, pct_b_uv = renderizar_panel_bajas_y_factor(sport_p, league_c, u_l, u_v, f"{league_c}_{u_l}_{u_v}")

    df_real_l = extraer_ultimos_partidos_reales_espn(sport_p, league_c, mapa_equipos_espn[u_l], u_l, n_partidos=8, condicion_filtro="ALL")
    df_real_v = extraer_ultimos_partidos_reales_espn(sport_p, league_c, mapa_equipos_espn[u_v], u_v, n_partidos=8, condicion_filtro="ALL")

    with st.expander(f"📋 TABLA DE AUDITORÍA {nom_dep}: Últimos partidos oficiales extraídos en vivo de ESPN ({u_l} vs {u_v})", expanded=True):
        st.success(f"✅ Datos de {nom_dep} extraídos 100% en tiempo real desde la API Oficial de ESPN (`site.api.espn.com`).")
        if pct_b_ul > 0 or pct_b_uv > 0:
            st.markdown(f"<div class='injury-alert'>🏥 <b>Factor de Incidencia {nom_dep} Aplicado:</b> {u_l} (-{pct_b_ul}%) | {u_v} (-{pct_b_uv}%).</div>", unsafe_allow_html=True)

        st.markdown(f"**🏠 Últimos {len(df_real_l)} partidos finalizados de {u_l}:**")
        if not df_real_l.empty:
            st.dataframe(df_real_l, use_container_width=True, hide_index=True)
        st.markdown(f"**✈️ Últimos {len(df_real_v)} partidos finalizados de {u_v}:**")
        if not df_real_v.empty:
            st.dataframe(df_real_v, use_container_width=True, hide_index=True)

    def_pts = 112.0 if sport_p == "basketball" else 4.5
    pf_l = (float(df_real_l["Anotados"].mean()) if not df_real_l.empty else def_pts) * mult_bajas_ul
    pa_l = float(df_real_l["Recibidos"].mean()) if not df_real_l.empty else def_pts
    pf_v = (float(df_real_v["Anotados"].mean()) if not df_real_v.empty else def_pts) * mult_bajas_uv
    pa_v = float(df_real_v["Recibidos"].mean()) if not df_real_v.empty else def_pts

    proy_l = (pf_l + pa_v) / 2.0
    proy_v = (pf_v + pa_l) / 2.0
    tot_esp = proy_l + proy_v
    p_ml_l = float(1.0 - norm.cdf(0.0, loc=proy_l - proy_v, scale=sigma_m))
    p_ml_v = 1.0 - p_ml_l

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 🟠 2. Cuotas Betano {nom_dep}")
    c_ul = st.sidebar.number_input(f"Gana {u_l}", 1.01, 25.0, round(1/max(p_ml_l*1.05, 0.05), 2), 0.05)
    c_uv = st.sidebar.number_input(f"Gana {u_v}", 1.01, 25.0, round(1/max(p_ml_v*1.05, 0.05), 2), 0.05)
    linea_u = st.sidebar.number_input("Línea Total Puntos/Carreras", 3.5, 275.5, round(tot_esp*2)/2, 0.5)
    c_ov_u = st.sidebar.number_input(f"Cuota Over {linea_u}", 1.01, 15.0, 1.90, 0.05)
    c_un_u = st.sidebar.number_input(f"Cuota Under {linea_u}", 1.01, 15.0, 1.90, 0.05)

    p_ov_u = float(1.0 - norm.cdf(linea_u, loc=tot_esp, scale=sigma_m * 1.15))

    st.markdown(f"### 🏟️ {u_l} vs. {u_v} <span style='font-size:16px; color:#71717a;'>({nom_dep})</span>", unsafe_allow_html=True)
    uk1, uk2, uk3 = st.columns(3)
    uk1.metric("🎯 Marcador Proyectado", f"{proy_l:.1f} - {proy_v:.1f}", f"Total Esperado: {tot_esp:.1f}")
    uk2.metric("🏆 Prob. Moneyline", f"{p_ml_l*100:.1f}% vs {p_ml_v*100:.1f}%")
    uk3.metric("📈 Prob. Over Línea", f"{p_ov_u*100:.1f}%", f"Línea: {linea_u}")

    utab1, utab2 = st.tabs(["🎯 1. Mercados Betano", "🔴 2. Radar En Vivo (In-Play)"])
    with utab1:
        m_u = [
            (f"Moneyline: Gana {u_l}", p_ml_l, c_ul),
            (f"Moneyline: Gana {u_v}", p_ml_v, c_uv),
            (f"Total: Más de {linea_u} (Over)", p_ov_u, c_ov_u),
            (f"Total: Menos de {linea_u} (Under)", 1.0 - p_ov_u, c_un_u)
        ]
        st.dataframe(pd.DataFrame([{"Mercado": m, "Prob. Real (%)": f"{p*100:.1f}%", "Cuota Justa": f"{1/p:.2f}", "Cuota Betano": f"{c:.2f}", "Edge (%)": f"{(p*c-1)*100:+.2f}%", "Veredicto": "✅ APOSTAR (+EV)" if (p*c-1)>0.05 else "❌ Pasar"} for m, p, c in m_u]).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)
    with utab2:
        mostrar_cancha_calor(u_l, u_v, p_ml_l*100, p_ml_v*100, 1.1, 1.0, cancha_k)
