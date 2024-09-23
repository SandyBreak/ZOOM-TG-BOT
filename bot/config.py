# -*- coding: UTF-8 -*-

import os
import ast

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

LIST_USERS_TO_NEWSLETTER = []

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
POSTGRES_DB = os.environ.get('POSTGRES_DB')

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{int(POSTGRES_PORT)}/{POSTGRES_DB}"


API_ACCOUNTS = ast.literal_eval(os.environ.get("API_ACCOUNTS"))