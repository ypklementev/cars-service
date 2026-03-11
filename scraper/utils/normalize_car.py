from pykakasi import kakasi
from utils.dicts import BRAND_MAP, COLOR_MAP, COLOR_MODIFIERS

kks = kakasi()
kks.setMode("J", "a")
kks.setMode("H", "a")
kks.setMode("K", "a")

converter = kks.getConverter()

def normalize_model(text: str) -> str:

    if not text:
        return None

    text = text.replace("\xa0", " ")
    text = text.strip()

    latin = converter.do(text)

    latin = latin.replace("-", " ")

    latin = " ".join(latin.split())

    return latin.title()

def normalize_brand(brand: str) -> str:

    if not brand:
        return None

    brand = brand.strip()

    return BRAND_MAP.get(brand, brand)


def normalize_color(color):

    if not color:
        return None

    parts = []

    for jp, en in COLOR_MAP.items():
        if jp in color:
            parts.append(en)

    for jp, en in COLOR_MODIFIERS.items():
        if jp in color:
            parts.append(en)

    if parts:
        return " ".join(parts)

    return color


def prepare_car_data(car):

    car["brand"] = normalize_brand(car.get("brand"))

    car["model"] = normalize_model(car.get("model"))

    car["color"] = normalize_color(car.get("color"))

    return car