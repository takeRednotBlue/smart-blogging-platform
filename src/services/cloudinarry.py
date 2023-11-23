"""Naming 'cloudinarry' is chosen to avoid arising conflicts with their SDK. SDK itself has to async calls. The JS widget they provide can't be modified."""
# https://cloudinary.com/documentation/upload_widget <-- an easier solution

import hashlib
import time
import aiohttp

from src.conf.config import settings

cloud_name = settings.cloudinary_name
api_key = settings.cloudinary_api_key
api_secret = settings.cloudinary_api_secret


def users_image_cloudinary_path(user_id):
    """General album of a user - defines project structure on the cloud."""
    return f"smart-blogging-platform/{user_id}"


def generate_cloudinary_signature(params, api_secret):
    """
    Needed for the API call.
    See https://cloudinary.com/documentation/upload_images#manual_signature_generation
    """
    params_to_sign = {k: v for k, v in params.items() if k not in ["file", "api_key"]}
    # Sort parameters alphabetically by key
    sorted_params = sorted(params_to_sign.items())

    # Concatenate parameters into a string
    param_str = "&".join([f"{key}={value}" for key, value in sorted_params])

    # Append the API secret
    to_sign = param_str + api_secret

    # Create the SHA-1 hash
    signature = hashlib.sha1(to_sign.encode("utf-8")).hexdigest()

    return signature


async def image_exists_on_cloudinary(user_id, image_name):
    """Again, pretty self-documented flag. See https://cloudinary.com/documentation/image_upload_api_reference"""

    endpoint = f"https://{api_key}:{api_secret}@api.cloudinary.com/v1_1/{cloud_name}/resources/image"
    params = {}
    params["prefix"] = f"{users_image_cloudinary_path(user_id)}/{image_name}"
    params["type"] = "upload"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, params=params) as response:
            result = await response.json()
            if result.get("resources"):
                return True
            return False


async def upload_image_to_cloudinary(user_id, image_url, image_name, unique=True):
    """Uploads image to cloudinary. If unique set to False, overwrites the previous image.
    See https://cloudinary.com/documentation/image_upload_api_reference"""
    # error_handling https://cloudinary.com/documentation/upload_images

    endpoint = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"

    params = {"file": image_url, "api_key": api_key, "timestamp": int(time.time())}

    params["public_id"] = image_name
    params["folder"] = users_image_cloudinary_path(user_id)

    params["signature"] = generate_cloudinary_signature(params, api_secret)

    if unique and await image_exists_on_cloudinary(user_id, image_name):
        raise ValueError("File alredy exists!")

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, data=params) as response:
            result = await response.json()
            if result.get("secure_url"):
                return result.get("secure_url")
            raise ConnectionError("Cloudinary error!")
