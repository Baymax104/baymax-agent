# -*- coding: UTF-8 -*-
from rich.prompt import Prompt

from chat import ChatController
from cli.container import container
from cli.menu import Menu
from cli.prompt import error, print_list, success
from conversation import ConversationController
from users import UserService


menu = Menu("对话管理")


@menu.action("创建对话")
async def create_conversation():
    controller: ConversationController = await container.conversation_controller()
    title = Prompt.ask("请输入标题")
    conversation_type = Prompt.ask("请输入对话类型")
    await controller.create(title, conversation_type)
    success(f"对话创建成功")


@menu.action("对话列表")
async def list_conversation():
    controller: ConversationController = await container.conversation_controller()
    conversations = await controller.get_all()
    conversations = [f"[cyan]{conv.title}[/]({conv.id})" for conv in conversations]
    print_list(conversations, title="历史对话", show_header=False)


@menu.action("进入对话")
async def start_conversation():
    controller: ConversationController = await container.conversation_controller()
    user_service: UserService = container.user.service()
    username = Prompt.ask("登录用户名")
    user = await user_service.get_by_name(username)
    if not user:
        error(f"用户\"{username}\"不存在")
        return
    # login
    container.current.user.override(user)

    # list conversation
    conversations = await controller.get_all()
    conversation_infos = [f"[cyan]{conv.title}[/]({conv.id})" for conv in conversations]
    print_list(conversation_infos, title="历史对话", show_header=False)
    conversation_id = Prompt.ask("请输入对话ID")
    conversation = next((conv for conv in conversations if conv.id == conversation_id), None)
    if not conversation:
        error(f"对话不存在")
        return
    # enter conversation
    container.current.conversation.override(conversation)

    chat_controller: ChatController = await container.chat_controller()
    while True:
        user_input = input("> ")
        if not user_input:
            continue
        if user_input == "/quit":
            break
        response = chat_controller.chat(user_input)
        async for message in response:
            print(message, end="")
        print()
    success("对话结束")


@menu.action("删除对话")
async def delete_conversation():
    controller: ConversationController = await container.conversation_controller()
    conversations = await controller.get_all()
    conversation_infos = [f"[cyan]{conv.title}[/]({conv.id})" for conv in conversations]
    print_list(conversation_infos, title="历史对话", show_header=False)
    conversation_id = Prompt.ask("请输入对话ID")
    conversation = next((conv for conv in conversations if conv.id == conversation_id), None)
    if not conversation:
        error(f"对话不存在")
        return
    await controller.delete(conversation.id)
    success("删除成功")
