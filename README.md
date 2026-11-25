# BlastSafe-DSS
Iowa Army Ammunition DSS. Decision Support System for Iowa Army Ammunition Plant event. 

# BlastSafe DSS — Simulador de Dispersión Atmosférica y Ventanas de Detonación

**BlastSafe DSS** (*Decision Support System*) es un prototipo geoespacial en Python diseñado para evaluar el impacto ambiental y poblacional de detonaciones controladas de materiales peligrosos (como azida de plomo), ayudando a identificar las ventanas horarias más seguras según las condiciones atmosféricas.

## Características Principales
* **Ingesta Meteorológica en Vivo (`clima.py`):** Conecta con la API oficial de NOAA (*National Weather Service*) para obtener pronósticos horarios de viento y temperatura por altitud, con respaldo automático local.
* **Motor de Dispersión Gaussiana (`dispersion.py`):** Modela la trayectoria y deposición gravitacional de partículas pesadas de plomo mediante una Pluma Gaussiana Inclinada.
* **Cruce Espacial GIS (`zonas_gis.py`):** Consulta OpenStreetMap (Overpass API) en un radio de 15 km para detectar hospitales, escuelas y centros poblados dentro del cono de dispersión.
* **Visualización Interactiva (`BlastSafe_Colab.ipynb`):** Interfaz en Google Colab con mapa satelital (Esri) y control deslizante de 24 horas con semáforo de decisión (`GO` / `NO_GO`).

## Ejecución Rápida en Google Colab
1. Abre `BlastSafe_Colab.ipynb` en Google Colab.
2. Ejecuta las celdas en orden (`Entorno de ejecución > Ejecutar todas`).
3. Utiliza el control deslizante `Hora (+h)` para evaluar el riesgo horario y la trayectoria del viento.

## Instalación Local
```bash
git clone https://github.com
cd blastsafe-dss
pip install -r requirements.txt
```
