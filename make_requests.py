import requests

user_ids = (1, 1, 2, 1, 3, 1, 10, 3, 2, 5, 1, 1, 1, 10, 9)

for i in user_ids:
    print(requests.get(f'http://127.0.0.1:8000/create_task/{i}/1'))
