import discord
import os
import asyncio
import openai
from discord.ext import commands
from dotenv import load_dotenv
import time

class ThiefButton(discord.ui.View):
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

class ThiefGame:
    def __init__(self, bot, channel, password, password_parts, guild, bankers, thieves, banker_role_id, thief_role_id):
        self.bot = bot
        self.channel = channel
        self.target_password = password
        self.password_parts = password_parts
        self.guild = guild
        self.bankers = bankers
        self.thieves = thieves
        self.banker_role_id = banker_role_id
        self.thief_role_id = thief_role_id
        self.List_attente_channel = guild.get_channel(1166381947564601404)  # Remplacez par l'ID du vocal Banker
        self.game_over = asyncio.Event()  # Événement pour signaler la fin du jeu
        self.winner = None
        self.score = 0
        load_dotenv()

    async def countdown(self, initial_time):
        time_left = initial_time
        message = await self.embed_message(self.channel, f"Temps restant : {time_left} secondes", view=None)
        while time_left > 0 and not self.game_over.is_set():
            await asyncio.sleep(1)
            time_left -= 1
            await self.edit_embed_message(message, f"Temps restant : {time_left} secondes")
        if time_left > 0 and not self.game_over.is_set():
            await self.edit_embed_message(message, "Temps écoulé !")
            self.winner = 'bankers'  # Les agents de sécurité gagnent si le temps est écoulé
            self.game_over.set()
        self.game_over.set()  # Signal que le jeu est terminé, en cas de compte à rebours atteint zéro ou les voleurs ont gagné
        return

    async def ask_for_input(self, prompt, hint):
        def check(m):
            return m.channel == self.channel and not m.author.bot

        await self.embed_message(self.channel, f"{prompt}\n{hint}", view=None)
        message = await self.bot.wait_for('message', check=check)
        return message.content

    async def start(self):
        api_key = os.getenv('API_KEY')
        self.start_time = time.time()
        await self.embed_message(self.channel, "Le mot de passe choisi se compose d'une capitale, d'un nombre entre 1 et 500, d'un animal, d'un fruit, d'un caractère spécial.\nVous disposez de 5 minutes pour le décrypter avant l'arrivée de la police.\nDébut du timer dans 3, 2, 1...", color=discord.Colour.blurple())
        countdown_task = asyncio.create_task(self.countdown(300))
        openai.api_key = api_key
        steps = [
            "Devinez le nom d'une capitale 🌇 :",
            "Devinez un nombre entre 1 et 500 🔢 :",
            "Devinez un animal 🐕 :",
            "Devinez un fruit 🍏 :",
            'Devinez un caractère spécial (parmi & " # ~ ( [ - _ ^ @ = + } ! ? : § $ £ € < > % * ) 🔣 :'
        ]
        for index, step in enumerate(steps):
            while True:  # Boucle jusqu'à ce que la réponse correcte soit donnée
                # Génére un indice en utilisant l'API OpenAI
                messages = [
                        {
                        "role": "system",
                        "content": "Tu dois aider les joueurs à deviner le mot de passe pour un mini jeux, tu vas avoir la question que les joueurs doivent deviné et le mot que que les joueurs doivent deviné, avec cela tu dois créer un indice pas trop simple pour aider les joueurs à trouver le mot qui constitue le mot de passe. Répond moi uniquement l'indice !!!. Si le joueur ne trouve pas je tu auras le précédent indice, la réponse, renvois moi un nouvel indice en fonction."
                        },
                        {
                        "role": "user",
                        "content": step + " " + self.password_parts[index]
                        }
                    ]
                gpt_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0,
                    max_tokens=256,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                hint = gpt_response.choices[0].message.content
                print(hint)
                # Demande aux utilisateurs de deviner
                guess = await self.ask_for_input(step, hint)
                confirmation = await self.wait_for_confirmation(guess)
                if confirmation and guess.lower() == self.password_parts[index].lower():
                    # Si la réponse est correcte, affiche un message de confirmation et passez à l'étape suivante
                    await self.embed_message(self.channel, "C'est correct !", color=discord.Colour.green())
                    break  # Sort de la boucle while et passe à l'étape suivante
                elif confirmation:
                    # Si la réponse est incorrecte, affiche un message d'erreur
                    await self.embed_message(self.channel, "Mot incorrect. Réessayez.", color=discord.Colour.red())
                    messages.append({"role": "system", "content": hint})
                    messages.append({"role": "user","content": guess})
                    print(messages)
                else:
                    # Si la confirmation a été annulée, affiche un message d'annulation
                    await self.embed_message(self.channel, "Annulé. Réessayez.", view=None)

        # À la fin, si toutes les parties du mot de passe sont correctes
        await self.embed_message(self.channel, "Code déverouillé, ouverture du coffre", view=None, color=discord.Colour.green())
        self.winner = 'thieves'  # Les voleurs gagnent si le mot de passe est correct
        self.game_over.set()  # Signale que le jeu est terminé
        await countdown_task
        print(self.winner)
        final_time = time.time()  # Obtiens le temps actuel
        time_taken = final_time - self.start_time  # Calcule le temps pris pour finir le jeu
        final_score_seconds = time_taken + self.score
        minutes = int(final_score_seconds // 60)
        seconds = int(final_score_seconds % 60)
        if self.winner == 'bankers':
            await self.embed_message(self.channel, "Les agents de sécurité ont gagné !", view=None, color=discord.Colour.red())
        else:
            final_score_str = f"{minutes:02d}:{seconds:02d}"
            await self.embed_message(self.channel, f"Les voleurs ont gagné la partie avec un score de {final_score_str} ", view=None, color=discord.Colour.green())
        
        await asyncio.sleep(20)
        for thief in self.thieves:
            thief_role = discord.utils.get(self.guild.roles, id=self.thief_role_id)
            await thief.remove_roles(thief_role)
            await thief.move_to(self.List_attente_channel)

        for banker in self.bankers:
            banker_role = discord.utils.get(self.guild.roles, id=self.banker_role_id)
            await banker.remove_roles(banker_role)
            await banker.remove_roles(thief_role)
            await banker.move_to(self.List_attente_channel)

    async def wait_for_confirmation(self, guess):
        view = ThiefButton()

        message = await self.embed_message(self.channel, f"Confirmez-vous {guess} ?", view=view)
        await view.wait()
        await message.delete()

        return view.value

    async def embed_message(self, channel, title, view=None, color=discord.Colour.blurple()):
        embed = discord.Embed(
            title=title,
            color=color,
        )
        message = await channel.send(embed=embed, view=view)

        return message

    async def edit_embed_message(self, message, new_title):
        new_embed = discord.Embed(
            title=new_title,
            color=discord.Colour.blurple(),
        )
        await message.edit(embed=new_embed)
