import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from planetadelibros.items import BookItem

# NC: Novela contemporanea
class PanaCrawlerNC(CrawlSpider):
    name = "crawlerPana"
    start_urls = ['https://www.panamericana.com.co/buscapagina?fq=C:/1/15/73/&PS=12&sl=5e2a6963-80df-4508-b796-cb6a21d8fa05&cc=1&sm=0&PageNumber=1'] #ciencia ficcion
    allowed_domains = ['panamericana.com.co']
    i = 1

    def parse(self, response):
        for libro in response.css('h3.item__showcase__category__title'):
            detalle_libro = libro.css('a::attr(href)').get()
            request = scrapy.Request(detalle_libro, callback=self.parse_libro, dont_filter=True)
            yield request
           
   
    def parse_libro(self, response):
        item = BookItem()
        nombre = response.css("div.productName::text").get()
        autor = response.css('td.Autor-es-::text').get()
        editorial = response.css('div.productP__infoCont__shortDecription > div > a::text').get().strip()
        nro_paginas = response.css('td.N-°-paginas::text').get()
        precio = response.css("#___rc-p-dv-id::attr(value)").get()

        item['nombre'] = nombre
        item['autor'] = autor
        item['editorial'] = editorial
        item['nro_paginas'] = int(nro_paginas)
        item['precio'] = float(precio)
        item['url'] = response.url
        return item
