import importlib
import folium
import ipywidgets as widgets
from itertools import islice
from shapely.geometry import mapping
from IPython.display import display, HTML, clear_output
import clima
import dispersion
import zonas_gis

# Recargar módulos por si editaste alguno
importlib.reload(clima)
importlib.reload(dispersion)
importlib.reload(zonas_gis)

# 1. Coordenadas de la Planta de Municiones de Iowa (IAAAP)
LAT, LON = 40.8065, -91.2468

# 2. Descargar pronóstico (24h) y zonas GIS una sola vez al iniciar
datos = clima.obtener_pronostico(LAT, LON, horas=24)
zonas_cercanas = zonas_gis.descargar_zonas_cercanas(LAT, LON)
total_horas = len(datos["time"])

salida_mapa = widgets.Output()

def actualizar_simulacion(indice_hora):
    with salida_mapa:
        clear_output(wait=True)

        # Extraer variables de la hora seleccionada
        hora_str = next(islice(datos["time"], indice_hora, None))
        ws10 = next(islice(datos["wind_speed_10m"], indice_hora, None))
        ws120 = next(islice(datos["wind_speed_120m"], indice_hora, None))
        wd = next(islice(datos["wind_direction_120m"], indice_hora, None))
        t2 = next(islice(datos["temperature_2m"], indice_hora, None))
        t120 = next(islice(datos["temperature_120m"], indice_hora, None))

        ws = (ws10 + ws120) / 2
        inversion = t120 > t2

        # Calcular nube y cruzar con escuelas/hospitales/pueblos
        poligono = dispersion.calcular_pluma(LAT, LON, masa_kg=4400, ws=ws, wd=wd)
        zonas_afectadas = zonas_gis.filtrar_afectados(zonas_cercanas, poligono)

        # Evaluar semáforo de seguridad
        if inversion or len(zonas_afectadas) > 0 or ws < 2.0 or ws > 10.0:
            estado = "NO_GO (ALTO RIESGO)"
            color_cono = "red"
        else:
            estado = "GO (VENTANA SEGURA)"
            color_cono = "green"

        print(f"=== HORA: {hora_str} | ESTADO: {estado} ===")
        print(f"Viento: {ws:.1f} m/s (Origen: {wd}°) | Inversión térmica: {inversion}")
        print(f"Zonas vulnerables dentro de la nube: {len(zonas_afectadas)}")
        for z in zonas_afectadas:
            print(f"  -> ALERTA: {z['nombre']} ({z['tipo']})")

        # Renderizar mapa satelital limpio
        mapa = folium.Map(location=[LAT, LON], zoom_start=11, tiles="Esri.WorldImagery")

        folium.Marker(
            [LAT, LON],
            popup="Punto de Detonación (IAAAP)",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(mapa)

        if poligono:
            folium.GeoJson(
                mapping(poligono),
                style_function=lambda x, c=color_cono: {
                    "fillColor": c,
                    "color": c,
                    "weight": 2,
                    "fillOpacity": 0.45
                }
            ).add_to(mapa)

        for z in zonas_afectadas:
            folium.Marker(
                [z["lat"], z["lon"]],
                popup=f"{z['nombre']} ({z['tipo']})",
                icon=folium.Icon(color="purple", icon="exclamation-sign")
            ).add_to(mapa)

        display(HTML(mapa._repr_html_()))

# Crear control deslizante de 0 a 23 horas
slider = widgets.IntSlider(
    value=0,
    min=0,
    max=max(0, total_horas - 1),
    step=1,
    description="Hora (+h):",
    continuous_update=False,
    layout=widgets.Layout(width="65%")
)

widgets.interact(actualizar_simulacion, indice_hora=slider)
display(salida_mapa)
