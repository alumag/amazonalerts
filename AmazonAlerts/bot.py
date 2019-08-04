import asyncio

from discord import Client
from discord import Message

from .bot_token import TOKEN
from .webhooks import UrlsHandler

client = Client()


def handle_announce(*args, **kwargs):
    pass


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message: Message):
    if message.author.bot:
        return

    # Announce channel
    if message.channel.id == 605831151201943598:
        handler = UrlsHandler()
        await handler.create_message(message, message.channel)

    # Register URL channel
    if message.channel.id == 605831229123723265:
        handler = UrlsHandler()
        if message.content.startswith("remove"):
            await handler.remove_webhook(message.content.split()[1],
                                         message.channel)
        elif message.content.startswith("list"):
            await handler.list(message.channel)
        elif message.content.startswith("https://"):
            await handler.add_webhook(message.content, message.channel)


def run_bot():
    client.run(TOKEN)
