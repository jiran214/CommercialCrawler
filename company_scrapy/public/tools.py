import datetime
import hashlib
import time

import requests

from company_scrapy.mongo_conf import db


def img_request(url):
    if isinstance(url,str) and url.startswith('http') :
            resp = requests.request(url=url, method='get',
                                    headers={'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42"})
            return resp.content
    else:
        if isinstance(url,str) and url.startswith('/assets') :
            print(f'{url}没有图片')
            return None
        else:
            print(f'{url}图片请求url非法')
            return None


def getItemMd5(dictData):
    hashMd5 = hashlib.md5()
    strDictValue = ""

    # 去除二进制字段
    dictData.pop('logo')
    dictData.pop('competitors')
    dictData.pop('extra_logo')

    dictData =sorted(dictData.items(),key=lambda x:x[0])

    for value in dictData:
        strDictValue += str(value)
    hashMd5.update(strDictValue.encode("utf-8"))
    return hashMd5.hexdigest()

def update_seed_state(websit,seed,state):
    """
    :param websit: 域名
    :param seed: seed name
    :param state: seed状态
    :return: None
    """
    collection = db['seeds']
    collection.update_one(
        {'crawled_website': websit, 'seeds.seed': seed},
        {'$set': {"seeds.$.state": state}}
    )


def check(file_path = '../log/check.txt'):
    collection = db['seeds']
    seeds = collection.find_one({'crawled_website': 'g2.com'})

    """seed集合检查"""
    website = seeds['crawled_website']
    seeds_num = len(seeds['seeds'])
    # print('爬取网站:%s\n种子数量:%d' % (website, seeds_num))

    """seed状态检查"""
    states={
        '-1':[],
        '0':[],
        '1':[],
        '2':[]
    }
    for seed in seeds['seeds']:
        states[str(seed['state'])].append(seed['seed'])


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
                        if not isinstance(array,dict):
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

    for i in range(-1,3):
        print('状态:',i,states[str(i)])

    print('异常数据:', error_seeds)

    print('数据报告:',check_res)


    with open(file_path, mode='a', encoding='utf-8') as file_obj:
        time =datetime.datetime.now().isoformat()
        file_obj.write('-'*50+time+'-'*50)
        file_obj.write('\n')
        file_obj.write(str(states))
        file_obj.write('\n')
        file_obj.write(str(list(error_seeds)))
        file_obj.write('\n')
        for res in check_res:
            if res['null']:
                file_obj.write(str(res))
                file_obj.write('\n')
        file_obj.write('-'*100)
        file_obj.write('\n')

if __name__ == '__main__':
    check()
