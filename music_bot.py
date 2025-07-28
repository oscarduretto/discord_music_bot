import discord
from discord.ext import commands
import os
import time
import sounddevice as REC
from pydub import AudioSegment
import logging
from dotenv import dotenv_values

config = dotenv_values(".env")
TOKEN = config["SECRET"]

# Instantiate discord bot
intent = discord.Intents.default()
# intent.members = fa
intent.message_content = True
bot = commands.Bot(intents=intent, command_prefix='$')

# State
voice_client = None
currently_playing = ""
audio_source = None

# Recording constants
SAMPLE_RATE = 48000
MONO = 1
STEREO = 2
# "python -m sounddevice" lists all device names. It will depend on what audio output you want to record and/or what Virtual Cable software you are using.
DEVICE = config["DEVICE"]
CHANNELS = 2
INCREMENT_SIZE = 0.02

# https://discordpy.readthedocs.io/en/stable/logging.html
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

class ComputerAudioSource(discord.AudioSource):
	stream = None
	frames_a = []
	frames_b = []
	is_frames_a = True
	start_sample = True
	
	def read(self):
		# Begin by sending "silence" to Discord as there won't be any audio recorded yet when the bot is first instantiated
		if self.start_sample:
			self.start_sample = False
			return AudioSegment.silent(duration=int(SAMPLE_RATE * INCREMENT_SIZE)).raw_data
		
		# frames_a and frames_b act as a Double Buffer
		elif self.is_frames_a:
			self.frames_b = []
			self.frames_b = self.stream.read(int(SAMPLE_RATE * INCREMENT_SIZE))
			self.is_frames_a = False
			return self.frames_a[0].tobytes()
		else:
			self.frames_a = []
			self.frames_a = self.stream.read(int(SAMPLE_RATE * INCREMENT_SIZE))
			self.is_frames_a = True
			return self.frames_b[0].tobytes()
	
	def start(self):
		self.start_sample = True
		self.stream = REC.InputStream(samplerate=SAMPLE_RATE, device=DEVICE, channels=CHANNELS, dtype="int16")
		self.stream.start()
		self.frames_a = self.stream.read(int(SAMPLE_RATE * INCREMENT_SIZE))

	def stop(self):
		self.start_sample = True
		self.stream.close()
		self.frames_b = []
		self.frames_a = []

@bot.event
async def on_ready():
	print("We have logged in.")

async def start_recording():
	if not voice_client: return
	
	global audio_source
	if audio_source:
		audio_source.stop()
	else:
		audio_source = ComputerAudioSource()
	audio_source.start()
	voice_client.play(audio_source, after=audio_source_finished)

@bot.command()
async def stop(ctx):
	global currently_playing
	if voice_client:
		voice_client.stop()
		currently_playing = ""

@bot.command()
async def restart(ctx):
	if voice_client:
		voice_client.stop()
		time.sleep(0.1)
		await start_recording()

# Shortened commands
@bot.command()
async def c(ctx):
	await connect(ctx)

@bot.command()
async def r(ctx):
	await restart(ctx)

@bot.command()
async def connect(ctx):
	global voice_client
	global currently_playing
	
	if voice_client:
		await ctx.send("I'm already in the Voice Channel.")
		return
	
	await ctx.send("Connected to Voice Channel")
	currently_playing = ""
	if voice_client: 
		await voice_client.disconnect()
		voice_client = None
	
	voice = ctx.message.author.voice
	if voice and voice.channel:
		await connect_to_voice_channel(voice.channel)
		await start_recording() # Auto plays computer audio
	else:
		await ctx.send("I don't know what to connect to. You're not in a Voice Channel.")

@bot.command()
async def disconnect(ctx):
	global voice_client
	if voice_client:
		await voice_client.disconnect()
		voice_client = None

def audio_source_finished(error):
	print("audio source finished")
	global audio_source
	audio_source = None

async def connect_to_voice_channel(voice_channel):
	global voice_client
	voice_client = await voice_channel.connect()
	await voice_client.guild.change_voice_state(channel=voice_channel,self_deaf=True)

bot.run(TOKEN)