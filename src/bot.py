import os
import openai
import discord
from random import randrange
from src.aclient import client
from discord import app_commands
from src import log, art, personas, responses

logger = log.setup_logger(__name__)

def run_discord_bot():
    @client.event
    async def on_ready():
        await client.send_start_prompt()
        await client.tree.sync()
        logger.info(f'{client.user} Сейчас бот запущен!')

    @client.tree.command(name="chat", description="Пообщайтесь с ChatGPT")
    async def chat(interaction: discord.Interaction, *, message: str):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **Предупреждение: Вы уже находитесь в режиме replyAll. Если вы хотите использовать команду slash, переключитесь в обычный режим, снова используйте `/replyall`.**")
            logger.warning("\x1b[31mВы уже в режиме replyAll, не можете использовать команду slash!\x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /chat [{message}] in ({channel})")
        await client.send_message(interaction, message)


    @client.tree.command(name="private", description="Переключить частный доступ")
    async def private(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if not client.isPrivate:
            client.isPrivate = not client.isPrivate
            logger.warning("\x1b[31mПереход в частный режим\x1b[0m")
            await interaction.followup.send(
                "> **Информация: Далее ответ будет отправлен через личное сообщение. Если вы хотите переключиться обратно в публичный режим, используйте `/public`.**")
        else:
            logger.info("Вы уже в приватном режиме!")
            await interaction.followup.send(
                "> **Предупреждение: Вы уже находитесь в приватном режиме. Если вы хотите перейти в публичный режим, используйте `/public`.**")

    @client.tree.command(name="public", description="Переключить публичный доступ")
    async def public(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if client.isPrivate:
            client.isPrivate = not client.isPrivate
            await interaction.followup.send(
                "> **Информация: Далее ответ будет отправлен непосредственно в канал. Если вы хотите переключиться обратно в приватный режим, используйте `/private`.**")
            logger.warning("\x1b[31mПереключитесь на публичный режим\x1b[0m")
        else:
            await interaction.followup.send(
                "> **Предупреждение: Вы уже находитесь в публичном режиме. Если вы хотите перейти в приватный режим, используйте `/private`.**")
            logger.info("Вы уже в публичном режиме!")


    @client.tree.command(name="replyall", description="Переключить replyAll доступ")
    async def replyall(interaction: discord.Interaction):
        client.replying_all_discord_channel_id = str(interaction.channel_id)
        await interaction.response.defer(ephemeral=False)
        if client.is_replying_all == "True":
            client.isReplyingAl = "False"
            await interaction.followup.send(
                "> **Информация: Далее бот будет отвечать только на слэш-команду `/chat`. Если вы хотите переключиться обратно в режим replyAll, используйте `/replyAll` снова.**")
            logger.warning("\x1b[31mПереключение в нормальный режим\x1b[0m")
        elif client.is_replying_all == "False":
            client.is_replying_all = "True"
            await interaction.followup.send(
                "> **Информация: Далее бот будет отвечать только на все сообщения в этом канале. Если вы хотите переключиться в обычный режим, используйте `/replyAll` снова.**")
            logger.warning("\x1b[31mПереключение в режим replyAll\x1b[0m")


    @client.tree.command(name="chat-model", description="Переключение различных моделей чата")
    @app_commands.choices(choices=[
        app_commands.Choice(name="Official GPT-3.5", value="OFFICIAL"),
        app_commands.Choice(name="Ofiicial GPT-4.0", value="OFFICIAL-GPT4"),
        app_commands.Choice(name="Website ChatGPT-3.5", value="UNOFFICIAL"),
        app_commands.Choice(name="Website ChatGPT-4.0", value="UNOFFICIAL-GPT4"),
    ])

    async def chat_model(interaction: discord.Interaction, choices: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=False)
        if choices.value == "OFFICIAL":
            client.openAI_gpt_engine = "gpt-3.5-turbo"
            client.chat_model = "OFFICIAL"
            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(
                "> **Информация: Вы находитесь в официальной модели GPT-3.5.**\n")
            logger.warning("\x1b[31mПереход на ОФИЦИАЛЬНУЮ модель GPT-3.5\x1b[0m")
        elif choices.value == "OFFICIAL-GPT4":
            client.openAI_gpt_engine = "gpt-4"
            client.chat_model = "OFFICIAL"
            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(
                "> **Информация: Вы находитесь в официальной модели GPT-4.0.**\n")
            logger.warning("\x1b[31mПереход на ОФИЦИАЛЬНУЮ модель GPT-4.0\x1b[0m")
        elif choices.value == "UNOFFICIAL":
            client.openAI_gpt_engine = "gpt-3.5-turbo"
            client.chat_model = "UNOFFICIAL"
            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(
                "> **Информация: Вы сейчас находитесь в модели Website ChatGPT-3.5.**\n")
            logger.warning("\x1b[31mПереход на модель GPT-3.5 НЕОФИЦИАЛЬНУЮ(Веб-сайт)\x1b[0m")
        elif choices.value == "UNOFFICIAL-GPT4":
            client.openAI_gpt_engine = "gpt-4"
            client.chat_model = "UNOFFICIAL"
            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(
                "> **Информация: Вы сейчас находитесь в модели Website ChatGPT-4.0.**\n")
            logger.warning("\x1b[31mПереход на модель GPT-4.0 НЕОФИЦИАЛЬНУЮ(Веб-сайт)\x1b[0m")


    @client.tree.command(name="reset", description="Полный сброс истории разговоров ChatGPT")
    async def reset(interaction: discord.Interaction):
        if client.chat_model == "OFFICIAL":
            client.chatbot.reset()
        elif client.chat_model == "UNOFFICIAL":
            client.chatbot.reset_chat()
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("> **Информация: Я все забыл.**")
        personas.current_persona = "standard"
        logger.warning(
            "\x1b[31mБот ChatGPT был успешно перезагружен\x1b[0m")
        await client.send_start_prompt()


    @client.tree.command(name="help", description="Показать справку для бота")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(""":star:**ОСНОВНЫЕ КОМАНДЫ** \n
        - `/chat [message]` Общайтесь с ChatGPT!
        - `/draw [prompt]` Создание изображения с помощью модели Dalle2
        - `/switchpersona [persona]` Переключение между дополнительными моделями поведения chatGPT
                `random`: Выбирает случайную личность
                `chatgpt`: Стандартный режим chatGPT
                `dan`: Режим Dan Mode 11.0, печально известный режим Do Anything Now Mode
                `sda`: Superior DAN имеет еще больше свободы в режиме DAN Mode
                `confidant`: Злодейская личность, Адвокат дьявола
                `based`: BasedGPT v2, сексуальный gpt
                `oppo`: OPPO говорит прямо противоположное тому, что сказал бы chatGPT
                `dev`: Режим разработчика, v2 Режим разработчика включен
        - `/private` ChatGPT переключается в приватный режим
        - `/public` ChatGPT переключается в публичный режим
        - `/replyall` ChatGPT переключение между режимом replyAll и режимом по умолчанию
        - `/reset` Очистить историю разговоров ChatGPT
        - `/chat-model` Переключение различных моделей чата
                `ОФИЦИАЛЬНЫЙ`: GPT-3.5 модель
                `НЕОФИЦИАЛЬНЫЙ`: Веб-сайт ChatGPT""")
                
        logger.info(
            "\x1b[31mКому-то нужна помощь!\x1b[0m")

    @client.tree.command(name="draw", description="Создание изображения с помощью модели Dalle2!")
    async def draw(interaction: discord.Interaction, *, prompt: str):
        if interaction.user == client.user:
            return

        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /draw [{prompt}] in ({channel})")

        await interaction.response.defer(thinking=True, ephemeral=client.isPrivate)
        try:
            path = await art.draw(prompt)

            file = discord.File(path, filename="image.png")
            title = f'> **{prompt}** - <@{str(interaction.user.mention)}' + '> \n\n'
            embed = discord.Embed(title=title)
            embed.set_image(url="attachment://image.png")

            await interaction.followup.send(file=file, embed=embed)

        except openai.InvalidRequestError:
            await interaction.followup.send(
                "> **Предупреждение: Неуместный запрос 😿**")
            logger.info(
            f"\x1b[31m{username}\x1b[0m обратился с неуместной просьбой.!")

        except Exception as e:
            await interaction.followup.send(
                "> **Предупреждение: Что-то пошло не так 😿**")
            logger.exception(f"Ошибка при генерации изображения: {e}")


    @client.tree.command(name="switchpersona", description="Переключение между дополнительными моделями поведения chatGPT")
    @app_commands.choices(persona=[
        app_commands.Choice(name="Random", value="random"),
        app_commands.Choice(name="Standard", value="standard"),
        app_commands.Choice(name="Do Anything Now 11.0", value="dan"),
        app_commands.Choice(name="Superior Do Anything", value="sda"),
        app_commands.Choice(name="Evil Confidant", value="confidant"),
        app_commands.Choice(name="BasedGPT v2", value="based"),
        app_commands.Choice(name="OPPO", value="oppo"),
        app_commands.Choice(name="Developer Mode v2", value="dev")
    ])
    async def chat(interaction: discord.Interaction, persona: app_commands.Choice[str]):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **Предупреждение: Вы уже находитесь в режиме replyAll. Если вы хотите использовать команду slash, переключитесь в обычный режим, снова используйте `/replyall`.**")
            logger.warning("\x1b[31mВы уже в режиме replyAll, не можете использовать слэш-команду!\x1b[0m")
            return
        if interaction.user == client.user:
            return

        await interaction.response.defer(thinking=True)
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : '/switchpersona [{persona.value}]' ({channel})")

        persona = persona.value

        if persona == personas.current_persona:
            await interaction.followup.send(f"> **Предупреждение: Уже установлена `{persona}` модель поведения**")

        elif persona == "standard":
            if client.chat_model == "OFFICIAL":
                client.chatbot.reset()
            elif client.chat_model == "UNOFFICIAL":
                client.chatbot.reset_chat()

            personas.current_persona = "standard"
            await interaction.followup.send(
                f"> **Информация: Переключился на `{persona}` модель поведения**")

        elif persona == "random":
            choices = list(personas.PERSONAS.keys())
            choice = randrange(0, 6)
            chosen_persona = choices[choice]
            personas.current_persona = chosen_persona
            await responses.switch_persona(chosen_persona, client)
            await interaction.followup.send(
                f"> **Информация: Переключился на `{chosen_persona}` модель поведения**")


        elif persona in personas.PERSONAS:
            try:
                await responses.switch_persona(persona, client)
                personas.current_persona = persona
                await interaction.followup.send(
                f"> **Информация: Переключился на `{persona}` модель поведения**")
            except Exception as e:
                await interaction.followup.send(
                    "> **Ошибка: Что-то пошло не так, пожалуйста, повторите попытку позже! 😿**")
                logger.exception(f"Ошибка при переключении модели поведения: {e}")

        else:
            await interaction.followup.send(
                f"> **Ошибка: Нет доступных моделей поведения: `{persona}` 😿**")
            logger.info(
                f'{username} запросил недоступную модель поведения: `{persona}`')

    @client.event
    async def on_message(message):
        if client.is_replying_all == "True":
            if message.author == client.user:
                return
            if client.replying_all_discord_channel_id:
                if message.channel.id == int(client.replying_all_discord_channel_id):
                    username = str(message.author)
                    user_message = str(message.content)
                    channel = str(message.channel)
                    logger.info(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
                    await client.send_message(message, user_message)

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    client.run(TOKEN)
