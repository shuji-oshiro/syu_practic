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
# print(df[""].value_counts()) #項目ごとの件数
print(df.isnull().sum()) #列ごとに欠損値数を表示
print(df[df.isnull().any(axis=1)]) #欠損値のある行を抽出



#TODO: 文字列データをダミー変数化----------------------

l_col = []
ans = ""
while True:
    ans = input("ダミーデータに変換するカラム名を入力してください。")
    if ans:
        l_col.append(ans)
    else:
        break
    
for col in l_col:
    dum_df = pd.get_dummies(df[col], drop_first=True, dtype=int, prefix=col)
    df = pd.concat([df, dum_df], axis=1)
    df = df.drop(col,axis=1)

#TODO: テストデータの分離
test_sizeval=0.2
random_stateval=0
train_df, test_df = train_test_split(df, test_size=test_sizeval, random_state=random_stateval)


#TODO：　#外れ値を確認するためのプロット図表示　確認の際は処理を中断
base_col = ""
while True:
    ans = input("外れ値をプロット図で確認しますか？ y or n")
    if "y" == ans:
        base_col = input("基準となるカラム名を入力してください")  
        if not base_col:
            continue
        flg = True
        break
    elif "n" ==ans:
        flg = False
        break
    else:
        print("無効な入力です。再度入力してください")
    
if flg: 
    se = train_df.corr()[base_col].map(abs).sort_values(ascending=False)
    print(se)
    
    plt.figure(figsize=(12, 8)) 
    for col in train_df.columns: 
        df.plot(kind="scatter", x=col, y=base_col)
    plt.show()

ans = ""
cound_l = []
while True:
    ans = input("外れ値で除去する条件式を入力してください") 
    if ans:
        #　条件をいくつか設定する必要あり-----------------------------------------？・・・・・・・・・・・・・・・・・・・・
        ans_s = ans.split()
        if len(ans_s)==3:            
            cound_l.append(ans_s)
        else:
            print("条件式は　カラム名、比較符号、値の3つをスペースで区切って構成してください")
    else:
       break

if cound_l:

    #TODO：　外れ値除去
    dic_l = [{"RM":["<",5],"PRICE":[">",45]},{"PTRATIO":[">",18],"PRICE":[">",40]}]
    
    for dic in dic_l:    
        temp_df = train_df    
        for key in dic:    
            cound = dic[key]
            if cound[0]=="<":
                temp_df = temp_df[temp_df[key] < cound[1]]
            else:
                temp_df = temp_df[temp_df[key] > cound[1]]
        if not temp_df.empty:
            train_df = train_df.drop(temp_df.index)
            print(f"外れ値データ削除：{temp_df.index}")
    
    # 外れ値除去後の影響係数確認
    se = train_df.corr()["PRICE"].map(abs).sort_values(ascending=False)
    print(se)


#TODO: 欠損値補完処理-------------------
flg = 0

if flg==0:
    naVal = train_df.mean(numeric_only=True) # 欠損値を置き換える処理
    train_df = train_df.fillna(naVal) #欠損値補完
elif flg ==1:
    naVal = train_df.median(numeric_only=True) # 欠損値を置き換える処理
    train_df = train_df.fillna(naVal) #欠損値補完
else:
    #特殊処理記述
        pass
       
print(train_df.isnull().sum()) # nullチェック


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

sc_x_2 = sc_model_x2.transform(x_df)
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

      

# model = tree.DecisionTreeClassifier(max_depth=5, random_state=0, class_weight="balanced")
# fle_pkl = tkinter.filedialog.askopenfilename(typ=[("pkl", '.pkl')], title="モデルデータの読み込み")
# model = None
# if fle_pkl:
#     with open(fle_pkl, "rb") as f:
#         model=pickle.load(f)
# else:
#     model = LinearRegression()


# def learn(x,y,x1,y1,depth=0):
#     model = tree.DecisionTreeClassifier(max_depth=depth, random_state=0, class_weight="balanced")
#     model.fit(x,y)    
#     print(f"depth={depth} 訓練{model.score(x,y)} 正解{model.score(x1,y1)}") # 回帰では決定係数、分類では確率評価
    
# for i in range(1,15):
#     learn(x_train, y_train, x_test, y_test, i)


model = tree.DecisionTreeClassifier(max_depth=5, random_state=0, class_weight="balanced")
model.fit(x_train,y_train)

print(f"訓練{model.score(x_train,y_train)} 正解{model.score(x_test,y_test)}") # 回帰では決定係数、分類では確率評価

# print(model.coef_)
# print(model.intercept_)
# print(pd.DataFrame(model.feature_importances_, index=x_train.columns))  #決定木において重要度を示す係数を表示 

  
# temp = pd.DataFrame(model.coef_) #回帰、係数確認
# temp.index = x_train.columns
# print(temp)

# print(f"：{model.score(x_test,y_test)}") # 回帰では決定係数、分類では確率評価

# pred= model.predict(x_test) # 学習データより予測

# print(f"平均絶対誤差：{mean_absolute_error(y_pred=pred, y_true=y_test)}") #平均絶対誤差

# print(f"決定係数：{model.score(x_test,y_test)}") # 回帰では決定係数、分類では確率評価

# plt.figure(figsize=(12, 8)) # 決定木モデルを可視化
# plot_tree(model, filled=True)
# plt.show()



save_path = tkinter.filedialog.asksaveasfilename(typ=[("pkl", '.pkl')], title="モデルデータの保存")
if save_path:
    with open(save_path, "wb") as f:
        pickle.dump(model, f)
        
    msg.showinfo(message="モデルを保存しました")
else:
    msg.showinfo(message="モデルを保存しませんでした")
    