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
    await channel.purge(limit=20)
    await channel.send(file=discord.File('../ressource/arnaud.png'), view=StartButton())

    # general = bot.get_channel(1087722096358064168)
    # await general.purge(limit=500)
    # await general.send(file=discord.File('../ressource/arnaud.png'))
    # embed = discord.Embed(
    #         title="Qu’est ce que NeoBank Hold-Up ?",
    #         color=discord.Colour.blurple(),
    #     )
    # embed.add_field(name="", value="```NeoBank Hold-Up est un jeu communautaire en ligne dans lequel vous incarnez soit un agent de sécurité, soit un voleur. Votre objectif est de créer un mot de passe indécodable ou, à l’inverse, de décrypter ce mot de passe le plus rapidement possible. Pour cela, Arnaud vous guidera dans la réalisation de ce mot de passe étape par étape et vous donnera des indices si vous êtes dans le rôle d’un voleur. À vos marques, prêts ? Créez et décryptez !```", inline=False)
    # embed.add_field(name="***Comment jouer ?***", value="", inline=True)
    # embed.add_field(name="> Étape 1 : Attribution des rôles", value="Arnaud va aléatoirement vous attribuer au rôle d’agents de sécurité ou au rôle de voleur. Votre objectif sera différent selon votre rôle", inline=False)
    # embed.add_field(name="> Étape 2 : Les agents de sécurité", value="Si vous avez la chance de faire partie des agents de sécurité, vous allez devoir imaginer un mot de passe comprenant une capitale, un nombre entre 1 et 500, un animal, un fruit et un caractère spécial parmi une sélection. Le tout en 3 minutes. Soyez créatifs !\nVous rejoindrez ensuite le channel vocal des voleurs où vous ne pourrez cependant pas communiquer.", inline=False)
    # embed.add_field(name="> Étape 3 : Les voleurs", value="Si vous devez endosser le rôle de voleur, vous allez devoir faire appel à votre réflexion et votre rapidité, mais aussi à votre esprit d’équipe. Vous disposez de 5 minutes maximum pour décrypter le mot de passe grâce à des indices que Arnaud pourra vous fournir. Attention, à chaque indice supplémentaire demandé, un malus de +10 secondes sera ajouté à votre temps final ! Utilisez l’entraide et soyez stratégiques !", inline=False)
    # embed.add_field(name="> Étape 4 : Classement et Récompenses", value="Si l’équipe des voleurs réussit à décrypter le mot de passe dans le temps imparti, leur temps est affiché dans le classement du chat général. Le top 3 des équipes est ensuite récompensé selon une actualisation tous les 3 jours : 100 community points pour les 1er, 80 pour les 2nd et 60 pour les 3e.\nPour les équipes d’agents de sécurité, toutes les personnes qui ont participé à une manche dans ce rôle et dans laquelle le mot de passe n’a pas été trouvé seront récompensé de 100 community points à la fin du roulement des 3 jours.", inline=False)
    # embed.set_footer(text="Nous espérons que vous vous divertirez avec NeoBank Hold-Up. Pour toute question, utilisez la commande /help ou contactez notre équipe de modération.") # footers can have icons too
    
    # await general.send(embed=embed)

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
            try :
                await interaction.response.edit_message(view=self)  # Modifier la réponse ici
            except Exception as e:
                print(f"Error: {e}")
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

    await thief_channel.purge(limit=100)
    await banker_channel.purge(limit=100) 

    random.shuffle(queue)  # Mélanger la queue pour une répartition aléatoire
    bankers = queue[1:]
    thieves = queue[:1]

    print(bankers)
    print(thieves)

    for thief in thieves:
        thief_role = discord.utils.get(guild.roles, id=thief_role_id)
        try :
            await thief.add_roles(thief_role)
            await thief.move_to(thief_channel)
        except Exception as e:
                print(f"Error: {e}")

    for banker in bankers:
        banker_role = discord.utils.get(guild.roles, id=banker_role_id)
        await banker.add_roles(banker_role)
        await banker.move_to(banker_channel)

    await start_minigame(bot, guild, bankers, thieves, banker_role_id, thief_role_id)

@bot.slash_command()
async def button(ctx):
    await ctx.respond(file=discord.File('../ressource/arnaud.png'), view=StartButton())

token = os.getenv('TOKEN')
bot.run(token)
