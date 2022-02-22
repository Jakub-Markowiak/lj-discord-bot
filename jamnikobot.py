import discord
from numpy import random
import pandas as pd
from discord.ext import commands
import youtube_dl
import time 
import asyncio

intents = discord.Intents().all()
client = discord.Client(intents=intents)
prefix = "jamnik:"
bot = commands.Bot(command_prefix=prefix, intents=intents)


def filter_list(module = "The Deluge"):
    dfs = pd.read_html('http://www.mnbcentral.net')
    df = dfs[0]
    df_filtered = df[df.Module == module]
    df_filtered['Current Players'] = pd.to_numeric(df_filtered['Current Players'])
    df_filtered = df_filtered.sort_values(by="Current Players", ascending = False)

    return(df_filtered)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
	# INCLUDES THE COMMANDS FOR THE BOT. WITHOUT THIS LINE, YOU CANNOT TRIGGER YOUR COMMANDS.
    await bot.process_commands(message)
    emojis = message.content.get_emoji

    print(emojis)

    for emoji in emojis:
        if emoji == "<:pika:870269011026403338>":
            await message.channel.send("To nie pika, to wykałaczka!")


@bot.command(help="Aportuj!")
async def aport(ctx, distance: int = 50):
    roll = round(random.uniform(0, distance), 2)
    await ctx.channel.send("Rzuciłeś piłeczkę na odległość {} metrów!".format(roll))
    
    speed = round(random.uniform(1,6),2)
    wait = round(roll/speed,2) * 2


    gif_roll = round(random.uniform(1,3),0)
    if gif_roll == 1:
        await ctx.channel.send("https://media.giphy.com/media/HsQKArTHbA0U0/giphy.gif",  delete_after=wait)
    elif gif_roll == 2:
        await ctx.channel.send("https://i.makeagif.com/media/9-03-2015/FjUhjW.gif",  delete_after=wait)
    else:
        await ctx.channel.send("https://thumbs.gfycat.com/MistyWideeyedLcont-size_restricted.gif",  delete_after=wait)

    await asyncio.sleep(wait)
    await ctx.channel.send("Jamnik pędził z prędkością {}m/s i wrócił z piłeczką w czasie {}s!".format(speed,wait))
    await ctx.channel.send("https://24.media.tumblr.com/4a1cba203ecdc10b1f9ff18333817906/tumblr_n4tl1oZEBu1qhv4h7o1_400.gif")
    


@bot.command(help='Jamniki robią hau hau')
async def hau(ctx):
    roll = random.uniform(0, 2)
    if roll < 1:
        await ctx.channel.send('Hau hau!')
    elif roll >= 1:
        await ctx.channel.send('Woof woof!')

@bot.command(help='Sprawdź czy ktoś gra w deluge')
async def deluge(ctx):
    df_filtered = filter_list(module="The Deluge")
    count_players = sum(df_filtered['Current Players'])
        
    if count_players > 0:
        text = 'Są ludzie na Deluge! Całe {}! \n'.format(count_players)
    elif count_players == 0:
        text = "Nie ma nikogo na Deluge. Chlip chlip... \n"

    for k in range(len(df_filtered)):
        row = df_filtered.iloc[k]
        server = row['Server Name']
        gamemode = row['Game Type']
        players = row['Current Players']
        password = row['Password']

        text = text + '**{}** | Gracze: {} | Tryb: {} | Hasło: {} \n'.format(server,players,gamemode, password)

    await ctx.channel.send(text)
    if count_players > 0:
        await ctx.channel.send("https://media.giphy.com/media/kreQ1pqlSzftm/giphy.gif \n")
    else:
        await ctx.channel.send(" https://i.imgur.com/H2i4PEE.jpg \n")

# BOT MUZYCZNY

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.command(name='join', help='Bot wbije na kanał głosowy')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.channel.send("{} nie jest na głosowym! ".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='Bot ucieknie z kanału głosowego')
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.channel.send("Nie jest połączony z głosowym.")


@bot.command(name='play', help='Zagraj coś jamniku')
async def play(ctx, url: str = 'http://s1.slotex.pl:7022/graj.mp3'):
    channel = ctx.message.author.voice.channel
    global player
    try:
        player = await channel.connect()
    except:
        pass
    await ctx.channel.send("https://1.bp.blogspot.com/-nbBfH7xXsGs/WQM9zNngCGI/AAAAAAAAdZE/Kc9Hxz8tvKg0YW7FPDz5ndY3arLbUfa9QCLcB/s1600/2815241QTBjAe6L.gif")
    player.play(discord.FFmpegPCMAudio('http://s1.slotex.pl:7022/graj.mp3', executable="./ffmpeg/bin/ffmpeg.exe"))


    # try :
    #     voice_channel = ctx.voice_client
    #     async with ctx.typing():
    #         filename = await YTDLSource.from_url(url, loop=bot.loop)
    #         voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=filename))
    #     await ctx.send('**Rozpoczynam grańsko** {}'.format(filename))
    # except:
    #     await ctx.send("Nie ma mnie na głosowym.")

@bot.command(name='pause', help='Zatrzymaj grańsko')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("Nic nie jest grane tutaj, tej.")
    
@bot.command(name='resume', help='Wznawia grańsko')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("Nic nie jest grane!")

@bot.command(name='stop', help='Zatrzymuje granie')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("Nic nie jest grane w chwili tej, tej.")

token =  "Nzg5ODE4OTQ5MjcyOTkzODIz.X93mNw.IvPRTr-VGEzTGDQu4tm06503h9M"
if __name__ == "__main__":
    bot.run(token)