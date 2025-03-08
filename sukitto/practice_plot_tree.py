# -*- coding: utf-8 -*-
"""
Spyderエディタ

これは一時的なスクリプトファイルです。
"""
import tkinter.messagebox as msg 
import tkinter.filedialog
import pandas as pd
from sklearn import tree
import pickle
import sys
from sklearn.model_selection import train_test_split
from sklearn.tree import plot_tree
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# %matplotlib inline

#TODO: データの読み取り処理----------------------
fle = tkinter.filedialog.askopenfilename(typ=[("csv", '.csv')], title="学習データの読み込み")

if not fle:
    msg.showinfo(message="処理をキャンセルしました")
    sys.exit()

df = pd.read_csv(fle)
print(df.head(5))
print(df.shape) # 全体の数（行数・列数）

# 数字以外の項目が入力されている場合、件数を表示する
need_dummy_l = []
for col in df.columns:
    is_numeric = pd.to_numeric(df[col], errors='coerce').notna()
    if not is_numeric.any():
        need_dummy_l.append(df[col])
    
print(df.isnull().sum()) #列ごとに欠損値数を表示
print(df[df.isnull().any(axis=1)]) #欠損値のある行を抽出


l_col = []
#TODO: 文字列データをダミー変数化----------------------
for need_dummy in need_dummy_l:
    print(need_dummy.value_counts())
    col = need_dummy.name
    
    if input(f"{col}:ダミーデータに変換しますか？ y or n : ") == "y":
        dum_df = pd.get_dummies(df[col], drop_first=True, dtype=int, prefix=col)
        df = pd.concat([df, dum_df], axis=1)

    df = df.drop(col,axis=1)


#TODO: テストデータの分離
test_sizeval=0.2
random_stateval=0
train_df, test_df = train_test_split(df, test_size=test_sizeval, random_state=random_stateval)


#TODO：　#外れ値を確認するためのプロット図表示　確認の際は処理を中断
if input("プロット図で外れ値を確認しますか？ y or n : ") == "y":
    base_col = input("基準となるカラム名を入力してください : ")  
    
    if base_col:
        se = train_df.corr()[base_col].map(abs).sort_values(ascending=False)
        print(se)
        
        plt.figure(figsize=(12, 8)) 
        for col in train_df.columns: 
            df.plot(kind="scatter", x=col, y=base_col)
        plt.show()
        

if input("外れ値を除去しますか？ : ") == "y":
    cound_l = []    
    while True:        
        cound =[]
        for xy in ["x","y"]:
            val = input(f"{xy}軸:条件式入力 : ")
            cound.append(val)
          
        cound_l.append(cound)   
               
        ans = input("続けて条件式を入力しますか？ : ")        
        if not ans == "y":
            break
        

# TODO：　外れ値除去
# dic_l = [{"RM":["<",5],"PRICE":[">",45]},{"PTRATIO":[">",18],"PRICE":[">",40]}]

for cound in cound_l:    
    
    temp_df = train_df    
    for val in cound:    
        a, b, c = val.split()
        
        if b =="<":
            temp_df = temp_df[temp_df[a] < int(c)]
        else:
            temp_df = temp_df[temp_df[a] > int(c)]
            
    if not temp_df.empty:
        train_df = train_df.drop(temp_df.index)
        print(f"外れ値データ削除:{temp_df.index}")

# 外れ値除去後の影響係数確認
se = train_df.corr()["PRICE"].map(abs).sort_values(ascending=False)
print(se)


#TODO: 欠損値補完処理-------------------
flg = input("欠損値を補完する項目を入力してください。0：平均値　1：中央値 : ")

if flg==0:
    naVal = train_df.mean(numeric_only=True) # 欠損値を置き換える処理
    train_df = train_df.fillna(naVal) #欠損値補完
elif flg ==1:
    naVal = train_df.median(numeric_only=True) # 欠損値を置き換える処理
    train_df = train_df.fillna(naVal) #欠損値補完
else:
    #特殊処理記述
        pass
       
# print(train_df.isnull().sum()) # nullチェック


# 学習結果を返す処理
def lean(x, t):
    
    test_size_val = 0.2
    randaom_state_val = 0
    x_t, x_v, y_t, y_v = train_test_split(x,t, test_size=test_size_val, random_state=randaom_state_val)
        
    sc_model_x = StandardScaler()
    sc_model_y = StandardScaler()
    sc_model_x.fit(x_t)
    sc_model_y.fit(y_t)
    
    sc_x = sc_model_x.transform(x_t)
    sc_y = sc_model_y.transform(y_t)
                               
    model = LinearRegression()
    model.fit(sc_x,sc_y)
    
    sc_x_v = sc_model_x.transform(x_v)
    sc_y_v = sc_model_y.transform(y_v)
    
    t_score = model.score(sc_x, sc_y)
    v_score = model.score(sc_x_v,sc_y_v)
    
    print(f"訓練データスコア={t_score} : 検証データスコア={v_score}")
    return t_score, v_score


x_cols = ["RM","LSTAT","PTRATIO"]
y_col = ["PRICE"]

x_df = train_df[x_cols]
y_df = train_df[y_col]

#　追加の多項式特徴量や交互作用特徴量が必要な場合
x_df["RM^2"] = x_df["RM"]**2
x_df["PTRATIO^2"] = x_df["PTRATIO"]**2
x_df["LSTAT^2"]= x_df["LSTAT"]**2
x_df["RM*LSTAT"]= x_df["RM"]*x_df["LSTAT"]

lean(x_df, y_df)

# sys.exit()

# TODO: 最終評価処理-----------------------------
      
sc_model_x2= StandardScaler()
sc_model_y2= StandardScaler()

sc_model_x2.fit(x_df)
sc_model_y2.fit(y_df)

sc_x_2 = sc_model_x2.transform(x_df) # 逆変換はinverse_transform
sc_y_2 = sc_model_y2.transform(y_df)

model = LinearRegression()
model.fit(sc_x_2, sc_y_2)


#TODO: テストデータに同様の処理実行
naval= test_df.mean()
test_df = test_df.fillna(naval)

x_test = test_df[["RM","LSTAT","PTRATIO"]]
y_test = test_df[["PRICE"]]

x_test["RM^2"]=x_test["RM"]**2
x_test["PTRATIO^2"] = x_test["PTRATIO"]**2
x_test["LSTAT^2"] = x_test["LSTAT"]**2
x_test["RM*LSTAT"]= x_test["RM"]*x_test["LSTAT"]

sc_model_x2.fit(x_test)
sc_model_y2.fit(y_test)

sc_x_test = sc_model_x2.transform(x_test)
sc_y_test = sc_model_y2.transform(y_test)
                           
model.fit(sc_x_test, sc_y_test)

t_score = model.score(sc_x_2, sc_y_2)
v_score = model.score(sc_x_test,sc_y_test)

print(f"訓練・検証データスコア={t_score} : テストデータスコア={v_score}")
      

if input("モデルを保存しますか？　: ") == "y":
    save_path = tkinter.filedialog.asksaveasfilename(typ=[("pkl", '.pkl')], title="モデルデータの保存")
    if save_path:
        with open(save_path, "wb") as f:
            pickle.dump(model, f)
            
        msg.showinfo(message="モデルを保存しました")
    else:
        msg.showinfo(message="モデルを保存しませんでした")
    