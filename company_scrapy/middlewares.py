# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time
from datetime import datetime

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse
from company_scrapy.public import cookies

from scrapy import signals
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse


class SeleniumDownloaderMiddleware:
    def spider_closed(self):
        self.driver.close()

    def __del__(self):
        self.driver.close()

    def __init__(self,timeout=None):
        self.timeout = timeout

        self.option = webdriver.EdgeOptions()
        # self.option = webdriver.ChromeOptions()

        self.option.add_argument('--ignore-certificate-errors')
        # self.option.add_argument('--load-images=false')
        self.option.add_argument('--disk-cache=true')
        # 忽略证书
        self.option.add_argument('-ignore-certificate-errors')
        self.option.add_argument('-ignore -ssl-errors')

        self.option.add_argument("--headless")  # => 为Chrome配置无头模式self.option.add_argument('--headless')
        self.option.add_argument('--disable-gpu')
        self.option.add_argument('--no-sandbox')
        self.option.add_argument('--disable-dev-shm-usage')
        self.option.add_argument('log-level=3')
        self.option.add_argument('--disable-blink-features=AutomationControlled')  # 谷歌浏览器去掉访问痕迹
        self.option.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42")
        # self.option.add_argument(
        #     "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0")

        self.option.add_argument("--window-size=1920,1050")  # 专门应对无头浏览器中不能最大化屏幕的方案
        self.option.add_experimental_option('excludeSwitches', ['enable-automation'])# 去除“Chrome正受到自动测试软件的控制”的显示
        self.option.add_experimental_option('useAutomationExtension', False)

        self.option.page_load_strategy = 'none'

    def open_driver(self):
        self.driver = webdriver.Edge(options=self.option)
        # self.driver = webdriver.Chrome(options=self.option)
        self.wait = WebDriverWait(self.driver, self.timeout)


    def process_request(self,request,spider):
        self.open_driver()
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                                                           Object.defineProperty(navigator, 'webdriver', {
                                                               get: () => undefined
                                                           })
                                                       """})

        if spider.name == 'g2':
            url = request.url
            page = request.meta.get('page')

            spider.logger.info(f'selemium解析中-page:{page}-url:{url}')
            try:
                # self.driver.get('https://www.baidu.com/')
                time.sleep(0.5)
                self.driver.get(url)
                start = datetime.now()

                if page == 'reviews':
                    element = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="leads-sticky-top"]')))
                    element = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="footnote p-1"]')))

                elif page == 'search':
                    element = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, '//div[@class="page paper-padding"]')))

                elif page == 'competitors':
                    # element = self.wait.until(
                    #     EC.presence_of_element_located((By.XPATH, '//div[@class="px-1 px-half-small-only"]')))
                    element = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, '//div[@class="page bg-offwhite-13 border mb-2"]')))

                elif page == 'features':
                    element = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="mb-3"]')))

                end = datetime.now()

                result=self.driver.page_source
                self.driver.close()
                spider.logger.info('page:%s爬取成功,共花费%s时间' % (page,end - start))
                return HtmlResponse(url=url,body=result,request=request,encoding='utf-8',status=200)

            except TimeoutException:
                spider.logger.warn(f'selenium Timeout-page:{page}-url:{url}抓取失败,重试中')
                self.driver.close()

                # 重试
                return HtmlResponse(url=url,request=request, encoding='utf-8', status=500)
                # 不重试
                # raise IgnoreRequest
                # HtmlResponse是textResponse的一个子类，它会自动寻找适当的html文件编码，然后返回html类型的数据
                # 返回的是一个response，所以，接下来不会继续调用剩下的中间件的request和exception

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),)

class FuckCloudflareDownloaderMiddleware:
    """破解Cloudflare"""
    def process_request(self, request, spider):
        url = request.url
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.37",
        }
        page = request.meta.get('page')
        if spider.name == 'g2' and page == 'search':
            rsp = spider.browser.get(url,
                                    # proxies={'http': 'http://47.74.51.30' # 这里的代理主要是爬取外国网站做的处理
                                    #          },
                                    headers=headers)

            return HtmlResponse(url=url,
                                body=rsp.text,
                                encoding="utf-8",
                                request=request)
        return None

class AngelScrapySpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class AngelScrapyDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        if spider.name == 'g2':
            referer = 'https://www.g2.com/'
            request.headers["referer"] = referer
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        # spider.logger.info('Spider headers: %s' % request.headers)
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
