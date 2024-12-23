from rq import Queue

from parsers.main1 import process_profession_data
from cache import Cache

connection = Cache().redis_client
queue = Queue(connection=connection)
queue.enqueue(process_profession_data, 'abcdef')
print('Task created')