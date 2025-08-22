import discord
import aiohttp
import asyncio
import bot_config
import datetime

TOKEN = bot_config.TOKEN
CHANNEL_ID = bot_config.CHANNEL_ID
API_URL = bot_config.API_URL
CHECK_INTERVAL = bot_config.CHECK_INTERVAL

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Track stale alerts so they only fire once until reset
alerted = {
    "chat": False,
    "players": False,
    "status": False,
    "server": False
}

async def check_status():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL) as resp:
                    if resp.status == 200:
                        data = await resp.json()

                        chat_age = data.get("last_chat_update_age", 999999) # NOTE API returns age in minutes!
                        players_age = data.get("last_players_update_age", 999999)
                        status = data.get("status", "stale")

                        print(f"Chat age: {chat_age}, Players age: {players_age}, Status: {status} at {datetime.datetime.now()}")

                        # Chat stale
                        if chat_age > 4:
                            if not alerted["chat"]:
                                await channel.send(
                                    f"⚠️ Chat updates are stale ({chat_age} minutes old) <@232014294303113216> (restart script, will not self reset)"
                                )
                                alerted["chat"] = True
                                print(f"Chat age alert sent: {chat_age} minutes")
                        else:
                            alerted["chat"] = False

                        # Players stale
                        if players_age > 4:
                            if not alerted["players"]:
                                await channel.send(
                                    f"⚠️ Player updates are stale ({players_age} minutes old) <@232014294303113216> (restart script, will not self reset)"
                                )
                                alerted["players"] = True
                                print(f"Players age alert sent: {players_age} minutes")
                        else:
                            alerted["players"] = False

                        # Status bad
                        if status != "ok":
                            if not alerted["status"]:
                                await channel.send(
                                    f"❌ Status is `{status}`. Stats updater may be down too. <@232014294303113216> (restart script, will not self reset)"
                                )
                                alerted["status"] = True
                                print(f"Status alert sent: {status}")
                        else:
                            alerted["status"] = False

                        # 200, reset server alert
                        alerted["server"] = False

                    elif resp.status != 200:
                        if not alerted["server"]:
                            await channel.send(
                                f"❗️ API returned HTTP {resp.status}. Is the server down? <@232014294303113216> (restart script, will not self reset)"
                            )
                            alerted["server"] = True
                            print(f"Server alert sent: HTTP {resp.status}")
                        
        except Exception as e:
            print("Error checking status:", e)

        await asyncio.sleep(CHECK_INTERVAL) # BUG: loop will no repeat. 


@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")
    client.loop.create_task(check_status())

client.run(TOKEN)
