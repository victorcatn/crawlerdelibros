import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from planetadelibros.items import BookItem


# NC: Novela contemporanea
class PlanetaCrawlerNC(scrapy.Spider):
    name = "crawlerPlaneta"
    start_urls = [
        'https://www.planetadelibros.com.co/libros/novelas/00038',
        'https://www.planetadelibros.com.co/libros/novela-historica/00013',
        'https://www.planetadelibros.com.co/libros/novela-literaria/00012',
        'https://www.planetadelibros.com.co/libros/novela-negra/00015',
        'https://www.planetadelibros.com.co/libros/novelas-romanticas/00014',
        'https://www.planetadelibros.com.co/libros/poesia/00051',
        'https://www.planetadelibros.com.co/libros/teatro/00052'
    ]
    npag = 0

    def parse(self, response):
        for libro in response.xpath('//ul[@class="llibres-miniatures llibres-graella"]/li'):
            tipoLibro = libro.xpath('div[@class="soporte"]/text()').extract()
            if tipoLibro[0] != "Audiolibro" and tipoLibro[0] != "Libro Electrónico":
                detalle_libro = libro.xpath('div[@class="titol"]/span/@data-link-js').get()
                request = scrapy.Request(detalle_libro, callback=self.parse_libro)
                yield request

        next_page = response.xpath('//div[@class="paginacio-seguent"]/a/@href').get()
        if next_page is not None and self.npag < int(self.maxpag):
            print("SIGUIENTE ", next_page)
            next_page = response.urljoin(next_page)
            #print(next_page)
            #print("********PAGINA ", self.i)
            self.npag += 1
            yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)

    def parse_libro(self, response):
        item = BookItem()
        nombre = response.css('div.titol::text').get()
        autor = response.css('div.autors h2 a::text').get()
        if autor is None:
            autor = response.css('div.autors h2::text').get()
        editorial = response.css('div.segell-nom a::text').get()
        nro_paginas = response.css('#num_pagines::text').get()[19:]
        precio = response.css('div.preu::text').get()[2:].replace(".", "")

        item['nombre'] = nombre
        item['autor'] = autor
        item['editorial'] = editorial
        item['nro_paginas'] = int(nro_paginas)
        item['precio'] = float(precio)
        item['url'] = response.url
        yield item
