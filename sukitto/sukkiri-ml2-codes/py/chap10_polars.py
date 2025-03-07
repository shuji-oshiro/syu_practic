#!/usr/bin/env python
# coding: utf-8

# In[1]:


import polars as pl


# In[3]:


df


# In[176]:


df = pl.read_csv('bike.tsv', separator='\t')
df2 = pl.read_csv('weather.csv', encoding='shift-jis')
df = df.join(df2, left_on='weather_id', right_on='weather_id')
df = df.drop('weather_id')
df.tail(10)


# In[182]:


# 金曜か土曜ならば１とする週末フラグ列を作ってください。
df = df.with_columns(
    pl.when((pl.col("weekday")==5) | (pl.col("weekday")==6)).then(1).otherwise(0).alias("weekend")
)


# In[190]:


df.filter(pl.col("workingday")==1).group_by("weather").agg(pl.col("cnt").sum())


# In[174]:


df.filter(pl.col("workingday") == 1).group_by("weather").agg(
     pl.col("cnt").mean()
)


# In[53]:


df3 = df.select('dteday','holiday')
df4 = df.select('weekday','workingday')

# 横に結合
pl.concat([df3, df4], how='horizontal')


# In[100]:


df.get_column('cnt').map_elements(lambda x: (round(x, -1)), return_dtype=pl.Int64)


# In[41]:


# 縦方向に結合
pl.concat([df2, df2])


# In[114]:


df = pl.read_csv('Bank.csv')
# df.select(
#     'age', 'amount', 'job'
    
# ).filter()

df.null_count()


# In[ ]:




