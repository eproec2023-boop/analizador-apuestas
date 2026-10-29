import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuración de la página
st.set_page_config(page_title="Pro Bet Analyzer", layout="wide")
st.title("⚽ Dashboard de Análisis Cuantitativo y Value Bets")
st.markdown("Calcula probabilidades reales mediante **xG (Goles Esperados)** y detecta ventaja matemática (**Edge**) frente a las cuotas.")

# --- BARRA LATERAL: INGRESO DE DATOS ---
st.sidebar.header("📊 1. Datos de los Equipos (Promedios)")

equipo_local = st.sidebar.text_input("Nombre Equipo Local", "Equipo Local")
xg_favor_local = st.sidebar.number_input("xG a Favor (Local en casa)", min_value=0.1, max_value=5.0, value=1.65, step=0.05)
xg_contra_local = st.sidebar.number_input("xG en Contra (Local en casa)", min_value=0.1, max_value=5.0, value=0.95, step=0.05)

st.sidebar.markdown("---")

equipo_visita = st.sidebar.text_input("Nombre Equipo Visitante", "Equipo Visitante")
xg_favor_visita = st.sidebar.number_input("xG a Favor (Visita fuera)", min_value=0.1, max_value=5.0, value=1.20, step=0.05)
xg_contra_visita = st.sidebar.number_input("xG en Contra (Visita fuera)", min_value=0.1, max_value=5.0, value=1.45, step=0.05)

st.sidebar.markdown("---")
promedio_liga = st.sidebar.number_input("Promedio de goles por equipo en la Liga", min_value=0.5, max_value=3.0, value=1.35, step=0.05)

# --- BARRA LATERAL: CUOTAS DE LA CASA ---
st.sidebar.header("💰 2. Cuotas de la Casa de Apuestas")
cuota_local = st.sidebar.number_input("Cuota Ganador Local (1)", min_value=1.01, value=2.10, step=0.05)
cuota_empate = st.sidebar.number_input("Cuota Empate (X)", min_value=1.01, value=3.40, step=0.05)
cuota_visita = st.sidebar.number_input("Cuota Ganador Visita (2)", min_value=1.01, value=3.60, step=0.05)
cuota_over25 = st.sidebar.number_input("Cuota Más de 2.5 Goles (Over)", min_value=1.01, value=1.95, step=0.05)
cuota_under25 = st.sidebar.number_input("Cuota Menos de 2.5 Goles (Under)", min_value=1.01, value=1.85, step=0.05)

# --- MOTOR MATEMÁTICO (MODELO DE POISSON CRUZADO) ---
# Calculamos la fuerza de ataque y defensa relativa a la liga
fuerza_ataque_local = xg_favor_local / promedio_liga
fuerza_defensa_visita = xg_contra_visita / promedio_liga
lambda_local = fuerza_ataque_local * fuerza_defensa_visita * promedio_liga

fuerza_ataque_visita = xg_favor_visita / promedio_liga
fuerza_defensa_local = xg_contra_local / promedio_liga
lambda_visita = fuerza_ataque_visita * fuerza_defensa_local * promedio_liga

# Matriz de probabilidades de marcadores exactos (de 0 a 7 goles)
max_goles = 8
matriz_prob = np.zeros((max_goles, max_goles))

for i in range(max_goles):
    for j in range(max_goles):
        matriz_prob[i, j] = poisson.pmf(i, lambda_local) * poisson.pmf(j, lambda_visita)

# Probabilidades 1X2 y Over/Under 2.5
prob_local = np.sum(np.tril(matriz_prob, -1))
prob_empate = np.sum(np.diag(matriz_prob))
prob_visita = np.sum(np.triu(matriz_prob, 1))

prob_under25 = matriz_prob[0,0] + matriz_prob[1,0] + matriz_prob[0,1] + matriz_prob[2,0] + matriz_prob[0,2] + matriz_prob[1,1]
prob_over25 = 1.0 - prob_under25

# --- PANEL PRINCIPAL: RESULTADOS ---
col1, col2 = st.columns(2)
with col1:
    st.metric(label=f"Goles Esperados proyectados: {equipo_local}", value=f"{lambda_local:.2f} xG")
with col2:
    st.metric(label=f"Goles Esperados proyectados: {equipo_visita}", value=f"{lambda_visita:.2f} xG")

st.subheader("🎯 Detector de Valor (Edge / +EV)")

# Creación de la tabla comparativa con Pandas
mercados = [f"Gana {equipo_local} (1)", "Empate (X)", f"Gana {equipo_visita} (2)", "Más de 2.5 Goles (Over)", "Menos de 2.5 Goles (Under)"]
probs_modelo = [prob_local, prob_empate, prob_visita, prob_over25, prob_under25]
cuotas_casa = [cuota_local, cuota_empate, cuota_visita, cuota_over25, cuota_under25]

datos_tabla = []
for m, p, c in zip(mercados, probs_modelo, cuotas_casa):
    cuota_justa = 1 / p if p > 0 else 99.0
    prob_implicita = 1 / c
    edge = (p * c) - 1  # Fórmula de Valor Esperado (EV)
    decision = "✅ APOSTAR (+EV)" if edge > 0.03 else "❌ Pasar (Sin valor)"
    
    datos_tabla.append({
        "Mercado": m,
        "Prob. Modelo (%)": f"{p*100:.1f}%",
        "Cuota Justa (Modelo)": round(cuota_justa, 2),
        "Cuota Casa": c,
        "Prob. Implícita Casa (%)": f"{prob_implicita*100:.1f}%",
        "Edge / Ventaja (%)": f"{edge*100:.2f}%",
        "Recomendación": decision
    })

df_resultados = pd.DataFrame(datos_tabla)
st.dataframe(df_resultados, use_container_width=True)

# --- MATRIZ VISUAL DE MARCADORES EXACTOS ---
st.subheader("🔢 Matriz de Probabilidad de Marcador Exacto (%)")
df_matriz = pd.DataFrame(matriz_prob[:6, :6] * 100, 
                         index=[f"{equipo_local} {i}" for i in range(6)], 
                         columns=[f"{equipo_visita} {j}" for j in range(6)])
st.dataframe(df_matriz.style.format("{:.1f}%").background_gradient(cmap="Greens"), use_container_width=True)
