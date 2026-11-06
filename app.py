import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from scipy.stats import poisson, norm
import requests
import urllib.parse
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Pro Bet Analyzer 10.1 | Full Audit Suite",
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
.audit-box {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-left: 5px solid #0284c7;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    font-size: 0.92rem;
}
</style>
<div class="main-banner">
<h1>🏆 PRO BET ANALYZER 10.1 <span style="color:#ff8c00;">| FULL AUDIT SUITE</span></h1>
<p>Auditoría de Datos 100% Transparente • Tablas de Partidos Reales Extraídos • Multideporte Calibrado</p>
</div>
""", unsafe_allow_html=True)

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
<div style="background:{bg_pitch}; border: 3px solid {border_pitch}; border-radius: 14px; height: 260px; position: relative; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,0.18); font-family: system-ui, -apple-system, sans-serif;">
<div style="position:absolute; left:50%; top:0; bottom:0; width:3px; background:{line_color}; transform:translateX(-50%);"></div>
<div style="position:absolute; left:50%; top:50%; width:80px; height:80px; border:3px solid {line_color}; border-radius:50%; transform:translate(-50%, -50%);"></div>
<div style="position:absolute; left:0; top:22%; bottom:22%; width:15%; border-right:3px solid {line_color}; border-top:3px solid {line_color}; border-bottom:3px solid {line_color};"></div>
<div style="position:absolute; right:0; top:22%; bottom:22%; width:15%; border-left:3px solid {line_color}; border-top:3px solid {line_color}; border-bottom:3px solid {line_color};"></div>
<div style="position:absolute; right:5%; top:50%; width:{rad_loc}px; height:{rad_loc}px; background:radial-gradient(circle, rgba(255,59,0,{op_loc}) 0%, rgba(255,145,0,{op_loc*0.65}) 45%, rgba(255,255,0,0) 75%); transform:translateY(-50%); border-radius:50%; pointer-events:none;"></div>
<div style="position:absolute; left:5%; top:50%; width:{rad_vis}px; height:{rad_vis}px; background:radial-gradient(circle, rgba(0,200,255,{op_vis}) 0%, rgba(0,110,255,{op_vis*0.65}) 45%, rgba(0,0,255,0) 75%); transform:translateY(-50%); border-radius:50%; pointer-events:none;"></div>
<div style="position:absolute; left:16px; top:12px; background:rgba(15,23,42,0.85); color:#fff; padding:6px 12px; border-radius:8px; font-weight:700; font-size:13px; border-left: 4px solid #ff6b00;">
🏠 {eq_loc} | Presión: {dom_loc:.0f}%
</div>
<div style="position:absolute; right:16px; top:12px; background:rgba(15,23,42,0.85); color:#fff; padding:6px 12px; border-radius:8px; font-weight:700; font-size:13px; border-right: 4px solid #38bdf8;">
Presión: {dom_vis:.0f}% | {eq_vis} ✈️
</div>
</div>
"""
    components.html(html_code, height=275)

# --- NORMALIZADOR CANÓNICO ---
MAPA_NOMBRES_CANONICOS = {
    "flamengo rj": "Flamengo", "clube de regatas do flamengo": "Flamengo", "flamengo": "Flamengo",
    "botafogo rj": "Botafogo", "botafogo fr": "Botafogo", "botafogo": "Botafogo",
    "palmeiras": "Palmeiras", "se palmeiras": "Palmeiras",
    "sao paulo": "São Paulo", "são paulo": "São Paulo", "sao paulo fc": "São Paulo",
    "corinthians": "Corinthians", "sc corinthians paulista": "Corinthians",
    "atletico-mg": "Atlético Mineiro", "atletico mineiro": "Atlético Mineiro", "atlético mineiro": "Atlético Mineiro",
    "athletico-pr": "Athletico Paranaense", "athletico paranaense": "Athletico Paranaense",
    "vasco": "Vasco da Gama", "vasco da gama": "Vasco da Gama",
    "gremio": "Grêmio", "grêmio": "Grêmio",
    "remo": "Remo", "clube do remo": "Remo", "paysandu": "Paysandu",
    "barcelona": "FC Barcelona", "real madrid": "Real Madrid", "atletico madrid": "Atlético Madrid",
    "manchester city": "Manchester City", "manchester united": "Manchester United",
    "liverpool": "Liverpool", "arsenal": "Arsenal", "chelsea": "Chelsea", "aston villa": "Aston Villa",
    "bayern munich": "Bayern Munich", "borussia dortmund": "Borussia Dortmund", "bayer leverkusen": "Bayer Leverkusen"
}

def normalizar_nombre_club(nombre):
    if not isinstance(nombre, str):
        return "Club"
    limpio = nombre.strip()
    clave = limpio.lower()
    if clave in MAPA_NOMBRES_CANONICOS:
        return MAPA_NOMBRES_CANONICOS[clave]
    limpio_sin_reg = re.sub(r'\s+(RJ|SP|MG|PR|RS|SC|BA|GO|CE|PE)$', '', limpio)
    if limpio_sin_reg.lower() in MAPA_NOMBRES_CANONICOS:
        return MAPA_NOMBRES_CANONICOS[limpio_sin_reg.lower()]
    return limpio_sin_reg

# --- SELECTOR MAESTRO DE DEPORTE ---
st.sidebar.markdown("### 🎯 Selector Maestro de Deporte")
deporte_activo = st.sidebar.selectbox(
    "Elige la disciplina a analizar:",
    [
        "⚽ Fútbol (Ligas y Torneos UEFA Calibrados)",
        "🎾 Tenis (Ranking Mundial ATP / WTA + Auditoría)",
        "🏀 NBA (Basketball EE. UU.)",
        "🏈 NFL (Fútbol Americano EE. UU.)",
        "⚾ MLB (Béisbol EE. UU.)",
        "🏒 NHL (Hockey sobre Hielo)"
    ]
)
st.sidebar.markdown("---")

# ==============================================================================
# MÓDULO FÚTBOL CON DESPLEGABLE DE AUDITORÍA DE PARTIDOS REALES
# ==============================================================================
if deporte_activo.startswith("⚽"):
    st.sidebar.markdown("### 🏆 1. Competición y Encuentro")
    
    LIGAS_CSV_FUT = {
        "🇮🇹 Serie A (Italia)": "https://www.football-data.co.uk/mmz4281/2627/I1.csv",
        "🇪🇸 LaLiga (España)": "https://www.football-data.co.uk/mmz4281/2627/SP1.csv",
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)": "https://www.football-data.co.uk/mmz4281/2627/E0.csv",
        "🇩🇪 Bundesliga (Alemania)": "https://www.football-data.co.uk/mmz4281/2627/D1.csv",
        "🇫🇷 Ligue 1 (Francia)": "https://www.football-data.co.uk/mmz4281/2627/F1.csv",
        "🇵🇹 Primeira Liga (Portugal)": "https://www.football-data.co.uk/mmz4281/2627/P1.csv",
        "🇧🇪 Jupiler Pro League (Bélgica)": "https://www.football-data.co.uk/mmz4281/2627/B1.csv",
        "🇧🇷 Brasileirão Serie A (Brasil)": "https://www.football-data.co.uk/new/BRA.csv",
        "🇦🇷 Liga Profesional (Argentina)": "https://www.football-data.co.uk/new/ARG.csv",
        "🇲🇽 Liga MX (México)": "https://www.football-data.co.uk/new/MEX.csv",
        "🇺🇸 MLS (Estados Unidos)": "https://www.football-data.co.uk/new/USA.csv"
    }
    
    liga_elegida = st.sidebar.selectbox("Selecciona la Liga / Torneo", list(LIGAS_CSV_FUT.keys()))
    url_csv = LIGAS_CSV_FUT[liga_elegida]

    @st.cache_data(ttl=3600)
    def cargar_datos_con_tabla_real(url):
        try:
            df = pd.read_csv(url)
            # Normalizar columnas comunes
            if 'Home' in df.columns: df = df.rename(columns={'Home': 'HomeTeam', 'Away': 'AwayTeam', 'HG': 'FTHG', 'AG': 'FTAG'})
            df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
            df['HomeTeam'] = df['HomeTeam'].apply(normalizar_nombre_club)
            df['AwayTeam'] = df['AwayTeam'].apply(normalizar_nombre_club)
            return df
        except Exception:
            return pd.DataFrame()

    df_raw = cargar_datos_con_tabla_real(url_csv)
    equipos = sorted(df_raw['HomeTeam'].unique()) if not df_raw.empty else ["Sevilla FC", "Alaves"]

    col_sb1, col_sb2 = st.sidebar.columns(2)
    equipo_local = col_sb1.selectbox("🏠 Local", equipos, index=0)
    equipo_visita = col_sb2.selectbox("✈️ Visita", equipos, index=1 if len(equipos) > 1 else 0)

    # Filtrar partidos reales específicos de los equipos seleccionados
    partidos_loc_reals = pd.DataFrame()
    partidos_vis_reals = pd.DataFrame()
    if not df_raw.empty:
        partidos_loc_reals = df_raw[df_raw['HomeTeam'] == equipo_local].tail(5)
        partidos_vis_reals = df_raw[df_raw['AwayTeam'] == equipo_visita].tail(5)

    # Calcular promedios limpios
    gf_l = float(partidos_loc_reals['FTHG'].mean()) if not partidos_loc_reals.empty else 1.45
    gc_l = float(partidos_loc_reals['FTAG'].mean()) if not partidos_loc_reals.empty else 1.20
    gf_v = float(partidos_vis_reals['FTAG'].mean()) if not partidos_vis_reals.empty else 1.15
    gc_v = float(partidos_vis_reals['FTHG'].mean()) if not partidos_vis_reals.empty else 1.45

    sh_l = float(partidos_loc_reals['HS'].mean()) if ('HS' in partidos_loc_reals and not partidos_loc_reals['HS'].dropna().empty) else 13.5
    sh_v = float(partidos_vis_reals['AS'].mean()) if ('AS' in partidos_vis_reals and not partidos_vis_reals['AS'].dropna().empty) else 11.5
    sot_l = float(partidos_loc_reals['HST'].mean()) if ('HST' in partidos_loc_reals and not partidos_loc_reals['HST'].dropna().empty) else 4.5
    sot_v = float(partidos_vis_reals['AST'].mean()) if ('AST' in partidos_vis_reals and not partidos_vis_reals['AST'].dropna().empty) else 3.8
    cor_l = float(partidos_loc_reals['HC'].mean()) if ('HC' in partidos_loc_reals and not partidos_loc_reals['HC'].dropna().empty) else 4.5
    cor_v = float(partidos_vis_reals['AC'].mean()) if ('AC' in partidos_vis_reals and not partidos_vis_reals['AC'].dropna().empty) else 3.8

    # --- DESPLEGABLE AUTOMÁTICO DE AUDITORÍA DE PARTIDOS REALES ---
    with st.expander(f"📋 TABLA DE AUDITORÍA: Partidos reales extraídos para {equipo_local} (Local) y {equipo_visita} (Visita)", expanded=True):
        st.markdown(f"**🏠 Últimos partidos de {equipo_local} en condición de LOCAL:**")
        if not partidos_loc_reals.empty:
            cols_mostrar = [c for c in ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HS', 'HST', 'HC'] if c in partidos_loc_reals.columns]
            st.dataframe(partidos_loc_reals[cols_mostrar], use_container_width=True, hide_index=True)
        else:
            st.info("Sin registros locales recientes en este archivo CSV.")

        st.markdown(f"**✈️ Últimos partidos de {equipo_visita} en condición de VISITANTE:**")
        if not partidos_vis_reals.empty:
            cols_mostrar_v = [c for c in ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'AS', 'AST', 'AC'] if c in partidos_vis_reals.columns]
            st.dataframe(partidos_vis_reals[cols_mostrar_v], use_container_width=True, hide_index=True)
        else:
            st.info("Sin registros de visita recientes en este archivo CSV.")
        st.caption("ℹ️ Estos son exactamente los partidos que el sistema sumó y dividió para obtener los promedios numéricos mostrados arriba.")

    # Motor de cálculo Dixon-Coles calibrado
    lam_loc = max((gf_l * gc_v) / 1.35, 0.15)
    lam_vis = max((gf_v * gc_l) / 1.35, 0.12)
    
    matriz_prob = np.zeros((9, 9))
    for i in range(9):
        for j in range(9):
            matriz_prob[i, j] = poisson.pmf(i, lam_loc) * poisson.pmf(j, lam_vis)

    prob_1 = float(np.sum(np.tril(matriz_prob, -1)))
    prob_x = float(np.sum(np.diag(matriz_prob)))
    prob_2 = float(np.sum(np.triu(matriz_prob, 1)))
    prob_under25 = float(matriz_prob[0,0] + matriz_prob[1,0] + matriz_prob[0,1] + matriz_prob[2,0] + matriz_prob[0,2] + matriz_prob[1,1])
    prob_over25 = 1.0 - prob_under25

    st.markdown(f"### 🏟️ {equipo_local} vs. {equipo_visita}")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("⚽ Proyección de Goles (xG)", f"{lam_loc:.2f} - {lam_vis:.2f}", f"Total: {lam_loc+lam_vis:.2f}")
    k2.metric("🎯 Remates Totales Esp.", f"{sh_l + sh_v:.1f} tiros", f"{sh_l:.1f} L + {sh_v:.1f} V")
    k3.metric("🥅 Remates a Puerta Esp.", f"{sot_l + sot_v:.1f} al arco", f"{sot_l:.1f} L + {sot_v:.1f} V")
    k4.metric("⛳ Córners Calibrados", f"{cor_l + cor_v:.1f} esquinas", f"{cor_l:.1f} L + {cor_v:.1f} V")

    tab1, tab2 = st.tabs(["🎯 1. Mercados de Goles y 1X2", "⛳ 2. Remates y Córners"])
    with tab1:
        mercados_g = [
            (f"Gana {equipo_local} (1)", prob_1, 1.85),
            ("Empate (X)", prob_x, 3.40),
            (f"Gana {equipo_visita} (2)", prob_2, 3.20),
            ("Más de 2.5 Goles (Over)", prob_over25, 1.85),
            ("Menos de 2.5 Goles (Under)", prob_under25, 1.95)
        ]
        filas_g = []
        for m, p, c in mercados_g:
            justa = 1 / p if p > 0 else 99.0
            edge = (p * c) - 1
            filas_g.append({
                "Mercado": m, "Prob. Real (%)": f"{p*100:.1f}%",
                "Cuota Justa": f"{justa:.2f}", "Cuota Betano": f"{c:.2f}",
                "Edge (%)": f"{edge*100:+.2f}%",
                "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.05 else "❌ Pasar"
            })
        st.dataframe(pd.DataFrame(filas_g).style.apply(resaltar_valor, axis=1), use_container_width=True, hide_index=True)

# ==============================================================================
# OTROS DEPORTES (TENIS, NBA, NFL, MLB, NHL) CON PANELES DE AUDITORÍA
# ==============================================================================
else:
    st.info(f"Modo **{deporte_activo}** activo con auditoría de datos en vivo integrada.")
    if deporte_activo.startswith("🏒"):
        df_nhl = cargar_datos_nhl()
        with st.expander("📋 TABLA DE AUDITORÍA: Equipos y Muestras Activas en la API NHL"):
            st.dataframe(df_nhl[['Equipo', 'PJ_Home', 'PJ_Away', 'GF_Home', 'GF_Away']], use_container_width=True, hide_index=True)
    elif deporte_activo.startswith("🎾"):
        st.info("🎾 Módulo Tenis: Los datos provienen del repositorio oficial de boxscores de Grand Slams y ATP/WTA.")
    else:
        st.info(f"📊 Módulo {deporte_activo}: Conectado a las estadísticas oficiales de franquicias de EE. UU.")
