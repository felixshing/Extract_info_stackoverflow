from concurrent.futures import ProcessPoolExecutor

import requests
import csv
from lxml import etree
import datetime
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['ekko']
col = db['stackoverflow']


# 1.0 数据爬取
def spider(url,day):
    headers = {
        'authority': 'stackoverflow.com',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://stackoverflow.com/questions/tagged/android?sort=Newest&edited=true',
        'accept-language': 'zh-CN,zh;q=0.9',
        # 'cookie': 'prov=20271510-a14b-e219-d06a-391363bde063; _ga=GA1.2.1782202514.1604546776; _gid=GA1.2.85864513.1604546776; __qca=P0-1507449979-1604546776646; __gads=ID=535da75ee4152ecb:T=1604546775:S=ALNI_MbFzxjHFWU4IWwPQhVlOIyW1XBi4A; usr=p=%5b160%7c%3bNewest%3b%5d',
    }

    response = requests.get(url, headers=headers, verify=False)
    if response.status_code != 200:
        return False
    parse_index(response.text,day)



def parse_index(response,day):
    doc = etree.HTML(response)
    item_list = doc.xpath('//*[@class="question-summary"]')
    for li in item_list:
        href = ''.join(li.xpath('./div[2]/h3/a/@href'))
        if not href:
            continue
        title = ''.join(li.xpath('./div[2]/h3/a/text()'))
        url = 'https://stackoverflow.com/' + href
        votes = int(''.join(li.xpath('./div[1]/div[1]/div[1]/div/span/strong/text()')))
        times = ''.join(li.xpath('./div[2]/div[3]/div/div[1]/span/@title')).split(' ')[0]
        views = int(''.join(li.xpath(".//div[contains(@class, 'views')]/@title")).split(' ')[0])
        beforetime = (datetime.datetime.now() + datetime.timedelta(days=-int(day))).strftime('%Y-%m-%d').replace('-', '')
        if int(beforetime) <= int(times.replace('-', '')):
            check_find = col.find_one({"_id":title+url})
            if check_find:
                continue
            col.insert({
                "_id": title + url,
                "url": url,
                'votes': votes,
                'times': times,
                'title':title,
                'views' : views
            })
        else:
            print('done')
            return False

def run():
    executor = ProcessPoolExecutor(6)
    res = []
    day = 30
    # 1.0 数据爬取
    for page in range(1, 1000):
        new_url = f'https://stackoverflow.com/questions/tagged/android?tab=newest&page={page}&pagesize=15'
        future = executor.submit(spider, new_url,day)
        res.append(future)
    executor.shutdown()



if __name__ == '__main__':

    run()
