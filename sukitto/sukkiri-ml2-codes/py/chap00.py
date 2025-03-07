#!/usr/bin/env python
# coding: utf-8

# # 練習問題解答

# In[1]:


height = int(input('身長(cm)を入力してください>>'))
weight = int(input('体重(kg)を入力してください>>'))

height = height / 100 # mに変換

# ( )をつけなくてもよいが可読性のため( )をつける
bmi = weight / (height ** 2)

print(f'あなたのbmiは{bmi}')


# In[3]:


# 手順1：3科目の試験得点を管理するリストを1つ作成
scores = []
# 手順2：国語の試験得点をキーボードから入力
japanese = int(input('国語の試験得点>>'))
#手順3：国語の得点を手順1で作成したリストに追加
scores.append(japanese)
# 手順4：数学の試験得点をキーボードから入力
math = int(input('数学の試験得点>>'))
# 手順5：数学の得点を手順１で作成したリストに追加
scores.append(math)
# 手順6：英語の試験得点をキーボードから入力
english = int(input('英語の試験得点>>'))
# 手順7：英語の得点を手順1で作成したリストに追加
scores.append(english)
# 手順8：リストの一覧を表示
print(scores)
# 手順9：リストの合計値を計算して表示
total = sum(scores)
print('合計得点:{}点 '.format(total))


# In[4]:


number = int(input('整数を入力してください'))

if number % 2 == 0:
    print('偶数')
else:
    print('奇数')


# In[6]:


data = input('please input data >> ')

if data == 'こんにちは':
    print('ようこそ！')
elif data == '景気は？':
    print('ぼちぼちです')
elif data == 'さようなら':
    print('お元気で！')
else:
    print('どうしました？')


# In[7]:


for i in range(10):
    print('{}, '.format(10 - i), end = ' ')
print('Lift Off!!')


# In[4]:


# 手順1
scores = []
# 手順2
for i in range(10):
    score = int(input(f'{i + 1}人目の試験得点 >> '))
    scores.append(score)
# 手順3
final_scores = [ ]
for score in scores:
    tmp = score * 0.8 + 20
    final_scores.append(tmp)

# 手順4
avg = sum(final_scores) / len(final_scores)
print(f'平均点は{avg}点')


# In[1]:


def uruu(year):
    result = None
    if year % 400 == 0:
        result = True
    elif year % 100 == 0:
        result = False
    elif year % 4 == 0:
        result = True
    else:
        result = False

    return result


# In[ ]:





# In[2]:


get_ipython().system('jupyter nbconvert --to python chap00.ipynb')


# In[ ]:




