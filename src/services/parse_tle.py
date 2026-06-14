import datetime
from src.models import Satellite, TLE_Data

def parse_epoch(epoch_year_str, epoch_day_str):
    """Преобразует год и дробный день года в объект datetime."""
    year = int(epoch_year_str)
    full_year = 2000 + year if year < 57 else 1900 + year

    start_of_year = datetime.datetime(full_year, 1, 1)
    return start_of_year + datetime.timedelta(days=float(epoch_day_str) - 1)

def parse_bstar(bstar_str):
    """Преобразует строку BSTAR в float математическим путем."""
    # Стандартный BSTAR из TLE всегда имеет длину 8 символов (например, ' 56564-3' или '-11606-4')
    if len(bstar_str) == 8:
        mantissa = bstar_str[:6]   # Например, ' 56564' или '-11606'
        exponent = bstar_str[6:]   # Например, '-3' или '-4'
    else:
        # Защита на случай, если строки пришли уже обрезанными
        bstar_str = bstar_str.strip()
        if not bstar_str or bstar_str == '0':
            return 0.0
        mantissa = bstar_str[:-2]
        exponent = bstar_str[-2:]

    try:
        mant_val = float(mantissa)
        # Если в экспоненте пробел (например, ' 2' вместо '+2'), заменяем его на плюс
        exp_val = int(exponent.replace(' ', '+'))
        
        # В TLE точка всегда предполагается перед первыми цифрами мантиссы.
        # Деление мантиссы на 1e5 (100 000) как раз сдвигает точку в начало (0.56564)
        return (mant_val / 1e5) * (10 ** exp_val)
    except (ValueError, IndexError):
        return 0.0

def parse_tle_to_dict(line1, line2):
    """Извлекает данные из двух строк TLE строго по позициям символов."""
    
    # Парсим Строку 1
    norad_id = line1[2:7].strip()
    intl_designator = line1[9:17].strip()
    epoch_year = line1[18:20]
    epoch_day = line1[20:32]
    bstar = line1[53:61] # Передаем полные 8 символов без .strip()
    
    # Парсим Строку 2
    inclination = line2[8:16].strip()
    raan = line2[17:25].strip()
    eccentricity = "0." + line2[26:33].strip()
    arg_perigee = line2[34:42].strip()
    mean_anomaly = line2[43:51].strip()
    mean_motion = line2[52:63].strip()
    rev_num = line2[63:68].strip()

    return {
        "norad_id": norad_id,
        "intl_designator": intl_designator,
        "epoch": parse_epoch(epoch_year, epoch_day),
        "bstar": parse_bstar(bstar),
        "inclination": float(inclination),
        "raan": float(raan),
        "eccentricity": float(eccentricity),
        "arg_perigee": float(arg_perigee),
        "mean_anomaly": float(mean_anomaly),
        "mean_motion": float(mean_motion),
        "rev_num_at_epoch": int(rev_num),
        "line1": str(line1),
        "line2": str(line2)
    }

def save_tle_to_db(session, parsed_data, satellite_name="UNKNOWN"):
    """Сохраняет распарсенные данные TLE в базу данных."""
    
    # 1. Проверяем наличие спутника в базе
    satellite = session.query(Satellite).filter_by(norad_id=parsed_data['norad_id']).first()
    
    if not satellite:
        # Добавили обязательное поле name, чтобы избежать ошибки базы данных
        satellite = Satellite(
            norad_id=parsed_data['norad_id'],
            name=satellite_name,
            intl_designator=parsed_data['intl_designator']
        )
        session.add(satellite)
        session.commit()
        print(f"Добавлен новый спутник: {satellite.norad_id} ({satellite.name})")

    # 2. Проверяем, нет ли уже точно такой же эпохи
    existing_tle = session.query(TLE_Data).filter_by(
        satellite_id=parsed_data['norad_id'], 
        epoch=parsed_data['epoch']
    ).first()

    if existing_tle:
        print(f"Данные TLE для спутника {parsed_data['norad_id']} на эпоху {parsed_data['epoch']} уже существуют.")
        return

    # 3. Создаем запись TLE
    new_tle = TLE_Data(
        satellite_id=parsed_data['norad_id'],
        epoch=parsed_data['epoch'],
        bstar=parsed_data['bstar'],
        inclination=parsed_data['inclination'],
        raan=parsed_data['raan'],
        eccentricity=parsed_data['eccentricity'],
        arg_perigee=parsed_data['arg_perigee'],
        mean_anomaly=parsed_data['mean_anomaly'],
        mean_motion=parsed_data['mean_motion'],
        rev_num_at_epoch=parsed_data['rev_num_at_epoch'],
        line1=parsed_data['line1'],
        line2=parsed_data['line2']
    )
    
    session.add(new_tle)
    session.commit()
    print(f"Новые элементы TLE успешно сохранены для спутника {satellite.norad_id}.")