#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from sklearn import tree
df = pd.read_csv('../datafiles/KvsT.csv')
x = df.loc[:, '体重':'年代']
t = df['派閥']
model = tree.DecisionTreeClassifier(max_depth = 1,
random_state = 0)
model.fit(x, t)

data = [[65, 20]] # 予測用未知データ
print(model.predict(data)) # 予測派閥
model.predict_proba(data) # 派閥の確率


# In[ ]:





# In[3]:


import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv('../datafiles/iris.csv')
df.head(2)


# In[ ]:





# In[4]:


# 平均値による欠損値の穴埋め
df_mean = df.mean(numeric_only=True)
train2 = df.fillna(df_mean)

# 特徴量と正解データに分割
x = train2.loc[:, :'花弁幅']
t = train2['種類']

# 特徴量の標準化
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
new = sc.fit_transform(x)


# In[5]:


# 訓練データと検証用データに分割
x_train, x_val, y_train, y_val = train_test_split(new, t,
    test_size = 0.2, random_state = 0)


# In[6]:


from sklearn.linear_model import LogisticRegression

model = LogisticRegression(C = 0.1,random_state=0,
    multi_class = 'auto', solver = 'lbfgs')

model.fit(x_train, y_train)
print( model.score(x_train, y_train) )
model.score(x_val, y_val)


# In[ ]:





# In[7]:


model.coef_


# In[8]:


x_new = [[1, 2, 3, 4]] # 新規データ

model.predict(x_new) # 新規データで予測


# In[9]:


model.predict_proba(x_new)


# In[10]:


model.intercept_


# In[11]:


# モジュールの読み込み
import pandas as pd
from sklearn.model_selection import train_test_split


# In[12]:


df = pd.read_csv('../datafiles/Survived.csv') # csvファイルの読み込み
# 確認する
df.head(2)


# In[ ]:





# In[13]:


# df["Age"] = df["Age"].fillna(df["Age"].mean())


# In[14]:


# jo1 = df['Pclass'] == 1
# jo2 = df['Survived'] == 0
# jo3 = df['Age'].isnull()
# df.loc[(jo1) & (jo2) & (jo3), 'Age'] = 43

# jo2= df['Survived'] == 1
# df.loc[(jo1) & (jo2) & (jo3), 'Age'] = 35

# jo1 = df['Pclass'] == 2
# jo2 = df['Survived'] == 0
# jo3 = df['Age'].isnull()
# df.loc[(jo1) & (jo2) & (jo3), 'Age'] = 26

# jo2 = df['Survived'] == 1
# df.loc[(jo1) & (jo2) & (jo3), 'Age'] = 20

# jo1 = df['Pclass'] == 3
# jo2 = df['Survived'] == 0
# jo3 = df['Age'].isnull()
# df.loc[(jo1) & (jo2) & (jo3), 'Age'] = 43

# jo2 = df['Survived'] == 1
# df.loc[(jo1) & (jo2) & (jo3), 'Age'] = 35

def fill_age(df, pclass, survived, value):
    joken1 = df['Pclass'] == pclass
    joken2 = df['Survived'] == survived
    joken3 = df['Age'].isnull()
    df.loc[(joken1) & (joken2) & (joken3), 'Age'] = value
    return df

print( df.pivot_table(index="Pclass",columns="Survived",values='Age') )

# ピボットテーブルの値を参考に補完
df = fill_age(df, 1, 0, 43)
df = fill_age(df, 1, 1, 35)
df = fill_age(df, 2, 0, 33)
df = fill_age(df, 2, 1, 25)
df = fill_age(df, 3, 0, 26)
df = fill_age(df, 3, 1, 20)


# In[15]:


# 特徴量として利用する列のリスト
col = ['Pclass', 'Age', 'SibSp', 'Parch', 'Fare']

x = df[col]
t = df['Survived']

# Sex列は文字の列なのでダミー変数化
dummy = pd.get_dummies(df['Sex'], drop_first = True,dtype=int)
x = pd.concat([x, dummy], axis = 1)
x.head(2)


# In[16]:


# ランダムフォレストのインポート
from sklearn.ensemble import RandomForestClassifier
x_train, x_test, y_train, y_test=train_test_split(x, t,
 test_size = 0.2, random_state = 0)
model = RandomForestClassifier(n_estimators = 200,
random_state = 0)


# In[17]:


model.fit(x_train, y_train)

print(model.score(x_train, y_train))
print(model.score(x_test, y_test))


# In[18]:


from sklearn import tree
model2 = tree.DecisionTreeClassifier(random_state = 0)
model2.fit(x_train, y_train)

print(model2.score(x_train, y_train))
print(model2.score(x_test, y_test))


# In[19]:


importance = model.feature_importances_ # 特徴量重要度

# 列との対応がわかりやすいようにシリーズ変換
pd.Series(importance, index = x_train.columns)


# In[20]:


# アダブーストのインポート
from sklearn.ensemble import AdaBoostClassifier


# ベースとなるモデル
from sklearn.tree import DecisionTreeClassifier

x_train, x_test, y_train, y_test = train_test_split(x, t,
test_size = 0.2, random_state = 0)
# 最大の深さ5の決定木を何個も作っていく
base_model = DecisionTreeClassifier(random_state = 0,
max_depth = 5)

# 決定木を500個作成
model = AdaBoostClassifier(n_estimators = 500,
    random_state = 0, estimator= base_model, algorithm="SAMME")
model.fit(x_train,y_train) # 学習

print(model.score(x_train, y_train)) # 訓練データの正解率
print(model.score(x_test, y_test)) # テストデータの正解率


# In[21]:


# データの読み込み
df = pd.read_csv('../datafiles/cinema.csv')
df = df.fillna(df.mean())
x = df.loc[:, 'SNS1':'original']
t = df['sales']
x_train, x_test, y_train, y_test = train_test_split(x, t,
 test_size = 0.2, random_state = 0)

# ランダムフォレスト回帰
from sklearn.ensemble import RandomForestRegressor
# 100個のモデルで並列学習
model = RandomForestRegressor(random_state = 0,
n_estimators = 100)
model.fit(x_train, y_train)
model.score(x_test, y_test) # 決定係数


# In[22]:


# アダブースト回帰
from sklearn.ensemble import AdaBoostRegressor
 # ベースモデルとしての回帰木
from sklearn.tree import DecisionTreeRegressor

base = DecisionTreeRegressor(random_state = 0,
 max_depth = 3)

# 100個のモデルで逐次学習
model = AdaBoostRegressor(random_state = 0,
 n_estimators = 100,estimator = base)
model.fit(x_train, y_train)
model.score(x_test, y_test)# 決定係数


# In[ ]:





# In[ ]:


#


# In[ ]:





# In[ ]:





# In[ ]:




