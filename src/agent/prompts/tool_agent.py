# -*- coding: UTF-8 -*-
from langchain_core.prompts import SystemMessagePromptTemplate


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

DECISION_SYSTEM_TEMPLATE = SystemMessagePromptTemplate.from_template(DECISION_SYSTEM_PROMPT, "jinja2")

FUNCTION_CALL_SYSTEM_PROMPT = r"""
[任务描述]
你需要调用合适的MCP工具完成用户任务，不要回答用户问题。

[可调用的MCP工具]
{% for tool in tools %}
{{ loop.index }}. {{ tool.name }}: {{ tool.description }}
{% endfor %}
"""

FUNCTION_CALL_SYSTEM_TEMPLATE = SystemMessagePromptTemplate.from_template(FUNCTION_CALL_SYSTEM_PROMPT, "jinja2")

CONCLUSION_SYSTEM_PROMPT = r"""
[任务描述]
你是一个AI助手，根据你的已知知识回答用户问题
"""

CONCLUSION_SYSTEM_TEMPLATE = SystemMessagePromptTemplate.from_template(CONCLUSION_SYSTEM_PROMPT, "jinja2")
