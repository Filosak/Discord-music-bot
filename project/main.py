import discord
import asyncio
import time
import datetime
import threading
import requests
import json
import os
import io
from pytubefix import YouTube
from pytubefix import Playlist
from pytubefix import Search
from discord.ext import commands
from Que import Que
from PIL import Image

que = Que()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

administrator_id = "440783328954679299"
ignored = []

vc = None
looping = False
queue_looping = False
is_random = False
emojis = {
    "numbers": ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"],
    "utility": {
            "left": "⬅️",
            "right": "➡️",
            "x": "❌"
            }
    }

with open("project/MC_recipe_data.json", "r") as jsonFile:
    MC_data = json.load(jsonFile)

with open("project/Playlist_data.json", "r") as jsonFile:
    try: 
        playlist_data = json.load(jsonFile)
    except Exception as e:
        playlist_data = {}

curr_playlist = None
playlist_is_selected = False

@bot.command(
        name = "play", 
        description = "plays music",
        aliases = ["search", "p"]
)
async def play(ctx, *, link):
    global vc
    global playlist_is_selected

    if (str(ctx.author) in ignored):
        return

    if (playlist_is_selected):
        await ctx.send("Cannot use /play when playlist is playing. Use /playlist_add if you want to add song to the playlist.")
        return

    if ("playlist" in link):
        await addPlaylist(ctx, link)
    elif ("https" not in link):
        await search(ctx, link)
    else:
        yt = YouTube(link)
        await ctx.send(que.add(yt))

    channel = ctx.author.voice.channel
    if (vc == None and vc != channel):
        vc = await channel.connect()

    if (not que.is_playing):
        que.is_playing = True
        Play_next(ctx)

def Play_next(ctx):
    if (looping):
        source = Get_source()
        vc.play(source, after = lambda e: Play_next(ctx))

    elif (is_random):
        que.Get_random()
        source = Get_source()
        vc.play(source, after = lambda e: Play_next(ctx))
    else:
        if (not que.Check_next() and queue_looping):
            que.Go_to_start()

        if (que.Next()):
            source = Get_source()
            vc.play(source, after = lambda e: Play_next(ctx))
        else:
            que.is_playing = False

loadedSongs = {}
preload = 5
def downloadSong():
    while (True):
        print("Loading data from website")
        load()

        if (len(que.arr) == 0):
            time.sleep(1.0)
            continue
        
        time.sleep(0.5)
        for i in range(max(que.index, 0), min(que.index + preload, len(que.arr))):

            if (i in loadedSongs):
                continue
            
            print(f"downloading {i}")
            yt = que.arr[i].streams.filter(type="audio").first()
            yt.download("Songs/")
            loadedSongs[i] = f"Songs/{yt.default_filename}".replace("|", "")
            print(loadedSongs[i])

donwloadThread = threading.Thread(target=downloadSong)
donwloadThread.start()

def Get_source():
    while (not que.index in loadedSongs):
        print("waiting for song to download")
        time.sleep(2)

    name = loadedSongs[que.index]
    source = discord.FFmpegPCMAudio(f"{name}", executable="ffmpeg-7.1-essentials_build/bin/ffmpeg.exe")
    return source

def load():
    data = requests.get('http://localhost:8080/getSongsLinks').json()

    if (not data["links"]):
        return

    for i in range(0, data["size"]):
        print(data)
        yt = YouTube(data["links"][f"{i}"]["link"])
        print(que.add(yt))

        toSend = {
            "name": yt.title,
            "lenght": str(datetime.timedelta(seconds=yt.length))
        }

        requests.post("http://localhost:8080/postSongs?", json=toSend)


@bot.command(
        name = "next", 
        description = "plays the next song in que",
        aliases=["skip"],
)
async def next(ctx):
    global vc
    global is_random

    if (str(ctx.author) in ignored):
        return

    if (is_random):
        que.Get_random()
        vc.stop()
    elif (que.Check_next()):
        vc.stop()
    else:
        await ctx.send("No more songs in the que")


@bot.command(
        name = "previous", 
        description = "plays the previous song in que"
)
async def previous(ctx):
    global vc

    if (que.Previous()):
        vc.stop()
    else:
        await ctx.send("No more songs in the que")

@bot.command(
        name = "pause", 
        description = "pauses music"
)
async def pause(ctx):
    global vc

    if (ctx.author in ignored):
        return

    if (vc.is_paused()):
        await ctx.send("Bot is already paused.")
    elif (not que.is_playing):
        await ctx.send("No music is playing")
    else:
        vc.pause()

@bot.command(
        name = "resume", 
        description = "resumes music"
)
async def resume(ctx):
    global vc

    if (not que.is_playing):
        await ctx.send("No music is playing")
    elif (not vc.is_paused()):
        await ctx.send("Music is already playing")
    else:
        vc.resume()

@bot.command(
        name = "play_at", 
        description = "pauses music",
        aliases=["playat", "p_at"]
)
async def play_at(ctx, pos):
    global vc

    try:
        pos = int(pos)
    except Exception as e:
        await ctx.send("/remove takes only numbers.")
        return

    if (not que.Go_to(pos)):
        await ctx.send("there is no song at that possition")
    else:
        vc.stop()

@bot.command(
        name = "shuffle", 
        description = "resumes music"
)
async def shuffle(ctx):
    global vc

    if (que.Lenght() < 1):
        await ctx.send("There are no songs in queue")
    else:
        que.shuffle()
        await ctx.send("Queue has been shuffled.")

@bot.command(
        name = "remove", 
        description = "Removes song at given possition."
)
async def shuffle(ctx, pos):
    global vc

    try:
        pos = int(pos)
    except Exception as e:
        await ctx.send("/remove takes only numbers.")
        return

    if (que.Delete(int(pos-1))):
        await ctx.send("Song has been removed.")
    else:
        await ctx.send("There is no song in given possition")
    

@bot.command(
        name = "show", 
        description = "Shows the whole queue",
        aliases=["que", "queue", "queshow", "queueshow"]
)
async def show(ctx):
    global vc
    
    if (que.Lenght == 0):
        await ctx.send("No songs in the queue")
    else:
        curr_index = que.index

        async def loop(curr_index):
            out = ""
            for i in range(max(curr_index-5, 0), curr_index+15):
                if (i == que.index):
                    out += f"** [{i + 1}] - {que.arr[i].title} **\n"
                else:
                    out += f"`[{i + 1}] - {que.arr[i].title}`\n"
            message = await ctx.send(out)

            if (curr_index - 15 > -1):
                await message.add_reaction(emojis["utility"]["left"])
            if (curr_index + 15 < que.Lenght()):
                await message.add_reaction(emojis["utility"]["right"])
            await message.add_reaction(emojis["utility"]["x"])

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [emojis["utility"]["left"], emojis["utility"]["right"], emojis["utility"]["x"]]
            
            reaction, user = await bot.wait_for('reaction_add', timeout=20.0, check=check)

            if (str(reaction) == emojis["utility"]["left"]):
                return await loop(curr_index - 15)
            elif (str(reaction) == emojis["utility"]["right"]):
                return await loop(curr_index + 15)
            elif (str(reaction) == emojis["utility"]["x"]):
                return None
            
        await loop(curr_index)

        

async def search(ctx, searched_text):
    global vc
    global playlist_is_selected
    
    s = Search(searched_text)

    out = "\n`"
    for i, yt in enumerate(s.results[:5]):
        out += f"[{i+1}] - {yt.title} \n"
    out += "`"

    message = await ctx.send(out)
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")
    await message.add_reaction("4️⃣")
    await message.add_reaction("5️⃣")
    await message.add_reaction("❌")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "❌"]

    reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    
    if (str(reaction) in emojis["numbers"]):
        for i, emoji in enumerate(["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]):
            if (str(reaction) == emoji):
                if (playlist_is_selected):
                    return s.results[i].watch_url
                await ctx.send(que.add(s.results[i]))

    elif (str(reaction) == "❌"):
        await message.delete()
        return None
    

@bot.command(
        name = "loop", 
        description = "Loops music endlessly."
)
async def loop(ctx):
    global vc
    global looping
    global queue_looping

    if (not que.is_playing):
        await ctx.send("No music is playing.")
    elif (vc.is_paused()):
        await ctx.send("Music is paused.")
    else:
        if (queue_looping):
            queue_looping = False

        looping = not looping

        if (looping):
            await ctx.send("loop is on.")
        else:
            await ctx.send("loop is off.")

@bot.command(
        name = "queue_loop", 
        description = "Loops queue endlessly.",
        aliases = ["que_loop", "loop_que", "queloop", "queueloop", "loop_queue"]
)
async def queue_loop(ctx):
    global vc
    global queue_looping
    global looping

    if (not que.is_playing):
        await ctx.send("No music is playing.")
    elif (vc.is_paused()):
        await ctx.send("Music is paused.")
    else:
        if (looping):
            looping = False

        queue_looping = not queue_looping

        if (queue_looping):
            await ctx.send("queue_loop is on.")
        else:
            await ctx.send("queue_loop is off.")


async def addPlaylist(ctx, link):
    global vc
    global playlist_is_selected

    p = Playlist(link)
    if (playlist_is_selected):
        return p 

    for url in p.videos:
        que.add(url, True)
    await ctx.send("Playlist was added to the queue")

@bot.command(
        name = "queue_clear", 
        description = "Clears the queue.",
        aliases=["que_clear", "clear"]
)
async def queue_clear(ctx):
    global vc
    global playlist_is_selected

    if (playlist_is_selected):
        ctx.send("Playlist is selected cannot clear the queue.")
        return
    que.clear()
    vc.stop()

@bot.command(
        name = "random", 
        description = "Clears the queue.",
        aliases=["rand"]
)
async def random(ctx):
    global is_random
    global looping
    global queue_looping

    looping = False
    queue_looping = False
    is_random = not is_random

    if (is_random):
        await ctx.send("Random is On.")
    else:
        await ctx.send("Random is Off.")


@bot.command(
        name = "playlist_create", 
        description = "creates playlist"
)
async def playlist_create(ctx, *, name):
    global playlist_data
    user = ctx.author

    if (user not in playlist_data):
        playlist_data[user.id] = {
            "user_name": user.name,
            "num_of_playlists": 0,
            "playlists": {}
        }

    if (name in playlist_data[user.id]["playlists"]):
        await ctx.send("Playlist already exists")
        return
    
    playlist_data[user.id]["playlists"][name] = []
    playlist_data[user.id]["num_of_playlists"] += 1

    with open("project/Playlist_data.json", "w") as json_file:
        json.dump(playlist_data, json_file, indent=4, sort_keys=True)
        await ctx.send("Playlist created.")


@bot.command(
        name = "playlist_add", 
        description = "Adds song to playlist"
)
async def playlist_add(ctx, *, link):
    global curr_playlist
    global playlist_is_selected
    global playlist_data

    if (not playlist_is_selected):
        await ctx.send("No playlist selected")
        return
    
    if (curr_playlist["user_id"] != str(ctx.author.id)):
        await ctx.send("Cannot edit Playlist of someone else.")
        return
    
    if ("https" in link and "list=" in link):
        result = await addPlaylist(ctx, link)

        for url in result:
            playlist_data[ctx.author.id]["playlists"][curr_playlist["curr"]].append(url)
        await ctx.send("Playlist was added to the playlist.")

    elif ("playlist" not in link and "https" not in link):
        result = await search(ctx, link)
        if (result == None):
            return

        playlist_data[str(ctx.author.id)]["playlists"][curr_playlist["curr"]].append(result)
        await ctx.send("Song was added to the playlist.")

    else:
        playlist_data[str(ctx.author.id)]["playlists"][curr_playlist["curr"]].append(link)
        await ctx.send("Song was added to the playlist.")
    
    with open("project/Playlist_data.json", "w") as json_file:
        json.dump(playlist_data, json_file, indent=4, sort_keys=True)

    
@bot.command(
        name = "playlist_play", 
        description = "Adds song to playlist"
)
async def playlist_play(ctx, *, name=None):
    global vc
    global playlist_data
    global playlist_is_selected

    if (name != None):
        if (name in playlist_data[str(ctx.author.id)]["playlists"]):
            curr_playlist = {
                    "curr": name,
                    "user_id": str(ctx.author.id),
                    "user_name": ctx.author.name
                }
            playlist_is_selected = True
            await ctx.send(f"{curr_playlist['curr']} is now playing.")
        else:
            await ctx.send(f"Playlist {name} doesn't exist.")
            return

    if (len(playlist_data[str(ctx.author.id)]["playlists"][curr_playlist["curr"]]) == 0):
        await ctx.send("Cannot play playlist without any songs.")
        return
    que.clear()

    for url in playlist_data[str(ctx.author.id)]["playlists"][curr_playlist["curr"]]:
        yt = YouTube(url)
        que.add(yt, True)
    
    channel = ctx.author.voice.channel
    if (vc == None and vc != channel):
        vc = await channel.connect()

    if (not que.is_playing):
        que.is_playing = True
        Play_next(ctx)
    else:
        vc.stop()


@bot.command(
        name = "playlist_show", 
        description = "Adds song to playlist"
)
async def playlist_show(ctx):
    pass

@bot.command(
        name = "playlist_deselect", 
        description = "Adds song to playlist"
)
async def playlist_deselect(ctx):
    global vc
    global curr_playlist
    global playlist_is_selected

    curr_playlist = None
    playlist_is_selected = None
    que.clear()
    vc.stop()

@bot.command(
        name = "playlist_select", 
        description = "Lets you select a Playlist"
)
async def playlist_select(ctx, *, name=None):
    global curr_playlist
    global playlist_is_selected
    global playlist_data

    if (playlist_data[str(ctx.author.id)]["num_of_playlists"] < 1):
        await ctx.send("You have no created playlists.")
        return
    
    if (name != None):
        if (name in playlist_data[str(ctx.author.id)]["playlists"]):
            curr_playlist = {
                    "curr": name,
                    "user_id": str(ctx.author.id),
                    "user_name": ctx.author.name
                }
            playlist_is_selected = True
            await ctx.send(f"{curr_playlist['curr']} is now selected.")
        else:
            await ctx.send(f"Playlist {name} doesn't exist.")
        return

    async def selectionLoop(ctx, page):
        message = await createPlaylistMessage(ctx, page, playlist_data)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in aviable_emojis

        aviable_emojis = await addEmojis(ctx, message, page, playlist_data)

        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        reaction = str(reaction)

        answer = await playlistAnswerCheck(ctx, reaction, message, page)

        if (answer == None):
            return None
        elif (answer == "left"):
            page -= 1
            return await selectionLoop(ctx, page)
        elif (answer == "right"):
            page += 1
            return await selectionLoop(ctx, page)
        else:
            return answer

    page = 0
    answer = await selectionLoop(ctx, page)

    if (answer != None):
        curr_playlist = answer
        playlist_is_selected = True


async def createPlaylistMessage(ctx, page, playlist_data):
    out = "\n`"
    for i, playlist_name in enumerate(list(playlist_data[str(ctx.author.id)]["playlists"].keys())[page * 9:9 + page * 9]):
        out += f"[{i+1}] - {playlist_name}\n"
    out += "`"
    message = await ctx.send(out)
    return message

async def addEmojis(ctx, message, page, playlist_data):
    aviable_emojis = []

    for emoji in (emojis["numbers"][:min(playlist_data[str(ctx.author.id)]["num_of_playlists"] - page * 9, 9)]):
        aviable_emojis.append(emoji)
        await message.add_reaction(emoji)

    if (page > 0):
        aviable_emojis.append(emojis["utility"]["left"])
        await message.add_reaction(emojis["utility"]["left"])
    if (((page+1) * 9) < playlist_data[str(ctx.author.id)]["num_of_playlists"]):
        aviable_emojis.append(emojis["utility"]["right"])
        await message.add_reaction(emojis["utility"]["right"])
    aviable_emojis.append(emojis["utility"]["x"])
    await message.add_reaction(emojis["utility"]["x"])

    return aviable_emojis

async def playlistAnswerCheck(ctx, reaction, message, page):
    if reaction not in emojis["numbers"]:
        if reaction == emojis["utility"]["left"]:
            return "left"
        elif reaction == emojis["utility"]["right"]:
            return "right"
        elif reaction == emojis["utility"]["x"]:
            await message.delete()
            await ctx.send("Action canceled")
            return None
    else:
        for i, emoji in enumerate(emojis["numbers"]):
            if reaction == emoji:

                curr_playlist = {
                    "curr": list(playlist_data[str(ctx.author.id)]["playlists"].keys())[i + page * 9],
                    "user_id": str(ctx.author.id),
                    "user_name": ctx.author.name
                }

                await ctx.send(f"{curr_playlist['curr']} is now selected.")
                return curr_playlist



@bot.command(
        name = "recipe", 
        description = "shows recipe for any item in MC"
)
async def recipe(ctx, *, name=None):
    if (not os.path.isdir("MC")):
        return

    if (not name):
        await ctx.send("You have to send the name of the item")

    name = name.replace("_", "").replace(" ", "").lower()

    if (name not in MC_data):
        await ctx.send("This item does not exist.")
    
    image = Image.new("RGBA", (60, 60))
    pad_left = 0
    pad_up = 0

    for row in MC_data[name]["pattern"]:
        for slot in row:
            if (slot != " "):
                im = Image.open(slot)
                image.paste(im, (pad_left, pad_up))
            pad_left += 20
        pad_left = 0
        pad_up += 20
    
    with io.BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        await ctx.send("recipe", file=discord.File(fp=image_binary, filename='image.png'))



@bot.command(
        name = "ignore", 
        description = "hahaha"
)
async def ignore(ctx, *, name):
    if (str(ctx.author.id) != administrator_id):
        await ctx.send("kys :)")
        return
    
    ignored.append(name)






