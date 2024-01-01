import disnake
from disnake.ext import commands
import mafic
import logging

from disnake import ApplicationCommandInteraction, TextChannel

from embed import default_embed, error_embed, track_embed
from audio import MaomaoPlayer
from meta import Metadata, MetaDep

from ui.player import InteractiveVolumeView
from ui.search import DropDownView

from typing import List


# Constants
EMBED_TITLES = {
    'results': "Search Results",
    'volume': "Volume Adjuster",
    'disconnect': "Disconnected",
    'skip': "Skipped to Next Track",
}

COMMAND_DESCRIPTIONS = {
    'play': "Search and play a song from YouTube, Spotify, SoundCloud, etc",
    'disconnect': "Disconnect the player and clear the queue",
    'volume': "Adjust the volume. Leave the options empty to use the interactive adjuster",
    'skip': "Skip to the next track in queue",
    'queue': "Get the list of all the songs in queue",
}


class MusicCog(commands.Cog):
    def __init__(self, client: commands.AutoShardedBot) -> None:
        self.client = client
        self.metadep = MetaDep()

    async def get_player(self, inter: ApplicationCommandInteraction) -> MaomaoPlayer:
        """
        Get the instance of MaomaoPlayer
        """
        voice_client: MaomaoPlayer | None = inter.guild.voice_client

        if not voice_client:
            voice_client = await inter.user.voice.channel.connect(cls=MaomaoPlayer)
        return voice_client

    async def is_user_connected(inter: ApplicationCommandInteraction) -> bool:
        """
        A check to confirm whether the user is connected to a voice channel.
        """
        await inter.response.defer()
        if not inter.author.voice:
            await inter.edit_original_response(embed=error_embed(f"You are not connected to a voice channel. Please connect to one and try again"))
            return False 
        return True

    @commands.Cog.listener()
    async def on_track_end(self, event: mafic.TrackEndEvent) -> None:
        try:
            if not isinstance(event.player, MaomaoPlayer):
                raise commands.CommandError("The player instance is not of MaomaoPlayer")

            player: MaomaoPlayer = event.player
            if player.queue:
                track: mafic.Track = player.queue.pop()
                
                metadata: Metadata = self.metadep.get(track)
                if metadata:
                    channel: TextChannel = self.client.get_channel(metadata.channel_id)
                    embed = await track_embed(metadata)
                    embed.title = "Now Playing"

                    await channel.send(embed=embed)
                    self.metadep.remove_meta(metadata.meta_id)

                await player.append_track(track)
                await player.play(track)
        except Exception as e:
            logging.exception(f"An error occurred during track end handling. Error: {e}")

    @commands.slash_command(name="play", description=COMMAND_DESCRIPTIONS['play'])
    @commands.check(is_user_connected)
    async def play(
        self, inter: ApplicationCommandInteraction, song: str, source: mafic.SearchType = mafic.SearchType.YOUTUBE
    ) -> None:

        player: MaomaoPlayer = await self.get_player(inter)

        results = await player.fetch_tracks(query=song, search_type=source)
        if not results:
            await inter.edit_original_response(embed=error_embed(f"I could not find anything with **`{song}`**"))
            return
        
        results_embed = default_embed(f"**Found `{len(results)}` search results for `{song}`**\n\nUse the menu below to navigate through the results.")

        view = DropDownView(results, self.metadep)
        menu = view._menu 

        for i, result in enumerate(results):
            title = result.title[:100] + ('...' if len(result.title) > 100 else '')

            menu.add_option(label=f"{i + 1}", value=f"{i}", description=f"{title}")

        await inter.edit_original_response(embed=results_embed, view=view)

    @commands.slash_command(name="disconnect", description=COMMAND_DESCRIPTIONS['disconnect'])
    @commands.check(is_user_connected)
    async def disconnect(self, inter: disnake.ApplicationCommandInteraction) -> None:
        player: MaomaoPlayer | None = inter.guild.voice_client
        if not player:
            await inter.edit_original_response(embed=error_embed("I am not playing any music right now"))
            return

        await player.disconnect()
        await inter.edit_original_response(embed=default_embed(f"I have disconnected from the voice channel. Bye :wave:"))

    @commands.slash_command(name="volume", description=COMMAND_DESCRIPTIONS['volume'])
    @commands.check(is_user_connected)    
    async def volume(self, inter: ApplicationCommandInteraction, amount: commands.Range[int, 0, 100]=None) -> None:
        player: MaomaoPlayer = await self.get_player(inter)

        if amount:
            await player.set_volume(amount)
            await inter.edit_original_response(embed=default_embed(f":thumbsup: Volume has been set to **`{amount}%`**"))
            return

        view = InteractiveVolumeView()
        embed = default_embed(f":loud_sound: **Volume Adjuster**\n\nCurrent Volume: **`{player._volume}%`**\nMax Volume: **`100%`**\nMax Volume: **`200%`** ***(DEAF MODE)***\n\n`It is recommended to not use deaf mode. It will reduce the audio quality significantly`")
        embed.set_footer(text="Use the buttons below to adjust the volume.")

        await inter.edit_original_response(embed=embed, view=view)

    @commands.slash_command(name="skip", help=COMMAND_DESCRIPTIONS['skip'])
    @commands.check(is_user_connected)
    async def skip(self, inter: ApplicationCommandInteraction) -> None:
        player: MaomaoPlayer = await self.get_player(inter)

        if not player.current:
            await inter.edit_original_response(embed=error_embed(f"There are no tracks in queue right now"))
            return

        current_track_pos: int | None = player.get_track_position(player.current)
        next_track: mafic.Track | None = player.get_track(current_track_pos + 1)

        if not next_track:
            await inter.edit_original_response(embed=error_embed(f"There is no track in queue after this"))
            return

        await player.stop()
        await player.play(next_track)

        await inter.edit_original_response(embeds=[default_embed(f"Skipped to next track in queue :thumbsup:")])

    @commands.slash_command(name="queue", description=COMMAND_DESCRIPTIONS['queue'])
    @commands.check(is_user_connected)
    async def queue(self, inter: ApplicationCommandInteraction) -> None:
        player: MaomaoPlayer = await self.get_player(inter)

        if not player.current:
            await inter.edit_original_response(embed=error_embed(f"There are no tracks in queue right now"))
            return

        tracks: List[mafic.Track] = list(player.queue)
        embed = default_embed(f"**There are `{len(tracks)}` tracks in queue**")

        track_list = "\n".join([f"{i + 1}. {track.title} by `{track.author}`" for i, track in enumerate(tracks)])
        embed.add_field(name="Queue", value=track_list, inline=False)

        await inter.edit_original_response(embed=embed)


def setup(client: commands.AutoShardedBot) -> None:
    client.add_cog(MusicCog(client))
