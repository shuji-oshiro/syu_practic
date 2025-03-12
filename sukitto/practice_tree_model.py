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
    dum_df = pd.get_dummies(df[col], drop_first=True, dtype=int, prefix=col)
    df = pd.concat([df, dum_df], axis=1)

    df = df.drop(col,axis=1)


#TODO: テストデータの分離
test_sizeval=0.1
random_stateval=0
train_df, test_df = train_test_split(df, test_size=test_sizeval, random_state=random_stateval)




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

print(train_df["y"].value_counts())



# 学習結果を返す処理
def lean(x, t, depoth):

    test_size_val = 0.2
    randaom_state_val = 0
    x_t, x_v, y_t, y_v = train_test_split(x,t, test_size=test_size_val, random_state=randaom_state_val)

    # sc_model_x = StandardScaler()
    # sc_model_y = StandardScaler()
    # sc_model_x.fit(x_t)
    # sc_model_y.fit(y_t)

    # sc_x = sc_model_x.transform(x_t)
    # sc_y = sc_model_y.transform(y_t)

    model = tree.DecisionTreeClassifier(max_depth=depoth, random_state=0,class_weight="balanced")
    model.fit(x_t,y_t)

    # sc_x_v = sc_model_x.transform(x_v)
    # sc_y_v = sc_model_y.transform(y_v)

    t_score = model.score(x_t, y_t)
    v_score = model.score(x_v,y_v)

    print(f"depoth={depoth} 訓練データスコア={t_score} : 検証データスコア={v_score}")

x = df.drop(columns=['id','y','day'])
t = df["y"]

for i in range(2,20):
    lean(x, t, i)

#深さ11以降はvalが停滞するので過学習が発生ここでテストデータでチェック
model = tree.DecisionTreeClassifier(max_depth=11,random_state=11)
model.fit(x,t)
test2 = test_df.copy()
test2 = test_df.fillna(train_df.median(numeric_only=True))

test_y=test2['y']
test_x =test2.drop(['id','y','day'],axis=1)
print(model.score(test_x,test_y))

# if input("モデルを保存しますか？　: ") == "y":
#     save_path = tkinter.filedialog.asksaveasfilename(typ=[("pkl", '.pkl')], title="モデルデータの保存")
#     if save_path:
#         with open(save_path, "wb") as f:
#             pickle.dump(model, f)
#         msg.showinfo(message="モデルを保存しました")
# else:
#     msg.showinfo(message="モデルを保存しませんでした")
