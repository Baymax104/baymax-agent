# -*- coding: UTF-8 -*-
from dependency_injector import containers, providers

from agent import ToolAgent
from chat import ChatController, ChatMemory, Conversation
from config import ConfigManager
from conversation import ConversationController
from conversation.repository import ConversationRepository
from injection.providers import *
from users import User, UserService
from users.repository import UserRepository


class AgentContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=Configuration)
    llm = providers.Resource(provide_llm, config=config)
    mcp_client = providers.Resource(provide_mcp_client, config=config)
    tool_agent = providers.Singleton(ToolAgent, mcp_client=mcp_client, llm=llm, config=config)


class DatabaseContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=Configuration)
    mongodb = providers.Resource(provide_mongodb, config=config)
    redis = providers.Resource(provide_redis, config=config)


class ChatContainer(containers.DeclarativeContainer):
    conversation = providers.Dependency(instance_of=Conversation)
    redis = providers.Dependency(instance_of=Redis)
    conversation_repository = providers.Singleton(ConversationRepository, redis=redis)
    chat_memory = providers.Factory(ChatMemory, conversation=conversation, redis=redis)


class UserContainer(containers.DeclarativeContainer):
    repository = providers.Singleton(UserRepository)
    service = providers.Singleton(UserService, repository=repository)


class CurrentContainer(containers.DeclarativeContainer):
    user = providers.Singleton(
        User,
        name="nobody",
        instructions=[]
    )
    conversation = providers.Singleton(
        Conversation,
        user_id="",
        title="",
        type="temporary"
    )


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["cli"])

    configuration = providers.Object(ConfigManager.get_config())

    current: CurrentContainer = providers.Container(CurrentContainer)
    user: UserContainer = providers.Container(UserContainer)
    agent: AgentContainer = providers.Container(AgentContainer, config=configuration)
    database: DatabaseContainer = providers.Container(DatabaseContainer, config=configuration)
    chat: ChatContainer = providers.Container(
        ChatContainer,
        conversation=current.conversation,
        redis=database.redis
    )

    chat_controller = providers.Factory(
        ChatController,
        conversation=current.conversation,
        user=current.user,
        agent=agent.tool_agent,
        memory=chat.chat_memory,
    )
    conversation_controller = providers.Factory(
        ConversationController,
        user=current.user,
        repository=chat.conversation_repository
    )
