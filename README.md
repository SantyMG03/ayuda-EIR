# Asistente Inteligente de Elección de Plazas EIR

Este proyecto es una herramienta de toma de decisiones diseñada para ayudar a enfermer@s residentes (EIR) a elegir su destino ideal de especialidad en España. Actualmente la convocatoria de 2026.

La aplicación analiza los datos oficiales del BOE, calcula distancias geográficas y permite ponderar factores económicos.

## Funcionalidades clave

* **Extracción Automática:** Scraper integrado que lee el PDF oficial del BOE y extrae todas las plazas de enfermería de España.
* **Geolocalización Dinámica:** Calcula la distancia exacta (en km) desde la ciudad del usuario hasta cada hospital mediante la API de OpenStreetMap (Nominatim).
* **Análisis Multicriterio:** Algoritmo que puntúa los destinos (0-100) basándose en:
    * **Proximidad:** Distancia a casa.
    * **Calidad de accesos:** Las principales ciudades se presusponen con mejores accesos (Trenes, autovías, ...)
    * **Economía:** Estimación del precio de alquiler por provincia.
* **Interfaz Interactiva:** Desarrollada en Streamlit para una navegación fluida desde PC o móvil.

## Stack Tecnológico

* **Lenguaje:** Python 3.10+
* **Framework Web:** Streamlit
* **Procesamiento de Datos:** Pandas / Numpy
* **Extracción de PDF:** PDFPlumber
* **Geolocalización:** Geopy 

## Estructura del Proyecto

* `app.py`: El núcleo de la aplicación web y motor de cálculo.
* `generador_final.py`: Script de backend para procesar el BOE y generar la base de datos.
* `base_datos_hospitales.csv`: Dataset maestro con coordenadas y plazas.
* `requirements.txt`: Lista de dependencias para el despliegue.

## Instalación Local

Si quieres ejecutarlo en tu máquina:

Clona el repositorio:
```bash
   git clone https://github.com/SantyMG03/ayuda-EIR.git
```
Crea y activa el entorno virtual:
```bash
   python3 -m venv entorno
   source entorno/bin/activate
```
Instala las dependencias
```bash
   pip install -r requirements.txt
```
Lanza la app
```bash
   streamlit run app.py
```
