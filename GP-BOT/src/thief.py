import asyncio
import discord

class ThiefGame:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        self.password_parts = []
        self.password = None
