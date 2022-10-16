# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# class SeedsItem(scrapy.Item):
#     crawled_website = scrapy.Field()
#     seeds = scrapy.Field()  # keyword and stat
#     last_crawled_time = scrapy.Field()
#     created_time = scrapy.Field()

class SeedItem(scrapy.Item):
    collection = 'seeds'
    state = scrapy.Field()
    seed = scrapy.Field()


class CompanyScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    collection = 'angel'
    logo = scrapy.Field()
    name = scrapy.Field()
    des = scrapy.Field()
    overview = scrapy.Field()
    website = scrapy.Field()
    locations = scrapy.Field()
    company_size = scrapy.Field()
    total_raised = scrapy.Field()
    company_type = scrapy.Field()
    market = scrapy.Field()

class G2ScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    collection = 'org'

    keyword = scrapy.Field()
    logo = scrapy.Field()
    name = scrapy.Field()
    desc = scrapy.Field()
    website = scrapy.Field()
    productDesc = scrapy.Field()
    seller = scrapy.Field()
    companyWebsite = scrapy.Field()
    yearFounded = scrapy.Field()
    HQLocation = scrapy.Field()
    twitter = scrapy.Field()
    twitterFollowers = scrapy.Field()
    page = scrapy.Field()
    employees = scrapy.Field()
    topRepresented = scrapy.Field()
    categories = scrapy.Field()
    popularMentions = scrapy.Field()

    score = scrapy.Field()
    extra_logo = scrapy.Field()

    domain = scrapy.Field()
    product_name = scrapy.Field()
    link = scrapy.Field()

    """嵌套字段"""
    competitors = scrapy.Field()  # 竞争对手集合
    features = scrapy.Field()

    md5 = scrapy.Field()

