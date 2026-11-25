from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from shapely.geometry import mapping
import clima
import dispersion
import zonas_gis

app = FastAPI(title="BlastSafe DSS API")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/simular")
def simular_escenario(lat: float = 40.8065, lon: float = -91.2468, masa_kg: float = 4400.0):
    datos = clima.obtener_pronostico(lat, lon, horas=24)
    zonas_cercanas = zonas_gis.descargar_zonas_cercanas(lat, lon)
    
    resultados_horas = []
    total = len(datos["time"])

    for i in range(total):
        ws10 = datos["wind_speed_10m"][i]
        ws120 = datos["wind_speed_120m"][i]
        wd = datos["wind_direction_120m"][i]
        t2 = datos["temperature_2m"][i]
        t120 = datos["temperature_120m"][i]

        ws = round((ws10 + ws120) / 2, 2)
        inversion = bool(t120 > t2)

        poligono = dispersion.calcular_pluma(lat, lon, masa_kg=masa_kg, ws=ws, wd=wd)
        afectados = zonas_gis.filtrar_afectados(zonas_cercanas, poligono)

        if inversion or len(afectados) > 0 or ws < 2.0 or ws > 10.0:
            estado = "NO_GO"
        else:
            estado = "GO"

        # Limpiar objeto Shapely 'punto' antes de serializar a JSON
        afectados_json = [
            {"nombre": z["nombre"], "tipo": z["tipo"], "lat": z["lat"], "lon": z["lon"]}
            for z in afectados
        ]

        resultados_horas.append({
            "hora": datos["time"][i],
            "estado": estado,
            "viento_ms": ws,
            "direccion_origen": wd,
            "inversion": inversion,
            "afectados": afectados_json,
            "pluma_geojson": mapping(poligono) if poligono else None
        })

    return {
        "origen": {"lat": lat, "lon": lon},
        "horas": resultados_horas
    }
