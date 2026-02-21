import pdfplumber
import pandas as pd
import re
import time
from geopy.geocoders import Nominatim

archivo_pdf = "BOE-A-2025-17059.pdf"
datos_filtrados = []

print("Analizando el PDF y extrayendo TODAS las plazas de Enfermería...")

provincia = ""
localidad = ""
centro = ""
capturando_centro = False

with pdfplumber.open(archivo_pdf) as pdf:
    for pagina in pdf.pages[32:]:
        texto = pagina.extract_text()
        if not texto: continue
        
        for linea in texto.split('\n'):
            linea = linea.strip()
            
            if linea.startswith("PROVINCIA:"):
                provincia = linea.replace("PROVINCIA:", "").strip().replace(".", "")
                capturando_centro = False
            elif linea.startswith("LOCALIDAD:"):
                localidad = linea.replace("LOCALIDAD:", "").strip().replace(".", "")
                capturando_centro = False
            elif linea.startswith("CODIGO:"):
                capturando_centro = True
                centro = ""
            elif capturando_centro:
                if linea.startswith("ESPECIALIDAD") or linea.startswith("TOTAL"):
                    capturando_centro = False
                else:
                    centro += linea + " "
            
            # Capturamos cualquier especialidad de enfermería o matrona
            if re.search(r'(ENFERMER[IÍ]A|ENF\.|MATRONA|OBST[EÉ]TRICO)', linea.upper()) and not linea.startswith("ESPECIALIDAD"):
                nombre_especialidad = re.sub(r'\d+', '', linea).strip().title()
                
                # Buscamos el número de plazas
                numeros = re.findall(r'\b\d+\b', linea)
                plazas = int(numeros[0]) if numeros else 0
                
                if plazas > 0:
                    datos_filtrados.append({
                        "Provincia": provincia,
                        "Localidad": localidad,
                        "Hospital / Unidad Docente": centro.strip(),
                        "Especialidad": nombre_especialidad,
                        "Plazas Ofertadas": plazas
                    })

df = pd.DataFrame(datos_filtrados)
print(f"Se encontraron {len(df)} plazas en total. Buscando coordenadas geográficas... (Esto tardará unos minutos)")

# --- FASE 2: OBTENER COORDENADAS ---
geolocator = Nominatim(user_agent="eir_scraper_produccion")
cache_coords = {}

def obtener_coordenadas(fila):
    ciudad = f"{fila['Localidad']}, {fila['Provincia']}, España"
    if ciudad in cache_coords: return cache_coords[ciudad]
    
    try:
        location = geolocator.geocode(ciudad, timeout=5)
        if location:
            coords = pd.Series([location.latitude, location.longitude])
            cache_coords[ciudad] = coords
            time.sleep(0.5) 
            return coords
    except Exception:
        pass
    return pd.Series([None, None])

df[['Latitud', 'Longitud']] = df.apply(obtener_coordenadas, axis=1)

# Guardamos la base de datos
df.to_csv("base_datos_hospitales.csv", index=False, encoding='utf-8-sig')
print("\n¡Base de datos global generada con éxito! 🌍")