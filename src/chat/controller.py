# -*- coding: UTF-8 -*-
from typing import AsyncIterator

from langchain_core.messages import AnyMessage, HumanMessage

from agent import Session, ToolAgent
from chat.memory import ChatMemory
from chat.models import ChatTurn, Conversation, Message
from config import Configuration
from monitor import get_logger
from users import User
from utils import AsyncResource


logger = get_logger()


class ChatController(AsyncResource):

    def __init__(self, conversation: Conversation, user: User, config: Configuration):
        self.conversation = conversation
        self.user = user
        self.config = config
        self.agent = ToolAgent(config)
        self.memory = ChatMemory(conversation, config)

    async def initialize(self):
        await self.agent.initialize()
        await self.memory.initialize()
        logger.debug("ChatController initialized")

    async def chat(self, user_input: str) -> AsyncIterator[AnyMessage]:
        context = await self.memory.get_message_context()
        logger.debug(f"User input: {user_input}")
        context.append(HumanMessage(user_input))
        session = Session(
            context=context,
            user_instructions=self.user.instructions
        )
        state = await self.agent.chat(session)
        ai_message_chunks = [chunk.content async for chunk in state.stream]
        ai_message = "".join(ai_message_chunks)
        logger.debug(f"AI response: {ai_message}")
        chat_turn = ChatTurn(
            human_message=Message(role="human", content=user_input),
            ai_message=Message(role="ai", content=ai_message)
        )
        await self.memory.add(chat_turn)
        for chunk in ai_message_chunks:
            yield chunk

    async def close(self):
        await self.agent.close()
        await self.memory.close()
        logger.debug("ChatController closed")
