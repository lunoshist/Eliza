import discord
import random
import os
from dotenv import load_dotenv
from banker import start_minigame

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.message_content = True
bot = discord.Bot(intents=intents)
load_dotenv()
queue = []

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    channel = bot.get_channel(1166381947564601404)  # Remplacez par l'ID de votre canal texte
    await channel.send('Click below to start the game!', view=StartButton())

class StartButton(discord.ui.View):
    @discord.ui.button(label="Lancez le jeu !", style=discord.ButtonStyle.primary, emoji="💰", custom_id='start_game')
    async def button_callback(self, button, interaction):
        user = interaction.user
        if user not in queue:
            queue.append(user)
        player_count = len(queue)

        if player_count < 2:
            button.label = f'En attente d\'autres joueurs ({player_count}/20)'
            button.style = discord.ButtonStyle.secondary
            await interaction.response.edit_message(view=self)  # Modifier la réponse ici
        else:
            button.label = 'Lancement du jeu !'
            button.style = discord.ButtonStyle.success
            button.disabled = True
            await interaction.response.edit_message(view=self)  # Modifier la réponse ici
            await start_game()

async def start_game():
    guild = bot.get_guild(1087717807413792811)  # Remplacez par l'ID de votre guilde
    thief_channel = guild.get_channel(1166377370182242304)  # Remplacez par l'ID du vocal Thief
    banker_channel = guild.get_channel(1166377084415901696)  # Remplacez par l'ID du vocal Banker
    banker_role_id = 1166378228894674964  # Remplacez par l'ID du rôle Banker
    thief_role_id = 1166377426859851817  # Remplacez par l'ID du rôle Thief

    random.shuffle(queue)  # Mélanger la queue pour une répartition aléatoire
    bankers = queue[1:]
    thieves = queue[:1]
    print(bankers)
    print(thieves)

    for thief in thieves:
        thief_role = discord.utils.get(guild.roles, id=thief_role_id)
        await thief.add_roles(thief_role)
        await thief.move_to(thief_channel)

    for banker in bankers:
        banker_role = discord.utils.get(guild.roles, id=banker_role_id)
        await banker.add_roles(banker_role)
        await banker.move_to(banker_channel)

    await start_minigame(bot, guild, bankers)

@bot.slash_command()
async def button(ctx):
    await ctx.respond("This is a button!", view=StartButton())

token = os.getenv('TOKEN')
bot.run(token)
