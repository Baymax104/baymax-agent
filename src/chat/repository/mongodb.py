# -*- coding: UTF-8 -*-
from beanie import init_beanie
from beanie.exceptions import CollectionWasNotInitialized
from motor.motor_asyncio import AsyncIOMotorClient

from chat.models import ChatTurn, Conversation
from chat.repository.base import ChatRepository
from config import Configuration, MongoDBConfig
from monitor import DatabaseError


class MongoDBChatRepository(ChatRepository):

    def __init__(self, config: Configuration):
        super().__init__(config)
        self.mongodb = self.__init_mongodb(config.database.mongodb)
        self.is_external_connection = self.__is_external_connection()

    def __init_mongodb(self, config: MongoDBConfig):
        if not config.host or not config.port:
            raise ConnectionError("Host and port are required.")
        if not config.db:
            raise ConnectionError("Database is required.")
        user_part = f"{config.user}:{config.password}@" if config.user else ""
        uri = f"mongodb://{user_part}{config.host}:{config.port}"
        client = AsyncIOMotorClient(uri)
        return client

    async def initialize(self):
        if not self.is_external_connection:
            await init_beanie(self.mongodb[self.config.mongodb.db], document_models=[Conversation])

    def __is_external_connection(self) -> bool:
        try:
            Conversation.get_settings()
            return True
        except CollectionWasNotInitialized:
            return False

    async def add(self, conversation_id: str, chat_turn: ChatTurn):
        chat_turn = chat_turn.model_dump()
        conversation = await Conversation.get(conversation_id)
        if not conversation:
            raise DatabaseError(f"Conversation {conversation_id} does not exist.")
        await conversation.update({"$push": {Conversation.content: chat_turn}})

    async def close(self):
        if not self.is_external_connection:
            self.mongodb.close()
