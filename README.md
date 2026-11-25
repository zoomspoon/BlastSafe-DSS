# BlastSafe DSS — Simulador de Dispersión Atmosférica y Ventanas de Detonación

**BlastSafe DSS** (*Decision Support System*) es un prototipo geoespacial en Python diseñado para evaluar el impacto ambiental y poblacional de detonaciones controladas de materiales peligrosos (como azida de plomo), ayudando a identificar las ventanas horarias más seguras según las condiciones atmosféricas.

---

## 1. ¿Cómo se monitorean estas variables en tiempo real?

Para alimentar un sistema de soporte a la decisión con precisión, se combinan datos de red meteorológica global con telemetría local en el sitio:

* **APIs Meteorológicas y Modelos Numéricos:** Servicios abiertos como **NOAA / NWS** (*National Weather Service*) y **Open-Meteo** proporcionan pronósticos horarios de velocidad y dirección del viento, temperatura, humedad y radiación solar en múltiples altitudes.
* **Perfiladores Verticales y Radiosondas:** Dado que la columna térmica de una explosión asciende cientos de metros, en operaciones reales se complementa el pronóstico con globos sonda o radares LIDAR/SODAR portátiles para medir corrientes de aire en altura.
* **Detección de Inversión Térmica:** Al comparar la temperatura a nivel del suelo (`2m`) frente a la temperatura en altura (`120m`), el sistema detecta si una capa de aire caliente superior actúa como "tapa", atrapando el polvo tóxico cerca de la superficie.
* **Capas Geográficas Abiertas (GIS):** Mediante consultas espaciales a **OpenStreetMap (Overpass API)** se extraen polígonos y coordenadas de hospitales, escuelas, zonas residenciales y cuerpos de agua en un radio de exclusión (15 km).

---

## 2. ¿Cómo funciona la lógica de la aplicación?

El motor de simulación (`dispersion.py` y `zonas_gis.py`) opera como un flujo de evaluación multicriterio para cada bloque horario de las próximas 24 horas:

1. **Altura Efectiva de la Nube Térmica (H):** Estima cuánto ascenderá la columna de humo según la masa del explosivo y el factor de mitigación física (barreras de arena, contención en búnker y nebulización de agua).
2. **Simulación de Pluma Gaussiana Inclinada:** A diferencia de un gas ligero, las micropartículas de plomo tienen peso y caen por gravedad a una velocidad de sedimentación (\(v_s \approx 0.12\text{ m/s}\)). El algoritmo calcula la huella en el suelo donde la deposición supera el umbral regulatorio (40 μg/ft²) y genera un polígono geográfico rotado según la dirección del viento.
3. **Cruce Espacial (Intersección GIS):** Cruza el polígono de la nube tóxica contra las coordenadas de escuelas, hospitales y centros poblados cercanos.
4. **Semáforo de Decisión (`GO` vs. `NO_GO`):**
   * **`NO_GO` (Rojo — Veto Crítico):** Se activa automáticamente si existe inversión térmica activa, si la nube intersecta con al menos una zona vulnerable, o si el viento está estancado (< 2 m/s) o es excesivamente errático (> 10 m/s).
   * **`GO` (Verde — Ventana Favorable):** Se asigna cuando el viento es laminar, no hay inversión térmica y la trayectoria de dispersión se dirige hacia zonas despobladas.

---

## 3. Estructura del Proyecto

```text
blastsafe-dss/
├── app.py                  # Servidor web y API REST con FastAPI
├── clima.py                # Módulo de ingesta meteorológica (NOAA + respaldo local)
├── dispersion.py           # Motor matemático de Pluma Gaussiana Inclinada
├── zonas_gis.py            # Módulo de cruce espacial con OpenStreetMap (Overpass API)
├── BlastSafe_Colab.ipynb   # Versión interactiva en cuaderno para Google Colab
├── requirements.txt        # Dependencias de Python
└── templates/
    └── index.html          # Interfaz web con mapa satelital, deslizador y exportación
```

---

## 4. Instalación y Ejecución

### Opción A: Aplicación Web Independiente (FastAPI + HTML)
1. Clona el repositorio e instala las dependencias:
   ```bash
   git clone https://github.com
   cd blastsafe-dss
   pip install -r requirements.txt
   ```
2. Inicia el servidor web local:
   ```bash
   uvicorn app:app --reload
   ```
3. Abre tu navegador en `http://127.0.0.1:8000`. Podrás modificar las coordenadas, la masa del explosivo, recorrer las 24 horas con el deslizador y descargar los resultados en **GeoJSON** o **CSV**.

### Opción B: Ejecución en Google Colab
1. Sube `BlastSafe_Colab.ipynb` a Google Colab (o ábrelo directamente desde GitHub).
2. Ejecuta todas las celdas en orden (`Entorno de ejecución > Ejecutar todas`) y utiliza el control deslizante `Hora (+h)`.

---

## 5. Limitaciones Prácticas y Advertencia de Uso

> **Aviso:** Este software es un **prototipo educativo y de demostración técnica**. No debe utilizarse como única herramienta para la toma de decisiones operativas reales en manejo de explosivos o emergencias químicas.

* **Microclima y Topografía Local:** Los modelos Gaussianos asumen terreno relativamente plano y viento uniforme. En la práctica, valles, colinas, bosques y edificaciones pueden desviar las corrientes de aire de forma distinta al pronóstico regional.
* **Resolución de Datos Abiertos:** Los pronósticos horarios gratuitos (NOAA/Open-Meteo) tienen una resolución espacial de varios kilómetros y no capturan micro-ráfagas instantáneas.
* **Inestabilidad Química Inminente:** Cuando un explosivo primario degradado (como la azida de plomo cristalizada) presenta riesgo de detonación espontánea, la seguridad física inmediata obliga a ejecutar la detonación sin poder esperar una ventana meteorológica óptima.
* **Validación Oficial:** En operaciones reales, los protocolos militares y ambientales emplean modelos Lagrangianas 3D de alta resolución (como *HYSPLIT* o *HPAC*) calibrados con radiosondas in situ y sensores de calidad del aire en tiempo real.
