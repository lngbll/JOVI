import math
import uuid

import pymmh3

__all__ = ['BloomFilter']


class BloomFilter(object):

    def __init__(self, redis, capacity=100000, error_rate=0.001,
                 redis_key: str = None):
        """Implements a space-efficient probabilistic data structure

        :param redis: aioredis connection object
        :param capacity:  this BloomFilter must be able to store at least
            *capacity* elements while maintaining no more than
            *error_rate* chance of false positives
        :param error_rate: the error_rate of the filter returning false
            positives. This determines the filters capacity. Inserting
            more than capacity elements greatly increases the chance of
            false positives.
        :param redis_key: key in redis, where bits for bloom filter will
            be stored.
        """
        # redis settings
        self._conn = redis
        # if redis key not provided, generate random one
        self._redis_key = redis_key or 'bloom:{}:cap:{}:err:{}'.format(
            uuid.uuid4().hex, redis_key, capacity, error_rate)

        self._capacity = capacity
        self._error_rate = error_rate
        # bloom filter settings
        self._filter_size, self._hash_funcs = self.optimal_bloom_filter(
            self._capacity, self._error_rate)
        self._bits_per_slice = int(self._filter_size / self._hash_funcs)

    @property
    def redis_key(self):
        """Key in redis database, where actual bit array is stored"""
        return self._redis_key

    @property
    def capacity(self):
        """Expected capacity of Bloom filter"""
        return self._capacity

    @property
    def error_rate(self):
        """Expected error rate for Bloom filter"""
        return self._error_rate

    def add(self, key):
        """Adds a key to this bloom filter.

        :param key: ``str``, key that must be added to the filter.
        """
        bit_positions = self._calc_bit_positions(key)
        return self._set_bits(self._redis_key, bit_positions)

    def contains(self, key):
        """Tests a key's membership in this bloom filter.

        :param key: ``str``, key to test membership
        :return: ``bool``
        """
        bit_positions = self._calc_bit_positions(key)
        result = self._check_bits(self._redis_key, bit_positions)
        return bool(result)

    def union(self, other_bloom, redis_key=None):
        """Calculates the union of the two Bloom filters and
        returns a new bloom filter object.

        :param other_bloom: other bloom filter for union
        :param redis_key: key for redis storage, if not present key will be
            generated automatically
        :return: ``BloomFilter``, new resulting filter
        """
        self._validate_bloom_input(other_bloom)
        if not redis_key:
            redis_key = 'bloom:union:{}:{}'.format(
                self.redis_key, other_bloom.redis_key)

        capacity = other_bloom.capacity
        error_rate = other_bloom.error_rate

        self._conn.execute_command(
            'BITOP', 'OR',
            redis_key, self.redis_key, other_bloom.redis_key
        )

        new_bloom = BloomFilter(self._conn, capacity, error_rate, redis_key)
        return new_bloom

    def intersection(self, other_bloom, redis_key=None):
        """Calculates the intersection of the two Bloom filters
        and returns a new Bloom filter object.

        :param other_bloom: ``BloomFilter`` to intersect with
        :param redis_key: ``str``
        :return: ``BloomFilter``, new resulting filter
        """
        self._validate_bloom_input(other_bloom)
        if not redis_key:
            redis_key = 'bloom:intersection:{}:{}'.format(
                self.redis_key, other_bloom.redis_key)

        capacity = other_bloom.capacity
        error_rate = other_bloom.error_rate

        self._conn.execute_command(
            'BITOP', 'AND',
            redis_key, self.redis_key, other_bloom.redis_key
        )

        new_bloom = BloomFilter(self._conn, capacity, error_rate, redis_key)
        return new_bloom

    @staticmethod
    def optimal_bloom_filter(capacity, failure_rate):
        """Calculate size of bit array and required number of hash functions
        for expected capacity and failure_rate

        :param capacity int:
        :param failure_rate:
        :returns: tuple, filter size and num of hash functions
        """
        if capacity < 0:
            raise ValueError('Capacity must be greater then 0 got: {}'
                             .format(capacity))
        if failure_rate < 0 or failure_rate > 1.0:
            raise ValueError('Failure rate must be in range (0, 1) got {}'
                             .format(failure_rate))

        n, p = float(capacity), float(failure_rate)
        m = -1 * (n * math.log(p)) / (math.log(2) ** 2)
        k = (m / n) * math.log(2)
        filter_size = int(math.ceil(m))
        hash_funcs = int(math.ceil(k))
        return filter_size, hash_funcs

    def _hash_bits(self, key):
        # http://spyced.blogspot.com/2009
        # /01/all-you-ever-wanted-to-know-about.html
        hash1 = pymmh3.hash(key, 0)
        hash2 = pymmh3.hash(key, hash1)
        for i in range(self._hash_funcs):
            yield abs((hash1 + i * hash2) % self._bits_per_slice)

    def _calc_bit_positions(self, key):
        offset = 0
        bit_positions = []
        for bit in self._hash_bits(key):
            bit_position = offset + bit
            offset += self._bits_per_slice
            bit_positions.append(bit_position)
        return bit_positions

    def _set_bits(self, key, bit_positions):
        script_set_bits = """
        for _, arg in ipairs(ARGV) do
            redis.call('SETBIT', KEYS[1], arg, 1)
        end
        """
        return self._conn.eval(script_set_bits, 1, key, *bit_positions)

    def _check_bits(self, key, bit_positions):
        script_check_bits = """
        for _, arg in ipairs(ARGV) do
            if redis.call('GETBIT', KEYS[1], arg) == 0
            then
                return 0
            end
        end
        return 1
        """
        is_all_bits_set = self._conn.eval(
            script_check_bits, 1, key, *bit_positions
        )
        return is_all_bits_set

    def _validate_bloom_input(self, other_bloom):
        if not isinstance(other_bloom, BloomFilter):
            raise TypeError('other_bloom must be instance of {}'
                            .format(self.__class__.__name__))

        if other_bloom.capacity != self.capacity:
            raise ValueError('Capacity of both bloom filters must be equal')

        if self.error_rate != other_bloom.error_rate:
            raise ValueError('Error rate of both bloom filters must be equal')
