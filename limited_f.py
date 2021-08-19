from time import sleep
from queue import Empty


def run_task_process(mp_queue_input, mp_dict_output):
    while True:
        try:
            task_id, x = mp_queue_input.get(timeout=0.05)
            res = limited_f(x)
            mp_dict_output[task_id] = {"input": x, "output": res}
            print('sag', mp_dict_output)
        except Empty:
            continue


def limited_f(x):
    print('starting process..')
    sleep(x * 5.0)
    result = x ** 2
    print('ending process...')
    return result