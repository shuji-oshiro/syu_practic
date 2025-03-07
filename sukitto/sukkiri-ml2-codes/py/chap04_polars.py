#!/usr/bin/env python
# coding: utf-8

# In[1]:


import polars as pl


# In[3]:


data = {
    '松田': [160,160],
    '浅木': [161, 175]
}
df = pl.DataFrame(data)
df


# In[5]:


df.shape


# In[7]:


df.columns = ['松田の労働時間(h)', '浅木の労働時間(h)']
df


# In[9]:


df.columns


# In[13]:


df.get_column_index('松田の労働時間(h)')


# In[35]:


data = {
    '松田': [160,160],
    '浅木': [161, 175]
}
df = pl.DataFrame(data,schema=["AA","BB"])
df


# In[37]:


df = pl.read_csv("KvsT.csv")
df


# In[89]:


df.select('身長', '派閥')


# In[93]:


df.select(
    '派閥'
)


# In[95]:


x = df.select('身長', '体重', '年代')
t = df.select('年代')


# In[97]:


from sklearn.tree import DecisionTreeClassifier


# In[99]:


model = DecisionTreeClassifier()
model.fit(x,t)


# In[101]:


model.score(x, t)

