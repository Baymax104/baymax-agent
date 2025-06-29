# -*- coding: UTF-8 -*-
from __future__ import annotations

from typing import Literal

from agent import ToolAgent
from config import Configuration
from conversation import Conversation
from conversation.repository import ConversationRepository
from monitor import ConversationNotFoundError
from users import User


class ConversationController:

    def __init__(self, user: User, config: Configuration):
        self.config = config
        self.current_user = user
        self.repo = ConversationRepository(config)

    async def create_conversation(
        self,
        title: str = "",
        conversation_type: Literal["archive", "temporary"] = "archive"
    ) -> str:
        conversation = Conversation(user_id=self.current_user.id, title=title, type=conversation_type)
        await self.repo.add_conversation(conversation)
        return conversation.id

    async def delete_conversation(self, conversation_id: str):
        await self.repo.delete_conversation(conversation_id)

    async def start_conversation(self, conversation_id: str) -> ChatController:
        conversation = await self.repo.get_conversation(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(f"Conversation with id {conversation_id} not found")
        chat_controller = ChatController(
            conversation=conversation,
            user=self.current_user,
            config=self.config
        )
        await chat_controller.start()
        return chat_controller


class ChatController:

    def __init__(self, conversation: Conversation, user: User, config: Configuration):
        self.conversation = conversation
        self.user = user
        self.config = config
        self.agent = ToolAgent(config)

    async def start(self):
        await self.agent.initialize()
