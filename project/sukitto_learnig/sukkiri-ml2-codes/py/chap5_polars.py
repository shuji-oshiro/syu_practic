#!/usr/bin/env python
# coding: utf-8

# In[1]:


import polars as pl


# In[209]:


df = pl.read_csv("iris.csv")
df.head(3)


# In[211]:


df.get_column("種類").unique()


# In[213]:


df.get_column("種類").value_counts()


# In[215]:


df.tail(3)


# In[217]:


df.with_columns(
    [ pl.col(col).is_null() for col in df.columns ]
)


# In[219]:


df.with_columns(
    [ pl.col(col).is_null() for col in df.columns ]
).sum()


# In[221]:


df.null_count()


# In[223]:


df.drop_nulls()


# In[227]:


df.filter(
    ~pl.all_horizontal(
        pl.all().is_null()
    )
)


# In[241]:


df.with_columns(
    pl.col("花弁長さ").fill_null(0)
)


# In[243]:


df.mean()


# In[245]:


df.fill_null(strategy='mean')


# In[ ]:




