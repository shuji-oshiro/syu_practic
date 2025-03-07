#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd

df = pd.read_csv('../datafiles/cinema.csv')
df.head(3) # 先頭3行の中身を表示


# In[ ]:





# In[ ]:





# In[3]:


df.isnull().any(axis = 0)


# In[4]:


# 欠損値を平均で補完して、df2に代入
df2 = df.fillna(df.mean())
# 穴埋めができたか確認
df2.isnull().any(axis = 0)


# In[5]:


# SNS2とsalesの散布図の作成
df2.plot(kind = 'scatter', x = 'SNS2', y = 'sales')


# In[6]:


df2.plot(kind = 'scatter', x = 'SNS1', y = 'sales')
df2.plot(kind = 'scatter', x = 'SNS2', y = 'sales')
df2.plot(kind = 'scatter', x = 'actor', y = 'sales')
df2.plot(kind = 'scatter', x = 'original', y = 'sales')


# In[7]:


for name in df.columns:
#for name in df: でも可

    # x軸がcinema_id列とsales列の散布図は
    #作っても意味が無いので外す
    if name == 'cinema_id' or name == 'sales':
        continue

    df2.plot(kind = "scatter", x = name, y = "sales")


# In[8]:


no = df2[(df2['SNS2'] > 1000) & (df2['sales'] < 8500)].index
df3 = df2.drop(no, axis = 0)


# In[9]:


test = pd.DataFrame(
{'Acolumn':[1,2,3],
 'Bcolumn':[4,5,6]
}
)


# In[10]:


test[test['Acolumn'] < 2]


# In[11]:


test['Acolumn'] < 2


# In[ ]:





# In[12]:


df[(df['SNS2'] > 1000 ) & (df['sales'] < 8500)]


# In[13]:


no = df2[(df['SNS2'] > 1000 ) & (df['sales'] < 8500)].index
no


# In[14]:


test.drop(0,axis=0)


# In[15]:


test.drop('Bcolumn',axis=1)


# In[16]:


df3 = df2.drop(no, axis = 0) # 外れ値の行を削除
df3.shape # 行が削除できたかどうかを行数で確認


# In[17]:


#特徴量の列の候補
col =['SNS1','SNS2','actor','original']
x=df3[col] #特徴量の抜き出し

t=df3['sales']#正解データの取り出し


# In[18]:


# インデックスが2、列がSNS1のマスの値のみ参照
df3.loc[2, 'SNS1']


# In[19]:


index = [2, 4, 6] # インデックス
col = ['SNS1', 'actor'] # 列名
df3.loc[index, col]


# In[20]:


sample = [10, 20, 30, 40] # リストの作成
sample[1:3] # 添え字が1以上3未満の要素を取得


# In[21]:


# 0行目以上2行目以下、actor列より左の列（actor列含む）
df3.loc[0:3, :'actor']


# In[22]:


x = df3.loc[ : , 'SNS1':'original'] # 特徴量の取り出し
t = df3['sales'] # 正解ラベルの取り出し


# In[23]:


from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, t,
                                                    test_size = 0.2, random_state = 0)


# In[24]:


from sklearn.linear_model import LinearRegression
model = LinearRegression()


# In[25]:


model.fit(x_train, y_train)


# In[26]:


# 新しいデータをデータフレームで作成
new = pd.DataFrame([[150, 700, 300, 0]], columns=x_train.columns)
model.predict(new) # 学習済みモデルで推論


# In[27]:


model.score(x_test, y_test)


# In[ ]:





# In[28]:


# 関数のインポート
from sklearn.metrics import mean_absolute_error

pred = model.predict(x_test)

# 平均絶対誤差の計算
mean_absolute_error(y_pred = pred, y_true = y_test)


# In[29]:


import pickle

with open('cineama.pkl', 'wb') as f:
    pickle.dump(model, f)


# In[30]:


print(model.coef_) # 計算式の係数の表示
print(model.intercept_) # 計算式の切片の表示


# In[31]:


tmp = pd.DataFrame(model.coef_) # データフレームの作成
tmp.index = x_train.columns # 列名をインデックスに指定
tmp


# # 演習問題

# In[32]:


import pandas as pd

df = pd.read_csv('../datafiles/ex3.csv')


# In[33]:


df.head(5)


# In[34]:


df.isnull().sum()


# In[35]:


df2 = df.fillna(df.median())


# In[37]:


df2.plot(kind = 'scatter', x = 'x0', y = 'target')


# In[38]:


for name in df.columns:
    if name == 'target':
        continue
    df2.plot(kind = 'scatter', x = name, y = 'target')


# In[39]:


no = df2[ (df2['x2'] < -2) & (df2['target'] > 100)].index

df3 = df2.drop(no, axis = 0)


# In[40]:


x = df3.loc[:, :'x3']
t = df3['target']


# In[41]:


from sklearn.model_selection import train_test_split

x_train, x_test, y_train, y_test = train_test_split(x, t,
    test_size = 0.2, random_state = 1)


# In[42]:


from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(x_train, y_train)


# In[43]:


model.score(x_test, y_test)


# In[ ]:





# In[ ]:




