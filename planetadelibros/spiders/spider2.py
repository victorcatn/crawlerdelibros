import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from planetadelibros.items import BookItem

# NC: Novela contemporanea
class PanaCrawlerNC(CrawlSpider):
    name = "crawlerPana"
    start_urls = ['https://www.panamericana.com.co/libros/literatura/ciencia-ficcion?PS=20']
    allowed_domains = ['panamericana.com.co']
    i = 1

    def parse(self, response):
        print("AQUI**************")
        for libro in response.xpath('//*[@id="ResultItems_20426749"]/div/ul'):
            item = BookItem()
            kkk = libro.xpath('div[@class="item__showcase__category__namePrice"]/h3/a/@href').extract()
            print(kkk)
            request = scrapy.Request(str(kkk[0]), callback=self.parse_libro, dont_filter=True)
            request.meta['item'] = item
            yield request
           
   
    def parse_libro(self, response):
        item = response.meta['item']
        titulo = response.xpath('//*[@id="titleProduct"]/text()').extract()
        autor = response.xpath('//*[@id="caracteristicas"]/table/tbody/tr[2]/td/text()').extract()
        editorial = response.xpath('/html/body/main/section/div[1]/div[2]/div[2]/div[2]/div/p[1]/a/text()').extract()
        num_paginas = response.xpath('//*[@id="caracteristicas"]/table/tbody/tr[6]/td/text()').extract()
        precio = response.xpath('//*[@id="productP__infoCont__price__desk"]/p/span[2]/text()').extract()

        item['titulo'] = titulo
        item['autor'] = autor
        item['editorial'] = editorial
        item['num_paginas'] = num_paginas
        item['precio'] = precio
        return item