#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
df = pd.read_csv('../datafiles/bike.tsv')
df.head()


# In[2]:


df = pd.read_csv('../datafiles/bike.tsv',sep="\t")
df.head(2)


# In[3]:


df2=pd.read_csv("../datafiles/weather.csv")


# In[4]:


weather = pd.read_csv("../datafiles/weather.csv",encoding="shift-jis")
weather


# In[5]:


temp= pd.read_json("../datafiles/temp.json")
temp.head(2)


# In[6]:


print(temp.T)


# In[7]:


df2=df.merge(weather,how="inner",on="weather_id")
# df2 = df2.sort_values(by='dteday') # 行の順番がweather_id順になってしまうため
df2.head(2)


# In[8]:


df2.groupby("weather")['cnt'].mean()


# In[9]:


temp=temp.T
temp.loc[199:201]


# In[10]:


df2[df2['dteday']=='2011-07-20']


# In[11]:


df3 = df2.merge(temp,how="left",on="dteday")
df3[df3["dteday"]=='2011-07-20']


# In[12]:


df3[df3['atemp'].isnull()]


# In[13]:


df3["temp"].plot()


# In[14]:


df3[["temp","hum"]].plot()
# plt.savefig("code10-13.png")


# In[15]:


df3["temp"].plot(kind="hist")
df3["hum"].plot(kind="hist",alpha=0.5)


# In[ ]:





# In[16]:


df3['atemp'].loc[695:705].plot(kind='line')


# In[17]:


#atemp列のdtypeをfloatに変換
df3["atemp"] = df3["atemp"].astype(float)


df3["atemp"] =df3["atemp"].interpolate()
df3.loc[695:705,"atemp"].plot()


# In[20]:


iris_df = pd.read_csv('../datafiles/iris.csv')
non_df = iris_df.dropna() # 欠損値を含む行を削除

iris_df.isnull().sum()


# In[21]:


from sklearn.linear_model import LinearRegression
x = non_df.loc[:,"がく片幅":"花弁幅" ]
t = non_df['がく片長さ']
model = LinearRegression()
model.fit(x,t) # 欠損値予測のためのモデルを予測


# In[22]:


# 欠損行の抜き出し
condition = iris_df['がく片長さ'].isnull()
non_data = iris_df.loc[ condition ]


# 欠損の予測に利用する特徴量だけを抜き出して、モデルで予測
x = non_data.loc[:,"がく片幅":"花弁幅"]
pred = model.predict(x)


# # 欠損行のがく片長さ(cm)のマスを抜き出して、predで代入
iris_df.loc[condition,'がく片長さ']=pred


# In[23]:


x = non_data.loc[:,"がく片幅":"花弁幅"]
pred = model.predict(x)
pred


# In[ ]:





# In[24]:


from sklearn.covariance import MinCovDet

#数値列を適当に取り出す
df4=df3.loc[:,"atemp":"windspeed"]
df4=df4.dropna()#欠損値を削除

#df4に対して、各データの中心点からのマハラノビス距離を計算

mcd = MinCovDet(random_state=0,support_fraction=0.7)
mcd.fit(df4)
#マハラノビス距離
distance = mcd.mahalanobis(df4)
distance


# In[25]:


distance=pd.Series(distance)
distance.plot(kind="box")


# In[26]:


tmp=distance.describe()#様々な基本統計量を計算
tmp


# In[27]:


IQR = tmp['75%'] -tmp['25%']#IQR計算
jougen = 1.5*(IQR) + tmp['75%'] # 上限値
kagen = tmp['25%'] -1.5*(IQR) # 下限値

# 上限と下限の条件をもとに、シリーズで条件検索
outliner = distance[ (distance > jougen) | (distance < kagen) ]
outliner


# In[28]:


730*0.25


# In[29]:


distance[ (distance > jougen)].shape


# In[30]:


# 演習問題


# In[ ]:





# In[31]:


import pandas as pd
from sklearn import tree
from sklearn.model_selection import train_test_split
get_ipython().run_line_magic('matplotlib', 'inline')


# In[33]:


df = pd.read_csv('../datafiles/Bank.csv')
print(df.shape)
df.head()


# In[34]:


# まず、ダミー変数化をしたいが、文字列の列が複数あるので抜き出す。
str_col_name=['job','default','marital','education','housing','loan','contact','month']
str_df = df[str_col_name]
#複数列を一気にダミー変数化
str_df2=pd.get_dummies(str_df,drop_first=True)

num_df = df.drop(str_col_name,axis=1)#数値列を抜き出す
df2 = pd.concat([num_df,str_df2,str_df],axis=1)#結合(今後の集計の利便性も考慮してstr_dfも結合しておく)


# In[35]:


#訓練&検証データとテストデータに分割
train_val,test = train_test_split(df2,test_size=0.1,random_state=9)
train_val.head()


# In[36]:


#欠損値の確認
is_nan=train_val.isnull().sum()
#欠損が存在している列だけ表示
is_nan[is_nan>0]


# In[ ]:





# In[37]:


# 改善案1  欠損値の補完方法を線形回帰で行ってみる。


# In[42]:


train_val.corr(numeric_only=True)['duration'].map(abs).sort_values(ascending=False)


# In[43]:


#特徴量の当たりがついた
#しかし、そもそもこの線形回帰は外れ値の影響を強く受けるので調べる。
num_df=train_val.drop(str_col_name,axis=1)
num_df=num_df.drop('id',axis=1)
num_df2=num_df.dropna()
mcd2 =MinCovDet(random_state=0,support_fraction=0.7)
mcd2.fit(num_df2)


# In[44]:


dis =mcd2.mahalanobis(num_df2)
dis=pd.Series(dis)
dis.plot(kind="box")


# In[45]:


print(dis[0:3])#先頭は0番からのラベル
no=dis[dis>300000].index
no[0]


# In[46]:


#先頭から2561番目が外れ値となる事が分かったので９章の付録で紹介したilocを利用する
no=num_df2.iloc[no[0]:(no[0]+1),:].index
train_val2 = train_val.drop(no)


# In[47]:


train_val2.corr(numeric_only=True)['duration'].map(abs).sort_values(ascending=False)


# In[48]:


#monthはdurationに本質的に影響あるとは思えないので特徴量を
#housing_yes ,loan_yes,age,marital_single ,job_student    とする。（ｙは最終的な正解データなので除外）    


# In[49]:


#欠損行を削除
not_nan_df = train_val2.dropna()
temp_t =not_nan_df['duration']
temp_x = not_nan_df[['housing_yes','loan_yes','age','marital_single' ,'job_student']]
# 線形回帰
from sklearn.linear_model import LinearRegression
model_liner = LinearRegression()

a,b,c,d= train_test_split(temp_x,temp_t,random_state=0,test_size=0.2)

#今回は予測させたいだけなので、標準化はしない
model_liner.fit(a,c)
print(model_liner.score(a,c),model_liner.score(b,d))


# In[50]:


# コード修正(不要なので削除)
# tain_val2 = train_val.copy()

is_null=train_val2['duration'].isnull()
non_x=train_val2.loc[is_null,['housing_yes','loan_yes','age','marital_single','job_student']]
pred_d = model_liner.predict(non_x)
train_val2.loc[is_null,'duration']=pred_d


# In[51]:


#ヒストグラムの確認
train_val2.loc[train_val['y']==0,"duration"].plot(kind="hist")
train_val2.loc[train_val['y']==1,"duration"].plot(kind="hist",alpha=0.4)

#y=1の方が、durationが大きい傾向がやっぱりありそう


# In[52]:


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


# In[53]:


t =train_val2['y']
x = train_val2.drop(str_col_name,axis=1)
x =x.drop(['id','y','day'],axis=1)


# In[54]:


#とりあえず、for文で様々な木の深さでの正解率を調べてみる
for i in range(1,15):
    s1,s2,model,datas = learn(x,t,i)
    print(i,s1,s2)


# In[ ]:





# In[55]:


#テストデータでも調べる
test2 = test.copy()
isnull=test2['duration'].isnull()
model_tree=tree.DecisionTreeClassifier(random_state=10,max_depth=10,class_weight="balanced")
if isnull.sum()>0:
    temp_x=test2.loc[isnull,['housing_yes','loan_yes','age','marital_single','job_student']]
    pred_d = model_liner.predict(temp_x)
    test2.loc[isnull,'duration']=pred_d
x_test = test2.drop(str_col_name,axis=1)
x_test =x_test.drop(['id','y','day'],axis=1)
y_test = test['y']

model.score(x_test,y_test)


# In[56]:


#9章の最後より若干低下している


# In[57]:


#どのような間違い方をしているのか確認
s1,s2,model,datas = learn(x,t,9)

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


# In[58]:


#訓練データと検証データの間違い型の傾向を調べる


# In[59]:


#値にばらつきが大きいので、標準化してもう一度グラフ化
from sklearn.preprocessing import StandardScaler

sc = StandardScaler()
tmp2=train_val2.drop(str_col_name,axis=1)
sc_data = sc.fit_transform(tmp2)
sc_df = pd.DataFrame(sc_data,columns=tmp2.columns,index=tmp2.index)

######挿入箇所#######
pre = model.predict(sc_df.drop(["id","day","y"],axis=1))
target = tmp2["y"]
true = (pre == target)
false = (pre!= target)
############

true_df=sc_df.loc[true]
false_df=sc_df.loc[false]
true_df
temp2=pd.concat([false_df.mean()["age":],true_df.mean()["age":]],axis=1)
temp2.plot(kind="bar")


# In[60]:


print(train_val2.groupby('loan')['y'].mean())
print(train_val2.groupby('housing')['y'].mean())


# In[61]:


train_val3=train_val2.copy()
train_val3['du*hou']=train_val3['duration']*train_val3['housing_yes']
train_val3['du*loan']=train_val3['duration']*train_val3['loan_yes']
train_val3['du*age']=train_val3['duration']*train_val3['age']


# In[62]:


t =train_val3['y']

monthcol=['month_aug',
       'month_dec', 'month_feb', 'month_jan', 'month_jul', 'month_jun',
       'month_mar', 'month_may', 'month_nov', 'month_oct', 'month_sep']
jobcol=['job_entrepreneur', 'job_housemaid', 'job_management', 'job_retired',
       'job_self-employed', 'job_services', 'job_student', 'job_technician',
       'job_unemployed', 'job_unknown']
x = train_val3.drop(str_col_name,axis=1)
x = x.drop(jobcol,axis=1)

x = x.drop(monthcol,axis=1)
x =x.drop(['id','y','day'],axis=1)
x.columns


# In[ ]:





# In[63]:


#とりあえず、for文で様々な木の深さでの正解率を調べてみる
for i in range(5,15):
    s1,s2,model,datas = learn(x,t,i)
    print(i,s1,s2)


# In[64]:


s1,s2,model,datas = learn(x,t,9)
tmp,a=syuukei(model,datas,False)
a


# In[65]:


pd.Series(model.feature_importances_,index=x.columns)


# In[66]:


i=9
model = tree.DecisionTreeClassifier(random_state=i,max_depth=i,class_weight="balanced")
model.fit(x,t)


# In[67]:


#テストデータでも調べる
test2 = test.copy()
isnull=test['duration'].isnull()
if isnull.sum()>0:
    temp_x=test2.loc[isnull,['housing_yes','loan_yes','age','marital_single','job_student']]
    pred_d = model_liner.predict(temp_x)
    test2.loc[isnull,'duration']=pred_d

test2['du*hou']=test2['duration']*test2['housing_yes']
test2['du*loan']=test2['duration']*test2['loan_yes']
test2['du*age']=test2['duration']*test2['age']

x_test = test2.drop(str_col_name,axis=1)
x_test = x_test.drop(jobcol,axis=1)
x_test = x_test.drop(monthcol,axis=1)
x_test =x_test.drop(['id','y','day'],axis=1)
y_test = test['y']
x_test.columns
model.score(x_test,y_test)


# In[68]:


# 直観的に考えて、9章では、housingとloanで集計しており、今回の線形回帰では、それらの列も含まれているから、
# durationの性能はよりよくなるはず、でも全体のモデルの正解率は1%ほど低下している

#原因の仮説⇒ １．現状の線形回帰だと訓練&検証に過学習してしまい、テストデータにフィットしない。
                 #（そもそもテストデータではdurationがあまり関係していない？？）
#            2. 純粋な決定木の限界？

#            3. 現在考慮していない特徴量ももっとしっかりした方が良いのか？？

#次以降の章で仮説1,2について検討できるので、次章に続く。


# In[ ]:




