# -*- coding: utf-8 -*-
# PlanetadelibrosPipeline
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy import signals
from scrapy.exporters import CsvItemExporter
from scrapy.exceptions import DropItem
from scrapy import Request
import csv

from sqlalchemy import Column, Integer, String, Float, text
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from unidecode import unidecode

DeclarativeBase = declarative_base()


class Libro(DeclarativeBase):
    __tablename__ = "libros_libro"

    id = Column(Integer, primary_key=True)
    nombre = Column('nombre', String)
    autor = Column('autor', String)
    editorial = Column('editorial', String)
    nro_paginas = Column('nro_paginas', Integer)
    precio = Column('precio', Float)
    url = Column('url', String)
    link2 = Column('link2', String, default="")
    observaciones = Column('observaciones', String, default="")
    estado = Column('estado', String,)
    nombreautor = Column('nombreautor', String)

    def __repr__(self):
        return "<Book({})>".format(self.nombre)


class PlanetadelibrosPipeline(object):
    def __init__(self, settings):
        self.database = settings.get('DATABASE')
        self.sessions = {}
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler.settings)
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def create_engine(self):
        engine = create_engine(URL(**self.database), poolclass=NullPool)
        return engine

    def create_tables(self, engine):
        DeclarativeBase.metadata.create_all(engine, checkfirst=True)

    def create_session(self, engine):
        session = sessionmaker(bind=engine)()
        return session

    def spider_opened(self, spider):
        engine = self.create_engine()
        self.create_tables(engine)
        session = self.create_session(engine)
        self.sessions[spider] = session
        if spider.name == "crawlerPlaneta":
            session.query(Libro).update({Libro.estado: "desactivado"})
            session.commit()

    def spider_closed(self, spider):
        session = self.sessions.pop(spider)
        session.close()

    def process_item(self, item, spider):
        session = self.sessions[spider]

        actualurl = item['url']
        del item['url']
        book = Libro(**item)

        book.estado = "activado"
        book.nombreautor = (unidecode(book.nombre)+unidecode(book.autor)).lower()
        book.nombreautor = ''.join(c for c in book.nombreautor if c not in ' -_,.:()')

        saved_book = session.query(Libro).filter(Libro.nombreautor == book.nombreautor).first()

        if spider.name == "crawlerPlaneta":
            book.url = actualurl
            if saved_book is not None: #
                saved_book.nombre = book.nombre
                saved_book.autor = book.autor
                saved_book.editorial = book.editorial
                saved_book.nro_paginas = book.nro_paginas
                saved_book.precio = book.precio
                saved_book.url = book.url
                saved_book.estado = book.estado

                book = saved_book
                print('{} actualizado en planeta'.format(book))
        elif spider.name == "crawlerPana":

            if saved_book is not None and saved_book.estado == "activado":
                saved_book.link2 = actualurl
                observaciones = ""
                for c in ['nombre','autor','editorial','nro_paginas','precio']:
                    X = getattr(saved_book, c)
                    Y = getattr(book, c)
                    if X != Y:
                        observaciones += """Diferencia de valor encontrado para {c}. Se selecciona el valor {X}. 
                        Posibles valores: {X} en planeta y {Y} en panamericana. """.format(c=c, X=X, Y=Y)
                saved_book.observaciones = observaciones
                book = saved_book
                print('{} anotaciones en panamericana'.format(book))
            else:
                book.url = actualurl
                if saved_book is not None:  #
                    saved_book.nombre = book.nombre
                    saved_book.autor = book.autor
                    saved_book.editorial = book.editorial
                    saved_book.nro_paginas = book.nro_paginas
                    saved_book.precio = book.precio
                    saved_book.url = book.url
                    saved_book.estado = book.estado

                    book = saved_book
                    print('{} actualizado en panamericana'.format(book))


        try:
            session.add(book)
            session.commit()
            #print('Item {} stored in db'.format(book))
        except:
            print('Failed to add {} to db'.format(book))
            session.rollback()
            raise

        return item
