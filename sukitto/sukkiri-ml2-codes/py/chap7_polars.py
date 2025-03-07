#!/usr/bin/env python
# coding: utf-8

# In[1]:


import polars as pl

df = pl.read_csv("Survived.csv")
df.head(2)


# In[5]:


df.get_column("Survived").value_counts()


# In[7]:


df.null_count()


# In[19]:


df = df.with_columns(
    pl.col("Age").fill_null(strategy='mean'),
    pl.col("Embarked").fill_null(
        pl.col("Embarked").mode()
    )
)


# In[23]:


x = df.select(
    ['Pclass', 'Age', 'SibSp', 'Parch', 'Fare']
        
)

t = df.get_column('Survived')


# In[25]:


df2 = pl.read_csv(
    'Survived.csv')


# In[29]:


df2.get_column('Age').median()


# In[33]:


df2.group_by('Survived').agg(
    pl.col('Age').mean()
)


# In[35]:


df2.group_by('Pclass').agg(
    pl.col('Age').mean()
)


# In[65]:


df2.pivot(
    on='Pclass', index='Survived',values="Age",
    aggregate_function='mean', sort_columns=True
)


# In[69]:


def condition(pclass:int, survived:int) -> pl.Expr:
    condition1 = (pl.col('Pclass') == pclass)
    condition2 = (pl.col('Survived') == survived)
    condition3 = (pl.col('Age').is_null())
    return condition1 & condition2 & condition3



# In[101]:


df2 = df2.with_columns(
    pl.when(condition(1, 0)).then(43).
    when(condition(1, 1)).then(35).
    when(condition(2, 0)).then(33).
    when(condition(2, 1)).then(25).
    when(condition(3, 0)).then(26).
    when(condition(3, 1)).then(20).
    otherwise(pl.col("Age")).alias("Age")
)


# In[ ]:





# In[156]:


df3 = df2.clone()

df3.columns = [ c+"_" for c in df3.columns]

x_temp = pl.concat([df2, df2.select("Sex").to_dummies(drop_first=True)],how="horizontal")


# In[162]:


x_new = x_temp.drop("Sex")


# In[ ]:




