#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd # pandasのインポート
# irisファイルを読み込んで、データフレームに変換
df = pd.read_csv('../datafiles/iris.csv')
df.head(3) # 上位3件の表示


# In[2]:


df['種類'].unique()


# In[3]:


syurui = df['種類'].unique()
syurui[0]


# In[4]:


df['種類'].value_counts()


# In[5]:


df.tail(8)#末尾3件の表示


# In[6]:


df.isnull()#各マスが欠損値かどうか調べる


# In[7]:


#列単位で欠損値が存在するか調べる
df.isnull().any(axis=0)


# In[8]:


df.sum()


# In[9]:


df.sum() # 各列の合計値を計算


# In[10]:


# 各列に欠損値がいくつあるか集計
tmp = df.isnull()
tmp.sum()


# In[11]:


# 欠損値が1つでもある行を削除した結果を、df2に代入
df2 = df.dropna(how = 'any', axis = 0)

df2.tail(3) # 欠損値の存在確認


# In[12]:


df.isnull().any(axis = 0)


# In[13]:


df['花弁長さ'] = df['花弁長さ'].fillna(0)
df.tail(3)


# In[14]:


#数値列の各平均値を計算（文字列の列は自動的に除外してくれる）
df.mean(numeric_only=True)


# In[15]:


#がく片長さ列の平均値を計算
df['がく片長さ'].mean()


# In[16]:


df.std(numeric_only=True) # 各列の標準偏差


# In[18]:


df = pd.read_csv('../datafiles/iris.csv')

# 各列の平均値を計算して、colmeanに代入
colmean = df.mean(numeric_only=True)

# 平均値で欠損値を穴埋めしてdf2に代入
df2 = df.fillna(colmean)
# 欠損値があるか確認
df2.isnull().any(axis = 0)


# In[21]:


xcol = ['がく片長さ', 'がく片幅', '花弁長さ', '花弁幅']

x = df2[xcol]
t = df2['種類']


# In[22]:


# 関数のインポート
from sklearn import tree
# モデルの作成
model = tree.DecisionTreeClassifier(max_depth = 2,
                                    random_state=0)


# In[23]:


model.fit(x, t) # モデルの学習
model.score(x, t) # 学習済みモデルの正解率計算


# In[24]:


# 関数のインポート
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, t,
    test_size = 0.3, random_state = 0)

#x_train,y_trainが学習に利用する訓練
#x_test,y_testが検証に利用するテストデータ


# In[ ]:





# In[25]:


print(x_train.shape) # x_trainの行数・列数を表示
print(x_test.shape) # x_test　の行数・列数を表示


# In[26]:


# 訓練データで再学習
model.fit(x_train, y_train)

# テストデータの予測結果と実際の答えが合致する正解率を計算
model.score(x_test, y_test)


# In[27]:


import pickle
with open('irismodel.pkl', 'wb') as f:
    pickle.dump(model, f)


# In[28]:


model.tree_.feature


# In[29]:


model.tree_.threshold


# In[30]:


# ノード番号1、3、4に到達したアヤメの種類ごとの数
print(model.tree_.value[1]) # ノード番号1に到達したとき
print(model.tree_.value[3]) # ノード番号3に到達したとき
print(model.tree_.value[4]) # ノード番号4に到達したとき


# In[33]:


model.classes_


# In[34]:


# 描画関数の仕様上、和名の特徴量を英字に直す
x_train.columns = ['gaku_nagasa', 'gaku_haba',
'kaben_nagasa','kaben_haba']
# 描画関数の利用
from sklearn.tree import plot_tree
# plot_tree関数で決定木を描画
plot_tree(model, feature_names = x_train.columns,
filled = True)


# # 練習問題

# In[99]:


import pandas as pd


# In[35]:


df = pd.read_csv('../datafiles/ex2.csv')
df.head(3)


# In[106]:


df.shape


# In[108]:


df["target"].value_counts()


# In[110]:


df.isnull().sum()


# In[112]:


df2 = df.fillna(df.median())


# In[114]:


xcol=['x0','x1','x2','x3']
x = df2[xcol]
t =df2['target']


# In[116]:


from sklearn.model_selection import train_test_split

x_train, x_test, y_train, y_test = train_test_split(x, t,
    test_size = 0.2, random_state = 0)


# In[118]:


from sklearn import tree
model = tree.DecisionTreeClassifier(max_depth = 3,
    random_state = 0)
model.fit(x_train, y_train)


# In[120]:


model.score(x_test, y_test)


# In[124]:


newdata = pd.DataFrame([[1.56,0.23, -1.1,2.8]], columns=x_train.columns)

answer = model.predict(newdata)
answer


# In[ ]:




