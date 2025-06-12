import json
import pykakasi
from rapidfuzz import fuzz


# メニュー情報JSONファイルを読み込む
with open("data/menu.json", "r", encoding="utf-8") as f:
    menu_data = json.load(f)

# 「検索用読み文字列」と「表示名」をペアにしたリストを作成
search_list = [(v["search_string"], k) for k, v in menu_data.items()]


# 認識したテキストデータをすべてひらがなに変換する
def to_hira(text):
    kakasi = pykakasi.kakasi()
    text_hira = kakasi.convert(text)
    text_hira = "".join(item["hira"] for item in text_hira)

    print("認識文字：",text, "－＞文字変換:",text_hira)
    return text_hira

# テキストと照合して、最も近いメニューを見つける
def fuzzy_menu_match(text, threshold=50):
    # 条件マッチ率を上げるために取得した音声テキストデータをひらがなに変換
    cnv_text = to_hira(text)

    # search_listは [(search_string, 表示名)] の形式
    results = []
    for search_string, display_name in search_list:
        score = fuzz.ratio(cnv_text, search_string)

        print(search_string,score)
        # マッチ基準スコアを超えるメニューはすべて返す
        if score >= threshold:
            results.append([display_name, score])

    return results