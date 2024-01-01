import disnake
import mafic
import logging

from disnake import Interaction

from embed import error_embed, track_embed
from audio import MaomaoPlayer
from meta import Metadata, MetaDep

from typing import List

class SearchResultSelect(disnake.ui.StringSelect):
    def __init__(self, results: List[mafic.Track], metadep: MetaDep) -> None:
        self.disabled = False
        self.results = results
        self.metadep = metadep

        super().__init__(
            placeholder="Select a song",
            disabled=self.disabled,
        )

    async def callback(self, inter: Interaction) -> None:
        await inter.response.defer()
        try:
            await self.process_selected_option(inter)
        except Exception as e:
            logging.exception(f"Failed to display information about track. Error: {e}")
            await inter.edit_original_response(
                embed=error_embed("Something went wrong while playing this song. Please try again.")
            )

    async def process_selected_option(self, inter: Interaction) -> None:
        option = int(self.values[0])
        track = self.results[option]
        player: MaomaoPlayer = inter.guild.voice_client

        metadata = Metadata(
            channel_id=inter.channel.id,
            requester=inter.author,
            track=track
        )
        self.metadep.append_meta(metadata)

        embed = await track_embed(metadata, option)
        embed.title = f"Added to queue {track.title}"

        await player.append_track(track)
        await inter.edit_original_response(embed=embed)


class DropDownView(disnake.ui.View):
    def __init__(self, results: List[mafic.Track], metadep: MetaDep) -> None:
        super().__init__()

        self._menu = SearchResultSelect(results, metadep)
        self.add_item(self._menu)