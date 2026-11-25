%%writefile dispersion.py
import math
import numpy as np
from shapely.geometry import Polygon
from shapely.affinity import rotate

def calcular_pluma(lat: float, lon: float, masa_kg: float, ws: float, wd: float):
    u = max(ws, 1.5)
    plomo_mg = (masa_kg * 0.71 * 0.35) * 1e6
    H = 18.5 * ((masa_kg * 0.35) ** 0.25)
    vs = 0.12
    umbral = 0.43

    x_vals = np.linspace(50, 12000, 200)
    y_vals = np.linspace(-2500, 2500, 100)
    X, Y = np.meshgrid(x_vals, y_vals)

    sy = 0.08 * X * ((1 + 0.0001 * X) ** -0.5)
    sz = 0.06 * X * ((1 + 0.0002 * X) ** -0.5)
    H_eff = np.maximum(0.0, H - (vs * X / u))

    dep = ((plomo_mg * vs) / (2 * np.pi * u * sy * sz)) * \
          np.exp(-(Y**2) / (2 * sy**2)) * np.exp(-(H_eff**2) / (2 * sz**2))

    mask = dep >= umbral
    if not np.any(mask):
        return None

    sup, inf = [], []
    for i in range(len(x_vals)):
        col = mask[:, i]
        if np.any(col):
            indices = np.flatnonzero(col)
            sup.append((x_vals[i], y_vals[indices.max()]))
            inf.append((x_vals[i], y_vals[indices.min()]))

    if len(sup) < 3:
        return None

    poly = Polygon(sup + inf[::-1]).buffer(40)
    angulo = 90.0 - ((wd + 180.0) % 360.0)
    poly_rot = rotate(poly, angulo, origin=(0, 0))

    m_lat = 111320.0
    m_lon = 111320.0 * math.cos(math.radians(lat))
    coords = [(lon + x / m_lon, lat + y / m_lat) for x, y in poly_rot.exterior.coords]
    return Polygon(coords)
