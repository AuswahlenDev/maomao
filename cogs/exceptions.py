from disnake.ext import commands 
from disnake import ApplicationCommandInteraction

from embed import error_embed

class ExceptionCog(commands.Cog):
    def __init__(self, client: commands.AutoShardedBot) -> None:
        self.client = client 

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error) -> None:
        await ctx.send(embeds=[error_embed(f"Something is not right..."), error_embed(f"{error}")]) 

def setup(client: commands.AutoShardedBot) -> None:
    client.add_cog(ExceptionCog(client))