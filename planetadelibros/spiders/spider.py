import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from planetadelibros.items import BookItem

# NC: Novela contemporanea
class PlanetaCrawlerNC(CrawlSpider):
    name = "crawlerPlaneta"
    start_urls = ['https://www.planetadelibros.com.co/libros/novelas/00038', 
    'https://www.planetadelibros.com.co/libros/novela-historica/00013', 
    'https://www.planetadelibros.com.co/libros/novela-literaria/00012', 
    'https://www.planetadelibros.com.co/libros/novela-negra/00015', 
    'https://www.planetadelibros.com.co/libros/novelas-romanticas/00014', 
    'https://www.planetadelibros.com.co/libros/poesia/00051', 
    'https://www.planetadelibros.com.co/libros/teatro/00052']
    allowed_domains = ['planetadelibros.com']
    i = 1

    def parse(self, response):
        for libro in response.xpath('//ul[@class="llibres-miniatures llibres-graella"]/li'):
            tipoLibro = libro.xpath('div[@class="soporte"]/text()').extract()
            if tipoLibro[0] != "Audiolibro" and tipoLibro[0] != "Libro Electrónico":
                item = BookItem()
                kkk = libro.xpath('div[@class="titol"]/span/@data-link-js').extract()
                request = scrapy.Request(str(kkk[0]), callback=self.parse_libro, dont_filter=True)
                request.meta['item'] = item
                yield request
           


        next_page = response.xpath('//div[@class="paginacio-seguent"]/a/@href').extract()
        if next_page is not None:
            print("SIGUIENTE ", next_page[0])
            next_page = response.urljoin(next_page[0])
            #print(next_page)
            #print("********PAGINA ", self.i)
            self.i = self.i + 1
            yield scrapy.Request(str(next_page), callback=self.parse, dont_filter=True)

   
    def parse_libro(self, response):
        item = response.meta['item']
        titulo = response.xpath('//div[@class="titol"]/h1/text()').extract()
        autor = response.xpath('/html/body/section/div/div[3]/div[1]/div[3]/div[1]/div[2]/div[2]/h2/a/text()').extract()
        if autor[0] is not None:
            autor = response.xpath('/html/body/section/div/div[3]/div[1]/div[3]/div[1]/div[2]/div[2]/h2/a/text()').extract()
        else:
            autor = response.xpath('/html/body/section/div/div[3]/div[1]/div[3]/div[1]/div[2]/div[2]/h2/text()').extract()
        
        editorial = response.xpath('/html/body/section/div/div[3]/div[1]/div[3]/div[1]/div[3]/div[1]/a/text()').extract()
        num_paginas = response.xpath('//*[@id="num_pagines"]/text()').extract()
        precio = response.xpath('/html/body/section/div/div[3]/div[1]/div[3]/div[2]/div/div[2]/span/div/text()').extract()

        item['titulo'] = titulo
        item['autor'] = autor
        item['editorial'] = editorial
        item['num_paginas'] = num_paginas
        item['precio'] = precio
        return item
