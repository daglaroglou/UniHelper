import nextcord
from datetime import datetime
from nextcord.ext import commands
from typing import Optional
import json

class LoginModal(nextcord.ui.Modal):
    def __init__(self, author: Optional[str] = None):
        super().__init__(title="Login Page")

        self.user = nextcord.ui.TextInput(
            label="Email / Username",
            style=nextcord.TextInputStyle.short,
            placeholder=f"{author}@mail.com / abc12345" if author else "you@mail.com / abc12345",
            required=True,
            max_length=254,
        )
        self.password = nextcord.ui.TextInput(
            label="Password",
            style=nextcord.TextInputStyle.short,
            placeholder="Your password",
            required=True,
            max_length=200,
        )
        self.university = nextcord.ui.TextInput(
            label="University name / Acronym",
            style=nextcord.TextInputStyle.short,
            placeholder="University of Macedonia / UOM",
            required=True,
            max_length=100,
        )

        self.add_item(self.user)
        self.add_item(self.password)
        self.add_item(self.university)

    async def callback(self, interaction: nextcord.Interaction):
        loading_embed = nextcord.Embed(
            description="Logging in...",
            timestamp=datetime.now(),
            color=nextcord.Color.dark_grey()
        )
        await interaction.response.send_message(embed=loading_embed, ephemeral=True)
        
        user = self.user.value.strip()
        password = self.password.value
        university = self.university.value.strip()
        authorid = interaction.user.id
        url = ""
        match university.upper():
            case "UOM" | "UNIVERSITY OF MACEDONIA":
                url = "https://sis-portal.uom.gr"
                from misc.login_uom import authenticate_user
                ok = await authenticate_user(user, password, university, url, authorid)

        if ok:
            with open(f"./students/{authorid}.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                id = data["student"]["studentNo"]
            success_embed = nextcord.Embed(
                title="Login Successful",
                description=f"Welcome back, **{id}**!",
                color=nextcord.Color.green()
            )
            await interaction.edit_original_message(embed=success_embed)
        else:
            error_embed = nextcord.Embed(
                title="Login Failed",
                timestamp=datetime.now(),
                description="Please check your credentials and try again.",
                color=nextcord.Color.red()
            )
            await interaction.edit_original_message(embed=error_embed)


class Login(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="Log in to university portal")
    async def login(self, interaction: nextcord.Interaction):
        author = interaction.user.name
        modal = LoginModal(author=author)
        await interaction.response.send_modal(modal)


def setup(bot):
    bot.add_cog(Login(bot))