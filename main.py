import importlib
import folium
from shapely.geometry import mapping
from IPython.display import HTML
import clima
import dispersion
import zonas_gis

# Recargar módulos por si editaste alguno
importlib.reload(clima)
importlib.reload(dispersion)
importlib.reload(zonas_gis)

# 1. Coordenadas de la Planta de Municiones de Iowa (IAAAP)
LAT, LON = 40.8065, -91.2468

# 2. Obtener pronóstico en vivo (NOAA) y zonas vulnerables (OpenStreetMap)
datos = clima.obtener_pronostico(LAT, LON, horas=24)
zonas_cercanas = zonas_gis.descargar_zonas_cercanas(LAT, LON)

# 3. Extraer variables de la hora actual (índice 0)
hora_actual = next(iter(datos["time"]))
ws10 = next(iter(datos["wind_speed_10m"]))
ws120 = next(iter(datos["wind_speed_120m"]))
wd = next(iter(datos["wind_direction_120m"]))
t2 = next(iter(datos["temperature_2m"]))
t120 = next(iter(datos["temperature_120m"]))

ws = (ws10 + ws120) / 2
inversion = t120 > t2

# 4. Calcular polígono de pluma de plomo y cruzar con zonas sensibles
poligono = dispersion.calcular_pluma(LAT, LON, masa_kg=4400, ws=ws, wd=wd)
zonas_afectadas = zonas_gis.filtrar_afectados(zonas_cercanas, poligono)

print(f"Hora: {hora_actual} | Viento: {ws:.1f} m/s (Origen: {wd}°) | Inversión térmica: {inversion}")
print(f"Zonas vulnerables dentro de la nube: {len(zonas_afectadas)}")
for z in zonas_afectadas:
    print(f"  -> ALERTA: {z['nombre']} ({z['tipo']})")

# 5. Renderizar mapa satelital limpio (Esri World Imagery)
mapa = folium.Map(location=[LAT, LON], zoom_start=12, tiles="Esri.WorldImagery")

# Marcador del punto de detonación
folium.Marker(
    [LAT, LON],
    popup="Punto de Detonación (IAAAP)",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(mapa)

# Dibujar el cono de dispersión de plomo
if poligono:
    folium.GeoJson(
        mapping(poligono),
        style_function=lambda x: {
            "fillColor": "orange",
            "color": "red",
            "weight": 2,
            "fillOpacity": 0.4
        }
    ).add_to(mapa)

# Dibujar marcadores morados para escuelas, hospitales o pueblos afectados
for z in zonas_afectadas:
    folium.Marker(
        [z["lat"], z["lon"]],
        popup=f"{z['nombre']} ({z['tipo']})",
        icon=folium.Icon(color="purple", icon="exclamation-sign")
    ).add_to(mapa)

HTML(mapa._repr_html_())
