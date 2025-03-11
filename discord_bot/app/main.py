import discord
from discord import Embed
from discord.ext import commands
import logging
from discord.ui import Button, View

from config import settings
from calls import telegram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced: {len(synced)} command's")
    except Exception as e:
        logger.error(e)


@bot.tree.command(name="reset", description="Отвязать Telegram аккаунта.")
async def cmd_reset(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    response = await telegram.reset(interaction.user.id)

    if response.status_code == 200:
        response = await telegram.link(interaction.user.id)
        view = View().add_item(
            Button(label="Авторизоваться", url=response.json()["link"])
        )
        embed = Embed(
            color=5763719,
            title="Аккаунт Telegram был отвязан",
            description="Нажмите на кнопку «Авторизоваться» для привязки аккаунта Telegram.",
        )
        await interaction.followup.send(embed=embed, view=view)  # noqa
    else:
        await interaction.followup.send(  # noqa
            embed=Embed(
                color=15548997,
                title="Ошибка",
                description="Обратитесь к администрации сервера.",
            ),
            ephemeral=True,
        )


@bot.tree.command(name="link", description="Привязать Telegram аккаунт.")
async def cmd_link(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)  # noqa
    response = await telegram.link(interaction.user.id)
    view = View().add_item(Button(label="Авторизоваться", url=response.json()["link"]))
    embed = Embed(
        color=5763719,
        title="Привязка аккаунта",
        description="Нажмите на кнопку «Авторизоваться» для привязки аккаунта Telegram.",
    )

    await interaction.followup.send(embed=embed, view=view)  # noqa


@bot.event
async def on_message(message):
    if message.channel.id != settings.discord_channel_id or message.author.bot:
        return

    if "https" in message.content:
        response = await telegram.send_gif(message.author.id, message.content)

        match response.status_code:
            case 200:
                await message.add_reaction("✅")
            case 401:
                await message.channel.send(
                    embed=Embed(
                        color=15548997,
                        title="Ошибка авторизации",
                        description="Для привязки Telegram аккаунта отправьте команду /link.",
                    )
                )
            case 404:
                await message.channel.send(
                    embed=Embed(
                        color=15548997,
                        title="Ошибка отправки GIF",
                        description="Нажмите на GIF в Discord и скопируйте ссылку на нее, далее отправьте в чат.",
                    )
                )
            case _:
                await message.channel.send(
                    embed=Embed(
                        color=15548997,
                        title="Неизвестная ошибка",
                        description="Что-то сломалось, но мы пока не знаем что :(",
                    )
                )

    await bot.process_commands(message)


bot.run(settings.discord_bot_token)
