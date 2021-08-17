from time import sleep
from queue import PriorityQueue, Empty as EmptyQueueException
from multiprocessing import Process
import asyncio
import asgiref.sync

from sanic import Sanic
from sanic.response import json

priority_q = PriorityQueue()


async def salam(request):
    return json({"message": "salam"})


async def prioritized_request(request, user_id: int, x: int):
    print(user_id, x)
    priority_q.put((user_id, x))
    return json({"message": "Task is added to queue.", "data": None})


async def get_task():
    print('starting task')
    while True:
        # print('checking...')
        try:
            user_id, x = await asgiref.sync.sync_to_async(priority_q.get)(block=False)
            print(f"calling process for user {user_id}, {x}")
            p = Process(target=limited_f, args=(x, user_id))
            p.start()
        except EmptyQueueException:
            await asyncio.sleep(0.5)


async def after_server_start(app, loop):
    app.add_task(get_task)
    return


def limited_f(x, user_id):
    print(f'Process started for user {user_id}, {x}')
    sleep(x * 5.0)
    print(f"Process ended for user {user_id}, {x}")
    return


if __name__ == '__main__':
    app = Sanic(__name__)
    app.add_route(salam, "/")
    app.add_route(prioritized_request, '/<user_id:int>/<x:int>')
    app.register_listener(after_server_start, "after_server_start")
    app.run()
