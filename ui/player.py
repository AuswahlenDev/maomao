from disnake.interactions import MessageInteraction
from disnake.ui import View
from disnake.ui import Button
from disnake import ButtonStyle

from audio import MaomaoPlayer
from embed import default_embed

class InteractiveVolumeView(View):
    """
    UI for the interactive volume adjuster
    """
    def __init__(self) -> None:  
        super().__init__() 
        self.buttons = [
            Button(label="Mute", custom_id="volume-set-mute", style=ButtonStyle.red),
            Button(label="Low (30%)", custom_id="volume-set-low", style=ButtonStyle.blurple),
            Button(label="Medium (50%)", custom_id="volume-set-med", style=ButtonStyle.secondary),
            Button(label="High (80%)", custom_id="volume-set-high", style=ButtonStyle.green),
            Button(label="Full (100%)", custom_id="volume-set-full", style=ButtonStyle.grey),
            Button(label="Deaf Mode (200%)", custom_id="volume-set-deaf", style=ButtonStyle.red)
        ]

        for button in self.buttons:
            self.add_item(button)
            
    async def interaction_check(self, inter: MessageInteraction) -> bool:
        await inter.response.defer()

        player: MaomaoPlayer | None = inter.guild.voice_client
        if not player:
            return 
        
        component = inter.component
        c_id = component.custom_id
        if not c_id:
            return 

        if c_id == "volume-set-mute":
            await player.set_volume(0)
        elif c_id == "volume-set-low":
            await player.set_volume(30)
        elif c_id == "volume-set-high":
            await player.set_volume(50)
        elif c_id == "volume-set-full":
            await player.set_volume(100)
        elif c_id == "volume-set-deaf":
            await player.set_volume(200)

        await inter.edit_original_response(embed=default_embed(f":thumbsup: Volume has been set to **`{component.label}`**"))