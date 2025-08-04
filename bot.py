import discord
from discord.ext import commands
from datetime import datetime
import socket
import requests
import os

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot läuft als {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
async def snowflake(ctx, user_id: int):
    timestamp = ((user_id >> 22) + 1420070400000) / 1000
    created = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    await ctx.send(f"📅 Account erstellt am: `{created}` UTC")

@bot.command()
async def whois(ctx, domain: str):
    try:
        ip = socket.gethostbyname(domain)
        await ctx.send(f"🔍 IP-Adresse von `{domain}`: `{ip}`")
    except Exception as e:
        await ctx.send(f"❌ Fehler: {e}")

@bot.command()
async def ipinfo(ctx, ip: str):
    try:
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url)
        data = response.json()
        output = f"""🌐 IP-Info zu `{ip}`:
• Stadt: {data.get("city", "N/A")}
• Region: {data.get("region", "N/A")}
• Land: {data.get("country", "N/A")}
• Provider: {data.get("org", "N/A")}
• Koordinaten: {data.get("loc", "N/A")}
"""
        await ctx.send(output)
    except Exception as e:
        await ctx.send(f"❌ Fehler bei der IP-Abfrage: {e}")

@bot.command()
async def userinfo(ctx, member: discord.Member):
    created = member.created_at.strftime('%Y-%m-%d %H:%M:%S')
    joined = member.joined_at.strftime('%Y-%m-%d %H:%M:%S') if member.joined_at else "Nicht verfügbar"
    await ctx.send(f"""
👤 Nutzerinfo für {member.mention}:
• Name & Tag: {member}
• ID: {member.id}
• Account erstellt: {created} UTC
• Server beigetreten: {joined} UTC
""")

@bot.command()
async def emailleak(ctx, email: str):
    try:
        api_key = os.getenv("HIBP_KEY")
        headers = {
            "hibp-api-key": api_key,
            "User-Agent": "discord-osint-bot"
        }
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=true"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            breaches = response.json()
            leaks = "\n• " + "\n• ".join([b for b in breaches])
            await ctx.send(f"🛑 Die E-Mail `{email}` wurde in folgenden Leaks gefunden:{leaks}")
        elif response.status_code == 404:
            await ctx.send(f"✅ Keine Leaks gefunden für `{email}`.")
        elif response.status_code == 401:
            await ctx.send("❌ Ungültiger oder fehlender HIBP-API-Key.")
        else:
            await ctx.send(f"❌ Fehler: Status {response.status_code}")
    except Exception as e:
        await ctx.send(f"❌ Ausnahmefehler: {e}")

bot.run(os.getenv("TOKEN"))
