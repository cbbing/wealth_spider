import scrapy
from tutorial.items import DmozItem

class DmozSpider(scrapy.Spider):
    name = 'dmoz'
    allowed_domains = ['dmoz.org','eastmoney.com']
    start_urls = [
        'http://blog.eastmoney.com/caijing.htm',
        #"http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
        #"http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    ]



    def parse(self, response):

        self.log('A response from {} just arrived'.format(response.url))

        for sel in response.xpath('//li[@class="w20_1"]'):
            item = DmozItem()
            item['title'] = sel.xpath('a/text()').extract()
            item['link'] = sel.xpath('a/@href').extract()
            #item['desc'] = sel.xpath('text()').extract()
            print item['title'], item['link']
            yield




        #s = selector.extract()

        # filename = response.url.split('/')[-2]
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        #     f.close()