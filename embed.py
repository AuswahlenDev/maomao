import disnake

from media import get_avatar, get_gif
from meta import Metadata

def default_embed(message: str=None) -> disnake.Embed:
    embed = disnake.Embed()

    embed.description = message or ""
    embed.color = disnake.Colour.dark_green()

    return embed

def error_embed(message: str) -> disnake.Embed:
    embed = disnake.Embed()

    embed.description = f":x: {message}" 
    embed.color = disnake.Colour.brand_red()

    return embed 

async def track_embed(metadata: Metadata, position: int=None) -> disnake.Embed:
    """
    Generate an embed containing information about the given track
    """
    track = metadata.track
    
    pos = f"**`{position + 1}`.** " if position else ""
    embed = default_embed(f"{pos}View this song **[on {track.source.upper()}]({track.uri})**")

    embed.set_author(name=f"{metadata.requester.name}", icon_url=get_avatar(metadata.requester))

    embed.add_field(name="Title", value=f"**`{track.title}`**", inline=False)

    embed.add_field(name="Duration", value=f"**`{track.length}` seconds**")
    embed.add_field(name="channel", value=f"**`{track.author}`**")
    embed.add_field(name="Added by", value=f"**`@{metadata.requester.name}`**")
    embed.set_image(track.artwork_url)
    embed.set_thumbnail(await get_gif("dance"))

    return embed