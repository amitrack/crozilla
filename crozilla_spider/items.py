# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

from .model import Listing


class CrozillaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    crozilla_id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    gok = scrapy.Field()
    city = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    rooms = scrapy.Field()
    bathrooms = scrapy.Field()
    living_area = scrapy.Field()
    features = scrapy.Field()
    zip_code = scrapy.Field()
    type = scrapy.Field()
    transaction_type = scrapy.Field()
    district = scrapy.Field()
    federal_state = scrapy.Field()
    country = scrapy.Field()
    address = scrapy.Field()
    broker_url = scrapy.Field()
    broker = scrapy.Field()
    image_src = scrapy.Field()
    area = scrapy.Field()
    balcony = scrapy.Field()
    garden = scrapy.Field()
    kitchen = scrapy.Field()
    cellar = scrapy.Field()

    def to_listing(self):
        listing = Listing()
        listing.__dict__.update(self._values)
        return listing
