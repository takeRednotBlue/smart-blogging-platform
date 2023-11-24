from easy_open_ai import aget_picture_url
import asyncio
from src.services.cloudinarry import round_profile_pic

async def test_round_profile_pic():
    url = await aget_picture_url("a young woman")
    print(f'url = "{url}"')
   
    result = await round_profile_pic(2, url)
    print(result)

if __name__=='__main__':
    asyncio.run(test_round_profile_pic())
