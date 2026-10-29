import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Pro Bet Analyzer - Goles, Remates y Córners", layout="wide")
st.title("⚽ Dashboard Pro: Goles, Remates y Córners vs. Betano")

# --- 1. CONFIGURACIÓN Y ENTRADA DE DATOS ---
st.sidebar.header("🏆 1. Configuración de Equipos")
equipo_local = st.sidebar.text_input("Equipo Local", "Fiorentina")
equipo_visita = st.sidebar.text_input("Equipo Visitante", "Atalanta")

st.sidebar.markdown("---")
st.sidebar.header("📊 Promedios de Goles y xG")
xg_favor_local = st.sidebar.number_input("xG a Favor (Local)", min_value=0.1, max_value=5.0, value=1.75, step=0.05)
xg_contra_local = st.sidebar.number_input("xG en Contra (Local)", min_value=0.1, max_value=5.0, value=1.74, step=0.05)
xg_favor_visita = st.sidebar.number_input("xG a Favor (Visita)", min_value=0.1, max_value=5.0, value=1.06, step=0.05)
xg_contra_visita = st.sidebar.number_input("xG en Contra (Visita)", min_value=0.1, max_value=5.0, value=2.69, step=0.05)
promedio_liga = st.sidebar.number_input("Promedio Goles Liga", min_value=0.5, max_value=3.0, value=1.35, step=0.05)

st.sidebar.markdown("---")
st.sidebar.header("🎯 Promedios de Remates y Córners")
remates_local = st.sidebar.number_input("Remates Totales Promedio (Local)", min_value=1.0, max_value=30.0, value=14.5, step=0.5)
remates_visita = st.sidebar.number_input("Remates Totales Promedio (Visita)", min_value=1.0, max_value=30.0, value=11.2, step=0.5)
puerta_local = st.sidebar.number_input("Remates a Puerta Promedio (Local)", min_value=0.5, max_value=15.0, value=5.2, step=0.1)
puerta_visita = st.sidebar.number_input("Remates a Puerta Promedio (Visita)", min_value=0.5, max_value=15.0, value=4.1, step=0.1)
corners_local = st.sidebar.number_input("Córners Promedio (Local)", min_value=0.5, max_value=15.0, value=5.8, step=0.1)
corners_visita = st.sidebar.number_input("Córners Promedio (Visita)", min_value=0.5, max_value=15.0, value=4.5, step=0.1)

# --- 2. LÍNEAS DE BETANO ---
st.sidebar.markdown("---")
st.sidebar.header("🟠 Líneas y Cuotas Betano")
cuota_over_remates = st.sidebar.number_input("Cuota Over Remates Totales", min_value=1.01, value=1.85, step=0.05)
linea_remates = st.sidebar.number_input("Línea Remates Totales (Ej. 24.5)", min_value=10.0, max_value=40.0, value=24.5, step=0.5)

cuota_over_puerta = st.sidebar.number_input("Cuota Over Remates a Puerta", min_value=1.01, value=1.85, step=0.05)
linea_puerta = st.sidebar.number_input("Línea Remates a Puerta (Ej. 8.5)", min_value=2.0, max_value=20.0, value=8.5, step=0.5)

cuota_over_corners = st.sidebar.number_input("Cuota Over Córners", min_value=1.01, value=1.85, step=0.05)
linea_corners = st.sidebar.number_input("Línea Córners (Ej. 9.5)", min_value=2.0, max_value=20.0, value=9.5, step=0.5)

# --- MOTOR MATEMÁTICO (POISSON) ---
# Goles
lam_loc = max((xg_favor_local * xg_contra_visita) / promedio_liga, 0.05)
lam_vis = max((xg_favor_visita * xg_contra_local) / promedio_liga, 0.05)
matriz_prob = np.zeros((8, 8))
for i in range(8):
    for j in range(8):
        matriz_prob[i, j] = poisson.pmf(i, lam_loc) * poisson.pmf(j, lam_vis)

prob_1 = float(np.sum(np.tril(matriz_prob, -1)))
prob_x = float(np.sum(np.diag(matriz_prob)))
prob_2 = float(np.sum(np.triu(matriz_prob, 1)))
prob_over25 = 1.0 - float(matriz_prob[0,0] + matriz_prob[1,0] + matriz_prob[0,1] + matriz_prob[2,0] + matriz_prob[0,2] + matriz_prob[1,1])
prob_btts = 1.0 - float(np.sum(matriz_prob[0, :]) + np.sum(matriz_prob[:, 0]) - matriz_prob[0, 0])

# Remates y Córners (Poisson sumado)
lam_remates = remates_local + remates_visita
prob_over_remates = 1.0 - sum(poisson.pmf(k, lam_remates) for k in range(int(linea_remates) + 1))

lam_puerta = puerta_local + puerta_visita
prob_over_puerta = 1.0 - sum(poisson.pmf(k, lam_puerta) for k in range(int(linea_puerta) + 1))

lam_corners = corners_local + corners_visita
prob_over_corners = 1.0 - sum(poisson.pmf(k, lam_corners) for k in range(int(linea_corners) + 1))

# --- PANEL PRINCIPAL ---
st.subheader(f"📊 Resumen del Partido: {equipo_local} vs {equipo_visita}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("⚽ Goles Proyectados", f"{lam_loc:.2f} - {lam_vis:.2f}")
c2.metric("🎯 Remates Totales Esp.", f"{lam_remates:.1f} tiros")
c3.metric("🎯 Remates a Puerta Esp.", f"{lam_puerta:.1f} a puerta")
c4.metric(f"⛳ Córners Esp.", f"{lam_corners:.1f} córners")

# --- TABLAS DE VALOR ---
st.subheader("🎯 Detector de Valor: Goles y Resultados")
tabla_goles = [
    {"Mercado": f"Gana {equipo_local}", "Prob. (%)": f"{prob_1*100:.1f}%", "Cuota Justa": round(1/prob_1, 2), "Cuota Betano": 2.37, "Veredicto": "✅ +EV" if (prob_1*2.37)-1 > 0.03 else "❌ Pasar"},
    {"Mercado": "Empate", "Prob. (%)": f"{prob_x*100:.1f}%", "Cuota Justa": round(1/prob_x, 2), "Cuota Betano": 3.40, "Veredicto": "✅ +EV" if (prob_x*3.40)-1 > 0.03 else "❌ Pasar"},
    {"Mercado": f"Gana {equipo_visita}", "Prob. (%)": f"{prob_2*100:.1f}%", "Cuota Justa": round(1/prob_2, 2), "Cuota Betano": 2.77, "Veredicto": "✅ +EV" if (prob_2*2.77)-1 > 0.03 else "❌ Pasar"},
    {"Mercado": "Más de 2.5 Goles", "Prob. (%)": f"{prob_over25*100:.1f}%", "Cuota Justa": round(1/prob_over25, 2), "Cuota Betano": 1.75, "Veredicto": "✅ +EV" if (prob_over25*1.75)-1 > 0.03 else "❌ Pasar"},
    {"Mercado": "Ambos Anotan - SÍ", "Prob. (%)": f"{prob_btts*100:.1f}%", "Cuota Justa": round(1/prob_btts, 2), "Cuota Betano": 1.80, "Veredicto": "✅ +EV" if (prob_btts*1.80)-1 > 0.03 else "❌ Pasar"}
]
st.dataframe(pd.DataFrame(tabla_goles), use_container_width=True)

st.subheader("🎯 Detector de Valor: Remates y Córners (Betano)")
tabla_estadisticas = [
    {"Mercado Estadísticas": f"Más de {linea_remates} Remates Totales (Over)", "Prob. (%)": f"{prob_over_remates*100:.1f}%", "Cuota Justa": round(1/prob_over_remates, 2), "Cuota Betano": cuota_over_remates, "Veredicto": "✅ +EV" if (prob_over_remates*cuota_over_remates)-1 > 0.03 else "❌ Pasar"},
    {"Mercado Estadísticas": f"Más de {linea_puerta} Remates a Puerta (Over)", "Prob. (%)": f"{prob_over_puerta*100:.1f}%", "Cuota Justa": round(1/prob_over_puerta, 2), "Cuota Betano": cuota_over_puerta, "Veredicto": "✅ +EV" if (prob_over_puerta*cuota_over_puerta)-1 > 0.03 else "❌ Pasar"},
    {"Mercado Estadísticas": f"Más de {linea_corners} Córners Totales (Over)", "Prob. (%)": f"{prob_over_corners*100:.1f}%", "Cuota Justa": round(1/prob_over_corners, 2), "Cuota Betano": cuota_over_corners, "Veredicto": "✅ +EV" if (prob_over_corners*cuota_over_corners)-1 > 0.03 else "❌ Pasar"}
]
st.dataframe(pd.DataFrame(tabla_estadisticas), use_container_width=True)
