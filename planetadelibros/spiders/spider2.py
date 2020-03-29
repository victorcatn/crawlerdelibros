import scrapy

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from planetadelibros.items import BookItem


# NC: Novela contemporanea
class PanaCrawlerNC(CrawlSpider):
    name = "crawlerPana"
    urls_base = [
        # ciencia ficcion
        'https://www.panamericana.com.co/buscapagina?fq=C:/1/15/73/&PS=12&sl=5e2a6963-80df-4508-b796-cb6a21d8fa05&cc=1&sm=0&PageNumber=',

        # cuento
        'https://www.panamericana.com.co/buscapagina?fq=C%3a%2f1%2f15%2f74%2f&PS=12&sl=5e2a6963-80df-4508-b796-cb6a21d8fa05&cc=1&sm=0&PageNumber=',
        # critica
        'https://www.panamericana.com.co/buscapagina?fq=C%3a%2f1%2f15%2f20%2f&PS=12&sl=5e2a6963-80df-4508-b796-cb6a21d8fa05&cc=1&sm=0&PageNumber=',
        # hispanoamericana
        'https://www.panamericana.com.co/buscapagina?fq=C%3a%2f1%2f15%2f17%2f&PS=12&sl=5e2a6963-80df-4508-b796-cb6a21d8fa05&cc=1&sm=0&PageNumber=',
        # colombiana
        'https://www.panamericana.com.co/buscapagina?fq=C%3a%2f1%2f15%2f18%2f&PS=12&sl=5e2a6963-80df-4508-b796-cb6a21d8fa05&cc=1&sm=0&PageNumber=',
        # teatro
        'https://www.panamericana.com.co/buscapagina?fq=C%3a%2f1%2f15%2f22%2f&PS=12&sl=5e2a6963-80df-4508-b796-cb6a21d8fa05&cc=1&sm=0&PageNumber=',
        # ficcion
        'https://www.panamericana.com.co/buscapagina?fq=C%3a%2f1%2f15%2f75%2f&PS=12&sl=5e2a6963-80df-4508-b796-cb6a21d8fa05&cc=1&sm=0&PageNumber=',
        # poesia
        'https://www.panamericana.com.co/buscapagina?fq=C%3a%2f1%2f15%2f21%2f&PS=12&sl=5e2a6963-80df-4508-b796-cb6a21d8fa05&cc=1&sm=0&PageNumber=',
        # historica
        'https://www.panamericana.com.co/buscapagina?fq=C%3a%2f1%2f15%2f19%2f&PS=12&sl=5e2a6963-80df-4508-b796-cb6a21d8fa05&cc=1&sm=0&PageNumber='

    ]
    # allowed_domains = ['panamericana.com.co']

    def start_requests(self):
        for url in self.urls_base:
            yield scrapy.Request(url + '1', meta={"urlbase": url, "page": 1})

    def parse(self, response):
        page = response.meta.get('page')
        if len(response.text.strip()) != 0 and page <= int(self.maxpag): #para cuando llega a una pagina vacia o al maximo

            for libro in response.css('h3.item__showcase__category__title'):
                detalle_libro = libro.css('a::attr(href)').get()
                request = scrapy.Request(detalle_libro, callback=self.parse_libro, dont_filter=True)
                yield request

            #otras paginas
            request = scrapy.Request(response.meta.get("urlbase") + str(page+1))
            request.meta["page"] = page+1
            request.meta["urlbase"] = response.meta.get("urlbase")
            yield request

    def parse_libro(self, response):
        item = BookItem()
        nombre = response.css("div.productName::text").get()
        autor = response.css('td.Autor-es-::text').get()
        editorial = response.css('div.productP__infoCont__shortDecription > div > a::text').get().strip()
        nro_paginas = response.css('td.N-°-paginas::text').get()
        precio = float(response.css("#___rc-p-dv-id::attr(value)").get())
        if precio == 9999876: precio = None


        item['nombre'] = nombre
        item['autor'] = autor
        item['editorial'] = editorial
        item['nro_paginas'] = int(nro_paginas)
        item['precio'] = precio
        item['url'] = response.url
        return item
