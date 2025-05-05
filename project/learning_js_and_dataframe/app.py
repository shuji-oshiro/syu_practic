# app.py

import json
import pandas as pd
from io import StringIO
from flask import Flask, render_template, jsonify, request

DATA_PAHT = "cours_info.json"
SUM_COLUMN = {"当年純売数量":"sum","当年純売金額":"sum","当年納品金額":"sum","当年納品数量":"sum","当年返品金額":"sum", "当年返品数量":"sum"}
SORT_COLUMN = ["当年返品金額","当年返品数量","当年純売金額","当年純売数量","当年納品金額","当年納品数量"]

app = Flask(__name__)

df_sales = None # coursesはグローバル変数として定義

@app.route("/")
def index():
    global df_sales
    try:        
        #return render_template("table.html", table=df_gp.to_html(classes='table table-bordered', index=False))
        return render_template("index.html")
   
    except Exception as e:
        print(f"Error: {e}")
        return "cours_info.json file not found.", 404


@app.route("/api/sales", methods=['POST'])
def set_salesdata():
    global df_sales
    
    try:
        file = request.files['file']

        df = pd.read_csv(StringIO(file.read().decode('cp932')),header=1)
                
        df_sales = pd.DataFrame(json.load(open(DATA_PAHT, encoding="utf-8")))

        # course_stors_code列を展開
        df_sales = df_sales.explode('course_stors_code')
        df_sales["course_stors_code"] = df_sales["course_stors_code"].astype(int)

        # コース別に店舗コードを関連付ける
        df_sales =pd.merge(df_sales, df, left_on='course_stors_code', right_on='店舗コード', how='left')

        # JSON形式でデータを返す
        return jsonify({"message": "データ読み込みに成功しました"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "データ読み込みに失敗しました"}), 500


@app.route("/api/sales", methods=['GET'])
def get_salesdata():
    global df_sales
    
    try:
        # コース名と店舗コードをキーにして、コース毎の集計を行う
        df_gp = df_sales.groupby(['course_name','course_charge'], as_index=False).agg(SUM_COLUMN)

        # JSON形式でデータを返す
        return jsonify(json.loads(df_gp.to_json(orient="records", force_ascii=False)))
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "データ取得に失敗しました"}), 500


@app.route("/api/stores",methods=['GET'])
def get_stores():

    global df_sales
    try:
        # クエリパラメータからコース名を取得
        key = request.args.get("course_name", default=None)

        if not key:
            return jsonify({"error": "course_name is required"}), 400
        
        # コース名をキーにして、コース情報を取得
        df_select_courses = df_sales[df_sales["course_name"] == key]
        # コースコードをキーにして、店舗毎の集計を行う
        df_select_courses = df_select_courses.groupby(['course_stors_code',"店舗名"], as_index=False).agg(SUM_COLUMN)

        df_select_courses["key_and_name"] = df_select_courses["course_stors_code"].astype(str) + ":" + df_select_courses["店舗名"].astype(str)
       
        # 店舗情報をJSON形式で返す　*array形式に変換できるloadsで返さないとエラーが発生する
        df_select_courses = json.loads(df_select_courses.to_json(orient="records", force_ascii=False))

        return jsonify(df_select_courses)
    
    except Exception as e:
        print(f"Error: {e}")
        return "cours_info.json file not found.", 404


@app.route("/api/items",methods=['GET'])
def get_items():

    global df_sales
    try:
        # クエリパラメータからコース名、店舗名を取得
        key = request.args.get("store_code", default=None)

        # コース名と店舗コードをキーにして、店舗p情報を絞り込む
        df_select_courses = df_sales[
            (df_sales["course_stors_code"] == int(key))
        ]
        # 商品コードをキーにして、商品毎の集計を行う
        df_select_courses = df_select_courses.groupby(['商品コード',"商品名"], as_index=False).agg(SUM_COLUMN)
        
        df_select_courses["key_and_name"] = df_select_courses["商品コード"].astype(str) + ":" + df_select_courses["商品名"].astype(str)
       
        # 店舗情報をJSON形式で返す　*array形式に変換できるloadsで返さないとエラーが発生する
        df_select_courses = json.loads(df_select_courses.to_json(orient="records", force_ascii=False))

        return jsonify(df_select_courses)
    except Exception as e:
        print(f"Error: {e}")
        return "cours_info.json file not found.", 404
    

@app.route("/api/courses",methods=['GET'])
def get_courses():
    js_courses = json.load(open(DATA_PAHT, encoding="utf-8"))
    return jsonify(js_courses)


@app.route("/api/courses", methods=['PATCH'])
def add_store():
    try:
        data = request.get_json()
        with open("cours_info.json", "r", encoding="utf-8") as f:
            courses = json.load(f)
        
        # コースを検索して店舗を追加
        for course in courses:
            if course["course_name"] == data["course_name"]:
                course["course_stors_code"].append(data["store_code"])
                course["course_stors_name"].append(data["store_name"])
                break
        
        # ファイルに保存
        with open("cours_info.json", "w", encoding="utf-8") as f:
            json.dump(courses, f, ensure_ascii=False, indent=4)
        
        return jsonify({"message": "店舗が追加されました"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "店舗の追加に失敗しました"}), 500
    

@app.route("/api/courses", methods=['DELETE'])
def delete_store():
    try:
        data = request.get_json()
        with open("cours_info.json", "r", encoding="utf-8") as f:
            courses = json.load(f)
        
        # コースを検索して店舗を削除
        for course in courses:
            if course["course_name"] == data["course_name"]:
                index = course["course_stors_code"].index(data["store_code"])
                course["course_stors_code"].pop(index)
                course["course_stors_name"].pop(index)
                break
        
        # ファイルに保存
        with open("cours_info.json", "w", encoding="utf-8") as f:
            json.dump(courses, f, ensure_ascii=False, indent=4)
        
        return jsonify({"message": "店舗が削除されました"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "店舗の削除に失敗しました"}), 500


@app.route("/api/courses", methods=['PUT'])
def update_courses():
    try:

        # ファイルを直接取得
        file = request.get_data()
        
        # バイト列を文字列にデコード
        csv_data = file.decode('utf-8')
        
        # CSVデータを行に分割
        rows = csv_data.strip().split('\n')
        
        # コース情報を格納する辞書
        courses_dict = {}
        
        # CSVデータから店舗情報を収集
        for row in rows[2:]:  # ヘッダー2行をスキップ
            cols = row.strip().split(',')
            course_name = cols[0]  # コース名
            charge_name = cols[1]  # 担当者名
            store_code = int(cols[2])  # 店舗コード
            store_name = cols[3]  # 店舗名
            
            # コース名と担当者名をキーとして使用
            course_key = (course_name, charge_name)
            
            if course_key not in courses_dict:
                courses_dict[course_key] = {
                    "course_name": course_name,
                    "course_charge": charge_name,
                    "course_stors_code": [],
                    "course_stors_name": []
                }
            
            courses_dict[course_key]["course_stors_code"].append(store_code)
            courses_dict[course_key]["course_stors_name"].append(store_name)
        
        # 辞書の値のリストを作成
        new_courses = list(courses_dict.values())
        
        # ファイルに保存
        with open("cours_info.json", "w", encoding="utf-8") as f:
            json.dump(new_courses, f, ensure_ascii=False, indent=4)
        
        return jsonify({"message": "コース情報が更新されました"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "コース情報の更新に失敗しました"}), 500


if __name__ == "__main__":
    app.run(debug=True)
