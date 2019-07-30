from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from discord import Webhook, AsyncWebhookAdapter, Embed, errors
import aiohttp

Base = declarative_base()


class WebhookTable(Base):
    __tablename__ = "webhook"
    token = Column(String(250), primary_key=True, nullable=False)
    id = Column(Integer, nullable=False)
    url = Column(String(250), nullable=False)
    channel_id = Column(Integer)
    guild_id = Column(Integer)


class UrlsHandler(object):

    def __init__(self):
        engine = create_engine('sqlite:///webhooks.db')
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    async def add_webhook(self, url: str, channel):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(url,
                                       adapter=AsyncWebhookAdapter(session))
            new_webhook = WebhookTable(token=webhook.token, id=webhook.id,
                                       url=url,
                                       channel_id=webhook.channel_id,
                                       guild_id=webhook.guild_id)

            self.session.add(new_webhook)
            self.session.commit()

            embed = Embed(title="Webhook saved",
                          description="New webhook saved", color=0xbda1a1)
            embed.add_field(name="Channel ID", value=webhook.channel)
            embed.add_field(name="Guild ID", value=webhook.guild)
            embed.add_field(name="URL", value=webhook.url)
            embed.add_field(name="ID", value=webhook.id)
            embed.add_field(name="Token", value=webhook.token)
            await channel.send(embed=embed)

    async def remove_webhook(self, webhook_id: str, channel):
        webhook = self.session.query(WebhookTable).\
            filter(WebhookTable.id == webhook_id).one()
        token = webhook.token
        self.session.delete(webhook)
        self.session.commit()
        embed = Embed(title="Webhook deleted",
                      description="Webhook removed", color=0x890b32)
        embed.add_field(name="ID", value=webhook_id)
        embed.add_field(name="Token", value=token)
        await channel.send(embed=embed)

    async def list(self, channel):
        webhooks = self.session.query(WebhookTable).all()

        embed = Embed(title="Webhooks list", color=0x0f3766)
        for index, webhook in enumerate(webhooks):
            embed.add_field(name="{}) Webhook id {}".format(index, webhook.id),
                            value="[🔗]({}) | TOKEN = {}".
                            format(webhook.url, webhook.token))
        await channel.send(embed=embed)

    async def create_message(self, message, channel):
        webhooks = self.session.query(WebhookTable).all()

        # Get the announcement header
        header = message.content.split("\n")[0]
        link = message.content.split("\n")[-1]
        if not link.startswith("http"):
            await channel.send("Error: '{}' is not a valid product URL".
                               format(link))
            await channel.send("Please send your announcement again and "
                               "make sure a valid link is appended to the end "
                               "of your message.")
            return
        data = "\n".join(message.content.split("\n")[1:-1])
        embed = Embed(title=header, url=link, description=data, color=0xeee5de)
        try:
            embed.set_thumbnail(url=message.attachments[0].url)
        except IndexError:
            # Except messages without attachment
            pass

        for webhook in webhooks:
            async with aiohttp.ClientSession() as session:
                try:
                    await Webhook.from_url(webhook.url,
                                     adapter=AsyncWebhookAdapter(session)).send(
                        embed=embed,
                        username="DealCopper",
                        avatar_url="https://i.imgur.com/crgub5N.jpg",
                    )
                except errors.NotFound:
                    self.session.delete(webhook)
                    self.session.commit()
