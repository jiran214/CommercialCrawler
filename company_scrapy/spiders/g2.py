import datetime

import scrapy

from company_scrapy.items import G2ScrapyItem, SeedItem
from company_scrapy.public import keywords, cookies, filed_map
from company_scrapy.settings import db


import cloudscraper


class G2Spider(scrapy.Spider):
    name = 'g2'

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.37",
    }

    MAX_MATCH = 2  # 最大匹配seed搜索结果

    # browser = cloudscraper.create_scraper()

    def start_requests(self):
        """查找seeds"""
        try:
            collection = db['seeds']
            res = collection.find_one({'crawled_website': 'g2.com'})

            time = datetime.datetime.now()
            # 更新爬虫时间
            collection.update_one(
                {'crawled_website': 'g2.com'}, {'$set': {'last_crawled_time': time}}, True
            )
        except Exception as e:
            print('读取seeds集合错误', e)
            return

        for one_seed in res['seeds'][:5]:
            """
            state 0：未爬取 -1：没有搜索结果  1：爬取成功 2:有结果，但未存储或者存储时发生错误
            """
            if one_seed['state'] != -3:
                base_url = 'https://www.g2.com/search?utf8=%E2%9C%93&query='
                seed_item = SeedItem()
                seed_item['seed'] = one_seed['seed']
                seed_item['state'] = one_seed['state']

                yield scrapy.Request(url=base_url + one_seed['seed'],
                                     # headers=self.headers,cookies=cookies.g2_search,
                                     meta={'page': 'search','seed_item': seed_item},
                                     callback=self.search_parse, )

    def search_parse(self, response):
        """解析搜索页"""

        seed_item = response.meta['seed_item']
        keyword = seed_item['seed']
        hrefs = response.xpath('//div[@class="product-listing__product-name"]/a/@href').getall()

        if hrefs:
            seed_item['state'] = 2
            yield seed_item  # 更新状态
            self.logger.info('%s关键词匹配%s结果,开始爬取共%d个' %
                             (keyword, len(hrefs), min(len(hrefs), self.MAX_MATCH)))

            for href in hrefs[:self.MAX_MATCH]:
                # 从url中解析
                item = G2ScrapyItem()
                item['keyword'] = keyword

                s = href.split('/')
                item['product_name']=s[-2]
                item['link'] ='/{}/{}'.format(s[-3], s[-2])

                print('开始爬取keyword:%s-href:%s' % (item['keyword'],href))
                yield scrapy.Request(url=href,
                                     meta={'page': 'reviews', 'item': item},
                                     callback=self.review_parse, )
        else:
            self.logger.info('%s关键词没有匹配到结果' % keyword)
            seed_item['state'] = -1
            yield seed_item

    def review_parse(self, response):

        item = response.meta['item']

        item['logo'] = response.xpath('//a[@class="product-head__logo__img pjax"]/img/@src').get()
        item['name'] = response.xpath('//a[@class="c-midnight-100"]/text()').get()
        # 拿到另外两个页面url
        competitors_url = response.xpath('//div[@class="footnote p-1"]/a/@href').get()
        features_url = response.xpath('//div[@class="product-head__nav__wrap"]/div/ul/li[4]/a/@href').get()

        """Overview板块"""
        item['desc'] = response.xpath('//div[@class="ws-pw"]/p/text()').get()
        divs = response.xpath('//*[@id="leads-sticky-top"]/div/div[1]/div[3]/div[1]/div/div[2]//div[@class="ml-1"]/div')
        xpaths = {
            'Website': './following-sibling::a/@href',
            'Seller': '../text()',
            'Company Website': './following-sibling::a/@href',
            'Year Founded': './text()',
            'HQ Location': './text()',

            'Twitter': '../text()',
            'LinkedIn® Page': './following-sibling::a/@href'
        }
        for div in divs:
            filed = div.xpath('./text()').get()
            if filed == 'Website':
                item['website'] = div.xpath(xpaths[filed]).get()
            elif filed == 'Seller':
                item['seller'] = div.xpath(xpaths[filed]).get()
            elif filed == 'Company Website':
                item['companyWebsite'] = div.xpath(xpaths[filed]).get()
            elif filed == 'Year Founded':
                item['yearFounded'] = div.xpath(xpaths[filed]).get()
            elif filed == 'HQ Location':
                item['HQLocation'] = div.xpath(xpaths[filed]).get()
            elif filed == 'Twitter':
                item['twitter'] = div.xpath(xpaths[filed]+'[1]').get()
                item['twitterFollowers'] = div.xpath(xpaths['Seller']+'[2]').get()
            elif filed == 'LinkedIn® Page':
                item['page'] = div.xpath(xpaths[filed]).get()
                item['employees'] = div.xpath(xpaths['Seller']).get()

        # 解析域名domain
        # str = item['website'].split('/')[2].split('.')
        # item['domain'] = str[1] + '.' + str[2]
        if item['website']:
            s = item['website'].split('/')[2]
            item['domain'] = s.replace('www.','')

        item['productDesc'] = response.xpath('//div[@class="paper paper--nestable border-top"]/div[3]/p/text()').get()

        topRepresented_key = response.xpath('//div[@class="c-midnight-100 mb-0 ml-half"]/text()').getall()
        topRepresented_value = response.xpath('//div[@class="text-right"]/text()').getall()
        item['topRepresented'] = dict(zip(topRepresented_key, topRepresented_value))

        categories = response.xpath('//a[@class="link link--chevron"]/@href').getall()
        links = response.xpath('//a[@class="link link--chevron"]/div/text()').getall()
        item['categories'] = {
            'link':links,
            'categories':categories
        }

        item['popularMentions'] = response.xpath(
            '//label[@class="radios__button"]/div/div[@class="filters--product__keyphrase-tag js-log-click"]/text()').getall()

        # 测试结果
        # for i,filed in enumerate(g2_review_fileds):
        #     print('review-',i,filed,'的值为',item[filed])
        yield scrapy.Request(url=competitors_url,
                             meta={'page': 'competitors', 'item': item, 'features_url': features_url},
                             callback=self.competitors_parse, )

    def competitors_parse(self, response):
        """解析竞争对手"""

        item = response.meta['item']
        features_url = response.meta['features_url']

        item['score'] = response.xpath('//span[@class="c-midnight-90"]/span[1]/text()').get()
        item['extra_logo'] =response.xpath('//img[@class="alternatives-banner__logo"]/@src').get()

        div = response.xpath('/html/body/div[1]/div/div/div[1]/div/div[5]/div[2]/ol')
        item['competitors'] = []  # 初始化
        content = {}
        content['name'] = div.xpath('//div[@itemprop="name"]/text()').getall()
        scores = div.xpath(
            '//li[@class="list--plain product-listing__title--competitor"]')
        content['score'] = [(score.xpath('./div/span[2]/span[1]/text()').get() or '没有评分') for score in scores]

        content['logo'] = div.xpath(
            '//a[@class="product-listing__img product-listing__img--competitor js-log-click"]/img/@src').getall()
        content['desc'] = div.xpath('//div[@class="my-1"]/div[1]/p/text()').getall()

        ul = div.xpath('//ul[@class="list list--spaced list--spaced--with-divider"]')

        for i, li in enumerate(ul):
            dic = {filed: content.get(filed)[i] for filed in filed_map.g2_competitors_fileds}

            link = li.xpath('./li/a/@href').getall()
            categories = li.xpath('./li/a/text()').getall()

            dic['similarCategories'] = {
                'link': link,
                'categories': categories
            }

            item['competitors'].append(dic)

        # 测试
        # for filed in filed_map.g2_competitors_fileds:
        #     print(filed,item['competitors'][0][filed])

        if features_url:
            yield scrapy.Request(url='https://www.g2.com' + features_url, meta={'page': 'features', 'item': item},
                                 callback=self.features_parse, )
        else:
            item['features'] = []
            yield item

    def features_parse(self, response):
        """解析功能页"""

        item = response.meta['item']
        divs = response.xpath('//div[@class="paper paper--box no-border-bottom"]')

        item['features'] = []
        for div in divs:
            h2 = div.xpath('./h2/text()').get()
            trs = div.xpath('./table/tbody/tr')

            features = []

            for tr in trs:
                dic = {}
                dic['feature'] = tr.xpath('./td[1]/h3/span/text()').get()
                dic['desc'] = tr.xpath('./td[3]/div/text()').get()
                dic['percent'] = tr.xpath('./td[4]/div/div[2]/text()').get()
                if not dic['percent']:
                    dic['percent'] = 'Not enough data available'
                features.append(dic)

            item['features'].append({
                h2: features
            })

        # print(
        #     dict(item)
        # )

        yield item
