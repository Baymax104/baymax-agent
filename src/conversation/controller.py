# -*- coding: UTF-8 -*-
from __future__ import annotations

from typing import Literal

from chat import ChatController, Conversation
from config import Configuration
from conversation.repository import ConversationRepository
from monitor import ConversationNotFoundError, get_logger
from users import User
from utils import AsyncResource


logger = get_logger()


class ConversationController(AsyncResource):

    def __init__(self, user: User, config: Configuration):
        self.config = config
        self.current_user = user
        self.repo = ConversationRepository(config)

    async def initialize(self):
        await self.repo.initialize()
        logger.debug("ConversationController initialized")

    async def create(
        self,
        title: str = "",
        conversation_type: Literal["archive", "temporary"] = "archive"
    ) -> str:
        conversation = Conversation(user_id=self.current_user.id, title=title, type=conversation_type)
        await self.repo.add(conversation)
        logger.debug(f"Created conversation: {conversation.id}")
        return conversation.id

    @logger.catch_exception(throw=True)
    async def delete(self, conversation_id: str):
        await self.repo.delete(conversation_id)
        logger.debug(f"Deleted conversation: {conversation_id}")

    async def get(self, conversation_id: str) -> Conversation | None:
        return await self.repo.get(conversation_id)

    @logger.catch_exception(throw=True)
    async def start_conversation(self, conversation_id: str) -> ChatController:
        conversation = await self.repo.get(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(f"Conversation with id {conversation_id} not found")
        chat_controller = ChatController(
            conversation=conversation,
            user=self.current_user,
            config=self.config
        )
        logger.debug(f"Started conversation: {conversation.id}")
        return chat_controller

    async def close(self):
        await self.repo.close()
        logger.debug("ConversationController closed")
