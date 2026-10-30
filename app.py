import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Pro Bet Analyzer 5.0 | Suite Cuantitativa",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DISEÑO VISUAL PROFESIONAL (CSS PERSONALIZADO) ---
st.markdown("""
<style>
    /* Encabezado Principal Ejecutivo */
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
    /* Tarjetas de Métricas (KPIs) */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e4e4e7;
        border-top: 4px solid #ff6b00;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
    }
    /* Estilo de Pestañas (Tabs) */
    button[data-baseweb="tab"] {
        font-size: 16px !important;
        font-weight: 700 !important;
    }
</style>

<div class="main-banner">
    <h1>⚽ PRO BET ANALYZER 5.0 <span style="color:#ff8c00;">| SUITE CUANTITATIVA</span></h1>
    <p>Motor Predictivo de Distribución de Poisson • Amortiguador Bayesiano • Auditoría de Valor (+EV) vs. Betano</p>
</div>
""", unsafe_allow_html=True)

# --- 1. CONFIGURACIÓN DE LIGAS Y FUENTES ABIERTAS (EUROPA + AMÉRICA) ---
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

# --- FUNCIONES DE EXTRACCIÓN AUTOMÁTICA SIN BLOQUEOS ---
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
        
        # Si alguna liga menor no reporta tiros en algún partido, estima con base en su ofensiva
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

# --- BARRA LATERAL: SELECCIÓN DE LIGA Y CLUBES ---
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

# --- MOTOR MATEMÁTICO POISSON ---
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

# --- CUOTAS Y LÍNEAS DE BETANO ---
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

# Cálculos Poisson para Remates y Córners
lam_remates = remates_local + remates_visita
prob_over_remates = 1.0 - sum(poisson.pmf(k, lam_remates) for k in range(int(linea_remates) + 1))

lam_puerta = puerta_local + puerta_visita
prob_over_puerta = 1.0 - sum(poisson.pmf(k, lam_puerta) for k in range(int(linea_puerta) + 1))

lam_corners = corners_local + corners_visita
prob_over_corners = 1.0 - sum(poisson.pmf(k, lam_corners) for k in range(int(linea_corners) + 1))

# --- PANEL PRINCIPAL: CABECERA DEL PARTIDO Y TARJETAS KPI ---
st.markdown(f"### 🏟️ {equipo_local} vs. {equipo_visita} <span style='font-size:16px; color:#71717a; font-weight:normal;'>({liga_elegida})</span>", unsafe_allow_html=True)

if usar_amortiguador and (pj_loc < 6 or pj_vis < 6):
    st.caption(f"🛡️ **Amortiguador Bayesiano Activo:** Muestra ponderada con la media de la liga ({media_goles_liga:.2f} goles) por pocos partidos jugados ({equipo_local}: {pj_loc} PJ Casa | {equipo_visita}: {pj_vis} PJ Visita).")

k1, k2, k3, k4 = st.columns(4)
k1.metric("⚽ Proyección de Goles (xG)", f"{lam_loc:.2f} - {lam_vis:.2f}", f"Total esperado: {lam_loc+lam_vis:.2f} goles")
k2.metric("🎯 Remates Totales Esp.", f"{lam_remates:.1f} tiros", f"{remates_local:.1f} Local + {remates_visita:.1f} Visita")
k3.metric("🥅 Remates a Puerta Esp.", f"{lam_puerta:.1f} al arco", f"{puerta_local:.1f} Local + {puerta_visita:.1f} Visita")
k4.metric("⛳ Córners Proyectados", f"{lam_corners:.1f} esquinas", f"{corners_local:.1f} Local + {corners_visita:.1f} Visita")

st.markdown("<br>", unsafe_allow_html=True)

# Función para colorear filas con Valor (+EV)
def resaltar_valor(fila):
    if "✅ APOSTAR" in str(fila["Veredicto"]):
        return ['background-color: rgba(22, 163, 74, 0.14); font-weight: 600;'] * len(fila)
    return [''] * len(fila)

# --- NAVEGACIÓN POR PESTAÑAS (TABS) ---
tab1, tab2, tab3 = st.tabs([
    "🎯 1. Mercados de Goles y 1X2", 
    "⛳ 2. Mercados de Remates y Córners", 
    "🔢 3. Matriz Exacta de Poisson"
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
