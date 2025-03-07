#!/usr/bin/env python
# coding: utf-8

# In[7]:


import polars as pl
import matplotlib.pyplot as plt
df = pl.read_csv('cinema.csv')
df.head(3)


# In[3]:


df.null_count()


# In[5]:


df2 = df.fill_null(strategy='mean')


# In[9]:


plt.scatter(df2.get_column('SNS1'), df2.get_column('sales'))


# In[19]:


for col in df2.columns:
    plt.scatter(df2.get_column(col), df2.get_column('sales'))
    plt.xlabel(col)
    plt.ylabel("sales")
    plt.show()


# In[91]:


no = df2.with_row_index().filter(
    (pl.col('SNS2') > 1000) & (pl.col('sales') < 8500)
).select('index')[0,0]


# In[97]:


df3 = df2.with_row_index().filter(
    pl.col('index') != no
).select(
    pl.all().exclude('index')
)


# In[103]:


df3[2, 'SNS1']


# In[147]:


df3['SNS1':'original']


# In[131]:


df.with_columns(df.sum_horizontal().alias('total'))


# In[143]:


df.columns[df.columns.index("SNS1"):]


# In[ ]:




