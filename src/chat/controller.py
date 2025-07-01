# -*- coding: UTF-8 -*-
from agent import ToolAgent
from chat.models import Conversation
from config import Configuration
from users import User


class ChatController:

    def __init__(self, conversation: Conversation, user: User, config: Configuration):
        self.conversation = conversation
        self.user = user
        self.config = config
        self.agent = ToolAgent(config)

    async def start(self):
        await self.agent.initialize()
