import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuración de la página
st.set_page_config(page_title="Pro Bet Analyzer 2.0", layout="wide")
st.title("⚽ Dashboard Automático de Value Bets (Versión 2.0)")
st.markdown("Selecciona la **Liga** y los **Clubes** en el menú izquierdo. El sistema descarga las estadísticas actualizadas de la temporada y calcula todo automáticamente.")

# --- CONEXIÓN AUTOMÁTICA A BASE DE DATOS DE LIGAS ---
LIGAS = {
    "🇮🇹 Serie A (Italia)": "https://www.football-data.co.uk/mmz4281/2627/I1.csv",
    "🇪🇸 LaLiga (España)": "https://www.football-data.co.uk/mmz4281/2627/SP1.csv",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)": "https://www.football-data.co.uk/mmz4281/2627/E0.csv",
    "🇩🇪 Bundesliga (Alemania)": "https://www.football-data.co.uk/mmz4281/2627/D1.csv",
    "🇫🇷 Ligue 1 (Francia)": "https://www.football-data.co.uk/mmz4281/2627/F1.csv"
}

@st.cache_data(ttl=3600)
def cargar_datos_liga(url):
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
        return df
    except Exception:
        # Respaldo automático a temporada previa si el archivo nuevo aún no inicia
        url_backup = url.replace("/2627/", "/2526/")
        df = pd.read_csv(url_backup)
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
        return df

# --- BARRA LATERAL: LISTAS DESPLEGABLES ---
st.sidebar.header("🏆 1. Selección de Liga y Partido")
liga_elegida = st.sidebar.selectbox("Selecciona la Liga", list(LIGAS.keys()))

df_liga = cargar_datos_liga(LIGAS[liga_elegida])
equipos = sorted(df_liga['HomeTeam'].unique())

equipo_local = st.sidebar.selectbox("🏠 Equipo Local", equipos, index=0)
equipo_visita = st.sidebar.selectbox("✈️ Equipo Visitante", equipos, index=1 if len(equipos) > 1 else 0)

# --- CÁLCULO AUTOMÁTICO DE PROMEDIOS (LOCAL / VISITANTE / LIGA) ---
partidos_local = df_liga[df_liga['HomeTeam'] == equipo_local]
partidos_visita = df_liga[df_liga['AwayTeam'] == equipo_visita]

gf_local_auto = float(partidos_local['FTHG'].mean()) if len(partidos_local) > 0 else 1.35
gc_local_auto = float(partidos_local['FTAG'].mean()) if len(partidos_local) > 0 else 1.35

gf_visita_auto = float(partidos_visita['FTAG'].mean()) if len(partidos_visita) > 0 else 1.15
gc_visita_auto = float(partidos_visita['FTHG'].mean()) if len(partidos_visita) > 0 else 1.35

promedio_liga_auto = float((df_liga['FTHG'].mean() + df_liga['FTAG'].mean()) / 2)

# Opción desplegable por si el usuario quiere ver o ajustar los datos arrastrados
with st.sidebar.expander("⚙️ Ver / Ajustar promedios arrastrados (Opcional)"):
    st.caption(f"Datos calculados de {len(partidos_local)} partidos en casa y {len(partidos_visita)} fuera.")
    xg_favor_local = st.number_input("Promedio Goles/xG a Favor (Local)", min_value=0.1, max_value=5.0, value=round(gf_local_auto, 2), step=0.05)
    xg_contra_local = st.number_input("Promedio Goles/xG en Contra (Local)", min_value=0.1, max_value=5.0, value=round(gc_local_auto, 2), step=0.05)
    xg_favor_visita = st.number_input("Promedio Goles/xG a Favor (Visita)", min_value=0.1, max_value=5.0, value=round(gf_visita_auto, 2), step=0.05)
    xg_contra_visita = st.number_input("Promedio Goles/xG en Contra (Visita)", min_value=0.1, max_value=5.0, value=round(gc_visita_auto, 2), step=0.05)
    promedio_liga = st.number_input("Promedio de la Liga", min_value=0.5, max_value=3.0, value=round(promedio_liga_auto, 2), step=0.05)

# --- BARRA LATERAL: CUOTAS DE LA CASA ---
st.sidebar.header("💰 2. Cuotas de tu Casa de Apuestas")
cuota_local = st.sidebar.number_input(f"Cuota Gana {equipo_local} (1)", min_value=1.01, value=2.10, step=0.05)
cuota_empate = st.sidebar.number_input("Cuota Empate (X)", min_value=1.01, value=3.40, step=0.05)
cuota_visita = st.sidebar.number_input(f"Cuota Gana {equipo_visita} (2)", min_value=1.01, value=3.50, step=0.05)
cuota_over25 = st.sidebar.number_input("Cuota Más de 2.5 Goles (Over)", min_value=1.01, value=1.90, step=0.05)
cuota_under25 = st.sidebar.number_input("Cuota Menos de 2.5 Goles (Under)", min_value=1.01, value=1.90, step=0.05)

# --- MOTOR MATEMÁTICO (POISSON) ---
fuerza_ataque_local = max(xg_favor_local, 0.1) / promedio_liga
fuerza_defensa_visita = max(xg_contra_visita, 0.1) / promedio_liga
lambda_local = fuerza_ataque_local * fuerza_defensa_visita * promedio_liga

fuerza_ataque_visita = max(xg_favor_visita, 0.1) / promedio_liga
fuerza_defensa_local = max(xg_contra_local, 0.1) / promedio_liga
lambda_visita = fuerza_ataque_visita * fuerza_defensa_local * promedio_liga

max_goles = 8
matriz_prob = np.zeros((max_goles, max_goles))

for i in range(max_goles):
    for j in range(max_goles):
        matriz_prob[i, j] = poisson.pmf(i, lambda_local) * poisson.pmf(j, lambda_visita)

prob_local = np.sum(np.tril(matriz_prob, -1))
prob_empate = np.sum(np.diag(matriz_prob))
prob_visita = np.sum(np.triu(matriz_prob, 1))

prob_under25 = matriz_prob[0,0] + matriz_prob[1,0] + matriz_prob[0,1] + matriz_prob[2,0] + matriz_prob[0,2] + matriz_prob[1,1]
prob_over25 = 1.0 - prob_under25

# Probabilidad de Ambos Anotan (BTTS)
prob_btts_no = np.sum(matriz_prob[0, :]) + np.sum(matriz_prob[:, 0]) - matriz_prob[0, 0]
prob_btts_si = 1.0 - prob_btts_no

# --- PANEL PRINCIPAL: RESUMEN AUTOMÁTICO DE CLUBES ---
st.subheader(f"📊 Rendimiento arrastrado automáticamente: {equipo_local} vs {equipo_visita}")
c1, c2, c3, c4 = st.columns(4)
c1.metric(f"⚽ {equipo_local} (Anote en Casa)", f"{xg_favor_local:.2f} goles/p", f"Recibe: {xg_contra_local:.2f}")
c2.metric(f"✈️ {equipo_visita} (Anote Fuera)", f"{xg_favor_visita:.2f} goles/p", f"Recibe: {xg_contra_visita:.2f}")
c3.metric(f"🎯 Proyección {equipo_local}", f"{lambda_local:.2f} Goles Esp.")
c4.metric(f"🎯 Proyección {equipo_visita}", f"{lambda_visita:.2f} Goles Esp.")

st.info(f"💡 **Dato extra del modelo:** La probabilidad matemática de **Ambos Equipos Anotan (BTTS - Sí)** es del **{prob_btts_si*100:.1f}%** (Cuota justa: **{1/prob_btts_si:.2f}**).")

# --- TABLA DETECTORA DE VALOR ---
st.subheader("🎯 Detector de Valor (Edge / +EV)")

mercados = [f"Gana {equipo_local} (1)", "Empate (X)", f"Gana {equipo_visita} (2)", "Más de 2.5 Goles (Over)", "Menos de 2.5 Goles (Under)"]
probs_modelo = [prob_local, prob_empate, prob_visita, prob_over25, prob_under25]
cuotas_casa = [cuota_local, cuota_empate, cuota_visita, cuota_over25, cuota_under25]

datos_tabla = []
for m, p, c in zip(mercados, probs_modelo, cuotas_casa):
    cuota_justa = 1 / p if p > 0 else 99.0
    prob_implicita = 1 / c
    edge = (p * c) - 1
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
