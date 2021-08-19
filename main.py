from collections import defaultdict
import asyncio
from queue import PriorityQueue, Empty, Full
from multiprocessing import Pool, Manager, Queue as MPQueue

import asgiref.sync
from sanic import Sanic
from sanic.response import json

from limited_f import run_task_process


async def create_task(request, user_id: int, x: int):
    global task_id
    try:
        task_id += 1
        user_tasks[user_id].append(task_id)
        print(user_id, task_id, x)
        await asgiref.sync.sync_to_async(priority_q.put)((user_id, task_id, x), block=False)
    except Full:
        return json({"message": "Couldn't add to queue right now. please try again later.", "data": None}, status=500)

    return json({"message": "Task is added to queue.", "data": {"task_id": task_id}}, status=200)


async def get_result(request, user_id: int, task_id: int):
    if task_id not in user_tasks.get(user_id, []):
        return json({"message": f"user {user_id} does not have a task with id {task_id}.", "data": None},
                    status=404)
    if not (data := mp_dict_output.get(task_id)):
        return json({"message": "task is not finished yet.", "data": None}, status=200)
    return json({"message": "task finished successfully.", "data": data}, status=200)


async def add_to_process_queue_bg_task():
    while True:
        try:
            _, task_id, x = await asgiref.sync.sync_to_async(priority_q.get)(block=False)
            await asgiref.sync.sync_to_async(mp_queue_input.put)((task_id, x), block=False)
        except Empty:
            await asyncio.sleep(0.5)
        else:
            await asyncio.sleep(1.0)


if __name__ == '__main__':
    NUM_PROCESSES = 3
    priority_q = PriorityQueue()
    user_tasks = defaultdict(list)
    task_id = -1

    app = Sanic(__name__)
    app.add_route(create_task, "/create_task/<user_id:int>/<x:int>")
    app.add_route(get_result, "/get_result/<user_id:int>/<task_id:int>")
    app.register_listener(lambda app, _: app.add_task(add_to_process_queue_bg_task), "after_server_start")

    with Manager() as mp_manager:
        mp_dict_output = mp_manager.dict()
        mp_queue_input = MPQueue()
        with Pool(NUM_PROCESSES, run_task_process, (mp_queue_input, mp_dict_output)) as mp_pool:
            app.run()
