import asyncio
import orm
from models import User,Blog,Comment
import logging as lg

async def test(loop):
    await orm.create_pool(loop,user='root',password='zjbaaa',db='awesome')
    u =User(name='test',email='test@example.com',passwd='abc123456',image='about:blank')
    lg.info(u.__insert__)
    await u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.run_forever()