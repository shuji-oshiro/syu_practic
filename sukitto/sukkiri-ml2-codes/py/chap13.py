#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
# 欠損値があるままでは学習できないので欠損値処理だけ行う
df = pd.read_csv('datafolda/cinema.csv')
df = df.fillna(df.mean())
x = df.loc[:, 'SNS1':'original']
t = df['sales']
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(x, t)


# In[5]:


from sklearn.metrics import mean_squared_error
# 訓練データでのMSE値
pred = model.predict(x)

mse = mean_squared_error(pred, t)
mse


# In[7]:


import math
math.sqrt(mse) # RMSEの計算


# In[9]:


from sklearn.metrics import mean_absolute_error 
yosoku = [2, 3, 5, 7, 11, 13] # 予測結果をリストで作成
target = [3, 5, 8, 11, 16, 19] # 実際の結果をリストで作成

mse = mean_squared_error(yosoku, target)
print('rmse:{}'.format(math.sqrt(mse)))
print('mae:{}'.format(mean_absolute_error(yosoku, target)))

print('外れ値の混入')
yosoku = [2, 3, 5, 7, 11, 13, 46] # 実際には23だけど46と予測
target = [3, 5, 8, 11, 16, 19, 23]
mse = mean_squared_error(yosoku, target)
print('rmse:{}'.format(math.sqrt(mse)))
print('mae:{}'.format(mean_absolute_error(yosoku, target)))


# In[11]:


# データの準備
df = pd.read_csv('datafolda/Survived.csv')
df = df.fillna(df.mean(numeric_only=True))

x = df[['Pclass', 'Age']]
t = df['Survived']


# In[13]:


# モデルの準備
from sklearn import tree
model = tree.DecisionTreeClassifier(max_depth = 2,
random_state = 0)
model.fit(x, t)


# In[ ]:





# In[15]:


from sklearn.metrics import classification_report
pred = model.predict(x)
out_put = classification_report(y_pred = pred, y_true = t)
print(out_put)


# In[17]:


out_put = classification_report(y_pred = pred, y_true = t,
output_dict = True)

# out_putをデータフレームに変換
pd.DataFrame(out_put)


# In[25]:


df = pd.read_csv('datafolda/cinema.csv')
# 学習できないので欠損値処理だけ行う
df = df.fillna(df.mean())
x = df.loc[:, 'SNS1':'original']
t = df['sales']


# In[27]:


from sklearn.model_selection import KFold
kf = KFold(n_splits = 3, shuffle = True, random_state = 0)


# In[31]:


from sklearn.linear_model import LinearRegression
model = LinearRegression()

from sklearn.model_selection import cross_validate

result = cross_validate(model, x, t, cv = kf, scoring = 'neg_mean_squared_error',
return_train_score = True)
result


# In[15]:


sum(result['test_score']) / len(result['test_score'])


# In[33]:


from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits = 5,
    shuffle = True,random_state = 0)


# In[35]:


iris = pd.read_csv("datafolda/iris.csv")
iris = iris.fillna(iris.mean(numeric_only=True))
x = iris.loc[:,:"花弁幅"]
t = iris["種類"]
from sklearn.tree import DecisionTreeClassifier
model = DecisionTreeClassifier(random_state=0)
result = cross_validate(model, x, t, cv = skf, scoring = 'accuracy',
return_train_score = True)


# In[37]:


result


# In[ ]:





# In[55]:


# 練習問題
import pandas as pd
from sklearn.ensemble import RandomForestClassifier,AdaBoostClassifier
from sklearn.model_selection import train_test_split

# 追加
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_validate
import numpy as np #本書ではあまり紹介していないnumpyライブラリ

get_ipython().run_line_magic('matplotlib', 'inline')

df = pd.read_csv('Bank.csv')
# まず、ダミー変数化をしたいが、文字列の列が複数あるので抜き出す。
str_col_name=['job','default','marital','education','housing','loan','contact','month']
str_df = df[str_col_name]
#複数列を一気にダミー変数化
str_df2=pd.get_dummies(str_df,drop_first=True)

num_df = df.drop(str_col_name,axis=1)#数値列を抜き出す
df2 = pd.concat([num_df,str_df2,str_df],axis=1)#結合(今後の集計の利便性も考慮してstr_dfも結合しておく)
#訓練&検証データとテストデータに分割
train_val,test = train_test_split(df2,test_size=0.1,random_state=9)
train_val.head()


# In[56]:


#欠損値の補正
from sklearn.covariance import MinCovDet
num_df=train_val.drop(str_col_name,axis=1)
num_df=num_df.drop('id',axis=1)
num_df2=num_df.dropna()
mcd2 =MinCovDet(random_state=0,support_fraction=0.7)
mcd2.fit(num_df2)
dis =mcd2.mahalanobis(num_df2)
dis=pd.Series(dis)
dis.plot(kind="box")
no=dis[dis>300000].index
#先頭から2561番目が外れ値となる事が分かったので９章の付録で紹介したilocを利用する
no=num_df2.iloc[no[0]:(no[0]+1),:].index
train_val2 = train_val.drop(no)


# In[57]:


#欠損行を削除
not_nan_df = train_val2.dropna()#df2は外れ値が無いデータ
temp_t =not_nan_df[['duration']]
temp_x = not_nan_df.drop(str_col_name,axis=1)

#durationとyに関係があるという仮定が成り立つならば、適切な推定をするためには,
temp_x = temp_x.drop(['y','duration','id'],axis=1)
from sklearn.preprocessing import PolynomialFeatures

from sklearn.linear_model import Lasso,Ridge

a,b,c,d= train_test_split(temp_x,temp_t,random_state=0,test_size=0.2)
maxvalue=0
v=0
#今回はLasso回帰を利用するので、特徴量選択はしない
for i in range(1,42):
    val = i/20
    model_liner = Lasso(random_state=0,alpha=val)
    #今回は予測させたいだけなので、標準化はしない
    model_liner.fit(a,c)
    if maxvalue < model_liner.score(b,d):
        v=val
        maxvalue = model_liner.score(b,d)
print(v,maxvalue)
model_liner = Lasso(random_state=0,alpha=v)
#今回は予測させたいだけなので、標準化はしない
model_liner.fit(a,c)
#pd.Series(model_liner)


# In[58]:


#実際に使うのは外れ値込みのデータ
train_val3 = train_val.copy()
is_null=train_val3['duration'].isnull()
temp_x = train_val3.drop(str_col_name,axis=1)
temp_x = temp_x.drop(['y','duration','id'],axis=1)
temp_x = temp_x[is_null]
#non_x=train_val2.loc[is_null,['housing_yes','loan_yes','age','marital_single','job_student']]
pred_d = model_liner.predict(temp_x)
train_val3.loc[is_null,'duration']=pred_d


# In[59]:


#12章付録で紹介したアンダーサンプリングを行う
def under_sampling(train_val):
    y_0=train_val[train_val['y']==0]
    y_1=train_val[train_val['y']==1]
    num_1 = len(y_1)
    #Y=1と同じ件数だけサンプリング
    y_0_2 =y_0.sample(n=num_1,random_state=0)
    train_val2 = pd.concat([y_1,y_0_2])
    return train_val2


# In[60]:


#学習をさせよう。ただし、13章で学習した知識を使いたい。これまでは正解率を考えてきたが、今回のケースだと適合率
#再現率のどちらを見るべきだろうか？

# y=1の適合率が高い⇒無駄なアポイントメントを減らす事が出来る。
# y=1の再現率が高い⇒潜在顧客を見逃さない

#スッキリ銀行は、効率よくキャンペーンを回したいと考えているので、y=1適合率に着目する


# In[62]:


#まず、さくっと学習できるようなlearn関数を定義する。ただし、正解率では無くて適合率をみる
from sklearn.metrics import classification_report
from sklearn.tree import DecisionTreeClassifier
def learn(x,t,i):
    x_train,x_val,y_train,y_val = train_test_split(x,t,test_size=0.2,random_state=13)

    datas=[x_train,x_val,y_train,y_val]
    base = DecisionTreeClassifier(max_depth=i,random_state=0,class_weight="balanced")
    #model = AdaBoostClassifier(n_estimators=150,base_estimator=base,random_state=0)
    
    #　追加
    
    base.fit(x_train,y_train)
    train_pred = base.predict(x_train)
    test_pred = base.predict(x_val)
    result = classification_report(y_pred=test_pred,y_true=y_val,output_dict=True)
    return result,base,datas

t =train_val3['y']
x = train_val3.drop(str_col_name,axis=1)
x =x.drop(['id','y','day'],axis=1)
res,model,datas = learn(x,t,i=8)
res_df=pd.DataFrame(res)
res_df
#res_df.iloc[0,1]


# In[ ]:





# In[63]:


#適合率が低い。
# 12章で学習したランダムフォレストとアダブーストだとどうなるか？
def learn2(x,t,i,de=5,forest=True):
    x_train,x_val,y_train,y_val = train_test_split(x,t,test_size=0.2,random_state=13)

    datas=[x_train,x_val,y_train,y_val]
    model=None
    if forest:
        model = RandomForestClassifier(n_estimators=i,random_state=0,max_depth=de,class_weight="balanced")
    #datas=[x_train,x_val,y_train,y_val]
    else:
        base = DecisionTreeClassifier(max_depth=de,random_state=0,class_weight="balanced")
        model = AdaBoostClassifier(n_estimators=i,base_estimator=base,random_state=0)
    #model = AdaBoostClassifier(n_estimators=150,base_estimator=base,random_state=0)
    model.fit(x_train,y_train)
    train_pred = model.predict(x_train)
    test_pred = model.predict(x_val)
    result = classification_report(y_pred=test_pred,y_true=y_val,output_dict=True)
    return result,model,datas
t =train_val3['y']
x = train_val3.drop(str_col_name,axis=1)
x =x.drop(['id','y','day'],axis=1)


# In[64]:


#ランダムフォレストでの検証
print("=================random_forest=========================")
max_pre=0
for i in [50,100,150,200]:#esti
    for j in range(5,11):#depth
        res,model,datas = learn2(x,t,i=i,de=j,forest=True)
        res2=pd.DataFrame(res)
        pre = res2.iloc[0,1]
        if max_pre < pre:
            max_pre=pre
            print(max_pre,i,j)
        print(i,j,pre,"finish next_i")
#アダブーストでの検証
print("=================adaboost=========================")
max_pre=0
for i in [50,100,150,200]:#esti
    for j in range(5,11):#depth
        res,model,datas = learn2(x,t,i=i,de=j,forest=False)
        res2=pd.DataFrame(res)
        pre = res2.iloc[0,1]
        if max_pre < pre:
            max_pre=pre
            print(max_pre,i,j)
        print(i,j,pre,"finish next_i")


# In[65]:


#非常に時間がかかるので途中で終了。
#random_forestよりadaboostの方がvalデータの精度が良く、その中でもestimator=100,max_depth=8が最も高い

#estimatorの値を100と固定して、max_depthについての考察を深める。k-分割交差検証
#で最適なmax_depthを考察するｂ
def learn_k_valid(x,t,i,dep):
    base = DecisionTreeClassifier(max_depth=dep,random_state=0,class_weight="balanced")
    model = AdaBoostClassifier(n_estimators=150,base_estimator=base,random_state=0)
    kv = StratifiedKFold(n_splits=3,shuffle=True,random_state=0)
    result = cross_validate(model,x,t,cv=kv,scoring='precision',return_train_score=True)
    
    #base.fit(x_train,y_train)
    #train_pred = base.predict(x_train)
    #test_pred = base.predict(x_val)
    #result = classification_report(y_pred=test_pred,y_true=y_val,output_dict=True)
    return result


# In[66]:


t =train_val3['y']
x = train_val3.drop(str_col_name,axis=1)
x =x.drop(['id','y','day'],axis=1)
for j in range(2,10):
    res = learn_k_valid(x,t,i=100,dep=j)
    res2=res["train_score"]
    print(j,sum(res2)/len(res2),end="  ")#平均値    
    res3=res["test_score"]
    
    print(j,sum(res3)/len(res3))#平均値
    print(" j end next")


# In[67]:


#検証データの適合率が最も良いのは深さ9だが、明らかに過学習している。
# アンダーサンプリングで不均衡データの影響が変わるか確認してみる


# In[68]:


train_val4 = under_sampling(train_val3)
t =train_val4['y']
x = train_val4.drop(str_col_name,axis=1)
x =x.drop(['id','y','day'],axis=1)
for j in range(2,10):
    res = learn_k_valid(x,t,i=100,dep=j)
    res2=res["train_score"]
    print(j,sum(res2)/len(res2),end="  ")#平均値    
    res3=res["test_score"]
    
    print(j,sum(res3)/len(res3))#平均値
    print(" j end next")


# In[81]:


#深さ2~３当たりが最もよさそうである。
#テストデータで検証するために再学習


# In[69]:


train_val4=under_sampling(train_val3)
t =train_val4['y']
x = train_val4.drop(str_col_name,axis=1)
x =x.drop(['id','y','day'],axis=1)
base_model = RandomForestClassifier(max_depth=3,random_state=0,class_weight="balanced")
model = AdaBoostClassifier(random_state=0,n_estimators=100,base_estimator=base_model)
model.fit(x,t)


# In[ ]:





# In[70]:


#テストデータ
test2 = test.copy()    
isnull=test2['duration'].isnull()
print(isnull.shape)
if isnull.sum()>0:
    temp_x = test2.drop(str_col_name,axis=1)
    temp_x = temp_x.drop(['y','duration','id'],axis=1)
    temp_x = temp_x[isnull]
    pred_d = model_liner.predict(temp_x)
    test2.loc[isnull,'duration']=pred_d    
x_test = test2.drop(str_col_name,axis=1)
x_test =x_test.drop(['id','y','day'],axis=1)
y_test = test['y']


# In[71]:


pre = model.predict(x_test)
result= classification_report(y_pred=pre,y_true=y_test,output_dict=True)
pd.DataFrame(result)


# In[72]:


#y=1の適合率は0.64


# In[73]:


#本書で紹介していないnumpyのテクニックを使っているが
#同様の事はpandasでもできる
#参考　予測確率の閾値を変更する事により予測結果を変えて調整する
#確率でいったん予測させる
y_p = model.predict_proba(x)
y_p
a=y_p[:,1]#y=1の確率を抜き出す
def conf(a,th=0.5):
    import numpy as np
    y_pre=np.where(a<th,0,1)#閾値以下なら0,以上なら1
    from sklearn.metrics import confusion_matrix
    #混同行列をscikit-learnの関数で作成
    mat= confusion_matrix(y_pred=y_pre,y_true=t)
    pre = mat[1,1]/(mat[1,1]+mat[0,1])
    re = mat[1,1]/(mat[1,1]+mat[1,0])
    f1 = 2*(pre*re)/(pre+re)
    return pre,f1,mat#適合率、ｆ１スコア、混同行列
conf(a,0.5)#閾値0.5


# In[74]:


#presitionを上げるためには閾値をもう少しあげればよい
#ただし、閾値を上げすぎると適合率が低下してしまうのでf1スコアも意識する
for i in range(1,30):
    val = 0.50+(i/1000)
    print(i)
    b=conf(a,val)#閾値0.5
    print(val,b[0],b[1])


# In[75]:


#閾値を0.503にすると全体的に最もよさそう。
th=0.503
#テストデータ
proba = model.predict_proba(x_test)


# In[76]:


a = proba[:,1]
pre=np.where(a<th,0,1)
result= classification_report(y_pred=pre,y_true=y_test,output_dict=True)
pd.DataFrame(result)


# In[ ]:




