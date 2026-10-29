import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests
import json
import re

st.set_page_config(page_title="Pro Bet Analyzer - Edición Betano", layout="wide")
st.title("⚽ Dashboard Automático xG + Analizador de Cuotas Betano")

LIGAS_UNDERSTAT = {
    "🇮🇹 Serie A (Italia)": "Serie_A",
    "🇪🇸 LaLiga (España)": "La_liga",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)": "EPL",
    "🇩🇪 Bundesliga (Alemania)": "Bundesliga",
    "🇫🇷 Ligue 1 (Francia)": "Ligue_1"
}

@st.cache_data(ttl=3600)
def obtener_datos_understat(liga_codigo, temporada="2026"):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    url = f"https://understat.com/league/{liga_codigo}/{temporada}"
    try:
        r = requests.get(url, headers=headers, timeout=8)
        match = re.search(r"teamsData\s*=\s*JSON\.parse\('([^']+)'\)", r.text)
        if match:
            raw_json = match.group(1).encode('utf-8').decode('unicode_escape')
            datos_equipos = json.loads(raw_json)
            filas = []
            for team_id, info in datos_equipos.items():
                nombre = info['title']
                hist = info['history']
                home_games = [m for m in hist if m['h_a'] == 'h']
                away_games = [m for m in hist if m['h_a'] == 'a']
                m_h = len(home_games) if len(home_games) > 0 else 1
                m_a = len(away_games) if len(away_games) > 0 else 1
                
                filas.append({
                    'Equipo': nombre,
                    'M_Home': len(home_games),
                    'G_Home': sum(m['scored'] for m in home_games) / m_h,
                    'GA_Home': sum(m['missed'] for m in home_games) / m_h,
                    'xG_Home': sum(m['xG'] for m in home_games) / m_h,
                    'xGA_Home': sum(m['xGA'] for m in home_games) / m_h,
                    'M_Away': len(away_games),
                    'G_Away': sum(m['scored'] for m in away_games) / m_a,
                    'GA_Away': sum(m['missed'] for m in away_games) / m_a,
                    'xG_Away': sum(m['xG'] for m in away_games) / m_a,
                    'xGA_Away': sum(m['xGA'] for m in away_games) / m_a,
                })
            return pd.DataFrame(filas).sort_values('Equipo')
    except Exception:
        pass
    
    # Respaldo automático por seguridad si la web externa se protege
    equipos_default = ["Fiorentina", "Atalanta", "Inter", "Milan", "Juventus", "Napoli", "Roma", "Lazio", "Bologna", "Torino"]
    filas_respaldo = [{
        'Equipo': eq, 'M_Home': 4, 'G_Home': 1.5, 'GA_Home': 1.0, 'xG_Home': 1.65, 'xGA_Home': 1.10,
        'M_Away': 4, 'G_Away': 1.2, 'GA_Away': 1.3, 'xG_Away': 1.35, 'xGA_Away': 1.40
    } for eq in equipos_default]
    return pd.DataFrame(filas_respaldo).sort_values('Equipo')

# --- 1. SELECCIÓN DE LIGA Y PARTIDO ---
st.sidebar.header("🏆 1. Selección de Liga y Partido")
liga_nombre = st.sidebar.selectbox("Selecciona la Liga", list(LIGAS_UNDERSTAT.keys()))
df_u = obtener_datos_understat(LIGAS_UNDERSTAT[liga_nombre])

equipos = df_u['Equipo'].tolist()
equipo_local = st.sidebar.selectbox("🏠 Equipo Local", equipos, index=equipos.index("Fiorentina") if "Fiorentina" in equipos else 0)
equipo_visita = st.sidebar.selectbox("✈️ Equipo Visitante", equipos, index=equipos.index("Atalanta") if "Atalanta" in equipos else 1)

tipo_modelo = st.sidebar.radio(
    "🧠 Motor Estadístico:",
    ["Híbrido Pro (70% xG + 30% Goles Reales)", "100% xG (Idéntico a Understat)", "100% Goles Reales (G / GA)"]
)

row_loc = df_u[df_u['Equipo'] == equipo_local].iloc[0]
row_vis = df_u[df_u['Equipo'] == equipo_visita].iloc[0]

if "100% xG" in tipo_modelo:
    fav_loc, con_loc = row_loc['xG_Home'], row_loc['xGA_Home']
    fav_vis, con_vis = row_vis['xG_Away'], row_vis['xGA_Away']
    media_liga = (df_u['xG_Home'].mean() + df_u['xG_Away'].mean()) / 2
elif "Híbrido" in tipo_modelo:
    fav_loc = 0.7 * row_loc['xG_Home'] + 0.3 * row_loc['G_Home']
    con_loc = 0.7 * row_loc['xGA_Home'] + 0.3 * row_loc['GA_Home']
    fav_vis = 0.7 * row_vis['xG_Away'] + 0.3 * row_vis['G_Away']
    con_vis = 0.7 * row_vis['xGA_Away'] + 0.3 * row_vis['GA_Away']
    media_liga = (df_u['xG_Home'].mean() + df_u['xG_Away'].mean()) / 2
else:
    fav_loc, con_loc = row_loc['G_Home'], row_loc['GA_Home']
    fav_vis, con_vis = row_vis['G_Away'], row_vis['G_Away']
    media_liga = (df_u['G_Home'].mean() + df_u['G_Away'].mean()) / 2

with st.sidebar.expander("⚙️ Ver / Ajustar promedios arrastrados"):
    xg_favor_local = st.number_input("xG/Goles a Favor (Local)", value=round(float(fav_loc), 2), step=0.05)
    xg_contra_local = st.number_input("xGA/Goles en Contra (Local)", value=round(float(con_loc), 2), step=0.05)
    xg_favor_visita = st.number_input("xG/Goles a Favor (Visita)", value=round(float(fav_vis), 2), step=0.05)
    xg_contra_visita = st.number_input("xGA/Goles en Contra (Visita)", value=round(float(con_vis), 2), step=0.05)
    promedio_liga = st.number_input("Promedio de la Liga", value=round(float(media_liga), 2), step=0.05)

# --- MOTOR POISSON ---
lambda_local = max((xg_favor_local * xg_contra_visita) / promedio_liga, 0.05)
lambda_visita = max((xg_favor_visita * xg_contra_local) / promedio_liga, 0.05)

max_goles = 8
matriz_prob = np.zeros((max_goles, max_goles))
for i in range(max_goles):
    for j in range(max_goles):
        matriz_prob[i, j] = poisson.pmf(i, lambda_local) * poisson.pmf(j, lambda_visita)

prob_local = float(np.sum(np.tril(matriz_prob, -1)))
prob_empate = float(np.sum(np.diag(matriz_prob)))
prob_visita = float(np.sum(np.triu(matriz_prob, 1)))

prob_under25 = float(matriz_prob[0,0] + matriz_prob[1,0] + matriz_prob[0,1] + matriz_prob[2,0] + matriz_prob[0,2] + matriz_prob[1,1])
prob_over25 = 1.0 - prob_under25

prob_btts_no = float(np.sum(matriz_prob[0, :]) + np.sum(matriz_prob[:, 0]) - matriz_prob[0, 0])
prob_btts_si = 1.0 - prob_btts_no

# --- ESTIMADOR DE CUOTAS BASE DE MERCADO ---
l_casa_loc = max((row_loc['G_Home'] * row_vis['GA_Away']) / max(media_liga, 0.5), 0.2)
l_casa_vis = max((row_vis['G_Away'] * row_loc['GA_Home']) / max(media_liga, 0.5), 0.2)
m_casa = np.zeros((max_goles, max_goles))
for i in range(max_goles):
    for j in range(max_goles):
        m_casa[i, j] = poisson.pmf(i, l_casa_loc) * poisson.pmf(j, l_casa_vis)

margen_betano = 1.055
c_sug_loc = round(max(1.05, 1 / (max(np.sum(np.tril(m_casa, -1)), 0.05) * margen_betano)), 2)
c_sug_emp = round(max(1.05, 1 / (max(np.sum(np.diag(m_casa)), 0.05) * margen_betano)), 2)
c_sug_vis = round(max(1.05, 1 / (max(np.sum(np.triu(m_casa, 1)), 0.05) * margen_betano)), 2)

# --- 2. CUOTAS DE BETANO ---
st.sidebar.header("🟠 2. Cuotas en Betano")
st.sidebar.caption("Ingresa las cuotas exactas de tu app Betano para detectar el Edge real:")

cuota_local = st.sidebar.number_input(f"1 - Gana {equipo_local}", min_value=1.01, value=c_sug_loc, step=0.05)
cuota_empate = st.sidebar.number_input("X - Empate", min_value=1.01, value=c_sug_emp, step=0.05)
cuota_visita = st.sidebar.number_input(f"2 - Gana {equipo_visita}", min_value=1.01, value=c_sug_vis, step=0.05)
cuota_over25 = st.sidebar.number_input("Más de 2.5 Goles (Over)", min_value=1.01, value=1.85, step=0.05)
cuota_under25 = st.sidebar.number_input("Menos de 2.5 Goles (Under)", min_value=1.01, value=1.95, step=0.05)
cuota_btts_si = st.sidebar.number_input("Ambos Anotan - SÍ (BTTS)", min_value=1.01, value=1.80, step=0.05)
cuota_btts_no = st.sidebar.number_input("Ambos Anotan - NO", min_value=1.01, value=1.95, step=0.05)

# --- PANEL PRINCIPAL ---
st.subheader(f"📊 Estadísticas del Partido: {equipo_local} (Local) vs {equipo_visita} (Visita)")
col1, col2, col3, col4 = st.columns(4)
col1.metric(f"🏠 {equipo_local} xG a Favor", f"{row_loc['xG_Home']:.2f} xG/p", f"Goles reales: {row_loc['G_Home']:.2f}")
col2.metric(f"🏠 {equipo_local} xGA Contra", f"{row_loc['xGA_Home']:.2f} xGA/p", f"Goles reales: {row_loc['GA_Home']:.2f}")
col3.metric(f"✈️ {equipo_visita} xG a Favor", f"{row_vis['xG_Away']:.2f} xG/p", f"Goles reales: {row_vis['G_Away']:.2f}")
col4.metric(f"✈️ {equipo_visita} xGA Contra", f"{row_vis['xGA_Away']:.2f} xGA/p", f"Goles reales: {row_vis['GA_Away']:.2f}")

st.subheader("🎯 Detector de Valor vs. Cuotas Betano (Edge / +EV)")

mercados = [
    f"Gana {equipo_local} (1)",
    "Empate (X)",
    f"Gana {equipo_visita} (2)",
    "Más de 2.5 Goles (Over)",
    "Menos de 2.5 Goles (Under)",
    "Ambos Equipos Anotan - SÍ",
    "Ambos Equipos Anotan - NO"
]
probs_modelo = [prob_local, prob_empate, prob_visita, prob_over25, prob_under25, prob_btts_si, prob_btts_no]
cuotas_casa = [cuota_local, cuota_empate, cuota_visita, cuota_over25, cuota_under25, cuota_btts_si, cuota_btts_no]

datos_tabla = []
for m, p, c in zip(mercados, probs_modelo, cuotas_casa):
    cuota_justa = 1 / p if p > 0 else 99.0
    edge = (p * c) - 1
    datos_tabla.append({
        "Mercado en Betano": m,
        "Prob. Real Modelo (%)": f"{p*100:.1f}%",
        "Cuota Mínima Justa": round(cuota_justa, 2),
        "Cuota en Betano": c,
        "Edge / Ventaja (%)": f"{edge*100:.2f}%",
        "Veredicto": "✅ APOSTAR (+EV)" if edge > 0.04 else "❌ No apostar (Sin valor)"
    })

st.dataframe(pd.DataFrame(datos_tabla), use_container_width=True)

# --- MATRIZ DE MARCADOR EXACTO ---
st.subheader("🔢 Matriz de Probabilidad de Marcador Exacto (%)")
df_matriz = pd.DataFrame(matriz_prob[:6, :6] * 100, 
                         index=[f"{equipo_local} {i}" for i in range(6)], 
                         columns=[f"{equipo_visita} {j}" for j in range(6)])
st.dataframe(df_matriz.style.format("{:.1f}%").background_gradient(cmap="Greens"), use_container_width=True)
