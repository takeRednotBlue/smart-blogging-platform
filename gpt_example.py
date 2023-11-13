"""
Demonstrating developers how to use GPT functionality for their functions, methods and fun
"""

from easy_open_ai import get_picture

result = get_picture("a white cat", save=True)
print(
    result[:30]
)  # it's gonna be a very long b64_json string, so I cut it to 30 not to flood

# async version of all the functions, add 'a' in front

# from easy_open_ai import aget_picture
# import asyncio
# asyncio.run(aget_picture('an alpaca'))
