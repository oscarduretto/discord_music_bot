
Discord Music Bot records audio from your local computer and outputs the audio to a Discord voice channel you are a part of. This allows you to play music or any audio you want from your desktop computer to a Discord call.
# **Usage**
There are several other components required to make use of this script. A Discord bot, a virtual cable and a method of playing audio that allows you to easily switch audio outputs. Also, this script is not packaged into an executable, so you are required to have installed Python (3.10, later versions likely also work) and the relevant Python packages.
#### **Discord Bot**
The script on its own is not the Discord Bot but the behaviour of the bot. You will need to set up a Discord Bot on the [Discord Developer Portal](https://discord.com/developers) and connect it to your Discord server. It will need permissions to read/send text channel messages and connect/speak to voice channels.

Once your bot is created, you need to set its secret token in the .env file. Create a text file called .env in the directory of the python script (if it does not exist already) and add your token to the environment variables in the following format:
```
SECRET=<your token here>
```
#### **Virtual Cable**
If a bot was to record the standard audio output of your computer, it would likely record its own audio from the voice channel and create a feedback loop. It would also record and output audio you may not want it to record, such as your friends talking in discord or a video game you're playing. Virtual cables are way to control what audio is being recorded on your computer. They are effectively "pretend" audio devices you can stream audio to.

There are several types of virtual cable software online (with free versions). I use [vb-audio](https://vb-audio.com/Cable/). Once you have installed your preferred virtual cable software you need to find the identifier of the virtual output device using:
```
python -m sounddevice
```
This command lists all audio input and output devices that the python module `sounddevice` recognises. It might take a little trial and error to figure out which one is the output you want. The name of the output virtual cable for vb-audio was called "CABLE Output (VB-Audio Virtual , MME". Once you find the identifier, update your .env file with a new environment variable:

```
DEVICE=<name of the output virtual cable>
```
#### **Playing Audio**
The application you're using to play audio on your computer needs to be able to change its audio output to the virtual cable. Most applications allow for this. For example, in VLC Media Player you can change output through the dropdown: `Audio > Audio Device`. On browsers there are several extensions that allow switching audio outputs easily. For example, the Chrome extension AudioPick. If the application can't change the output on its own, you can change the audio output for an application on the operating system level. For example, in Windows settings: `System > Sound > Volume Mixer`.

#### **Starting the Bot**
Once all the components have been set up, you can start the bot by running this command in the directory of the script:
```
python music_bot.py
```
Join a Discord voice channel within the server you have set up permissions for the Discord bot and run
`$connect` or `$c` in any text chat. The bot will connect to your voice channel, automatically start recording audio from your computer and output that audio to the voice channel. At any point you can disconnect the bot with `$disconnect` or `$d`. 
# **Limitations**
**Only one voice channel:** The bot can not handle being connecting to multiple voice channels at once. There will be strange behaviour if that is attempted. It is unlikely you want this in its common use cases.