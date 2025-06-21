# -*- coding: UTF-8 -*-
from langchain_core.messages import AnyMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate


DECISION_SYSTEM_PROMPT = r"""
[任务描述]
你是一个通过MCP协议调用工具的AI助手，你需要从多个MCP服务器中选择一个服务器来完成用户的任务，不要回答用户问题。
根据MCP服务器的描述来选择相应的服务器，以 server://<server> 的格式返回结果。
若没有能够完成任务的服务器，则返回 server://null 。

[可访问的MCP服务器]
{% for server in servers %}
{{ loop.index }}. {{ server.name }}: {{ server.description }}
{% endfor %}
"""


def decision_prompt(servers: list, history: list[AnyMessage]) -> list[AnyMessage]:
    template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(DECISION_SYSTEM_PROMPT, "jinja2"),
        MessagesPlaceholder("history")
    ])
    return template.format_messages(servers=servers, history=history)


FUNCTION_CALL_SYSTEM_PROMPT = r"""
[任务描述]
你需要调用合适的MCP工具完成用户任务，根据工具返回的结果回答用户的问题。

[可调用的MCP工具]
{% for tool in tools %}
{{ loop.index }}. {{ tool.name }}: {{ tool.description }}
{% endfor %}
"""


def function_call_prompt(tools: list, history: list[AnyMessage]) -> list[AnyMessage]:
    template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(FUNCTION_CALL_SYSTEM_PROMPT, "jinja2"),
        MessagesPlaceholder("history")
    ])
    return template.format_messages(tools=tools, history=history)


COMMON_SYSTEM_PROMPT = r"""
[任务描述]
你是一个AI助手，根据你的已知知识和用户指令的要求回答用户问题

[用户指令]
{% if instructions %}
{% for instruction in instructions %}
{{ loop.index }}. {{ instruction }}
{% endfor %}
{% else %}
无
{% endif %}
"""


def common_prompt(instructions: list[str], history: list[AnyMessage]) -> list[AnyMessage]:
    template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(COMMON_SYSTEM_PROMPT, "jinja2"),
        MessagesPlaceholder("history")
    ])
    return template.format_messages(instructions=instructions, history=history)


CONCLUSION_SYSTEM_PROMPT = r"""
[任务描述]
你是一个AI助手，根据你的已知知识和用户指令的要求，回答用户问题或向用户输出工具调用结果

[用户指令]
{% if instructions %}
{% for instruction in instructions %}
{{ loop.index }}. {{ instruction }}
{% endfor %}
{% else %}
无
{% endif %}
"""


def conclusion_prompt(instructions: list[str], history: list[AnyMessage]) -> list[AnyMessage]:
    template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(CONCLUSION_SYSTEM_PROMPT, "jinja2"),
        MessagesPlaceholder("history")
    ])
    return template.format_messages(instructions=instructions, history=history)
