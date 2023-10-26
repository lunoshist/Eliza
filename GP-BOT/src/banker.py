import asyncio
import discord
from thief import ThiefGame

class BankerButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, button, interaction):
        self.value = True
        self.stop()

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel(self, button, interaction):
        self.value = False
        self.stop()

class BankerGame:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        self.password_parts = []
        self.password = None
        self.game_over = asyncio.Event()

    async def countdown(self, initial_time):
        time_left = initial_time
        message = await self.embed_message(self.channel, f"Temps restant : {time_left} secondes", view=None)
        while time_left > 0 and not self.game_over.is_set():
            await asyncio.sleep(1)
            time_left -= 1
            await self.edit_embed_message(message, f"Temps restant : {time_left} secondes")
        await self.edit_embed_message(message, "Temps écoulé !")
        self.game_over.set()
        return

    async def ask_for_input(self, prompt):
        def check(m):
            return m.channel == self.channel and not m.author.bot

        await self.embed_message(self.channel, prompt, view=None)
        message = await self.bot.wait_for('message', check=check)
        return message.content

    async def start(self):
        countdown_task = asyncio.create_task(self.countdown(180))
        steps = [
            "Écrivez le nom d'une capital 🌇 :",
            "Écrivez un nombre entre 1 et 500 🔢 :",
            "Écrivez un animal 🐕 :",
            "Écrivez un fruit 🍏 :",
            'Écrivez un caractère spécial (parmi & " # ~ ( [ - _ ^ @ = + } ! ? : § $ £ € < > % * ) 🔣 :'
        ]

        for step in steps:
            response = await self.ask_for_input(step)
            self.password_parts.append(response)
            # await self.embed_message(self.channel, response)
            confirmation = await self.wait_for_confirmation(response)
            print(confirmation)
            if confirmation == False:
                await self.embed_message(self.channel, "Annulé. Veuillez réessayer.", view=None)
                self.password_parts = []  # Réinitialise les parties du mot de passe
                return await self.start()  # Recommence le processus depuis le début

        # À la fin, affiche le mot de passe complet
        self.password = ''.join(self.password_parts)
        self.password = self.password.lower()
        await self.embed_message(self.channel, f"Voici le mot de passe que vous avez sélectionné pour sécuriser le coffre de la NeoBank : {self.password}\nQuelle imagination !", view=None)
        self.game_over.set()  # signale que le jeu est terminé
        await countdown_task

    async def wait_for_confirmation(self, response):
        view=BankerButton()

        message = await self.embed_message(self.channel, f"Confirmez-vous {response} ?", view=view)
        await view.wait()
        await message.delete()

        return view.value

    async def embed_message(self, channel, title, view=None):
        embed = discord.Embed(
            title=title,
            color=discord.Colour.blurple(),
        )
        message = await channel.send(embed=embed, view=view)

        return message

    async def edit_embed_message(self, message, new_title):
        new_embed = discord.Embed(
            title=new_title,
            color=discord.Colour.blurple(),
        )
        await message.edit(embed=new_embed)


async def embed_message_banker(channel):
    print(channel)
    embed = discord.Embed(
        title="Bienvenue dans le channel des agents de sécurité.",
        description="Votre objectif est de créer un mot de passe indécryptable afin de sécuriser la NeoBank. Soyez créatifs !",
        color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
    )
    embed.set_footer(text="*Début du timer de 3 minutes") # footers can have icons too
    await channel.send(file=discord.File('../ressource/Security_officer.png'), embed=embed)

async def embed_message_thief(channel):
    print(channel)
    embed = discord.Embed(
        title="Bienvenue dans le channel des voleurs.",
        description="Votre objectif est de décrypter le mot de passe du coffre fort de la NeoBank afin de rafler tout le butin ! Veuillez patienter pendant le minage de la porte d'entrée...",
        color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
    )
    await channel.send(file=discord.File('../ressource/The_masked_boy.png'), embed=embed)

async def start_minigame(bot, guild, bankers, thieves, banker_role_id, thief_role_id):
    banker_channel = guild.get_channel(1166377084415901696)
    thief_channel = guild.get_channel(1166377370182242304)
    channel = guild.get_channel(1166381947564601404)
    try:
        await embed_message_banker(banker_channel)
        await embed_message_thief(thief_channel)
    except Exception as e:
        print(f"Error: {e}")
    game = BankerGame(bot, banker_channel)
    # lance le jeu et attend qu'il se termine
    game_task = asyncio.create_task(game.start())
    await game.game_over.wait()

    if len(game.password_parts) != 5:
        game.password = "paris20chienpomme!"

    for banker in bankers:
        await banker.move_to(thief_channel)

    thief_game = ThiefGame(bot, thief_channel, game.password, game.password_parts, guild, bankers, thieves, banker_role_id, thief_role_id)
    print(game.password)

    await thief_game.start()
