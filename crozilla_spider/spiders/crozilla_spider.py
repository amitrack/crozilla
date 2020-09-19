import decimal
import locale
import logging
import re
from urllib.parse import urljoin

import scrapy

from crozilla_spider.items import CrozillaItem

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')


class TableReader:
    row_xpath = '//*[@class="ct-u-displayTableRow"]'
    label_xpath = 'div[1]/span/text()'
    value_xpath = 'div[2]/span/text()'
    broker_xpath = '//*[contains(@class,"advertiser-name")][1]/text()'
    title_xpath = '//*[@class="ct-fw-300 obj-headline"]/text()'
    description_xpath = '//p[@class="ct-u-marginBottom20"]/text()'
    broker_url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    zip_code_regex = r'\d{4,8}'
    image_xpath = '//meta[@property="og:image"]/@content'
    address_regex = '''//*[@id="two"]/span/text()'''

    def __init__(self, response):
        self.formatted_data = dict()
        for row in response.xpath(self.row_xpath):
            try:
                label = row.xpath(self.label_xpath).extract_first().replace(":",
                                                                            "").strip()
                value = row.xpath(self.value_xpath).extract_first().replace(
                    "\n", "").replace("\t", "").strip()
            except:
                continue
            self.formatted_data[label] = value
        self.formatted_data["title"] = response.xpath(
            self.title_xpath).extract_first().strip()
        self.formatted_data["broker"] = re.sub('\s+', ' ', response.xpath(
            self.broker_xpath).extract_first().strip())
        description = " ".join(response.xpath(self.description_xpath).extract())
        self.formatted_data["image_src"] = response.xpath(
            self.image_xpath).extract_first()
        try:
            self.formatted_data["broker_url"] = \
                re.findall(self.broker_url_regex, description)[0][0]
        except:
            pass
        self.formatted_data["address"] = re.sub('\s+', ' ', " ".join(
            response.xpath(self.address_regex).extract()))
        self.extract_address()

    def extract_address(self):
        split_address = self["address"].split(":")
        zip_codes = re.findall(self.zip_code_regex, split_address[0])
        if zip_codes:
            self.formatted_data["zip_code"] = zip_codes[0]
            split_address[0] = split_address[0].replace(zip_codes[0],
                                                        "").strip()
        else:
            self.formatted_data["zip_code"] = ""

        self.formatted_data["region"] = split_address[0]
        try:
            self.formatted_data["city"] = split_address[1].strip()
        except:
            self.formatted_data["city"] = ""
        try:
            self.formatted_data["district"] = split_address[2].strip()
        except:
            self.formatted_data["district"] = ""

    def __getitem__(self, key):
        return self.formatted_data.get(key, "")


class CrozillaSpider(scrapy.Spider):
    name = 'crozilla'
    allowed_domains = ['www.crozilla-nekretnine.com']
    result_list_xpath = """//*[contains(@class,"ct-itemProducts")]/a/@href"""
    next_page_xpath = """//a[text()="›"]/@href"""
    custom_settings = {"CONNECTION_STRING": "EXAMPLE_CONNECTION_STRING",
                       "CRAWL_ID": "DEFAULT"}

    def start_requests(self):
        yield scrapy.Request(self.url)

    def parse(self, response, **kwargs):
        logging.info("starting:" + self.url)
        return self.parse_search_list(response)

    def parse_search_list(self, response):
        results = response.xpath(self.result_list_xpath).extract()
        for result in results:
            yield scrapy.Request(urljoin(response.url, result),
                                 callback=self.parse_result)
        next_page = response.xpath(self.next_page_xpath).extract_first()
        if next_page:
            yield scrapy.Request(urljoin(response.url, next_page), self.parse)

    def parse_result(self, response):
        reader = TableReader(response)
        item = CrozillaItem()
        item["url"] = response.url
        item["country"] = "Kroatien"
        item["price"] = self.extract_price(reader)
        item["area"] = self.extract_land_area(reader)
        item["living_area"] = self.extract_living_area(reader)
        item["rooms"] = self.extract_rooms(reader)
        item["bathrooms"] = self.extract_bathrooms(reader)
        item["transaction_type"] = self.extract_transaction_type(reader)
        item["type"] = self.extract_type(reader)
        item["currency"] = "EUR"
        item["crozilla_id"] = reader["Crozilla ID"]
        item["balcony"] = "Terrasse" in reader["Ausstattung"] or "Balkon" in \
                          reader["Ausstattung"]
        item["cellar"] = "Keller" in reader["Ausstattung"]
        item["garden"] = "Swimmingpool" in reader["Ausstattung"] or "garten" in \
                         reader["Ausstattung"].lower() or "Garte/-mitbeutzug" in \
                         reader["Ausstattung"]
        item["kitchen"] = "Küche" in reader["Ausstattung"]
        item["features"] = reader["Ausstattung"].split(", ")
        item["title"] = reader["title"]
        item["address"] = reader["address"]
        item["federal_state"] = reader["region"]
        item["district"] = reader["district"]
        item["city"] = reader["city"]
        item["zip_code"] = reader["zip_code"]
        item["broker"] = reader["broker"]
        item["broker_url"] = reader["broker_url"]
        item["image_src"] = reader["image_src"]
        return item

    def extract_price(self, reader: TableReader):
        try:
            return locale.atof(reader["Preis"].replace("€", ""),
                               decimal.Decimal)
        except decimal.InvalidOperation:
            return 0

    def extract_living_area(self, reader: TableReader):
        try:
            return locale.atof(reader["Wohnfläche"].replace("m", ""),
                               decimal.Decimal)
        except decimal.InvalidOperation:
            return 0

    def extract_land_area(self, reader: TableReader):
        try:
            return locale.atof(reader["Grundstück"].replace("m", ""),
                               decimal.Decimal)
        except decimal.InvalidOperation:
            return 0

    def extract_rooms(self, reader: TableReader):
        try:
            return locale.atof(reader["Zimmer"], decimal.Decimal)
        except decimal.InvalidOperation:
            return 0

    def extract_bathrooms(self, reader: TableReader):
        try:
            return locale.atof(reader["Anzahl Badezimmer"],
                               decimal.Decimal)
        except decimal.InvalidOperation:
            return 0

    def extract_transaction_type(self, reader: TableReader):
        return "KAUF" if reader["Anzeigetyp"].strip().endswith(
            "kaufen") else "MIETE"

    def extract_year(self, reader: TableReader):
        try:
            return locale.atof(reader["Baujahr"], decimal.Decimal)
        except decimal.InvalidOperation:
            return 0

    def extract_type(self, reader: TableReader):
        return reader["Anzeigetyp"].strip().rsplit(' ', 1)[0].upper()
