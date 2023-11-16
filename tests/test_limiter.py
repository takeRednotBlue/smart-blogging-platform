import requests
import asyncio

endpoint = "http://localhost:8000/api/v1/autocomplete/fruits?query_param=a"
times = 65


def test_limiter():
    for n in range(1, times+1):
        response = requests.get(endpoint)
        print(
            f"{n} - Status Code: {response.status_code}, Response Text: {response.text}"
        )

async def test_limiter_async():
    tasks = []
    for n in range(1, times+1):
        task = asyncio.create_task(make_request(n))
        tasks.append(task)
    await asyncio.gather(*tasks)

async def make_request(n):
    response = await asyncio.get_event_loop().run_in_executor(None, requests.get, endpoint)
    print(
        f"{n} - Status Code: {response.status_code}, Response Text: {response.text}"
    )

if __name__=='__main__':
    asyncio.run(test_limiter_async())