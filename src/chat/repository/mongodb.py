# -*- coding: UTF-8 -*-
from chat.models import ChatTurn, ConversationDB
from chat.repository.base import ChatRepository
from monitor import DatabaseError


class MongoDBChatRepository(ChatRepository):

    async def add(self, conversation_id: str, chat_turn: ChatTurn) -> list[ChatTurn]:
        chat_turn = chat_turn.model_dump()
        conversation = await ConversationDB.get(conversation_id)
        if not conversation:
            raise DatabaseError(f"Conversation {conversation_id} does not exist.")
        conversation = await conversation.update({"$push": {ConversationDB.content: chat_turn}})
        return conversation.content
