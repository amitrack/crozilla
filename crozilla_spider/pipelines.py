# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sys
import traceback
from datetime import datetime

from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker

from crozilla_spider.model import Listing, db_connect, create_table


class PersistencePipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        connection_string = settings.get("CONNECTION_STRING")
        crawl_id = settings.get("CRAWL_ID")
        return cls(connection_string, crawl_id)

    def __init__(self, connection_string, crawl_id):
        self.crawl_id = crawl_id
        try:
            self.engine = db_connect(connection_string)
            create_table(self.engine)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as err:
            traceback.print_tb(err.__traceback__)
            sys.exit(0)

    def process_item(self, item, spider):
        if item is None:
            raise DropItem("Invalid item found")
        session = self.Session()
        listing = item.to_listing()
        listing.crawl_id = self.crawl_id
        try:
            is_duplicate = self.check_duplicates(session, listing)
            if not is_duplicate:
                listing.found_last = listing.first_found
                session.add(listing)
            else:
                listing.found_last = datetime.now()
                session.merge(listing)
            session.commit()

        except Exception as err:
            traceback.print_tb(err.__traceback__)
            session.rollback()
            raise

        finally:
            session.close()
        if is_duplicate:
            raise DropItem("Duplicate item found: %s" % item['url'])
        return item

    def check_duplicates(self, session, listing: Listing):
        existing = session.query(Listing).filter_by(
            crozilla_id=listing.crozilla_id).first()
        if existing is not None:
            listing.id = existing.id
        else:
            listing.first_found = datetime.now()
        return existing is not None
