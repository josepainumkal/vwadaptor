import os 
# import docker
# import docker.utils

import requests
import json
from celery import Celery

from sets import Set
from time import sleep
from celery.result import AsyncResult
from time import sleep
# import docker
# import docker.utils

from redis import Redis
redis = Redis(host='workerdb', port=6379, db=1)

# client = docker.Client()
celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')


print "ACTIVE: ",celery.control.inspect().active()
print "SCHEDULE: ",celery.control.inspect().scheduled()
print "REGISTERED: ",celery.control.inspect().registered()




# def queue_length():
#     r = requests.get("http://192.168.99.100:5555/api/queues/length")
#     # print r.status_code, r.headers, r.content
#     resp_dict = json.loads(r.content)
#     queue_length = int(resp_dict['active_queues'][0]['messages'])
#     # print queue_length
#     return queue_length

p = redis.pipeline()
p.set('MaxRentedModelsAllowed', 3200)
p.set('CurrentRentedModels', 200)
p.execute()

# # print "Done"

MaxRentedModelsAllowed = redis.get('MaxRentedModelsAllowed')
CurrentRentedModels = redis.get('CurrentRentedModels')

print 'MaxRentedModelsAllowed:',MaxRentedModelsAllowed
print 'CurrentRentedModels:',CurrentRentedModels
# print 'queue_length: ',queue_length()


# def get_user_last_activity(user_id):
#     last_active = redis.get('user-activity/%s' % user_id)
#     if last_active is None:
#         return None
#     return datetime.utcfromtimestamp(int(last_active))




# p.sadd(all_users_key, user_id)
#     p.set(user_key, now)
#     p.expireat(all_users_key, expires)
#     p.expireat(user_key, expires)
#     p.execute()

# def mark_online(user_id):
#     now = int(time.time())
#     expires = now + (ONLINE_LAST_MINUTES * 60) + 10
#     all_users_key = 'online-users/%d' % (now // 60)
#     user_key = 'user-activity/%s' % user_id
#     p = redis.pipeline()
#     p.sadd(all_users_key, user_id)
#     p.set(user_key, now)
#     p.expireat(all_users_key, expires)
#     p.expireat(user_key, expires)
#     p.execute()

