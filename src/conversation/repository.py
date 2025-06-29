# -*- coding: UTF-8 -*-
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config import Configuration, MongoDBConfig
from conversation import Conversation
from monitor import DatabaseError


class ConversationRepository:

    def __init__(self, config: Configuration):
        self.config = config.database.mongodb
        self.mongodb = self.__init_mongodb(config.database.mongodb)

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
        await init_beanie(database=self.mongodb[self.config.db], document_models=[Conversation])

    async def add_conversation(self, conversation: Conversation):
        await Conversation.insert_one(conversation)

    async def get_conversation(self, conversation_id: str) -> Conversation | None:
        return await Conversation.get(conversation_id)

    async def delete_conversation(self, conversation_id: str):
        conversation = await Conversation.get(conversation_id)
        if conversation is None:
            raise DatabaseError(f"Conversation {conversation_id} does not exist.")
        await conversation.delete()  # noqa

    def close(self):
        self.mongodb.close()
