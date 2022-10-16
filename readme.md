# 项目：
Angel_scrapy
### 项目简介

基于关键词搜索 爬取angel.co网站的公司信息

### 项目源码

### 项目启动

```
pip freeze > requirements.txt

# 拉取代码后 进入主目录
pip install requirements
```

### 代码结构

```python
"""
| - items.py
| - log -- 日志
|| - 2022108.log --日志
|| - waitKeyword.txt --未搜索到关键词
| - middlewares.py
| - pipelines.py --mongodb存储
| - settings.py --配置
| - spiders --爬虫
|| - company.py
|| - __pycache__
||| - company.cpython-38.pyc
| - test.py
"""
```

### 系统模块

#### 爬虫parse

```python
"""
def search_parse():
	解析搜索页面...
    yield Request( callback=self.company_parse)
def company_parse():
    解析公司详情页面...
	yield company_item"""
```

。。。



