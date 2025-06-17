import json
import pykakasi
from rapidfuzz import fuzz

# メニュー情報の読み込み
with open("backend/data/menu.json", "r", encoding="utf-8") as f:
    menu_data = json.load(f)

search_list = [(v["search_string"], k) for k, v in menu_data.items()]

def to_hira(text: str) -> str:
    kakasi = pykakasi.kakasi()
    text_hira = kakasi.convert(text)
    return "".join(item["hira"] for item in text_hira)

def fuzzy_menu_match(text: str, threshold: int = 50):
    cnv_text = to_hira(text)
    results = []
    for search_string, display_name in search_list:
        score = fuzz.ratio(cnv_text, search_string)
        if score >= threshold:
            results.append((display_name, score))
    return results
