from datetime import datetime

import requests
import scrapy
import pymongo

from company_scrapy.items import G2ScrapyItem, SeedItem
from company_scrapy.public.tools import img_request, getItemMd5, update_seed_state, check
from company_scrapy.settings import db

class SeedPipeline:

    def process_item(self, item, spider):
        if isinstance(item, SeedItem):
            try:
                update_seed_state(websit='g2.com',seed=item['seed'],state=2)
            except:
                spider.logger.error('seed：%s状态更新错误' % item['seed'])
        return item

class G2Pipeline:

    # def open_spider(self, spider):
    num = 0

    def process_item(self, item, spider):
        if isinstance(item, SeedItem):
            return item

        elif isinstance(item, G2ScrapyItem):
            collection = db['org']

            item['md5'] = getItemMd5(dict(item))

            """判断是否有name"""
            if not collection.find_one({"name": item['name']}):
                """数据不存在"""
                try:
                    data = {}
                    data['name'] = item['name']
                    data['domain']=item['domain']

                    time = datetime.now()
                    data['created_time'] = time
                    data['last_compared_time'] = time
                    data['history'] = [dict(item)]
                    collection.insert_one(data)  # company 重复则更新
                    spider.logger.info('seed:%s状态已更新，新增数据name:%s' % (item['keyword'],item['name']))
                except Exception as e:
                    spider.logger.error('%s管道-新增数据错误错误-%s' % (spider.name, e))

                # 更新状态
                try:
                    update_seed_state(websit='g2.com', seed=item['keyword'], state=1)
                except Exception as e:
                    spider.logger.error('seed:%s状态更新错误:%s' % (item['seed'],e))

            else:
                time = datetime.now()
                last = collection.find_one(
                    {'name': item['name']},
                    {'history': {"$slice":-1}}
                )
                last_md5 = last['history'][0]['md5']

                """判断是否需要更新版本"""
                if item['md5'] != last_md5:
                    """更新"""
                    try:
                        collection.update_one(
                            {'name': item['name']}, {"$set": {'last_compared_time': time}}
                        )
                        collection.update_one(
                            {'name': item['name']},
                            # {"$push": {'history': {dict(item): {"$position": 0}}}}
                            {"$push": {'history': dict(item)}}
                        )
                        spider.logger.info('name:%s数据发生变化，版本更新成功' % item['name'])
                    except Exception as e:
                        spider.logger.error('name:%s版本更新错误-%s' % (item['name'],e))

                    # 更新状态
                    try:
                        update_seed_state(websit='g2.com', seed=item['keyword'], state=1)
                    except Exception as e:
                        spider.logger.error('seed:%s状态更新错误:%s' % (item['seed'], e))

                else:
                    """忽略"""
                    try:
                        collection.update_one(
                            {'name': item['name']}, {"$set":{'last_compared_time': time}}
                        )
                        spider.logger.info('md5:%s重复,name:%s数据未发生变化，忽略更新' % (last_md5,item['name']))
                    except Exception as e:
                        spider.logger.error('name:%s忽略更新错误%s' % (item['name'],e))

                self.num += 1
                spider.logger.info('------------------------已更新%s-----------------------',self.num)
        return item

    def close_spider(self, spider):
        # 检查数据库数据
        check(file_path = './log/check.txt')


class AngelPipeline:
    """
    存储数据到mongodb
    """

    # def open_spider(self, spider):
    #     host = spider.settings['MONGODB_HOST']
    #     port = spider.settings['MONGODB_PORT']
    #     db_name = spider.settings['MONGODB_NAME']
    #     # client = pymongo.MongoClient(host=host, port=port,username=spider.settings['USERNAME'],password=spider.settings['PASSWORD'],authMechanism='SCRAM-SHA-1',authSource=spider.settings['AUTH_DB'])
    #     client = pymongo.MongoClient(host=host, port=port)
    #
    #     self.db = client[db_name]

    def process_item(self, item, spider):

        collection = self.db[item.collection]
        try:
            collection.update_one({'name': item['name']}, {'$set': dict(item)}, True)  # company 重复则更新
            spider.logger.info('公司:%s插入或更新数据' % item['name'])
        except Exception as e:
            spider.logger.error('%s管道-插入或更新错误-%s' % (spider.name, e))
        return item


class ImagePipeline:
    """
    图片url转为二进制数据
    """

    def process_item(self, item, spider):
        if spider.name == 'g2':
            if isinstance(item, G2ScrapyItem):
                spider.logger.info('g2.com图片二进制转换中...')
                try:
                    url=item['logo']
                    item['logo'] = img_request(url)

                    url = item['extra_logo']
                    item['extra_logo'] = img_request(url)

                    for i in item['competitors']:
                        url = i['logo']
                        if url:
                            i['logo'] = img_request(url)
                except Exception as e:
                    spider.logger.error('%s图片请求错误-%s' % (spider.name, e))
                    raise e

        elif spider.name == 'angel':
            image_url = item['logo']
            try:
                resp = requests.request(url=image_url, method='get').content
                item['logo'] = resp
            except Exception as e:
                spider.logger.error('%s图片请求错误-%s' % (spider.name, e))

        return item
