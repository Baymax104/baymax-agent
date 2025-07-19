# -*- coding: UTF-8 -*-
from __future__ import annotations

from chat import Conversation
from conversation.repository import ConversationRepository
from monitor import get_logger
from users import User


logger = get_logger()


class ConversationController:

    def __init__(self, user: User, repository: ConversationRepository):
        self.current_user = user
        self.repo = repository

    async def create(self, title: str = "", conversation_type: str = "archive") -> str:
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

    async def get_all(self) -> list[Conversation]:
        return await self.repo.get_all()
