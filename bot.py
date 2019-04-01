import discord
import urllib.request
import pdfkit
from wand.image import Image
from wand.color import Color
import bs4 as bs

# Works only with python version lower than 3.7
# Reason:
# https://github.com/Rapptz/discord.py/issues/1249

MENSA_URL = "https://www.stw-thueringen.de/deutsch/mensen/einrichtungen/weimar/mensa-am-park.html"

def get_discord_token():
    filename = "token"
    with open(filename, "r") as f:
        token = f.read().strip()
    return token

def load_mensa():
    """
    get the content of the mensa page and store it on disc as pdf
    :return: true when done
    """
    content = urllib.request.urlopen(MENSA_URL).read()
    content = content.decode("ISO-8859-1")
    extract = extract_div(content, 4)
    options = {
        "page-size": "Letter"
    }
    pdfkit.from_string(extract, "mensa.pdf", options=options)
    return True

def extract_div(source, number):
    """
    get the div for the given day
    :param source: the html of the mensa page
    :param number: number of the day 2=Mon, 3=Tue, 4=Wed, 5=Thu, 6=Fri
    :return: the div of that day
    """
    search_for = "day_" + str(number)
    soup = bs.BeautifulSoup(source, 'html')
    div = soup.find("div", {"id": search_for})
    return str(div)


def create_png():
    """
    create a pdf and convert it to png
    """
    if load_mensa():
        with Image(filename="mensa.pdf", resolution=300) as img:
            img.background_color = Color("white")
            img.alpha_channel = False
            img.crop(0, 0, img.size[0], 1500)
            img.save(filename='mensa.png')
        return True

def get_channel(channels, channel_name):
    for channel in client.get_all_channels():
        print(channel)
        if channel.name == channel_name:
            return channel
    return None

# create a new discord client
client = discord.Client()
channel = None

@client.event
async def on_message(msg):
    """
    on message receive
    :param msg: the incoming message
    """
    if msg.author == client.user:
        return
    if msg.channel.name != "test":
        return
    if msg.content.startswith("!ping"):
        # reply = "Hello {0.author.mention}".format(msg)
        if create_png():
            with open("mensa.png", 'rb') as picture:
                await client.send_file(msg.channel, picture)

@client.event
async def on_ready():
    """
    on bot logged in
    """
    await client.wait_until_ready()
    await client.wait_until_login()
    print("logged in as")
    print(client.user.name)
    print(client.user.id)
    print("-------")

    c = get_channel(client.get_all_channels(), 'test')

    await client.send_message(c, "Hello there! I am the Mensa bot and you can trigger me with the command \"!mensa\"")
    await client.send_message(c, "Unfortunately, I can currently only answer to commands and cannot send on my own")

token = get_discord_token()
# run the bot
client.run(token)

# https://stackoverflow.com/questions/49835742/how-to-send-a-message-with-discord-py-without-a-command