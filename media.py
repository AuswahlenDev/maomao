import aiohttp 
import logging 
import disnake 

NEKOS_BEST_API = "https://nekos.best/api/v2/" 

async def get_gif(search_query: str) -> str:
    """
    Get a GIF url based on the search query 

    Returns a `str`, may be a `None` if there is an error or the API sends a status code other than 200
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(NEKOS_BEST_API + search_query) as response:
                if response.status != 200:
                    return None 
                body = await response.json()
                return body.get("results")[0].get("url")
    except aiohttp.ClientError as e:
        logging.error(f"Failed to fetch GIF from NEKOS BEST API for the search query: {search_query};\n{e}")
        return None 
    
def get_avatar(user: disnake.User | disnake.Member) -> str:
    return user.avatar.url if user.avatar else user.default_avatar.url 