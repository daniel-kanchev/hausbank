import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from hausbank.items import Article


class HausbankSpider(scrapy.Spider):
    name = 'hausbank'
    start_urls = ['https://www.hausbank.de/unternehmen/presse/pressemitteilung.html']

    def parse(self, response):
        links = response.xpath('//div[@class="teaseraslink"]/a')
        for link in links:
            l = link.xpath('./@href').get()
            date = link.xpath('./@title').get().split()[0]
            yield response.follow(l, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//main//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
