# ZOOM-TG-BOT

Telegram bot for simplifying the creation of conferences in zoom. You need to select the date, start time and duration, after which the bot will automatically create a zoom conference on one of your accounts. When forming a keyboard for choosing the start time and duration, it selects only free time slots, that is, the created conferences do not overlap with each other
How to deploy:

Ubuntu 22.04:

1. sudo apt install docker.io docker-compose -y | install docker

2. git clone git@github.com:SandyBreak/ZOOM-TG-BOT.git | Copy app to server

3. Change mongodb pass&login and telegram_token in docker-compose.env

4. In project dir: sudo docker-compose up -d --build | deploy containers

5. How to connect using mongodb compass: mongodb://{mongodb_login}:{mongodb_password}@{sever_ip_adress}:27021/



Commands:

1. sudo docker ps -a | list all running containers

2. sudo docker stop <container name> | stop container

3. sudo docker rm <container name> | remove container

4. sudo docker-compose down | stop&remove containers