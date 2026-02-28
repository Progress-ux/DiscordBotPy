import discord
from discord.ext import commands
from discord import app_commands
from cogs.locales.locale_manager import LocaleManager

class LanguageCommand(commands.Cog):
    """
    A Discord bot cog that handles the '/language' slash command.
    Allows users to select their preferred language for bot responses.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.locale_manager: LocaleManager = bot.locale_manager
    
    @app_commands.command(name="language", description="Select bot response language / Выбрать язык бота")
    @app_commands.describe(language="Choose language / Выберите язык")
    @app_commands.choices(language=[
        app_commands.Choice(name="English", value="eng"),
        app_commands.Choice(name="Русский", value="rus")
    ])
    async def language(self, interaction: discord.Interaction, language: app_commands.Choice[str]):
        """
        Change the bot's language for this server.
        """
        guild_id = interaction.guild.id
        
        # Set the new language
        success = self.locale_manager.set_guild_locale(guild_id, language.value)
        
        if success:
            # Get confirmation message in the new language
            response = self.locale_manager.get_text(
                guild_id,
                "language.changed",
                language=language.name
            )
            
            embed = discord.Embed(
                title=self.locale_manager.get_text(guild_id, "language.title"),
                description=response,
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "Failed to change language. / Не удалось изменить язык.",
                ephemeral=True
            )
    
    @app_commands.command(name="lang", description="Show current language / Показать текущий язык")
    async def lang(self, interaction: discord.Interaction):
        """
        Show the current language setting for this server.
        """
        guild_id = interaction.guild.id
        current_lang = self.locale_manager.get_guild_locale(guild_id)
        lang_name = self.locale_manager.get_available_languages().get(current_lang, "English")
        
        embed = discord.Embed(
            title=self.locale_manager.get_text(guild_id, "language.title"),
            color=discord.Color.blue()
        )
        embed.add_field(
            name=self.locale_manager.get_text(guild_id, "language.current"),
            value=f"{lang_name} ({current_lang})",
            inline=False
        )
        embed.add_field(
            name=self.locale_manager.get_text(guild_id, "language.select"),
            value="Use `/language` to change",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LanguageCommand(bot))