# Dog Bot

This cool Telegram DogBot can send images/gifs of dogs. Either randomly or by breed.

The bot is running on my Raspberry Pi and can be found here https://t.me/send_random_dog_bot 

## Development

### Setup

```shell
source setup-local-venv.sh
```

## Deployment

### Setup Environment

- Create a Telegram Bot using the BotFather
- Create a chat where the bot will send logs and errors
- Create a Dog Api key [here](https://thedogapi.com/)
- Create a file `env.json` in the `dogbot` subdirectory with the developer_chat_id and the bot_token
```json
{
  "developer_chat_id": "<REPLACE WITH DEVELOPER CHAT ID>",
  "bot_token": "<REPLACE WITH BOT TOKEN>",
  "dog_api_key": "<REPLACE WITH DOG API KEY>"
}
```

### Build docker

#### Raspberry Pi

```shell
./docker-build-raspberry-pi.sh
```

#### Linux/Mac

```shell
./docker-build-linux.sh
```

### Run docker

```shell
./docker-run.sh
```