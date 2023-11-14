import time
import requests
import asyncio

# This script sends GET requests to the localhost server at port 8000 and
# prints out the status code and response text for each request.
# import aiohttp
# import asyncio

# counter=0
# times=2
# async def fetch_data(url):
#     global counter
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             counter+=1
#             return await (response.text(), response.url())
#             # yield response

# async def test():
#     global counter
#     url = 'http://localhost:8000/api/v1/autocomplete?query_param=fgh'
#     data = await fetch_data(url)
#     print(counter)
#     print(data)
#         # Print the final URL after redirection
#     # redirected_url = data.url
#     # print(f'Redirected URL: {redirected_url}')

# async def main():
#     tasks=[test() for i in range(times)]
#     await asyncio.gather(*tasks)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# asyncio.run(main())
for _ in range(5):  # Loop to send 10 GET requests
    # Send a GET request to the server running on localhost at port 8000
    response = requests.get("http://localhost:8000/api/v1/autocomplete/fruits?query_param=fgh") 
    tasts=[]
    # Print the status code and the response text from the server
    print(f"Status Code: {response.status_code}, Response Text: {response.text}")
    
    # time.sleep(1)  # Pause execution for 1 second before the next iteration
