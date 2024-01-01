from disnake.ext import commands 
import logging 
import mafic

from env import get_env

class MaomaoClient(commands.AutoShardedBot):
    INITIAL_EXTENSIONS = [
        "cogs.music",
        "cogs.exceptions"
    ]
    """
    Factory class for interacting with discord
    """
    def __init__(self) -> None:
        self.pool = mafic.NodePool(self)
        self.env = get_env()
        commands_sync_config = commands.CommandSyncFlags.default()
        commands_sync_config.sync_commands_debug = True 

        super().__init__(command_sync_flags=commands_sync_config)

    async def init_lavalink(self) -> None:
        logging.info("Establishing connection with lavalink node(s)")

        await self.pool.create_node(
            host=self.env.get("LAVALINK_HOST"),
            port=int(self.env.get("LAVALINK_PORT")),
            label="MAIN",
            password=self.env.get("LAVALINK_PASSWORD")
        )

    async def on_ready(self) -> None:
        """
        This method is called when the bot is ready. It initialises the required dependencies.
        """
        logging.info("Starting to gload custom extensions")
        for extension in self.INITIAL_EXTENSIONS:
            self.load_extension(extension)

        await self.init_lavalink()

    def ok(self) -> None:
        """
        Custom method to start the bot with the bot token
        """
        self.run(self.env.get("MAOMAO_TOKEN"))