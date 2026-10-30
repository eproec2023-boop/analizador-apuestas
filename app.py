import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests

st.set_page_config(page_title="Pro Bet Analyzer 4.1 - Multiligas Pro", layout="wide")
st.title("⚽ Dashboard Automático Multiligas: Goles, Remates y Córners (v4.1)")
st.markdown("Datos 100% automáticos desde **Football-Data.co.uk** con **Amortiguador Bayesiano** para máxima fiabilidad estadística.")

# --- 1. CONFIGURACIÓN DE LIGAS Y FUENTES ABIERTAS ---
LIGAS_EUROPA_CSV = {
    "🇮🇹 Serie A (Italia)": "https://www.football-data.co.uk/mmz4281/2627/I1.csv",
    "🇪🇸 LaLiga (España)": "https://www.football-data.co.uk/mmz4281/2627/SP1.csv",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)": "https://www.football-data.co.uk/mmz4281/2627/E0.csv",
    "🇩🇪 Bundesliga (Alemania)": "https://www.football-data.co.uk/mmz4281/2627/D1.csv",
    "🇫🇷 Ligue 1 (Francia)": "https://www.football-data.co.uk/mmz4281/2627/F1.csv"
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
        filas.append({
            'Equipo': eq,
            'PJ_Home': int(len(h)),
            'PJ_Away': int(len(a)),
            'GF_Home': float(h['FTHG'].mean()) if len(h) > 0 else 1.40,
            'GC_Home': float(h['FTAG'].mean()) if len(h) > 0 else 1.15,
            'GF_Away': float(a['FTAG'].mean()) if len(a) > 0 else 1.15,
            'GC_Away': float(a['FTHG'].mean()) if len(a) > 0 else 1.40,
            'Shots_Home': float(h['HS'].mean()) if 'HS' in h and len(h) > 0 else 13.5,
            'Shots_Away': float(a['AS'].mean()) if 'AS' in a and len(a) > 0 else 11.0,
            'SoT_Home': float(h['HST'].mean()) if 'HST' in h and len(h) > 0 else 4.8,
            'SoT_Away': float(a['AST'].mean()) if 'AST' in a and len(a) > 0 else 3.9,
            'Corners_Home': float(h['HC'].mean()) if 'HC' in h and len(h) > 0 else 5.5,
            'Corners_Away': float(a['AC'].mean()) if 'AC' in a and len(a) > 0 else 4.4
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
st.sidebar.header("🏆 1. Selección de Liga y Partido")
liga_elegida = st.sidebar.selectbox("Selecciona la Liga", TODAS_LAS_LIGAS)

if liga_elegida in LIGAS_EUROPA_CSV:
    df_liga = cargar_europa_football_data(LIGAS_EUROPA_CSV[liga_elegida])
else:
    df_liga = cargar_america_datos(liga_elegida)

lista_equipos = df_liga['Equipo'].tolist()

equipo_local = st.sidebar.selectbox("🏠 Equipo Local", lista_equipos, index=0)
equipo_visita = st.sidebar.selectbox("✈️ Equipo Visitante", lista_equipos, index=1 if len(lista_equipos) > 1 else 0)

# --- INTERRUPTOR DE AMORTIGUADOR BAYESIANO (MUESTRA PEQUEÑA) ---
usar_amortiguador = st.sidebar.checkbox(
    "🛡️ Activar Amortiguador de Pocos Partidos (Corrección Bayesiana)", 
    value=True,
    help="Suaviza promedios extremos cuando un club lleva menos de 6 partidos de local o visitante, mezclándolos con la media de la liga."
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

# Peso de confianza: alcanza 100% a partir de 6 partidos en esa condición
peso_loc = min(pj_loc / 6.0, 1.0) if usar_amortiguador else 1.0
peso_vis = min(pj_vis / 6.0, 1.0) if usar_amortiguador else 1.0

gf_loc_calc = (peso_loc * float(row_loc['GF_Home'])) + ((1.0 - peso_loc) * media_gf_home)
gc_loc_calc = (peso_loc * float(row_loc['GC_Home'])) + ((1.0 - peso_loc) * media_gc_home)
gf_vis_calc = (peso_vis * float(row_vis['GF_Away'])) + ((1.0 - peso_vis) * media_gf_away)
gc_vis_calc = (peso_vis * float(row_vis['GC_Away'])) + ((1.0 - peso_vis) * media_gc_away)

# --- PANEL DESPLEGABLE PARA VER O AJUSTAR DATOS ARRASTRADOS ---
with st.sidebar.expander("⚙️ Ver / Ajustar promedios arrastrados (xG, Remates, Córners)"):
    st.caption(f"Muestra detectada: {equipo_local} ({pj_loc} PJ Casa) | {equipo_visita} ({pj_vis} PJ Visita).")
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

# --- MOTOR MATEMÁTICO POISSON (GOLES, REMATES Y CÓRNERS) ---
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
prob_btts_si = 1.0 - float(np.sum(matriz_prob[0, :]) + np.sum(matriz_prob[:, 0]) - matriz_prob[0, 0])

# --- CUOTAS Y LÍNEAS DE BETANO ---
st.sidebar.header("🟠 2. Cuotas y Líneas en Betano")
margen = 1.055
c_sug_1 = round(max(1.05, 1 / (max(prob_1, 0.05) * margen)), 2)
c_sug_x = round(max(1.05, 1 / (max(prob_x, 0.05) * margen)), 2)
c_sug_2 = round(max(1.05, 1 / (max(prob_2, 0.05) * margen)), 2)

cuota_1 = st.sidebar.number_input(f"1 - Gana {equipo_local}", min_value=1.01, value=c_sug_1, step=0.05)
cuota_x = st.sidebar.number_input("X - Empate", min_value=1.01, value=c_sug_x, step=0.05)
cuota_2 = st.sidebar.number_input(f"2 - Gana {equipo_visita}", min_value=1.01, value=c_sug_2, step=0.05)
cuota_over25 = st.sidebar.number_input("Cuota Más de 2.5 Goles", min_value=1.01, value=1.85, step=0.05)
cuota_btts = st.sidebar.number_input("Cuota Ambos Anotan - SÍ", min_value=1.01, value=1.80, step=0.05)

st.sidebar.markdown("---")
st.sidebar.subheader("📏 Líneas Especiales Betano")
linea_remates = st.sidebar.number_input("Línea Remates Totales", min_value=10.5, max_value=40.5, value=24.5, step=1.0)
cuota_over_rem = st.sidebar.number_input("Cuota Over Remates Totales", min_value=1.01, value=1.85, step=0.05)

linea_puerta = st.sidebar.number_input("Línea Remates a Puerta", min_value=3.5, max_value=20.5, value=8.5, step=1.0)
cuota_over_pue = st.sidebar.number_input("Cuota Over Remates a Puerta", min_value=1.01, value=1.85, step=0.05)

linea_corners = st.sidebar.number_input("Línea Córners Totales", min_value=4.5, max_value=20.5, value=9.5, step=1.0)
cuota_over_cor = st.sidebar.number_input("Cuota Over Córners", min_value=1.01, value=1.85, step=0.05)

# Cálculos Poisson para Remates y Córners
lam_remates = remates_local + remates_visita
prob_over_remates = 1.0 - sum(poisson.pmf(k, lam_remates) for k in range(int(linea_remates) + 1))

lam_puerta = puerta_local + puerta_visita
prob_over_puerta = 1.0 - sum(poisson.pmf(k, lam_puerta) for k in range(int(linea_puerta) + 1))

lam_corners = corners_local + corners_visita
prob_over_corners = 1.0 - sum(poisson.pmf(k, lam_corners) for k in range(int(linea_corners) + 1))

# --- PANEL PRINCIPAL ---
st.subheader(f"📊 Proyecciones Automáticas ({liga_elegida}): {equipo_local} vs {equipo_visita}")

if usar_amortiguador and (pj_loc < 6 or pj_vis < 6):
    st.info(f"🛡️ **Amortiguador Bayesiano Activo:** Como la muestra es corta ({equipo_local}: {pj_loc} PJ en casa | {equipo_visita}: {pj_vis} PJ fuera), se suavizaron los extremos con la media de la liga ({media_goles_liga:.2f} goles) para evitar proyecciones infladas.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("⚽ Goles Esperados", f"{lam_loc:.2f} vs {lam_vis:.2f}", f"Total: {lam_loc+lam_vis:.2f} goles")
c2.metric("🎯 Remates Totales Esp.", f"{lam_remates:.1f} tiros", f"{remates_local:.1f} L + {remates_visita:.1f} V")
c3.metric("🥅 Remates a Puerta Esp.", f"{lam_puerta:.1f} a puerta", f"{puerta_local:.1f} L + {puerta_visita:.1f} V")
c4.metric("⛳ Córners Esperados", f"{lam_corners:.1f} córners", f"{corners_local:.1f} L + {corners_visita:.1f} V")

# --- TABLA 1: GOLES Y RESULTADO ---
st.subheader("🎯 1. Detector de Valor: Resultado y Goles")
mercados_g = [f"Gana {equipo_local} (1)", "Empate (X)", f"Gana {equipo_visita} (2)", "Más de 2.5 Goles (Over)", "Ambos Equipos Anotan - SÍ"]
probs_g = [prob_1, prob_x, prob_2, prob_over25, prob_btts_si]
cuotas_g = [cuota_1, cuota_x, cuota_2, cuota_over25, cuota_btts]

filas_g = []
for m, p, c in zip(mercados_g, probs_g, cuotas_g):
    justa = 1 / p if p > 0 else 99.0
    edge = (p * c) - 1
    filas_g.append({
        "Mercado en Betano": m,
        "Prob. Modelo (%)": f"{p*100:.1f}%",
        "Cuota Mínima Justa": round(justa, 2),
        "Cuota Betano": c,
        "Edge / Ventaja (%)": f"{edge*100:.2f}%",
        "Recomendación": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
    })
st.dataframe(pd.DataFrame(filas_g), use_container_width=True)

# --- TABLA 2: REMATES, REMATES A PUERTA Y CÓRNERS ---
st.subheader("🎯 2. Detector de Valor: Remates y Córners")
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
        "Prob. Modelo (%)": f"{p*100:.1f}%",
        "Cuota Mínima Justa": round(justa, 2),
        "Cuota Betano": c,
        "Edge / Ventaja (%)": f"{edge*100:.2f}%",
        "Recomendación": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ Pasar (Sin valor)"
    })
st.dataframe(pd.DataFrame(filas_e), use_container_width=True)

# --- MATRIZ DE MARCADOR EXACTO ---
st.subheader("🔢 Matriz de Probabilidad de Marcador Exacto (%)")
df_matriz = pd.DataFrame(matriz_prob[:6, :6] * 100, 
                         index=[f"{equipo_local} {i}" for i in range(6)], 
                         columns=[f"{equipo_visita} {j}" for j in range(6)])
st.dataframe(df_matriz.style.format("{:.1f}%").background_gradient(cmap="Greens"), use_container_width=True)
