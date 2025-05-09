# app.py

import json
import pandas as pd
from io import StringIO
from flask import Flask, render_template, jsonify, request

DATA_PAHT = "cours_info.json"
DISP_CUSTOMER_CODE_PATH = "disp_customer_code.csv"

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
USE_COLUMNS_TYPES = {
    "customer_code": str,
    "product_code": str,
    "product_name": str,
    "store_code": str,
    "store_name": str,
    "return_amount": int,
    "return_quantity": int,
    "net_sales_amount": int, 
    "net_sales_quantity": int,
    "delivery_amount": int,
    "delivery_quantity": int
}

USE_COLUMNS_DISP_CUSTOMER_CODE = {
    "customer_code": str,
    "customer_name": str
}

USE_COURSE_CODE_TYPES = {
    "course_name": str,
    "course_charge": str,
    "store_code": str
}

app = Flask(__name__)


df_sales = None # salesはグローバル変数として定義
df_courses = None # coursesはグローバル変数として定義

@app.route('/api/check_data', methods=['GET'])
def check_data():
    """
    グローバル変数の値の有無をチェックするエンドポイント
    """
    global df_sales, df_courses

    if df_sales is not None and df_courses is not None:
        return jsonify({"message": "データが存在します"}), 200
    else:
        return jsonify({"message": "データが存在しません"}), 404


@app.after_request
def add_header(response):
    """
    ブラウザを閉じた時にキャッシュをクリアし、グローバル変数を初期化するためのヘッダーを追加
    """
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/api/clear', methods=['POST'])
def clear_data():
    """
    グローバル変数を初期化するエンドポイント
    """
    global df_sales, df_courses
    df_sales = None
    df_courses = None
    
    return jsonify({"message": "データがクリアされました"}), 200


@app.route("/")
def index():
    global df_courses

    try:
        df_temp = pd.DataFrame(json.load(open(DATA_PAHT, encoding="utf-8")))

        # course_stors_code列を展開
        df_courses = df_temp.explode(['store_code'])
        df_courses = df_courses.astype(USE_COURSE_CODE_TYPES)

        return render_template("index.html")
   
    except Exception as e:
        print(f"Error: {e}")
        return "cours_info.json コース情報の読み込みに失敗しました。", 404


@app.route("/api/sales", methods=['POST'])
def set_salesdata():
    global df_sales
    
    try:
        file = request.files['file']

        df_customer = pd.read_csv(DISP_CUSTOMER_CODE_PATH)
        df_customer = df_customer.astype(USE_COLUMNS_DISP_CUSTOMER_CODE)

        df_temp = pd.read_csv(StringIO(file.read().decode('cp932')),header=1)

        # USE_COLUMNに含まれていないカラムを抽出
        missing_columns = [col for col in USE_COLUMNS.keys() if col not in df_temp.columns]
        if missing_columns:
            return jsonify({
                "error": f"集計に必要な項目値が含まれていません：{', '.join(missing_columns)}"
            }), 422        
        
        df_temp = df_temp.rename(columns=USE_COLUMNS)[list(USE_COLUMNS.values())]     
        df_temp = df_temp.astype(USE_COLUMNS_TYPES)

        temp2 = pd.merge(df_customer, df_temp, left_on='customer_code', right_on='customer_code', how='left')
        temp3 = df_temp[~df_temp['customer_code'].isin(df_customer['customer_code'])]
        temp3["customer_code"] = "999999"
        temp3['customer_name'] = 'その他'
        temp3['store_code'] = '999999'
        temp3['store_name'] = 'その他'

        df_sales = pd.concat([temp2, temp3])

        # JSON形式でデータを返す
        return jsonify({"message": f"データ読み込みに成功しました。ファイル名：{file.filename}"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"データ読み込みに失敗しました。{str(e)}"}), 500


@app.route("/api/sales", methods=['GET'])
def get_salesdata():
    global df_sales
    
    try:
        df_select_data = df_sales
        
        # クエリパラメータからコース名、店舗名を取得
        item_code = request.args.get("item_code", default=None)
        if item_code:
            df_select_data = df_select_data[df_select_data["product_code"] == item_code]

        
        # 得意先コードと得意先名をキーにして、得意先毎の集計を行う
        df_select_data["store_count"] = df_select_data["store_code"]
        df_select_data = df_select_data.groupby(['customer_name'], as_index=False).agg({
            **SUM_COLUMN,
            'customer_code': lambda x: ','.join(map(str, x.unique())),
            'store_count': lambda x: len(x.unique())
        })

        # JSON形式でデータを返す
        return jsonify(json.loads(df_select_data.to_json(orient="records", force_ascii=False))), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"売上データ取得に失敗しました。{str(e)}"}), 500


@app.route("/api/courses", methods=['GET'])
def get_course():
    global df_sales
    global df_courses
    
    try:    
        # コースに該当する店舗のデータを取得
        df_select_data =pd.merge(df_courses, df_sales, left_on='store_code', right_on='store_code', how='left')

        
        # コース名と店舗コードをキーにして、コース毎の集計を行う
        df_select_data = df_select_data.groupby(['course_name','course_charge'], as_index=False).agg(SUM_COLUMN)

        # JSON形式でデータを返す
        return jsonify(json.loads(df_select_data.to_json(orient="records", force_ascii=False)))
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"コース売上データ取得に失敗しました。{str(e)}"}), 500


@app.route("/api/stores",methods=['GET'])
def get_stores():

    global df_sales
    global df_courses
    try:
        # クエリパラメータからコース名またはBPコードを取得
        bpcode = request.args.get("bpcode", default=None)

        if bpcode:
            bpcode = [code for code in bpcode.split(',')]

        item_code = request.args.get("item_code", default=None)
        course_name = request.args.get("course_name", default=None)


        if not course_name and not bpcode and not item_code:
            return jsonify({"error": "course_name or bpcode or item_code is required"}), 400
        
        df_select_data = df_sales
        if bpcode:
            df_select_data = df_select_data[df_select_data["customer_code"].isin(bpcode)]

        if item_code:
            df_select_data = df_select_data[df_select_data["product_code"] == item_code]

        if course_name:
            l = df_courses[df_courses["course_name"] == course_name]["store_code"].tolist()
            df_select_data = df_select_data[df_select_data["store_code"].isin(l)]

         
        # 店舗コードと店舗名をキーにして、店舗毎の集計を行う
        #df_select_data = df_select_data.groupby(['store_code',"store_name"], as_index=False).agg(SUM_COLUMN)

        
        # 得意先コードと得意先名をキーにして、得意先毎の集計を行う
        df_select_data = df_select_data.groupby(['store_name'], as_index=False).agg({
            **SUM_COLUMN,
            'store_code': lambda x: ','.join(map(str, x.unique()))
        })


        # 店舗コードと店舗名を結合して、表示用キーとして使用
        df_select_data["key_and_name"] = df_select_data["store_code"] + ":" + df_select_data["store_name"]
       
        # 店舗情報をJSON形式で返す　*array形式に変換できるloadsで返さないとエラーが発生する
        df_select_data = json.loads(df_select_data.to_json(orient="records", force_ascii=False))

        return jsonify(df_select_data)
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"店舗売上データ取得に失敗しました。{str(e)}"}), 500


@app.route("/api/items",methods=['GET'])
def get_items():

    global df_sales
    global df_courses
    try:
        # クエリパラメータからコース名、店舗名を取得
        bpcode = request.args.get("bpcode", default=None)
        stor_code = request.args.get("store_code", default=None)
        course_name = request.args.get("course_name", default=None)

        df_select_data = df_sales
        if bpcode:
            df_select_data = df_select_data[df_select_data["customer_code"] == bpcode]

        if stor_code:
            stor_code = [code for code in stor_code.split(',')]
            df_select_data = df_select_data[df_select_data["store_code"].isin(stor_code)]
        
        if course_name:
            l = df_courses[df_courses["course_name"] == course_name]["store_code"].tolist()
            df_select_data = df_select_data[df_select_data["store_code"].isin(l)]

        # temp = df_select_data.groupby(['customer_name',"product_code","product_name"], as_index=False).agg({
        #     **SUM_COLUMN
        # })
        # temp2 = temp.groupby(["product_code","product_name"], as_index=False).agg({
        #     **SUM_COLUMN,
        #     'customer_name' : 'size'
        # })
        df_select_data["customer_count"] = df_select_data["customer_name"]
        # 商品コードをキーにして、商品毎の集計を行う
        df_select_data = df_select_data.groupby(['product_code',"product_name"], as_index=False).agg({
            **SUM_COLUMN,
            'customer_count': lambda x: len(x.unique())
        })
        
        df_select_data["key_and_name"] = df_select_data["product_code"] + ":" + df_select_data["product_name"]
       
        # 店舗情報をJSON形式で返す　*array形式に変換できるloadsで返さないとエラーが発生する
        df_select_data = json.loads(df_select_data.to_json(orient="records", force_ascii=False))

        return jsonify(df_select_data)
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
