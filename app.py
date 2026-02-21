import streamlit as st
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

st.set_page_config(page_title="Elección EIR Universal", page_icon="🏥", layout="wide")

st.title("🏥 Asistente Inteligente de Plazas EIR")
st.write("Encuentra tu destino ideal de residencia basándote en tus prioridades. ¡Válido para toda España y todas las especialidades!")

@st.cache_data
def cargar_datos():
    df = pd.read_csv("base_datos_hospitales.csv")
    
    precios_m2_provincia = {
        'Madrid': 18.5, 'Barcelona': 21.0, 'Baleares': 17.5, 'Málaga': 14.5, 
        'Guipúzcoa': 15.5, 'Las Palmas': 13.5, 'Santa Cruz de Tenerife': 13.0, 
        'Valencia': 14.0, 'Vizcaya': 13.5, 'Sevilla': 11.5, 'Alicante': 11.0, 
        'Cádiz': 10.5, 'Cantabria': 10.5, 'Álava': 11.5, 'Navarra': 10.5, 
        'Girona': 12.0, 'Tarragona': 9.5, 'Zaragoza': 9.5, 'Granada': 9.5, 
        'Murcia': 8.5, 'Huelva': 8.5, 'Córdoba': 8.0, 'Almería': 8.0, 
        'Toledo': 8.0, 'Burgos': 8.5, 'Valladolid': 8.0, 'Segovia': 8.5, 
        'Lleida': 8.0, 'Castellón': 7.5, 'A Coruña': 8.5, 'Pontevedra': 8.5, 
        'Asturias': 8.5, 'La Rioja': 8.0, 'León': 7.0, 'Palencia': 7.0, 
        'Salamanca': 8.5, 'Zamora': 6.5, 'Ávila': 6.5, 'Soria': 7.0, 
        'Guadalajara': 8.0, 'Cuenca': 6.5, 'Albacete': 7.0, 'Ciudad Real': 6.0, 
        'Badajoz': 6.5, 'Cáceres': 6.5, 'Jaén': 6.5, 'Ourense': 7.0, 'Lugo': 6.5,
        'Huesca': 8.0, 'Teruel': 6.5
    }

    dic_seguro = {
        k.upper().replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U'): v 
        for k, v in precios_m2_provincia.items()
    }

    provincia_csv = df['Provincia'].astype(str).str.upper()
    provincia_csv = provincia_csv.str.replace('Á','A').str.replace('É','E').str.replace('Í','I').str.replace('Ó','O').str.replace('Ú','U').str.strip()

    df['Precio_m2'] = provincia_csv.map(dic_seguro).fillna(9.0)

    df['Precio Alquiler (€)'] = (df['Precio_m2'] * 50).astype(int)
    df = df.drop(columns=['Precio_m2'])
    
    if 'Nota Ambiente (1-10)' not in df.columns:
        np.random.seed(42)
        df['Nota Ambiente (1-10)'] = np.random.randint(4, 11, df.shape[0])
        
    return df

df_completo = cargar_datos()

# Barra lateral - Interfaz del Usuario
st.sidebar.header("📍 ¿De dónde eres?")
ciudad_origen = st.sidebar.text_input("Tu ciudad actual:", "Málaga")

st.sidebar.header("💉 ¿Qué especialidades te interesan?")
# Lista de todas las especialidades disponibles en el CSV
lista_especialidades = df_completo['Especialidad'].unique().tolist()
# Multiselector (por defecto seleccionamos todas para que no salga vacío)
especialidades_elegidas = st.sidebar.multiselect(
    "Selecciona una o varias:", 
    options=lista_especialidades, 
    default=lista_especialidades
)

st.sidebar.header("⚖️ Tus Prioridades (0-10)")
peso_distancia = st.sidebar.slider("🚗 Cercanía a mi ciudad", 0, 10, 8)
#peso_ambiente = st.sidebar.slider("🤝 Buen ambiente (Docencia)", 0, 10, 10)
peso_alquiler = st.sidebar.slider("💰 Alquiler barato", 0, 10, 5)

# --- FILTRAMOS LOS DATOS SEGÚN LO QUE HAYA ELEGIDO EL USUARIO ---
if not especialidades_elegidas:
    st.warning("⚠️ Por favor, selecciona al menos una especialidad en el menú de la izquierda.")
else:
    df = df_completo[df_completo['Especialidad'].isin(especialidades_elegidas)].copy()

    # Cálculo Espacial
    @st.cache_data
    def obtener_coordenadas_usuario(ciudad):
        geolocator = Nominatim(user_agent="app_eir_produccion")
        try:
            location = geolocator.geocode(ciudad + ", España", timeout=5)
            if location: return (location.latitude, location.longitude)
        except: return None
        return None

    coords_usuario = obtener_coordenadas_usuario(ciudad_origen)

    if coords_usuario:
        st.success(f"📍 Coordenadas de {ciudad_origen} localizadas. Mostrando {len(df)} opciones...")
        
        def calcular_distancia(fila):
            if pd.isna(fila['Latitud']) or pd.isna(fila['Longitud']): return 9999 
            return geodesic(coords_usuario, (fila['Latitud'], fila['Longitud'])).kilometers

        df['Distancia (km)'] = df.apply(calcular_distancia, axis=1)
        df['Distancia (km)'] = df['Distancia (km)'].round(1)

        # Normalización
        def normalizar_inverso(columna):
            if columna.max() == columna.min(): return 1
            return (columna.max() - columna) / (columna.max() - columna.min() + 0.00001)

        def normalizar_directo(columna):
            if columna.max() == columna.min(): return 1
            return (columna - columna.min()) / (columna.max() - columna.min() + 0.00001)

        norm_dist = normalizar_inverso(df['Distancia (km)'])
        #norm_amb = normalizar_directo(df['Nota Ambiente (1-10)'])
        norm_alq = normalizar_inverso(df['Precio Alquiler (€)'])

        df['Puntos'] = (norm_dist * peso_distancia) + (norm_alq * peso_alquiler) #+ (norm_amb * peso_ambiente)
        df['Score (0-100)'] = ((df['Puntos'] / df['Puntos'].max()) * 100).round(1)

        df_ranking = df.sort_values(by='Score (0-100)', ascending=False).reset_index(drop=True)
        
        columnas_mostrar = ['Hospital / Unidad Docente', 'Localidad', 'Provincia', 'Especialidad', 'Plazas Ofertadas', 
                            'Distancia (km)', 'Precio Alquiler (€)', 'Score (0-100)']
        
        st.dataframe(
            df_ranking[columnas_mostrar].style.background_gradient(subset=['Score (0-100)'], cmap='Greens'),
            use_container_width=True,
            height=600
        )
    else:
        st.error("❌ No hemos podido encontrar esa ciudad en el mapa.")