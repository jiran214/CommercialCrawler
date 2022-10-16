# 打印文档树
import datetime
import os
from company_scrapy.settings import db
from company_scrapy.public import keywords

def join(path, item):
    if path == '.':
        return item
    return os.path.join(path, item)


def print_file_tree(path='.', level=1):
    items = os.listdir(path)

    for item in items:
        fill_path = join(path, item)
        print('|' * level, '-', item)
        if os.path.isdir(fill_path):
            print_file_tree(fill_path, level + 1)

def save_keywords():
    collection = db['seeds']

    data={}

    time = datetime.datetime.now()

    data = {}
    data['crawled_website'] = 'g2.com'
    data['seeds'] = []
    data['last_crawled_time'] = time
    data['created_time'] = time

    data['seeds']  = [{'seed':filed,'state':0} for filed in keywords.g2]
    collection.insert_one(data)

def find_keywords():
    collection = db['seeds']
    res = collection.find_one({'crawled_website':'g2.com'})
    return res

def update_seeds():
    collection = db['seeds']
    data = {}
    time = datetime.datetime.now()
    data['crawled_website'] = 'g2.com'
    data['seeds'] = []
    data['last_crawled_time'] = time
    data['created_time'] = time

    data['seeds'] = [{'seed': filed, 'stat': 0} for filed in keywords.g2]
    collection.update_one({'crawled_website': 'g2.com'}, {'$set': data}, True)

def update_seed():
    collection = db['seeds']
    collection.update_one(
        {'crawled_website': 'g2.com','seeds.seed':'plume'},
        {'$set': { "seeds.$.stat" : -1} }
    )

def get_url():
    url = 'https://www.g2.com/products/matillion-etl/reviews'

    s =url.split('/')
    t =s[-2]
    u = '/{}/{}'.format(s[-3],s[-2])

    url ='https://www.grubmarket.com/wholesaleware/#/home/product'
    s =url.split('/')[2].split('.')
    g = s[1]+'.'+s[2]
    print(g)

def check():
    collection = db['seeds']
    seeds = collection.find_one({'crawled_website': 'g2.com'})

    """seed集合检查"""
    website = seeds['crawled_website']
    seeds_num = len(seeds['seeds'])
    print('爬取网站:%s\n种子数量:%d' % (website, seeds_num))

    """seed状态检查"""
    states={
        '-1':[],
        '0':[],
        '1':[],
        '2':[]
    }
    for seed in seeds['seeds']:
        states[str(seed['state'])].append(seed['seed'])
    for i in range(-1,3):
        print('状态:',i,states[str(i)])

    """seed最新版本数据验证"""
    collection1 = db['org']
    try:
        res = collection1.find(
            {'history.0.keyword':  {"$in": states['1']}},
            {
                'history': {"$slice": -1},
            }
        )
    except Exception as e:
        print(e)

    saved_seed = []
    check_res = []

    for data in res:
        null_data = []  # 空数据
        error_data = []  # 错误数据

        latest_data = data['history'][0]

        nested_fields = ('topRepresented', 'categories', 'popularMentions', 'competitors', 'features',)  # 嵌套字段

        latest_form_data = {
            **latest_data,
            **{filed: latest_data[filed] for filed in nested_fields}
        }

        for filed, val in latest_form_data.items():
            if filed == 'keyword':
                saved_seed.append(val)
            if val in ('', None, 0):
                null_data.append(filed)

            else:
                if filed in ('popularMentions', 'competitors', 'features'):
                    for array in latest_data[filed]:
                        if array is not dict:
                            break
                        for filed_, val in array.items():
                            if val in ('', None, 0):
                                null_data.append(filed+'的'+filed_)

        check_res.append({
            'name':data['name'],
            'null':null_data,
            'link':latest_data['link']
        })

    error_seeds = set(states['1']) - set(saved_seed)  # 异常数据：state显示数据入库的seed，数据库实际存储seed不同步 输出差集
    print('异常数据:', error_seeds)

    print('数据报告:',check_res)

if __name__ == '__main__':
    # a={
    #     'b':1
    #     ,'a':2
    # }
    # update_seeds()
    # save_keywords()
    check()
    # add_dict()
    # get_url()
    # print(hasattr(f,'s'))