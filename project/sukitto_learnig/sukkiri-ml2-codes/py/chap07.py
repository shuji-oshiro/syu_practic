#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
from sklearn import tree
from sklearn.model_selection import train_test_split
df = pd.read_csv('datafolda/Survived.csv')
df.head(2) # 先頭2行の確認


# In[10]:


df['Survived'].value_counts()


# In[18]:


df.isnull().sum()


# In[20]:


df.shape


# In[22]:


# Age列を平均値で穴埋め
df["Age"] = df["Age"].fillna(df["Age"].mean())
# Embarked列を最頻値で穴埋め
df["Embarked"] = df['Embarked'].fillna(df['Embarked'].mode())


# In[24]:


# 特徴量として利用する列のリスト
col = ['Pclass','Age','SibSp','Parch','Fare']

x = df[col]
t = df['Survived']


# In[26]:


x_train,x_test,y_train,y_test = train_test_split(x,t,
test_size = 0.2,random_state = 0)
# x_trainのサイズの確認
x_train.shape


# In[28]:


model = tree.DecisionTreeClassifier(max_depth = 5,
 random_state = 0,class_weight ='balanced')

model.fit(x_train,y_train) # 学習


# In[30]:


model.score(X = x_test,y = y_test)


# In[32]:


def learn(x,t,depth=3):
    x_train,x_test,y_train,y_test = train_test_split(x,
        t,test_size = 0.2,random_state = 0)
    model = tree.DecisionTreeClassifier(max_depth =depth,random_state = 0,class_weight="balanced")
    model.fit(x_train,y_train)

    score=model.score(X=x_train,y=y_train)
    score2=model.score(X=x_test,y=y_test)
    return round(score,3),round(score2,3),model


# In[36]:


for j in range(1,15): # jは木の深さ jには1～14が入る
    # xは特徴量、tは正解データ
    train_score,test_score,model = learn(x,t,depth = j)
    sentence="訓練データの正解率{}"
    sentence2="訓練データの正解率{}"
    total_sentence='深さ{}:'+sentence+sentence2
    print(total_sentence.format(j,
    train_score,test_score))


# In[38]:


df2 = pd.read_csv('datafolda/Survived.csv')
print(df2['Age'].mean()) # 平均値の計算
print(df2['Age'].median()) # 中央値の計算


# In[60]:


df2.head()


# In[ ]:





# In[40]:


df2.groupby('Survived')['Age'].mean()


# In[42]:


df2.groupby('Pclass')['Age'].mean()


# In[44]:


pd.pivot_table(df2,index = 'Survived',columns = 'Pclass',
values = 'Age')


# In[50]:


pd.pivot_table(df2,index = 'Survived',columns = 'Pclass',
values = 'Age',aggfunc='max')


# In[52]:


# Age列の欠損値行を抜き出すのに必要（欠損だとTrue)
is_null = df2['Age'].isnull()

# Pclass 1　に関する埋め込み
df2.loc[(df2['Pclass'] == 1) & (df2['Survived'] == 0)
    &(is_null),'Age'] = 43
df2.loc[(df2['Pclass'] == 1) & (df2['Survived'] == 1)
    &(is_null),'Age'] = 35

# Pclass 2　に関する埋め込み
df2.loc[(df2['Pclass'] == 2) & (df2['Survived'] == 0)
    &(is_null),'Age'] = 33
df2.loc[(df2['Pclass'] == 2) & (df2['Survived'] == 1)
    &(is_null),'Age'] = 25

# Pclass 3　に関する埋め込み
df2.loc[(df2['Pclass'] == 3) & (df2['Survived'] == 0)
    &(is_null),'Age'] = 26
df2.loc[(df2['Pclass'] == 3) & (df2['Survived'] == 1)
    &(is_null),'Age'] = 20


# In[56]:


#特徴量として利用する列のリスト
col = ['Pclass','Age','SibSp','Parch','Fare']
x = df2[col]
t = df2['Survived']

for j in range(1,15): # jは木の深さ
    s1,s2,m = learn(x,t,depth = j)
    sentence='深さ{}:訓練データの精度{}::テストデータの精度{}'
    print(sentence.format(j,s1,s2))


# In[58]:


#性別ごとの各列の平均値を集計。戻り値はデータフレーム
sex = df2.groupby('Sex')['Survived'].mean()
sex


# In[60]:


sex.plot(kind='bar')


# In[62]:


# 特徴量として利用する列のリスト
col = ['Pclass','Age','SibSp','Parch','Fare','Sex']

x = df2[col]
t = df2['Survived']

train_score,test_score,model = learn(x,t) # 学習


# In[64]:


male = pd.get_dummies(df2['Sex'],drop_first = True, dtype=int)
male


# In[66]:


pd.get_dummies(df2['Sex'],dtype=int)


# In[68]:


pd.get_dummies(df2['Embarked'],drop_first = True, dtype=int)


# In[70]:


embarked = pd.get_dummies(df2['Embarked'],drop_first = False, dtype=int)
embarked.head(3)


# In[72]:


x_tmp=pd.concat([x,male],axis=1)

x_tmp.head(2)


# In[159]:


tmp = pd.concat([x,x],axis = 0)
tmp.shape


# In[74]:


x_new = x_tmp.drop("Sex",axis=1)
for j in range(1,6): # jは木の深さ
 # xは特徴量、tは目的変数
    s1,s2,m = learn(x_new,t,depth = j)
    s='深さ{}:訓練データの精度{}::テストデータの精度{}'
    print(s.format(j,s1,s2))


# In[76]:


s1,s2,model = learn(x_new,t,depth = 5)

# モデルの保存
import pickle
with open('survived.pkl','wb') as f:
    pickle.dump(model,f)


# In[165]:


model.feature_importances_


# In[80]:


#データフレームに変換
pd.DataFrame(model.feature_importances_,index = x_new.columns)


# # 練習問題

# In[83]:


df = pd.read_csv('datafolda/ex4.csv')
df.head(3)


# In[85]:


df["sex"].mean()


# In[87]:


df.groupby('class').mean()['score']


# In[183]:


pd.pivot_table(df,index='class',columns='sex',values='score')


# In[191]:


dummy = pd.get_dummies(df['dept_id'],drop_first = True,dtype=int)

df2 = pd.concat([df,dummy],axis = 1)

df2 = df2.drop('dept_id',axis = 1)


# In[193]:


df2


# In[ ]:




