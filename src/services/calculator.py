import math
import datetime
from sgp4.api import Satrec, jday

# --- Константы эллипсоида Земли (стандарт WGS84) ---
WGS84_A = 6378.137            # Большая полуось (экваториальный радиус), км
WGS84_F = 1 / 298.257223563   # Сжатие
WGS84_B = WGS84_A * (1 - WGS84_F) # Малая полуось (полярный радиус), км
WGS84_E2 = 1 - (WGS84_B**2 / WGS84_A**2) # Квадрат эксцентриситета
# ---------------------------------------------------

def teme_to_ecef(x_teme, y_teme, z_teme, jd_day, jd_fraction):
    """Конвертирует координаты TEME -> ECEF с учетом вращения Земли."""
    T = ((jd_day - 2451545.0) + jd_fraction) / 36525.0
    gmst_sec = 67310.54841 + (876600 * 3600 + 8640184.812866) * T + 0.093104 * (T**2) - 6.2e-6 * (T**3)
    gmst_rad = (gmst_sec % 86400.0) * (2 * math.pi / 86400.0)
    
    cos_g = math.cos(gmst_rad)
    sin_g = math.sin(gmst_rad)
    
    x_ecef = x_teme * cos_g + y_teme * sin_g
    y_ecef = -x_teme * sin_g + y_teme * cos_g
    z_ecef = z_teme
    
    return x_ecef, y_ecef, z_ecef

def ecef_to_geodetic(x, y, z):
    """Конвертирует ECEF (X, Y, Z) в Широту, Долготу и Высоту над эллипсоидом WGS84."""
    ep2 = (WGS84_A**2 - WGS84_B**2) / WGS84_B**2
    p = math.sqrt(x**2 + y**2)
    th = math.atan2(WGS84_A * z, WGS84_B * p)
    
    lon = math.atan2(y, x)
    lat = math.atan2((z + ep2 * WGS84_B * math.sin(th)**3), (p - WGS84_E2 * WGS84_A * math.cos(th)**3))
    
    # Радиус кривизны первого вертикала
    N = WGS84_A / math.sqrt(1 - WGS84_E2 * math.sin(lat)**2)
    alt = p / math.cos(lat) - N
    
    return math.degrees(lat), math.degrees(lon), alt

def calculate_speed_kmh(vx, vy, vz):
    """Вычисляет абсолютную скорость в км/ч по вектору скорости (км/с)."""
    v_kms = math.sqrt(vx**2 + vy**2 + vz**2)
    return v_kms * 3600

def get_satellite_data(line1: str, line2: str, calc_time: datetime.datetime = None):
    """Получает полные данные о спутнике на конкретный момент времени."""
    satellite = Satrec.twoline2rv(line1, line2)
    if calc_time is None:
        calc_time = datetime.datetime.utcnow()
        
    jd, fr = jday(calc_time.year, calc_time.month, calc_time.day, calc_time.hour, calc_time.minute, calc_time.second)
    error_code, pos, vel = satellite.sgp4(jd, fr)
    
    if error_code != 0:
        raise ValueError(f"Ошибка SGP4: {error_code}")
        
    # Трансформации
    x_ecef, y_ecef, z_ecef = teme_to_ecef(pos[0], pos[1], pos[2], jd, fr)
    lat, lon, alt = ecef_to_geodetic(x_ecef, y_ecef, z_ecef)
    speed_kmh = calculate_speed_kmh(vel[0], vel[1], vel[2])
    
    return {
        "time": calc_time,
        "latitude": lat,
        "longitude": lon,
        "altitude_km": alt,
        "speed_kmh": speed_kmh,
        "ecef": {"x": x_ecef, "y": y_ecef, "z": z_ecef}
    }

def generate_orbit_path(line1: str, line2: str, start_time: datetime.datetime, points_count: int = 100):
    """Генерирует массив точек для отрисовки трассы на один полный виток орбиты."""
    satellite = Satrec.twoline2rv(line1, line2)
    
    # satellite.no_kozai хранит среднее движение в радианах в минуту
    # Период (минуты) = 2 * Pi / no_kozai
    period_minutes = (2 * math.pi) / satellite.no_kozai
    
    step_minutes = period_minutes / points_count
    path = []
    
    for i in range(points_count + 1):
        t = start_time + datetime.timedelta(minutes=i * step_minutes)
        data = get_satellite_data(line1, line2, t)
        
        path.append({
            "time": t.isoformat(),
            "lat": data["latitude"],
            "lon": data["longitude"],
            "alt": data["altitude_km"]
        })
        
    return path