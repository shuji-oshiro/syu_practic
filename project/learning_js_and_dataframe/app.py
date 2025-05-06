# app.py

import json
import pandas as pd
from io import StringIO
from flask import Flask, render_template, jsonify, request

DATA_PAHT = "cours_info.json"

SUM_COLUMN = {
    "net_sales_quantity":"sum",
    "net_sales_amount":"sum",
    "delivery_amount":"sum",
    "delivery_quantity":"sum",
    "return_amount":"sum",
    "return_quantity":"sum"
}

USE_COLUMNS = {
    "得意先コード": "customer_code",
    "得意先名": "customer_name", 
    "商品コード": "product_code",
    "商品名": "product_name",
    "店舗コード": "store_code",
    "店舗名": "store_name",
    "当年返品金額": "return_amount",
    "当年返品数量": "return_quantity",
    "当年純売金額": "net_sales_amount", 
    "当年純売数量": "net_sales_quantity",
    "当年納品金額": "delivery_amount",
    "当年納品数量": "delivery_quantity"
}

app = Flask(__name__)

df_sales = None # salesはグローバル変数として定義
df_courses = None # coursesはグローバル変数として定義

@app.route("/")
def index():
    global df_courses

    try:
        df_temp = pd.DataFrame(json.load(open(DATA_PAHT, encoding="utf-8")))

        # course_stors_code列を展開
        df_courses = df_temp.explode(['store_code'])
        df_courses["store_code"] = df_courses["store_code"].astype(int)

        return render_template("index.html")
   
    except Exception as e:
        print(f"Error: {e}")
        return "cours_info.json コース情報の読み込みに失敗しました。", 404


@app.route("/api/sales", methods=['POST'])
def set_salesdata():
    global df_sales
    
    try:
        file = request.files['file']
        df_sales = pd.read_csv(StringIO(file.read().decode('cp932')),header=1)
        
        # USE_COLUMNに含まれていないカラムを抽出
        missing_columns = [col for col in USE_COLUMNS.keys() if col not in df_sales.columns]
        if missing_columns:
            return jsonify({
                "error": f"集計に必要な項目値が含まれていません：{', '.join(missing_columns)}"
            }), 422
            
        df_sales = df_sales.rename(columns=USE_COLUMNS)[list(USE_COLUMNS.values())]

        # JSON形式でデータを返す
        return jsonify({"message": f"データ読み込みに成功しました。ファイル名：{file.filename}"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"データ読み込みに失敗しました。{str(e)}"}), 500


@app.route("/api/sales", methods=['GET'])
def get_salesdata():
    global df_sales
    

    bpname_list=[112000,104000,103000] #

    try:
        # クエリパラメータからコース名、店舗名を取得
        item_code = request.args.get("item_code", default=None)

        df_bp = df_sales[df_sales["customer_code"].isin(bpname_list)]
        
        if item_code:
            df_bp = df_bp[df_bp["product_code"] == int(item_code)]

        
        # 得意先コードと得意先名をキーにして、得意先毎の集計を行う
        df_bp = df_bp.groupby(['customer_code','customer_name'], as_index=False).agg(SUM_COLUMN)

        # JSON形式でデータを返す
        return jsonify(json.loads(df_bp.to_json(orient="records", force_ascii=False))), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"売上データ取得に失敗しました。{str(e)}"}), 500


@app.route("/api/courses", methods=['GET'])
def get_course():
    global df_sales
    global df_courses
    
    try:

        # コース別に店舗コードを関連付ける
        df_courses_sales =pd.merge(df_courses,df_sales, left_on='store_code', right_on='store_code', how='left')

        # コース名と店舗コードをキーにして、コース毎の集計を行う
        df_courses_sales = df_courses_sales.groupby(['course_name','course_charge'], as_index=False).agg(SUM_COLUMN)

        # JSON形式でデータを返す
        return jsonify(json.loads(df_courses_sales.to_json(orient="records", force_ascii=False)))
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"コース売上データ取得に失敗しました。{str(e)}"}), 500


@app.route("/api/stores",methods=['GET'])
def get_stores():

    global df_sales
    global df_courses
    try:
        # クエリパラメータからコース名またはBPコードを取得
        course_name = request.args.get("course_name", default=None)
        bpcode = request.args.get("bpcode", default=None, type=int)
        item_code = request.args.get("item_code", default=None)


        if not course_name and not bpcode:
            return jsonify({"error": "course_name or bpcode is required"}), 400
        
        # コース名をキーにして、コース情報を取得
        if course_name:
            df_select_data = df_courses[df_courses["course_name"] == course_name]
            # コースに該当する店舗のデータを取得
            df_select_data_sales =pd.merge(df_select_data, df_sales, left_on='store_code', right_on='store_code', how='left')

        elif bpcode :
            # 得意先に該当する店舗のデータを取得
            df_select_data_sales = df_sales[df_sales["customer_code"] == bpcode]
            
        elif item_code:
            # 商品に該当する店舗のデータを取得
            df_select_data_sales = df_sales[df_sales["product_code"] == item_code]
            

        # 店舗コードと店舗名をキーにして、店舗毎の集計を行う
        df_select_data_sales = df_select_data_sales.groupby(['store_code',"store_name"], as_index=False).agg(SUM_COLUMN)

        # 店舗コードと店舗名を結合して、表示用キーとして使用
        df_select_data_sales["key_and_name"] = df_select_data_sales["store_code"].astype(str) + ":" + df_select_data_sales["store_name"].astype(str)
       
        # 店舗情報をJSON形式で返す　*array形式に変換できるloadsで返さないとエラーが発生する
        df_select_data_sales = json.loads(df_select_data_sales.to_json(orient="records", force_ascii=False))

        return jsonify(df_select_data_sales)
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"店舗売上データ取得に失敗しました。{str(e)}"}), 500


@app.route("/api/items",methods=['GET'])
def get_items():

    global df_sales
    try:
        # クエリパラメータからコース名、店舗名を取得
        key = request.args.get("store_code", default=None)

        if key:
            df_select_store = df_sales[df_sales["store_code"] == int(key)]

        # 商品コードをキーにして、商品毎の集計を行う
        df_select_store = df_select_store.groupby(['product_code',"product_name"], as_index=False).agg(SUM_COLUMN)
        
        df_select_store["key_and_name"] = df_select_store["product_code"].astype(str) + ":" + df_select_store["product_name"].astype(str)
       
        # 店舗情報をJSON形式で返す　*array形式に変換できるloadsで返さないとエラーが発生する
        df_select_store = json.loads(df_select_store.to_json(orient="records", force_ascii=False))

        return jsonify(df_select_store)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"商品売上データ取得に失敗しました。{str(e)}"}), 500
    


@app.route("/api/coursesinfo", methods=['PUT'])
def update_coursesinfo():
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
            
            # コース名と担当者名をキーとして使用
            course_key = (course_name, charge_name)
            
            if course_key not in courses_dict:
                courses_dict[course_key] = {
                    "course_name": course_name,
                    "course_charge": charge_name,
                    "store_code": []
                }
            
            courses_dict[course_key]["store_code"].append(store_code)
        # 辞書の値のリストを作成
        new_courses = list(courses_dict.values())
        
        # ファイルに保存
        with open("cours_info.json", "w", encoding="utf-8") as f:
            json.dump(new_courses, f, ensure_ascii=False, indent=4)
        
        df_temp = pd.DataFrame(json.load(open(DATA_PAHT, encoding="utf-8")))

        # course_stors_code列を展開
        df_courses = df_temp.explode(['store_code'])
        df_courses["store_code"] = df_courses["store_code"].astype(int)

        return jsonify({"message": "コース情報が更新されました"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "コース情報の更新に失敗しました"}), 500


if __name__ == "__main__":
    app.run(debug=True)
