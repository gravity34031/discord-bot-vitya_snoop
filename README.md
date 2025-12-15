# discord-bot-vitya_snoop

Установить docker
curl -fsSL https://get.docker.com | sudo sh

Установить docker-compose(plugin)
sudo apt install -y docker-compose-plugin

Добавить пользователя в docker(чтобы без sudo)
sudo usermod -aG docker $USER
перезайти по ssh

Склонить/спулить репозиторий
git clone http://
git pull

Создать и настроить .env
nano .env

собрать контейнер
docker compose up -d --build

проверить
docker compose ps



#.env пример
discord_token = ''
discord_token_dev = ''
DEBUG = 'True'

POSTGRES_HOST=docker_service_name
POSTGRES_DB=name
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_PORT=5432
POSTGRES_URI=postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

DATABASE_URL=${POSTGRES_URI}