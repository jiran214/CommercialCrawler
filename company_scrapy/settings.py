
from company_scrapy.mongo_conf import *
# Scrapy settings for company_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import datetime

BOT_NAME = 'company_scrapy'

SPIDER_MODULES = ['company_scrapy.spiders']
NEWSPIDER_MODULE = 'company_scrapy.spiders'

LOG_LEVEL = 'INFO'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.37'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 2

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#     'Connection': 'keep-alive',
#     'Host': 'www.g2.com',
#     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#
#    'company_scrapy.middlewares.AngelScrapySpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'company_scrapy.middlewares.FuckCloudflare':500,
    'company_scrapy.middlewares.SeleniumDownloaderMiddleware': 600,
    # 'company_scrapy.middlewares.FuckCloudflareDownloaderMiddleware' : 200
    # 'company_scrapy.middlewares.AngelScrapyDownloaderMiddleware': 400,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'company_scrapy.pipelines.AngelPipeline': 300,
    'company_scrapy.pipelines.G2Pipeline': 600,
    'company_scrapy.pipelines.ImagePipeline': 550,
    'company_scrapy.pipelines.SeedPipeline': 500,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 日志配置
# to_day = datetime.datetime.now()
LOG_ENABLED = True
# LOG_FILE = "D:/mypro/scrpay_pro/angel/company_scrapy/log/{}{}{}.log".format(to_day.year, to_day.month,
#                                                                                      to_day.day)
# LOG_LEVEL = "INFO"
# # 显示日志级别以上的日志信息（包括自己）
# LOG_DATEFORMAT = "%Y-%m-%d %H:%M:%S"
# LOG_FORMAT = "%(asctime)s-%(levelname)s-%(filename)s-%(funcName)s-%(message)s--%(lineno)d"

SELENIUM_TIMEOUT = 20

# 无头浏览器设置 及防检测
ARGS = [
    '--ignore-certificate-errors',
    '--load-images=false',
    '--disk-cache=true',
    '--headless',
    '--disable-gpu',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    'log-level=3',
    '--disable-blink-features=AutomationControlled',
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "--window-size=1920,1050"]
