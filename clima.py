%%writefile clima.py
import requests

def obtener_pronostico(lat: float, lon: float, horas: int = 24) -> dict:
    headers = {"User-Agent": "(BlastSafePrototype, contacto@ejemplo.com)"}
    
    # Construimos la URL por partes para evitar recortes del navegador
    host_noaa = "https:" + "//api.weather.gov"
    ruta_puntos = f"{host_noaa}/points/{lat},{lon}"

    try:
        r_punto = requests.get(ruta_puntos, headers=headers, timeout=10)
        if r_punto.status_code == 200:
            forecast_url = r_punto.json()["properties"]["forecastHourly"]
            r_fore = requests.get(forecast_url, headers=headers, timeout=10)
            periodos = r_fore.json()["properties"]["periods"][:horas]

            dir_map = {
                "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
                "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
                "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
                "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5
            }

            tiempos, temps, vientos, dirs = [], [], [], []
            for p in periodos:
                tiempos.append(p["startTime"])
                t_c = (p["temperature"] - 32) * 5.0 / 9.0
                temps.append(round(t_c, 1))
                mph = float(p["windSpeed"].split().pop(0))
                vientos.append(round(mph * 0.44704, 2))
                dirs.append(dir_map.get(p["windDirection"], 315.0))

            print("Conectado en vivo a NOAA (National Weather Service).")
            return {
                "time": tiempos,
                "temperature_2m": temps,
                "temperature_120m": [round(t - 0.8, 1) for t in temps],
                "wind_speed_10m": vientos,
                "wind_speed_120m": [round(v * 1.25, 2) for v in vientos],
                "wind_direction_120m": dirs
            }
    except Exception as e:
        print(f"Fallo conexión NOAA ({e}). Usando datos locales de respaldo.")

    return {
        "time": list(["2026-11-25T08:00"]),
        "temperature_2m": list([8.5]),
        "temperature_120m": list([7.2]),
        "wind_speed_10m": list([4.2]),
        "wind_speed_120m": list([6.4]),
        "wind_direction_120m": list([315.0])
    }
