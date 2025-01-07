from aiogram.fsm.storage.redis import RedisStorage
import redis

storage = RedisStorage.from_url('redis://El0ovA7S4LkfK36qNKVeOqh8b8k5xAP1@redis-16728.c244.us-east-1-2.ec2.redns.redis-cloud.com:16728')

r = redis.StrictRedis(
    host='redis-16728.c244.us-east-1-2.ec2.redns.redis-cloud.com',
    port=16728,
    password='El0ovA7S4LkfK36qNKVeOqh8b8k5xAP1',
    charset='utf-8',
    decode_responses=True
)


try:
    info = r.info()
    print(info['redis_version'])
    response = r.ping()
    if response:
         print("Подключение успешно!")
    else:
         print("Не удалось подключиться к Redis.")
except redis.exceptions.RedisError as e:
    print(f"Ошибка: {e}")
