from easy_open_ai import aget_picture_url
import asyncio
from src.services.cloudinarry import round_profile_pic


async def mock_round_profile_pic():
    url = await aget_picture_url("a young woman")

    result = await round_profile_pic(2, url)


if __name__ == "__main__":
    asyncio.run(mock_round_profile_pic())
