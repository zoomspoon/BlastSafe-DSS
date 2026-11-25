import requests
from shapely.geometry import Point

def descargar_zonas_cercanas(lat: float, lon: float) -> list:
    """Descarga una sola vez hospitales, escuelas y pueblos en 15 km a la redonda."""
    servidores = [
        "https:" + "//overpass.kumi.systems/api/interpreter",
        "https:" + "//lz4.overpass-api.de/api/interpreter",
        "https:" + "//overpass-api.de/api/interpreter"
    ]
    query = f"""
    [out:json][timeout:15];
    (
      node["amenity"~"hospital|clinic|school|university"](around:15000,{lat},{lon});
      way["amenity"~"hospital|clinic|school|university"](around:15000,{lat},{lon});
      node["place"~"town|village|city"](around:15000,{lat},{lon});
    );
    out center;
    """
    headers = {"User-Agent": "BlastSafePrototype/1.0"}
    zonas = []

    for url in servidores:
        try:
            resp = requests.post(url, data={"data": query}, headers=headers, timeout=12)
            if resp.status_code == 200:
                for el in resp.json().get("elements", []):
                    tags = el.get("tags", {})
                    p_lat = el.get("lat") or el.get("center", {}).get("lat")
                    p_lon = el.get("lon") or el.get("center", {}).get("lon")
                    if p_lat and p_lon:
                        zonas.append({
                            "nombre": tags.get("name", "Zona sin nombre"),
                            "tipo": tags.get("amenity") or tags.get("place") or "zona",
                            "lat": p_lat,
                            "lon": p_lon,
                            "punto": Point(p_lon, p_lat)
                        })
                print(f"Cargadas {len(zonas)} zonas sensibles desde OpenStreetMap.")
                return zonas
        except Exception:
            continue

    print("Aviso: Servidores OSM ocupados, continuando sin capa GIS externa.")
    return zonas

def filtrar_afectados(zonas_cercanas: list, poligono_pluma) -> list:
    if poligono_pluma is None:
        return []
    return [z for z in zonas_cercanas if poligono_pluma.contains(z["punto"])]
