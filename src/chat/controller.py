# -*- coding: UTF-8 -*-
from typing import AsyncIterator

from langchain_core.messages import AnyMessage, HumanMessage

from agent import Session, ToolAgent
from chat.memory import ChatMemory
from chat.models import ChatTurn, Conversation, Message
from monitor import get_logger
from users import User


logger = get_logger()


class ChatController:

    def __init__(
        self,
        conversation: Conversation,
        user: User,
        agent: ToolAgent,
        memory: ChatMemory,
    ):
        self.conversation = conversation
        self.user = user
        self.agent = agent
        self.memory = memory


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

