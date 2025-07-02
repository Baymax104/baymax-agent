# -*- coding: UTF-8 -*-
from beanie import init_beanie

from chat.models import ChatTurn, ConversationDB
from chat.repository.base import ChatRepository
from config import Configuration
from monitor import DatabaseError
from utils import init_mongodb, is_connected


class MongoDBChatRepository(ChatRepository):

    def __init__(self, config: Configuration):
        super().__init__(config)
        self.mongodb = init_mongodb(config.database.mongodb)
        self.is_external_connection = is_connected(ConversationDB)

    async def initialize(self):
        if not self.is_external_connection:
            await init_beanie(self.mongodb[self.config.mongodb.db], document_models=[ConversationDB])

    async def add(self, conversation_id: str, chat_turn: ChatTurn) -> list[ChatTurn]:
        chat_turn = chat_turn.model_dump()
        conversation = await ConversationDB.get(conversation_id)
        if not conversation:
            raise DatabaseError(f"Conversation {conversation_id} does not exist.")
        conversation = await conversation.update({"$push": {ConversationDB.content: chat_turn}})
        return conversation.content

    async def close(self):
        if not self.is_external_connection:
            self.mongodb.close()
