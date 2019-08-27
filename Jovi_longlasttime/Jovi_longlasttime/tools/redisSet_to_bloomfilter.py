import redis

from .bloomfilter import BloomFilter


def translate():
    r = redis.StrictRedis(host='localhost', port=6379, db=1)
    Filter = BloomFilter(redis=r, capacity=100000000, error_rate=0.00001, redis_key='JOVI_URLS')
    for i in r.sscan_iter('ZakerSpiderSpider'):
        Filter.add(i)
        print(i)


if __name__ == '__main__':
    translate()
