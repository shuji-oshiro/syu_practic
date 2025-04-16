#!/usr/bin/env python
# coding: utf-8

# In[5]:


import polars as pl


df = pl.read_csv('Boston.csv')
df.head()


# In[8]:





# In[7]:


df.get_column('CRIME').value_counts()


# In[17]:


crime = df.select('CRIME').to_dummies(drop_first=True)
df2 = pl.concat([df,crime], how="horizontal").drop('CRIME')
df2.head()


# In[21]:


from sklearn.model_selection import train_test_split

train_val, test = train_test_split(df2, test_size=0.2, random_state=0)


# In[23]:


train_val.null_count()


# In[25]:


train_val2 = train_val.fill_null(strategy='mean')


# In[29]:


import matplotlib.pyplot as plt

for col in train_val2.columns:
    plt.scatter(train_val2.get_column(col), train_val2.get_column('PRICE'))
    plt.show()


# In[43]:


out_line1 = (pl.col('RM') < 6) & (pl.col('PRICE') > 40) 

out_line2 = (pl.col('RM') > 18) & (pl.col('PRICE') > 40) 



train_val3 = train_val2.filter(
    ~(out_line1) & ~(out_line2)
)

train_val4 = train_val3.select(
    ['INDUS', 'NOX', 'RM', 'PTRATIO', 'LSTAT', 'PRICE']
)
train_val4.head()


# In[65]:


train_val4.corr().select(
    pl.col('PRICE').map_elements(abs, return_dtype=pl.Float32).alias("corr")
).with_columns(
    pl.Series(train_val4.columns).alias("col")
).sort("corr", descending=True)


# In[ ]:


train_val4.with_columns


# In[ ]:





# In[73]:


train_val3.select(
    
        ['RM', 'PTRATIO', 'LSTAT', 'INDUS',
            (pl.col('RM')**2).alias("RM^2")
        ]
    
)


# In[79]:


data = train_val3.select(
    
        ['RM', 'PTRATIO', 'LSTAT', 'INDUS',
            
        ]
    
)
pl.concat([data]).shape


# In[109]:


simple_data = pl.DataFrame([{
                "A":1.0,
               "B":1.0,
               "C":1.0,
               "D":1.0}],
            )
simple_data.columns = data.columns
pl.concat([data, simple_data])


# In[113]:


train_val3.select(
    
        ['RM', 'PTRATIO', 'LSTAT', 'INDUS',
            (pl.col('RM')**2).alias("RM^2"),
            (pl.col('RM') * pl.col("LSTAT")).alias("RM*lstat"),
         pl.col("RM").cast(pl.Int64).alias("rm_int")
         
        ]
    
)


# In[129]:


df = pl.DataFrame({
    "group": ["A", "A", "B", "B", "C", "C"],
    "value": [10, 20, 30, 40, 50, 60]
})

# # グループごとの平均を計算
df_with_avg = df.with_columns(
    pl.col("value").mean().over("group").alias("group_avg")
)

df_with_avg


# In[137]:


import polars as pl
df = pl.DataFrame({
    "group": ["A", "A", "B", "B", "C", "C"],
    "value": [10, 20, 30, 40, 50, 60]
})
df.head(2)

