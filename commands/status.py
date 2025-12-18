import psutil
import requests
import nextcord
from nextcord.ext import commands
from datetime import datetime, timedelta
import sys

class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.now()

    def _get_progress_bar(self, percentage: float, length: int = 10) -> str:
        filled = int(length * percentage / 100)
        bar = "█" * filled + "░" * (length - filled)
        return bar

    @nextcord.slash_command(name="status", description="Check bot and system status")
    async def status(self, interaction: nextcord.Interaction):
        portal = requests.get("https://sis-portal.uom.gr", timeout=5).status_code
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        bot_latency = round(self.bot.latency * 1000)
        
        uptime = datetime.now() - self.start_time
        uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))
        
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        nextcord_version = nextcord.__version__
        
        status_embed = nextcord.Embed(
            title="Status",
            color=nextcord.Color.light_grey(),
            timestamp=datetime.now()
        )
        
        portal_status = "Online" if portal == 200 else "Offline"
        status_embed.add_field(
            name="Portal",
            value=f"`{portal_status}`",
            inline=True
        )
        
        status_embed.add_field(
            name="Uptime",
            value=f"`{uptime_str}`",
            inline=True
        )
        
        status_embed.add_field(
            name="Latency",
            value=f"`{bot_latency}ms`",
            inline=True
        )

        cpu_bar = self._get_progress_bar(cpu_usage)
        status_embed.add_field(
            name="CPU",
            value=f"{cpu_bar} `{cpu_usage}%`",
            inline=False
        )
        
        ram_bar = self._get_progress_bar(memory_percent)
        status_embed.add_field(
            name="RAM",
            value=f"{ram_bar} `{memory_percent}%`",
            inline=False
        )
        
        disk_bar = self._get_progress_bar(disk_percent)
        status_embed.add_field(
            name="Disk",
            value=f"{disk_bar} `{disk_percent}%`",
            inline=False
        )
        
        status_embed.add_field(
            name="Python",
            value=f"`{python_version}`",
            inline=True
        )
        
        status_embed.add_field(
            name="Nextcord",
            value=f"`{nextcord_version}`",
            inline=True
        )

        await interaction.response.send_message(embed=status_embed)

def setup(bot: commands.Bot):
    bot.add_cog(Status(bot))