import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from scipy.stats import poisson, norm
import requests
import unicodedata
import io
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Pro Bet Analyzer 11.5 | Surface & Live Audit Suite",
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
</style>
<div class="main-banner">
<h1>🏆 PRO BET ANALYZER 11.5 <span style="color:#ff8c00;">| TENNIS SURFACE & LIVE AUDIT</span></h1>
<p>Tenis con Estadísticas Reales por Superficie (Dura, Arcilla, Césped) y Partidos de Boxscore • Nations League • Radar En Vivo</p>
</div>
""", unsafe_allow_html=True)

HEADERS_HTTP = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def limpiar_texto_nombre(txt):
    if not isinstance(txt, str):
        return ""
    sin_tildes = ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-zA-Z\s]', '', sin_tildes).lower().strip()

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
# FUNCIONES GLOBALES DE CONEXIÓN A APIS Y REPOSITORIOS OFICIALES
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
def extraer_ultimos_partidos_reales_espn(sport, league, team_id, nombre_equipo, n_partidos=8):
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
                        sc_yo_raw = yo.get("score", 0)
                        sc_riv_raw = rival.get("score", 0)
                        pts_yo = float(sc_yo_raw.get("value", sc_yo_raw.get("displayValue", 0))) if isinstance(sc_yo_raw, dict) else float(sc_yo_raw or 0)
                        pts_riv = float(sc_riv_raw.get("value", sc_riv_raw.get("displayValue", 0))) if isinstance(sc_riv_raw, dict) else float(sc_riv_raw or 0)
                        es_local = (yo.get("homeAway", "") == "home")
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

@st.cache_data(ttl=900)
def extraer_ultimos_partidos_reales_nhl(abbrev, n_partidos=8):
    if not abbrev:
        return pd.DataFrame()
    filas = []
    try:
        r = requests.get(f"https://api-web.nhle.com/v1/club-schedule-season/{abbrev}/now", headers=HEADERS_HTTP, timeout=8).json()
        for g in r.get("games", []):
            if g.get("gameState") in ["OFF", "FINAL"]:
                fecha = g.get("gameDate", "")
                h_tm = g.get("homeTeam", {})
                a_tm = g.get("awayTeam", {})
                h_ab = h_tm.get("abbrev", "")
                a_ab = a_tm.get("abbrev", "")
                h_sc = int(h_tm.get("score", 0))
                a_sc = int(a_tm.get("score", 0))
                es_local = (h_ab == abbrev)
                gf = h_sc if es_local else a_sc
                gc = a_sc if es_local else h_sc
                rival = a_ab if es_local else h_ab
                filas.append({
                    "Fecha": fecha,
                    "Condición": "🏠 Casa" if es_local else "✈️ Ruta",
                    "Rival": rival,
                    "Goles a Favor": gf,
                    "Goles en Contra": gc,
                    "Total Goles": gf + gc,
                    "Resultado": "✅ Victoria" if gf > gc else "❌ Derrota"
                })
    except Exception:
        pass
    df_out = pd.DataFrame(filas)
    if not df_out.empty:
        df_out = df_out.sort_values("Fecha").tail(n_partidos)
    return df_out

# ==============================================================================
# MOTOR DE TENIS MULTI-SUPERFICIE (CDN JSDELIVR + GITHUB RAW + RANKINGS ESPN)
# ==============================================================================
def calcular_hold_desde_spw(p_srv):
    p = float(np.clip(p_srv, 0.45, 0.82))
    q = 1.0 - p
    p_deuce = (20.0 * (p ** 3) * (q ** 3)) * ((p ** 2) / ((p ** 2) + (q ** 2)))
    return round(float(((p ** 4) + (4.0 * (p ** 4) * q) + (10.0 * (p ** 4) * (q ** 2)) + p_deuce) * 100.0), 1)

@st.cache_data(ttl=3600)
def cargar_boxscores_reales_tenis(circuito):
    """Descarga boxscores reales desde CDN jsDelivr (sin bloqueo de IP en Streamlit Cloud) y GitHub."""
    pref = "atp" if "ATP" in circuito else "wta"
    urls_candidatas = [
        f"https://cdn.jsdelivr.net/gh/JeffSackmann/tennis_{pref}@master/{pref}_matches_2024.csv",
        f"https://cdn.jsdelivr.net/gh/JeffSackmann/tennis_{pref}@master/{pref}_matches_2023.csv",
        f"https://raw.githubusercontent.com/JeffSackmann/tennis_{pref}/master/{pref}_matches_2024.csv",
        f"https://raw.githubusercontent.com/JeffSackmann/tennis_{pref}/master/{pref}_matches_2023.csv"
    ]
    cols_validas = {
        'tourney_date', 'tourney_name', 'surface', 'winner_name', 'loser_name', 'score',
        'w_ace', 'w_svpt', 'w_1stWon', 'w_2ndWon', 'w_SvGms', 'w_bpSaved', 'w_bpFaced',
        'l_ace', 'l_svpt', 'l_1stWon', 'l_2ndWon', 'l_SvGms', 'l_bpSaved', 'l_bpFaced',
        'winner_rank', 'loser_rank'
    }
    frames = []
    anos_cargados = set()
    for u in urls_candidatas:
        ano = "2024" if "2024" in u else "2023"
        if ano in anos_cargados:
            continue
        try:
            resp = requests.get(u, headers=HEADERS_HTTP, timeout=12)
            if resp.status_code == 200 and len(resp.text) > 5000:
                df_u = pd.read_csv(io.StringIO(resp.text), usecols=lambda c: c in cols_validas, low_memory=False)
                df_u = df_u.dropna(subset=['winner_name', 'loser_name'])
                frames.append(df_u)
                anos_cargados.add(ano)
        except Exception:
            pass

    if frames:
        df_all = pd.concat(frames, ignore_index=True)
        df_all['w_clean'] = df_all['winner_name'].apply(limpiar_texto_nombre)
        df_all['l_clean'] = df_all['loser_name'].apply(limpiar_texto_nombre)
        conteo = pd.concat([df_all['winner_name'], df_all['loser_name']]).value_counts()
        jugadores_activos = sorted(conteo[conteo >= 5].index.tolist())
        return df_all, jugadores_activos

    return pd.DataFrame(), []

def analizar_tenista_por_superficie(df_all, tenista, circuito, n_ultimos=10):
    """Extrae los últimos partidos reales del tenista y calcula sus estadísticas exactas en Dura, Arcilla y Césped."""
    es_atp = "ATP" in circuito
    base_hold = 83.5 if es_atp else 73.5
    base_brk = 23.5 if es_atp else 34.5
    base_aces = 6.5 if es_atp else 3.5

    stats_sup = {
        "Hard": {"Hold": base_hold, "Break": base_brk, "PJ": 0, "G": 0, "P": 0, "WinPct": 50.0},
        "Clay": {"Hold": round(base_hold - 3.0, 1), "Break": round(base_brk + 2.5, 1), "PJ": 0, "G": 0, "P": 0, "WinPct": 50.0},
        "Grass": {"Hold": round(base_hold + 2.5, 1), "Break": round(base_brk - 2.8, 1), "PJ": 0, "G": 0, "P": 0, "WinPct": 50.0}
    }

    if df_all.empty:
        return pd.DataFrame(), stats_sup, base_aces, 99

    clave_jug = limpiar_texto_nombre(tenista)
    sub = df_all[(df_all['w_clean'] == clave_jug) | (df_all['l_clean'] == clave_jug)].copy()
    if sub.empty:
        return pd.DataFrame(), stats_sup, base_aces, 99

    sub = sub.sort_values('tourney_date')

    # Calcular último ranking registrado en boxscore
    ult_fila = sub.iloc[-1]
    rk_jug = ult_fila.get('winner_rank') if ult_fila['w_clean'] == clave_jug else ult_fila.get('loser_rank')
    rank_final = int(rk_jug) if (pd.notna(rk_jug) and float(rk_jug) > 0) else 50

    # Calcular rendimiento desglosado por cada tipo de superficie (Hard, Clay, Grass)
    for sup_key in ["Hard", "Clay", "Grass"]:
        sub_s = sub[sub['surface'].astype(str).str.contains(sup_key, case=False, na=False)]
        if len(sub_s) > 0:
            spw_s, svpt_s, brk_s, rgms_s, ganados_s = 0.0, 0.0, 0.0, 0.0, 0
            for _, r in sub_s.iterrows():
                gano = (r['w_clean'] == clave_jug)
                if gano:
                    ganados_s += 1
                svpt = r.get('w_svpt') if gano else r.get('l_svpt')
                w1 = r.get('w_1stWon', 0) if gano else r.get('l_1stWon', 0)
                w2 = r.get('w_2ndWon', 0) if gano else r.get('l_2ndWon', 0)
                rgms = r.get('l_SvGms') if gano else r.get('w_SvGms')
                bp_f = r.get('l_bpFaced', 0) if gano else r.get('w_bpFaced', 0)
                bp_s = r.get('l_bpSaved', 0) if gano else r.get('w_bpSaved', 0)

                if pd.notna(svpt) and float(svpt) > 0:
                    spw_s += float((w1 or 0) + (w2 or 0))
                    svpt_s += float(svpt)
                if pd.notna(rgms) and float(rgms) > 0:
                    brk_s += max(float((bp_f or 0) - (bp_s or 0)), 0.0)
                    rgms_s += float(rgms)

            pj_s = len(sub_s)
            win_pct_s = round((ganados_s / pj_s) * 100.0, 1)
            hold_s = calcular_hold_desde_spw(spw_s / svpt_s) if svpt_s > 20 else stats_sup[sup_key]["Hold"]
            brk_calc = round(float(np.clip((brk_s / rgms_s) * 100.0, 10.0, 58.0)), 1) if rgms_s > 5 else stats_sup[sup_key]["Break"]
            stats_sup[sup_key] = {
                "Hold": hold_s, "Break": brk_calc,
                "PJ": pj_s, "G": ganados_s, "P": pj_s - ganados_s, "WinPct": win_pct_s
            }

    # Extraer tabla de los últimos N partidos reales
    ultimos_df = sub.tail(n_ultimos)
    filas = []
    aces_lista = []
    for _, r in ultimos_df.iterrows():
        gano = (r['w_clean'] == clave_jug)
        rival = r['loser_name'] if gano else r['winner_name']
        aces = r.get('w_ace') if gano else r.get('l_ace')
        svpt = r.get('w_svpt') if gano else r.get('l_svpt')
        w1 = r.get('w_1stWon', 0) if gano else r.get('l_1stWon', 0)
        w2 = r.get('w_2ndWon', 0) if gano else r.get('l_2ndWon', 0)
        spw = float((w1 or 0) + (w2 or 0))
        bp_f = r.get('l_bpFaced', 0) if gano else r.get('w_bpFaced', 0)
        bp_s = r.get('l_bpSaved', 0) if gano else r.get('w_bpSaved', 0)
        bp_won = max(int((bp_f or 0) - (bp_s or 0)), 0) if pd.notna(bp_f) and pd.notna(bp_s) else 0

        if pd.notna(aces):
            aces_lista.append(float(aces))

        pct_saque = f"{(spw / float(svpt))*100:.1f}%" if (pd.notna(svpt) and float(svpt) > 0) else "-"
        f_str = str(r.get('tourney_date', ''))
        f_fmt = f"{f_str[:4]}-{f_str[4:6]}-{f_str[6:8]}" if len(f_str) >= 8 else f_str

        filas.append({
            "Fecha Torneo": f_fmt,
            "Torneo": str(r.get('tourney_name', '')),
            "Cancha": str(r.get('surface', '')),
            "Rival": rival,
            "Resultado": "✅ Victoria" if gano else "❌ Derrota",
            "Marcador": str(r.get('score', '')),
            "Aces": int(aces) if pd.notna(aces) else 0,
            "% Pts Saque": pct_saque,
            "Quiebres": bp_won
        })

    aces_prom = round(float(np.mean(aces_lista)), 1) if aces_lista else base_aces
    return pd.DataFrame(filas).iloc[::-1], stats_sup, aces_prom, rank_final

def calcular_h2h_tenis(df_all, jug_a, jug_b):
    if df_all.empty:
        return 0, 0, pd.DataFrame()
    ca, cb = limpiar_texto_nombre(jug_a), limpiar_texto_nombre(jug_b)
    h2h = df_all[((df_all['w_clean'] == ca) & (df_all['l_clean'] == cb)) | ((df_all['w_clean'] == cb) & (df_all['l_clean'] == ca))].sort_values('tourney_date')
    if h2h.empty:
        return 0, 0, pd.DataFrame()
    ga = int((h2h['w_clean'] == ca).sum())
    gb = int((h2h['w_clean'] == cb).sum())
    filas_h2h = []
    for _, r in h2h.iterrows():
        f_str = str(r.get('tourney_date', ''))
        f_fmt = f"{f_str[:4]}-{f_str[4:6]}-{f_str[6:8]}" if len(f_str) >= 8 else f_str
        filas_h2h.append({
            "Fecha": f_fmt,
            "Torneo": str(r.get('tourney_name', '')),
            "Superficie": str(r.get('surface', '')),
            "Ganador(a)": str(r.get('winner_name', '')),
            "Marcador": str(r.get('score', ''))
        })
    return ga, gb, pd.DataFrame(filas_h2h).iloc[::-1]

# --- SELECTOR MAESTRO DE DEPORTE ---
st.sidebar.markdown("### 🎯 Selector Maestro de Deporte")
opciones_deportes = [
    "⚽ Fútbol (15 Ligas + UEFA Nations League)",
    "🎾 Tenis (ATP / WTA por Superficie + Boxscores Reales)",
    "🏀 Basketball (NBA - API ESPN en Vivo)",
    "🏈 Fútbol Americano (NFL - API ESPN en Vivo)",
    "⚾ Béisbol (MLB - API ESPN en Vivo)",
    "🏒 Hockey sobre Hielo (NHL - API NHL.com en Vivo)"
]
deporte_activo = st.sidebar.selectbox("Elige la disciplina a analizar:", opciones_deportes, index=0)
st.sidebar.markdown("---")

# ==============================================================================
# 1. MÓDULO FÚTBOL (15 COMPETICIONES INCLUYENDO UEFA NATIONS LEAGUE)
# ==============================================================================
if deporte_activo.startswith("⚽"):
    st.sidebar.markdown("### 🏆 1. Competición y Equipos")
    LIGAS_FUT = {
        "🌍 UEFA Nations League (Selecciones UEFA)": "NATIONS_LEAGUE",
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

    tiene_tiros_csv = ('HS' in df_csv.columns and not p_l['HS'].dropna().empty and not p_v['AS'].dropna().empty)
    sh_l = float(p_l['HS'].mean()) if tiene_tiros_csv else round(9.5 + gf_l * 2.4, 1)
    sh_v = float(p_v['AS'].mean()) if tiene_tiros_csv else round(8.5 + gf_v * 2.3, 1)
    sot_l = float(p_l['HST'].mean()) if tiene_tiros_csv else round(2.6 + gf_l * 1.25, 1)
    sot_v = float(p_v['AST'].mean()) if tiene_tiros_csv else round(2.2 + gf_v * 1.2, 1)
    cor_l = float(p_l['HC'].mean()) if tiene_tiros_csv else round(3.8 + gf_l * 0.68, 1)
    cor_v = float(p_v['AC'].mean()) if tiene_tiros_csv else round(3.4 + gf_v * 0.62, 1)

    with st.expander(f"📋 TABLA DE AUDITORÍA: Partidos reales extraídos para {eq_l} (Local) y {eq_v} (Visita)", expanded=True):
        if tiene_tiros_csv:
            st.success("✅ Fuente con Telemetría Completa (Opta / Football-Data): Goles (FTHG/FTAG), Remates (HS/AS), Remates a Puerta (HST/AST) y Córners (HC/AC) 100% reales.")
        else:
            st.warning("⚠️ Torneo Internacional / Liga de América: El registro oficial público contiene Goles Reales (FTHG/FTAG) verificados partido a partido. Los tiros y córners son proyecciones matemáticas.")
        if usar_amortiguador:
            st.info(f"🛡️ **Amortiguador Bayesiano Activo:** Goles {eq_l} calibrados a `{gf_l:.2f} GF / {gc_l:.2f} GC` | {eq_v} calibrados a `{gf_v:.2f} GF / {gc_v:.2f} GC`.")

        cols_l = [c for c in ['Date', 'Tournament', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HS', 'HST', 'HC'] if c in p_l.columns]
        st.markdown(f"**🏠 Últimos {len(p_l)} partidos de {eq_l} como LOCAL:**")
        st.dataframe(p_l[cols_l], use_container_width=True, hide_index=True)
        cols_v = [c for c in ['Date', 'Tournament', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'AS', 'AST', 'AC'] if c in p_v.columns]
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

    with st.sidebar.expander("📏 Cuotas y Líneas de Remates / Córners"):
        linea_remates = st.number_input("Línea Remates Totales", 10.5, 40.5, 24.5, 1.0)
        cuota_over_rem = st.number_input("Cuota Over Remates", 1.01, 15.0, 1.85, 0.05)
        linea_puerta = st.number_input("Línea Remates a Puerta", 3.5, 20.5, 8.5, 1.0)
        cuota_over_pue = st.number_input("Cuota Over a Puerta", 1.01, 15.0, 1.85, 0.05)
        linea_corners = st.number_input("Línea Córners Totales", 4.5, 20.5, 8.5, 1.0)
        cuota_over_cor = st.number_input("Cuota Over Córners", 1.01, 15.0, 1.85, 0.05)

    lam_rem = sh_l + sh_v
    p_ov_rem = float(1.0 - norm.cdf(linea_remates, loc=lam_rem, scale=4.8))
    lam_pue = sot_l + sot_v
    p_ov_pue = float(1.0 - norm.cdf(linea_puerta, loc=lam_pue, scale=2.75))
    lam_cor = cor_l + cor_v
    p_ov_cor = float(1.0 - norm.cdf(linea_corners, loc=lam_cor, scale=3.35))

    st.markdown(f"### 🏟️ {eq_l} vs. {eq_v} <span style='font-size:16px; color:#71717a;'>({liga_sel})</span>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("⚽ Proyección Goles (xG)", f"{lam_loc:.2f} - {lam_vis:.2f}", f"Total: {lam_loc+lam_vis:.2f}")
    k2.metric("🎯 Remates Esperados", f"{lam_rem:.1f} tiros", f"{sh_l:.1f} L + {sh_v:.1f} V")
    k3.metric("🥅 A Puerta Esp.", f"{lam_pue:.1f} al arco", f"{sot_l:.1f} L + {sot_v:.1f} V")
    k4.metric("⛳ Córners Calibrados", f"{lam_cor:.1f} esquinas", f"{cor_l:.1f} L + {cor_v:.1f} V")

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 1. Mercados de Goles y 1X2", "⛳ 2. Remates y Córners", "🔢 3. Matriz Exacta", "🔴 4. Radar En Vivo (In-Play)"])
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
        df_mat = pd.DataFrame(mat[:6, :6]*100, index=[f"🏠 {eq_l} ({i})" for i in range(6)], columns=[f"✈️ {eq_v} ({j})" for j in range(6)])
        st.dataframe(df_mat.style.format("{:.1f}%").background_gradient(cmap="YlOrBr"), use_container_width=True)

    with tab4:
        lc1, lc2, lc3, lc4 = st.columns(4)
        min_act = lc1.slider("⏱️ Minuto Actual", 1, 90, 60)
        g_loc_v = lc2.number_input(f"⚽ Goles {eq_l}", 0, 10, 0)
        g_vis_v = lc3.number_input(f"⚽ Goles {eq_v}", 0, 10, 0)
        pos_loc = lc4.slider(f"📊 Posesión {eq_l} (%)", 20, 80, 54)
        mostrar_cancha_calor(eq_l, eq_v, pos_loc, 100 - pos_loc, 1.1, 1.0, "futbol")
        frac_rest = max((94.0 - min_act) / 94.0, 0.04)
        lam_rest = (lam_loc + lam_vis) * frac_rest
        p_1_gol_mas = 1.0 - poisson.pmf(0, lam_rest)
        st.info(f"🔥 **Probabilidad de +0.5 Goles Restantes (Al menos 1 gol más):** `{p_1_gol_mas*100:.1f}%` | **Cuota Mínima Justa:** `{1/max(p_1_gol_mas, 0.01):.2f}`")


# ==============================================================================
# 2. MÓDULO TENIS (CON SUPERFICIE, FAVORITO(A) CLARO Y BOXSCORES REALES)
# ==============================================================================
elif deporte_activo.startswith("🎾"):
    st.sidebar.markdown("### 🎾 1. Circuito, Superficie y Tenistas")
    circuito = st.sidebar.radio("Circuito:", ["ATP (Masculino)", "WTA (Femenino)"])
    superficie_elegida = st.sidebar.selectbox(
        "🌍 Superficie de la Cancha:",
        [
            "🟦 Cancha Dura (Hard Court - Outdoor/Indoor)",
            "🟧 Polvo de Ladrillo / Arcilla (Clay)",
            "🟩 Césped (Grass - Wimbledon/Halle)"
        ]
    )
    formato_sets = st.sidebar.radio("Formato del Partido:", ["Al mejor de 3 Sets (Estándar)", "Al mejor de 5 Sets (Grand Slam)"])

    df_tenis_raw, lista_tenistas = cargar_boxscores_reales_tenis(circuito)
    if not lista_tenistas:
        st.error("No se pudo conectar al mirror CDN de Boxscores oficiales de Tenis en este momento.")
        st.stop()

    def_a = "Jannik Sinner" if "ATP" in circuito else "Marta Kostyuk"
    def_b = "Carlos Alcaraz" if "ATP" in circuito else "Jessica Pegula"
    idx_a = lista_tenistas.index(def_a) if def_a in lista_tenistas else 0
    idx_b = lista_tenistas.index(def_b) if def_b in lista_tenistas else (1 if len(lista_tenistas) > 1 else 0)

    col_t1, col_t2 = st.sidebar.columns(2)
    jug_a = col_t1.selectbox("🎾 Tenista A", lista_tenistas, index=idx_a)
    jug_b = col_t2.selectbox("🎾 Tenista B", lista_tenistas, index=idx_b)

    df_part_a, sup_a, aces_a, rank_a = analizar_tenista_por_superficie(df_tenis_raw, jug_a, circuito, 10)
    df_part_b, sup_b, aces_b, rank_b = analizar_tenista_por_superficie(df_tenis_raw, jug_b, circuito, 10)
    h2h_a, h2h_b, df_h2h = calcular_h2h_tenis(df_tenis_raw, jug_a, jug_b)

    if "Arcilla" in superficie_elegida:
        clave_sup, nombre_sup_corto, estilo_cancha = "Clay", "Arcilla (Clay)", "tenis_clay"
    elif "Césped" in superficie_elegida:
        clave_sup, nombre_sup_corto, estilo_cancha = "Grass", "Césped (Grass)", "tenis_grass"
    else:
        clave_sup, nombre_sup_corto, estilo_cancha = "Hard", "Cancha Dura (Hard)", "tenis_hard"

    hold_a_sup = sup_a[clave_sup]["Hold"]
    brk_a_sup = sup_a[clave_sup]["Break"]
    hold_b_sup = sup_b[clave_sup]["Hold"]
    brk_b_sup = sup_b[clave_sup]["Break"]

    # Cálculo de Probabilidad Real por Superficie + Peso de Ranking y H2H
    hold_eff_a = (hold_a_sup + (100.0 - brk_b_sup)) / 2.0
    hold_eff_b = (hold_b_sup + (100.0 - brk_a_sup)) / 2.0
    bono_rank_a = np.clip((np.log10(max(rank_b, 1)) - np.log10(max(rank_a, 1))) * 2.2, -4.0, 4.0)
    diff_efectivo = (hold_eff_a - hold_eff_b) + bono_rank_a

    p_set_a = float(np.clip(0.50 + (diff_efectivo / 100.0) * 2.15, 0.08, 0.92))
    p_set_b = 1.0 - p_set_a
    if "3 Sets" in formato_sets:
        p_gana_a = float((p_set_a ** 2) + 2.0 * (p_set_a ** 2) * p_set_b)
        sets_esp = 2.0 * ((p_set_a**2) + (p_set_b**2)) + 3.0 * (2.0 * p_set_a * p_set_b)
    else:
        p_gana_a = float((p_set_a ** 3) + 3.0 * (p_set_a ** 3) * p_set_b + 6.0 * (p_set_a ** 3) * (p_set_b ** 2))
        sets_esp = 3.65
    p_gana_b = 1.0 - p_gana_a

    media_hold = (hold_eff_a + hold_eff_b) / 2.0
    juegos_totales_esp = round((9.3 + ((media_hold - 70.0) / 25.0) * 1.65) * sets_esp, 1)

    # Identificación clara del Favorito(a) según el tipo de cancha seleccionado
    favorito_nom = jug_a if p_gana_a >= p_gana_b else jug_b
    fav_prob = max(p_gana_a, p_gana_b) * 100.0
    fav_cuota_justa = 1.0 / max(p_gana_a, p_gana_b)
    fav_rec_sup = sup_a[clave_sup] if p_gana_a >= p_gana_b else sup_b[clave_sup]

    st.markdown(f"""
    <div class="fav-banner">
        👑 <b>FAVORITO(A) EN {nombre_sup_corto.upper()}: {favorito_nom} ({fav_prob:.1f}% Prob. Real | Cuota Mínima Justa: {fav_cuota_justa:.2f})</b><br>
        📌 En <b>{nombre_sup_corto}</b> registra <b>{fav_rec_sup['G']}V - {fav_rec_sup['P']}D ({fav_rec_sup['WinPct']}% victorias)</b> con <b>{fav_rec_sup['Hold']}% Hold de Saque</b> y <b>{fav_rec_sup['Break']}% Quiebre al Resto</b> • Cara a Cara (H2H): <b>{jug_a} {h2h_a} - {h2h_b} {jug_b}</b>
    </div>
    """, unsafe_allow_html=True)

    # --- DESPLEGABLE AUTOMÁTICO DE AUDITORÍA DE TENIS (SUPERFICIE + PARTIDOS REALES) ---
    with st.expander(f"📋 TABLA DE AUDITORÍA TENIS: Estadísticas por Tipo de Cancha y Últimos Partidos Reales ({jug_a} vs {jug_b})", expanded=True):
        st.markdown("**🌍 1. Rendimiento Real Comparado por Tipo de Cancha (Dura vs. Arcilla vs. Césped):**")
        df_comparativa_canchas = pd.DataFrame([
            {
                "Tenista": jug_a,
                "Rank": f"#{rank_a}",
                "🟦 Dura (V-D | %Vict)": f"{sup_a['Hard']['G']}-{sup_a['Hard']['P']} ({sup_a['Hard']['WinPct']}%)",
                "🟦 Dura (Hold / Break)": f"{sup_a['Hard']['Hold']}% / {sup_a['Hard']['Break']}%",
                "🟧 Arcilla (V-D | %Vict)": f"{sup_a['Clay']['G']}-{sup_a['Clay']['P']} ({sup_a['Clay']['WinPct']}%)",
                "🟧 Arcilla (Hold / Break)": f"{sup_a['Clay']['Hold']}% / {sup_a['Clay']['Break']}%",
                "🟩 Césped (V-D | %Vict)": f"{sup_a['Grass']['G']}-{sup_a['Grass']['P']} ({sup_a['Grass']['WinPct']}%)",
                "🟩 Césped (Hold / Break)": f"{sup_a['Grass']['Hold']}% / {sup_a['Grass']['Break']}%",
                "Aces/PJ": aces_a
            },
            {
                "Tenista": jug_b,
                "Rank": f"#{rank_b}",
                "🟦 Dura (V-D | %Vict)": f"{sup_b['Hard']['G']}-{sup_b['Hard']['P']} ({sup_b['Hard']['WinPct']}%)",
                "🟦 Dura (Hold / Break)": f"{sup_b['Hard']['Hold']}% / {sup_b['Hard']['Break']}%",
                "🟧 Arcilla (V-D | %Vict)": f"{sup_b['Clay']['G']}-{sup_b['Clay']['P']} ({sup_b['Clay']['WinPct']}%)",
                "🟧 Arcilla (Hold / Break)": f"{sup_b['Clay']['Hold']}% / {sup_b['Clay']['Break']}%",
                "🟩 Césped (V-D | %Vict)": f"{sup_b['Grass']['G']}-{sup_b['Grass']['P']} ({sup_b['Grass']['WinPct']}%)",
                "🟩 Césped (Hold / Break)": f"{sup_b['Grass']['Hold']}% / {sup_b['Grass']['Break']}%",
                "Aces/PJ": aces_b
            }
        ])
        st.dataframe(df_comparativa_canchas, use_container_width=True, hide_index=True)

        if not df_h2h.empty:
            st.markdown(f"**⚔️ Historial de Enfrentamientos Directos (H2H: {jug_a} {h2h_a} - {h2h_b} {jug_b}):**")
            st.dataframe(df_h2h, use_container_width=True, hide_index=True)

        c_aud1, c_aud2 = st.columns(2)
        with c_aud1:
            st.markdown(f"**🎾 Últimos {len(df_part_a)} partidos reales en Boxscore de {jug_a}:**")
            st.dataframe(df_part_a, use_container_width=True, hide_index=True)
        with c_aud2:
            st.markdown(f"**🎾 Últimos {len(df_part_b)} partidos reales en Boxscore de {jug_b}:**")
            st.dataframe(df_part_b, use_container_width=True, hide_index=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas Betano Tenis")
    c_ta = st.sidebar.number_input(f"Gana {jug_a}", 1.01, 20.0, round(1/max(p_gana_a*1.05, 0.05), 2), 0.05)
    c_tb = st.sidebar.number_input(f"Gana {jug_b}", 1.01, 20.0, round(1/max(p_gana_b*1.05, 0.05), 2), 0.05)
    linea_j_ten = st.sidebar.number_input("Línea Total de Juegos", 16.5, 42.5, 21.5 if "WTA" in circuito else 22.5, 0.5)
    c_ov_j = st.sidebar.number_input(f"Cuota Más de {linea_j_ten} Juegos", 1.01, 15.0, 1.87, 0.05)
    c_un_j = st.sidebar.number_input(f"Cuota Menos de {linea_j_ten} Juegos", 1.01, 15.0, 1.90, 0.05)

    p_over_juegos = float(1.0 - norm.cdf(linea_j_ten, loc=juegos_totales_esp, scale=3.4))

    st.markdown(f"### 🎾 {jug_a} vs. {jug_b} <span style='font-size:16px; color:#71717a;'>({circuito} • {nombre_sup_corto})</span>", unsafe_allow_html=True)
    tk1, tk2, tk3, tk4 = st.columns(4)
    tk1.metric("🏆 Prob. Victoria", f"{p_gana_a*100:.1f}% vs {p_gana_b*100:.1f}%", f"Favorito(a): {favorito_nom}")
    tk2.metric(f"🎾 Hold Efectivo ({nombre_sup_corto})", f"{hold_eff_a:.1f}% vs {hold_eff_b:.1f}%", f"1er Set {jug_a}: {p_set_a*100:.1f}%")
    tk3.metric("📏 Total Juegos Esperados", f"{juegos_totales_esp} juegos", f"Sets Esp.: {sets_esp:.2f}")
    tk4.metric("🔥 Aces Promedio Combinados", f"{aces_a + aces_b:.1f} aces", f"{aces_a} + {aces_b}")

    tab1, tab2 = st.tabs(["🎯 1. Mercados Tenis (Betano)", "🔴 2. Radar En Vivo"])
    with tab1:
        m_t = [
            (f"Moneyline: Gana {jug_a} ({nombre_sup_corto})", p_gana_a, c_ta),
            (f"Moneyline: Gana {jug_b} ({nombre_sup_corto})", p_gana_b, c_tb),
            (f"Ganador(a) 1er Set: {jug_a}", p_set_a, round(1/max(p_set_a*1.05, 0.05), 2)),
            (f"Total Juegos: Más de {linea_j_ten} Juegos (Over)", p_over_juegos, c_ov_j),
            (f"Total Juegos: Menos de {linea_j_ten} Juegos (Under)", 1.0 - p_over_juegos, c_un_j)
        ]
        st.dataframe(pd.DataFrame([{"Mercado": m, "Prob. Real (%)": f"{p*100:.1f}%", "Cuota Justa": f"{1/p:.2f}", "Cuota Betano": f"{c:.2f}", "Edge (%)": f"{(p*c-1)*100:+.2f}%", "Veredicto": "✅ APOSTAR (+EV)" if (p*c-1)>0.05 else "❌ Pasar"} for m, p, c in m_t]).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)
    with tab2:
        mostrar_cancha_calor(jug_a, jug_b, hold_eff_a, hold_eff_b, 1.1, 1.0, estilo_cancha)


# ==============================================================================
# 3. MÓDULOS NBA (🏀), NFL (🏈) Y MLB (⚾)
# ==============================================================================
elif deporte_activo.startswith(("🏀", "🏈", "⚾")):
    if deporte_activo.startswith("🏀"):
        sport_p, league_c, nom_dep, sigma_m, cancha_k = "basketball", "nba", "NBA Basketball", 11.8, "nba"
    elif deporte_activo.startswith("🏈"):
        sport_p, league_c, nom_dep, sigma_m, cancha_k = "football", "nfl", "NFL Fútbol Americano", 13.2, "nfl"
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

    df_real_l = extraer_ultimos_partidos_reales_espn(sport_p, league_c, mapa_equipos_espn[u_l], u_l, 8)
    df_real_v = extraer_ultimos_partidos_reales_espn(sport_p, league_c, mapa_equipos_espn[u_v], u_v, 8)

    with st.expander(f"📋 TABLA DE AUDITORÍA {nom_dep}: Últimos partidos oficiales extraídos en vivo de ESPN ({u_l} vs {u_v})", expanded=True):
        st.success(f"✅ Datos de {nom_dep} extraídos 100% en tiempo real desde la API Oficial de ESPN (`site.api.espn.com`).")
        st.markdown(f"**🏠 Últimos {len(df_real_l)} partidos finalizados de {u_l}:**")
        if not df_real_l.empty:
            st.dataframe(df_real_l, use_container_width=True, hide_index=True)
        st.markdown(f"**✈️ Últimos {len(df_real_v)} partidos finalizados de {u_v}:**")
        if not df_real_v.empty:
            st.dataframe(df_real_v, use_container_width=True, hide_index=True)

    def_pts = 112.0 if sport_p == "basketball" else (22.5 if sport_p == "football" else 4.5)
    pf_l = float(df_real_l["Anotados"].mean()) if not df_real_l.empty else def_pts
    pa_l = float(df_real_l["Recibidos"].mean()) if not df_real_l.empty else def_pts
    pf_v = float(df_real_v["Anotados"].mean()) if not df_real_v.empty else def_pts
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


# ==============================================================================
# 4. MÓDULO HOCKEY SOBRE HIELO (NHL - API OFICIAL NHL.COM EN VIVO)
# ==============================================================================
else:
    st.sidebar.markdown("### 🏒 1. Equipos NHL")
    mapa_nhl = obtener_catalogo_equipos_nhl()
    if not mapa_nhl:
        st.error("No se pudo conectar con la API Oficial de la NHL (api-web.nhle.com).")
        st.stop()

    lista_nhl = sorted(list(mapa_nhl.keys()))
    nh_l = st.sidebar.selectbox("🏠 Local (Home)", lista_nhl, index=0)
    nh_v = st.sidebar.selectbox("✈️ Visita (Road)", lista_nhl, index=1 if len(lista_nhl) > 1 else 0)

    df_nhl_l = extraer_ultimos_partidos_reales_nhl(mapa_nhl[nh_l], 8)
    df_nhl_v = extraer_ultimos_partidos_reales_nhl(mapa_nhl[nh_v], 8)

    with st.expander(f"📋 TABLA DE AUDITORÍA NHL: Últimos partidos oficiales extraídos de NHL.com ({nh_l} vs {nh_v})", expanded=True):
        st.success("✅ Datos extraídos en tiempo real desde `api-web.nhle.com/v1/club-schedule-season`.")
        st.markdown(f"**🏠 Últimos {len(df_nhl_l)} partidos finalizados de {nh_l}:**")
        st.dataframe(df_nhl_l, use_container_width=True, hide_index=True)
        st.markdown(f"**✈️ Últimos {len(df_nhl_v)} partidos finalizados de {nh_v}:**")
        st.dataframe(df_nhl_v, use_container_width=True, hide_index=True)

    gf_nhl_l = float(df_nhl_l["Goles a Favor"].mean()) if not df_nhl_l.empty else 3.1
    gc_nhl_l = float(df_nhl_l["Goles en Contra"].mean()) if not df_nhl_l.empty else 3.0
    gf_nhl_v = float(df_nhl_v["Goles a Favor"].mean()) if not df_nhl_v.empty else 3.0
    gc_nhl_v = float(df_nhl_v["Goles en Contra"].mean()) if not df_nhl_v.empty else 3.1

    lam_nhl_l = max((gf_nhl_l + gc_nhl_v) / 2.0, 0.5)
    lam_nhl_v = max((gf_nhl_v + gc_nhl_l) / 2.0, 0.5)
    tot_nhl = lam_nhl_l + lam_nhl_v

    mat_n = np.zeros((13, 13))
    for i in range(13):
        for j in range(13):
            mat_n[i, j] = poisson.pmf(i, lam_nhl_l) * poisson.pmf(j, lam_nhl_v)
    p_reg_l = float(np.sum(np.tril(mat_n, -1)))
    p_emp = float(np.sum(np.diag(mat_n)))
    p_reg_v = float(np.sum(np.triu(mat_n, 1)))
    p_ml_l = p_reg_l + (p_emp * (lam_nhl_l / tot_nhl))
    p_ml_v = 1.0 - p_ml_l

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟠 2. Cuotas Betano NHL")
    c_nh_l = st.sidebar.number_input(f"Moneyline {nh_l}", 1.01, 20.0, round(1/max(p_ml_l*1.05, 0.05), 2), 0.05)
    c_nh_v = st.sidebar.number_input(f"Moneyline {nh_v}", 1.01, 20.0, round(1/max(p_ml_v*1.05, 0.05), 2), 0.05)
    linea_nhl = st.sidebar.selectbox("Línea Goles Totales NHL", [5.5, 6.0, 6.5], index=2)
    c_ov_nhl = st.sidebar.number_input(f"Cuota Over {linea_nhl}", 1.01, 15.0, 1.88, 0.05)
    c_un_nhl = st.sidebar.number_input(f"Cuota Under {linea_nhl}", 1.01, 15.0, 1.92, 0.05)

    p_ov_nhl = 1.0 - sum(poisson.pmf(k, tot_nhl) for k in range(int(linea_nhl) + 1))

    st.markdown(f"### 🧊 {nh_l} vs. {nh_v}")
    nk1, nk2 = st.columns(2)
    nk1.metric("🏒 Goles Esperados", f"{lam_nhl_l:.2f} - {lam_nhl_v:.2f}", f"Total: {tot_nhl:.2f} goles")
    nk2.metric("🏆 Prob. Moneyline (Inc. OT)", f"{p_ml_l*100:.1f}% vs {p_ml_v*100:.1f}%")

    ntab1, ntab2 = st.tabs(["🏆 1. Mercados NHL (Betano)", "🔴 2. Radar En Vivo"])
    with ntab1:
        m_nhl = [
            (f"Moneyline: Gana {nh_l} (Inc. OT)", p_ml_l, c_nh_l),
            (f"Moneyline: Gana {nh_v} (Inc. OT)", p_ml_v, c_nh_v),
            (f"Total: Más de {linea_nhl} Goles (Over)", p_ov_nhl, c_ov_nhl),
            (f"Total: Menos de {linea_nhl} Goles (Under)", 1.0 - p_ov_nhl, c_un_nhl)
        ]
        st.dataframe(pd.DataFrame([{"Mercado": m, "Prob. Real (%)": f"{p*100:.1f}%", "Cuota Justa": f"{1/p:.2f}", "Cuota Betano": f"{c:.2f}", "Edge (%)": f"{(p*c-1)*100:+.2f}%", "Veredicto": "✅ APOSTAR (+EV)" if (p*c-1)>0.05 else "❌ Pasar"} for m, p, c in m_nhl]).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)
    with ntab2:
        mostrar_cancha_calor(nh_l, nh_v, p_ml_l*100, p_ml_v*100, 1.1, 1.0, "nhl")
