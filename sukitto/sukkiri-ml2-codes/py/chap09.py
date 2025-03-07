#!/usr/bin/env python
# coding: utf-8

# # 練習9-1 
# ## どのような機械学習手法を用いると良いか？
# 
# ### 解答例
# 教師あり学習の分類

# # 練習9-2
# ## どのようなアウトプットを得られるか？また、その分析結果からどのようにスッキリ銀行の課題を解決する事が出来るか？

# ### 解答例  
# ｙ列を予測する分類モデルを作ることにより、その顧客が購入してくれるかどうかが事前に分かる。また、特徴量にこちらからのアプローチ法を入れる事により、「この顧客の場合、こういうアプローチをとったら購入してくれる」というような営業の最適化を行う事が出来る
# 

# # 練習9-3 
# ## ひとまず何でもいいのでモデルを作ってみましょう。ただし、データは訓練、検証、テストデータの3分割をする方法を利用すること

# In[1]:


import pandas as pd
from sklearn import tree
from sklearn.model_selection import train_test_split


# In[ ]:





# In[ ]:





# In[4]:


df = pd.read_csv('../datafiles/Bank.csv')
print(df.shape)
df.head()


# In[5]:


# まず、ダミー変数化をしたいが、文字列の列が複数あるので抜き出す。
str_col_name=['job','default','marital','education','housing','loan','contact','month']
str_df = df[str_col_name]
#複数列を一気にダミー変数化
str_df2=pd.get_dummies(str_df,drop_first=True)

num_df = df.drop(str_col_name,axis=1)#数値列を抜き出す
df2 = pd.concat([num_df,str_df2,str_df],axis=1)#結合(今後の集計の利便性も考慮してstr_dfも結合しておく)


# In[6]:


df2.columns


# In[7]:


#訓練&検証データとテストデータに分割
train_val,test = train_test_split(df2,test_size=0.1,random_state=9)
train_val.head()


# In[ ]:





# In[ ]:





# # 欠損値の確認

# In[8]:


a=train_val.isnull().sum()
a[a>0]


# In[9]:


train_val['duration'].median()


# In[11]:


#とりあえず最初は中央値で補完
train_val2= train_val.fillna(train_val.median(numeric_only=True))


# In[12]:


#不均衡なデータであるか確認
train_val2['y'].value_counts()


# In[ ]:





# ### 今回は不均衡データの分類。モデル作成時にclass_weight="balanced"と指定する事で、不均衡データに対応したモデルにする。
# 
# ### class_weightを指定すると、通常より正解率は上がりにくい。

# In[13]:


#とりあえず、全ての特徴量を利用してモデルを作ってみる。
t =train_val2['y']
x = train_val2.drop(str_col_name,axis=1)
x =x.drop(['id','y','day'],axis=1)

x_train,x_val,y_train,y_val = train_test_split(x,t,test_size=0.2,random_state=13)

#不均衡データに対応できるように、class_weight引数も設定
model = tree.DecisionTreeClassifier(random_state=3,max_depth=3,class_weight='balanced')

#class_weightを指定しないとちなみに正解率は0.7ぐらい
#model = tree.DecisionTreeClassifier(random_state=3,max_depth=5)
model.fit(x_train,y_train)
model.score(x_val,y_val)


# # 練習9-4　様々な検証をしてテストデータでの性能を高めましょう。ただし、テストデータを集計したり、図示したりはしてはいけません。
# 
# # 実はこのデータは、決定木では試行錯誤しても性能が高まりませんが、どういう着眼点で進めていくべきか、その一例を紹介します。(第3部で決定木以外の手法を紹介します)

# In[ ]:





# 

# In[14]:


#まず、さくっと学習できるようなlearn関数を定義する。
def learn(x,t,i):
    x_train,x_val,y_train,y_val = train_test_split(x,t,test_size=0.2,random_state=13)

    datas=[x_train,x_val,y_train,y_val]
    #不均衡データに対応できるように、class_weight引数も設定
    model = tree.DecisionTreeClassifier(random_state=i,max_depth=i,class_weight='balanced')
    model.fit(x_train,y_train)
    train_score=model.score(x_train,y_train)
    
    val_score=model.score(x_val,y_val)
    return train_score,val_score,model,datas


# In[15]:


#とりあえず、for文で様々な木の深さでの正解率を調べてみる
for i in range(1,20):
    s1,s2,model,datas = learn(x,t,i)
    print(i,s1,s2)


# In[17]:


#深さ11以降はvalが停滞するので過学習が発生ここでテストデータでチェック
model = tree.DecisionTreeClassifier(max_depth=11,random_state=11)
model.fit(x,t)
test2 = test.copy()
test2=test2.fillna(train_val.median(numeric_only=True))

test_y=test2['y']
test_x = test2.drop(str_col_name,axis=1)
test_x =test_x.drop(['id','y','day'],axis=1)
model.score(test_x,test_y)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# 

# In[18]:


#特徴量重要度の確認(ちなみに、連続量とダミー変数を比べると、連続量の方が重要度は高め出力されてしまう事に注意)
a=pd.Series(model.feature_importances_,index=x.columns).sort_values(ascending=False)
a[0:9]#campaignやdurationが重要度が大きいと分かる


# # durationの欠損値処理

# In[19]:


# durationに関係がありそうなものを見つけるためには7章の様に集計処理で判断したい。
#よって、集計処理の軸になるstr_dfの列名をいったん確認
print(str_df.columns)


# In[20]:


for name in str_df.columns:
    print(train_val.groupby(name)['y'].mean())
    print("next=========")


# #### housing ,loan, contactが関係してそう。　ただ、contactにおいて、sending_documentは資料送付しかしていないのに接触時間が長いとはどういうことか？？
# #### 実際ならば、このデータはどう解釈すればいいのか実際の現場の人間に聞き取りをする必要があるが、今回は不可能なのでこのまま分析を進める。

# In[21]:


print(pd.pivot_table(train_val,index="housing",columns="loan",values="duration"))
print(pd.pivot_table(train_val,index="housing",columns="contact",values="duration"))
print(pd.pivot_table(train_val,index="loan",columns="contact",values="duration"))


# ##### どれも強く関係してそうに見える。今回は2×2で処理しやすい。loan×housingを採用しよう

# In[ ]:





# In[22]:


def nan_fill(train_val):
    isnull = train_val['duration'].isnull()

    #train_valを変えたくないので、py基本文法のcopyメソッドでコピーを作って
    #train_val2に代入
    train_val2 = train_val.copy()
    #housing=yesの処理
    train_val2.loc[(isnull) & (train_val2['housing']=='yes') 
                  &(train_val2['loan']=='yes'),'duration' ]=439
    train_val2.loc[(isnull) & (train_val2['housing']=='yes') 
                  &(train_val2['loan']=='no'),'duration' ]=332

    #housing=noの処理
    train_val2.loc[(isnull) & (train_val2['housing']=='no') 
                  &(train_val2['loan']=='yes'),'duration' ]=301
    train_val2.loc[(isnull) & (train_val2['housing']=='no') 
                  &(train_val2['loan']=='no'),'duration' ]=237
    
    return train_val2
train_val2=nan_fill(train_val)


# In[23]:


#特徴量重要度が大きかった項目とyの関係
train_val2.groupby('y')['duration'].median()


# In[24]:


train_val2.groupby('y')['amount'].median()


# In[25]:


train_val2.groupby('y')['campaign'].median()


# In[26]:


train_val2.groupby('y')['age'].median()


# # durationは値が大きいほど、y=1になりやすい傾向がありそう

# In[27]:


#ここでいったん、learn関数で分析

t =train_val2['y']

x = train_val2.drop(str_col_name,axis=1)
x =x.drop(['id','y','day'],axis=1)
#x =train_val2[xcol]
for i in range(1,20):
    s1,s2,model,datas = learn(x,t,i)
    print(i,s1,s2)


# In[ ]:





# In[28]:


#どのような間違い方をしているのか確認
s1,s2,model,datas = learn(x,t,10)

#訓練データでの予測結果と実際の値の2軸で個数集計flagがFalseならば、検証データで集計
def syuukei(model,datas,flag=False):
    if flag:
        pre=model.predict(datas[0])
        y_val=datas[2]
    else:
        pre=model.predict(datas[1])
        y_val=datas[3]
    data={
        "pred":pre,
        "true":y_val
    }
    tmp=pd.DataFrame(data)
    return tmp,pd.pivot_table(tmp,index="true",columns="pred",values="true",aggfunc=len)
tmp,a=syuukei(model,datas,False)
a


# In[ ]:





# In[30]:


#本当はｙ＝０の中で、正確に予測された人と謝った予測をされた人でどういう傾向があるか分析

false=tmp.loc[(tmp['pred']==1)&(tmp['true']==0)].index
true=tmp.loc[(tmp['pred']==0)&(tmp['true']==0)].index
true_df=train_val2.loc[true]
false_df=train_val2.loc[false]
pd.concat([true_df.mean(numeric_only=True)["age":],false_df.mean(numeric_only=True)["age":]],axis=1).plot(kind="bar")
true


# In[ ]:





# In[26]:


#値にばらつきが大きいので、標準化してもう一度グラフ化
from sklearn.preprocessing import StandardScaler

sc = StandardScaler()
tmp2=train_val2.drop(str_col_name,axis=1)
sc_data = sc.fit_transform(tmp2)
sc_df = pd.DataFrame(sc_data,columns=tmp2.columns,index=tmp2.index)

true_df=sc_df.loc[true]
false_df=sc_df.loc[false]
true_df
temp2=pd.concat([false_df.mean()["age":],true_df.mean()["age":]],axis=1)
temp2.plot(kind="bar")


# In[27]:


#青色の０は誤分類、オレンジ１は正解のデータ

# durationと housing_yesが大きく異なる
#実際はy=0の人で、 durationが大きい人は誤分類しやすい
#実際はy=0の人で、 housingが大きい人は誤分類しやすい


#事前に、durationが大きい人はy=1になりやすいということは分かっているので、「こういう人はy=0になりやすい」という
#特徴量を見つけ出して、特徴量×durationという特徴量を作って、durationに重み付けをする列を作れば正解率
#があがるのではないか？ 続きは3部に譲ってここでテストデータ評価を行う


# In[31]:


model_tree=tree.DecisionTreeClassifier(max_depth=10,random_state=10,class_weight="balanced")
model_tree.fit(x,t)

test2=nan_fill(test)
t =test2['y']
x = test2.drop(str_col_name,axis=1)
x =x.drop(['id','y','day'],axis=1)
model_tree.score(x,t)


# In[635]:


#テストデータの正解率は上昇した


# In[ ]:




