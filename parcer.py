import logging
import collections
import bs4
import requests
import csv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wb")

ParseReusult = collections.namedtuple(
    "ParseReusult",
    (
        "brand_name",
        "goods_name",
        "url",
        "price",
    ),
)

HEADERS = (
    "БРЕНД",
    "НАЗВАНИЕ",
    "ССЫЛКА",
    "ЦЕНА"

)

class Client:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
        "user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",

        }
        self.resuli =[]

    def load_page(self, page):
        url = f"https://www.wildberries.ru/catalog/obuv/muzhskaya/kedy-i-krossovki/krossovki?page={page}"
        res = self.session.get(url=url)
        res.raise_for_status()
        if not res:
            print("страниц больше нет")
            return
        return  res.text


    def parse_page(self, text):
        soup = bs4.BeautifulSoup(text, "lxml")
        container = soup.select("div.dtList.i-dtList.j-card-item")
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        url_block = block.select_one("a.ref_goods_n_p")

        if not url_block:
            logger.error("no url_block")
            return

        url = url_block.get("href")
        if not url:
            logger.error("no href")
            return

        name_block = block.select_one("div.dtlist-inner-brand-name")
        if not name_block:
            logger.error(f"no name_block on{url}")
            return

        brand_name = block.select_one("strong.brand-name")

        if not brand_name:
            logger.error(f"no brand_name on {url}")
            return

        brand_name = brand_name.text
        brand_name = brand_name.replace("/", "").strip()

        goods_name = name_block.select_one("span.goods-name")
        if not goods_name:
            logger.error(f"no goods_block on {url}")
            return
        goods_name = goods_name.text.strip()

        price = block.select_one(".lower-price")
        if not price:
            logger.error(f"not price no{url}")
            return
        price = price.text


        self.resuli.append(ParseReusult(
            url=url,
            brand_name=brand_name,
            goods_name=goods_name,
            price=price,
        ))
        logger.debug("%s, %s, %s, %s", url, brand_name, goods_name, price)
        logger.debug("-" * 100)

    def save_result(self):
        path = "/Users/denis/PycharmProjects/parcer/test.csv"
        with open(path, "w") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for i in self.resuli:
                writer.writerow(i)

    def run(self, page):
        text = self.load_page(page=page)
        self.parse_page(text=text)
        logger.info(f"Получили{len(self.resuli)} элементов")
        self.save_result()


if __name__ == "__main__":
    parce = Client()
    for i in range(1, 100):
        parce.run(page=i)