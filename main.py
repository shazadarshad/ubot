from telethon.sync import TelegramClient, events

api_id = 27364741
api_hash = '3fde55dbc0c6c6c4ffb883c89acca87f'
phone_number = '+94776512486'
group_username = 'ZUBotLogs'  # Replace with your group username

client = TelegramClient('userbot_session', api_id, api_hash)

async def is_user_id_valid(user_id):
    try:
        user = await client.get_entity(user_id)
        return True
    except Exception as e:
        return False

async def extract_user_id(argument):
    try:
        # Check if the argument is a valid user ID
        user_id = int(argument)
        if await is_user_id_valid(user_id):
            return user_id
    except ValueError:
        pass  # Ignore if the argument is not a valid integer

    try:
        # Check if the argument is a message link
        if 'http' in argument:
            message = await client.get_messages(argument)
            return message.sender_id
    except Exception as e:
        pass  # Ignore if extraction from the link fails

    return None

@client.on(events.NewMessage(incoming=True))
async def handle_incoming_message(event):
    sender = event.sender
    sender_name = sender.first_name if sender and sender.first_name else "N/A"
    sender_username = sender.username if sender and sender.username else "N/A"
    sender_id = event.sender_id
    time_received = event.message.date.strftime("%Y-%m-%d %H:%M:%S")
    message_content = event.raw_text
    message_link = f"https://t.me/c/{event.chat_id}/{event.id}"

    log_message = (
        f"Name: {sender_name}\n"
        f"Username: {sender_username}\n"
        f"User ID: {sender_id}\n"
        f"Time: {time_received}\n"
        f"Message: {message_content}\n"
        f"Link: {message_link}\n"
    )

    await client.send_message(group_username, log_message)  # Send the log to the group

@client.on(events.NewMessage(chats=group_username, pattern=r'\.msg'))
async def handle_send_direct_message(event):
    # Extract the user ID and message content from the command, e.g., ".msg 123456 Hello, how are you?"
    args = event.raw_text.split(maxsplit=2)
    user_id = await extract_user_id(args[1])
    message_content = args[2].strip() if len(args) > 2 else None

    if user_id and await is_user_id_valid(user_id) and message_content:
        try:
            await client.send_message(user_id, message_content)
            await event.reply(f"Message sent to user {user_id}: {message_content}")
        except Exception as e:
            await event.reply(f"Failed to send message. Error: {e}")
    else:
        await event.reply("Invalid command format or user ID. Use '.msg user_id message'")

@client.on(events.NewMessage(chats=group_username, pattern=r'\.reply'))
async def handle_reply_to_message(event):
    # Extract the user ID and reply content from the command, e.g., ".reply 123456 Hello, how are you?"
    args = event.raw_text.split(maxsplit=2)
    user_id = await extract_user_id(args[1])
    reply_content = args[2].strip() if len(args) > 2 else None

    if user_id and await is_user_id_valid(user_id) and reply_content:
        try:
            reply_message = f"Reply from the group:\n{reply_content}"
            await client.send_message(user_id, reply_message)
            await event.reply(f"Replied to user {user_id}: {reply_content}")
        except Exception as e:
            await event.reply(f"Failed to reply. Error: {e}")
    else:
        await event.reply("Invalid command format or user ID. Use '.reply user_id message' or '.reply message_link message'")

async def main():
    await client.start(phone_number)
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())