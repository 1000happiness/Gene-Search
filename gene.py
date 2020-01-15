
# coding: utf-8

# In[28]:

# 引入所需要的库
import pandas as pd
import numpy as np
import requests
import time
import copy


# In[115]:

# 读取数据：第一个是文件名，第二个是表名
data = pd.read_excel("data.xlsx", sheet_name="H37RV 基因ID")
# data = pd.read_excel("data.xlsx", sheet_name="Sheet1") # 测试用
data


# In[116]:

# 将ID设置为索引
data.set_index(["ID"],inplace=True)


# In[117]:

# 显示数据
data


# In[118]:

# 函数定义
# 作用：根据ID号，发请求进行查询并进行结果处理
# 参数：gene的ID号
# 返回值：
#   1. Gene symbol
#   2. Locus tag
#   3. raw string（这个string是返回的html文件中包含symbol和tag的部分，主要是为了方便后面的人工校验）
# 补充：
#   1.如果一个请求超过100秒没有响应则会丢弃，但是此处没有写丢弃的错误处理

def requestAGene(id):
    response = requests.request("get", "https://www.ncbi.nlm.nih.gov/gene/?term=" + str(id), timeout = 100)
    text = str(response.text.encode("utf-8"))
    
    # 提取raw string
    index = text.find("Gene symbol")
    text = text[index: index + 250]
    raw = copy.deepcopy(text)
    s1 = raw[0: raw.find("Gene description")]
    s2 = raw[raw.find("Locus tag"): -1]
    raw = s1 + s2

    # 提取gene symbol
    symbol_index_begin = text.find("<dd class=\"noline\">") + 19
    symbol_index_end = text.find("</dd>")
    symbol = text[symbol_index_begin:symbol_index_end]

    # 提取Locus tag
    index = text.find("Locus tag")
    text = text[index: -1]
    tag_index_begin = text.find("<dd>") + 4
    tag_index_end = text.find("</dd>")
    tag = text[tag_index_begin:tag_index_end]

    # 显示并返回数据
    print(symbol, tag)
    return symbol, tag, raw
    

# In[120]:

# 遍历整个表，如果发现某一行的为空"Gene symbol"（NaN），则调用上面的函数得到这一个gene ID的相关信息，并写入表格

for row in data.iterrows():
    # 此处判断是否为空利用了NaN特性：(NaN == NaN)为false
    if(not row[1]["Gene symbol"] == row[1]["Gene symbol"]):
        time.sleep(1)
        print("request for :", row[0])
        symbol, tag, raw = requestAGene(row[0])
        data.loc[row[0],"Gene symbol"] = symbol
        data.loc[row[0],"Locus tag"] = tag
        data.loc[row[0],"Raw"] = raw


# In[121]:

# 显示最终的数据
data


# In[122]:

# 将数据写入文件
data.to_excel("result.xlsx", sheet_name="Result")

