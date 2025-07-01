# -*- coding: UTF-8 -*-
from chat.controller import ChatController
from chat.memory.mongodb import MongoDBChatRepository
from chat.memory.redis import InMemoryChatRepository
from chat.models import *
