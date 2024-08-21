from dotenv import load_dotenv
import json
import os

from admin.assistant import AdminOperations

helper = AdminOperations()

load_dotenv()
#Количество попыток ввода пароля
MAX_ATTEMPTS = int(helper.get_attempts_enter_wrong_password())
#Список забаненных пользователей
BANNED_USERS = json.loads((os.environ.get("BANNED_USERS")))
#Список админов
ADMIN_USERS = json.loads((os.environ.get("ADMIN_USERS")))
#Список пользователей для рассылки
LIST_USERS_TO_NEWSLETTER = []