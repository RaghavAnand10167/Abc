import shutil
import sys
import subprocess
import os
from telebot import TeleBot, types



# Use environment variables for sensitive information
API_TOKEN = "7517822450:AAEFNxUWD8jIW7rfRF-wYKkBjShQdXR68HM"
bot = TeleBot(API_TOKEN)

# List of admin IDs
admins = {'5173016128'}

# Directory path for bot files
BOT_FOLDER = '.'

# To save running processes
processes = {}

def list_files():
    """Lists all files in the bot directory."""
    try:
        files = os.listdir(BOT_FOLDER)
        files_list = [f for f in files if os.path.isfile(os.path.join(BOT_FOLDER, f))]
        return files_list
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

@bot.message_handler(commands=['start'])
def start_command(message):
    """Handles the /start command."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    files_list = list_files()
    if not files_list:
        bot.reply_to(message, 'No files found in the bot directory.')
        return
    markup = types.ReplyKeyboardMarkup(row_width=1)
    buttons = [
        'LIST FILES', 'START A FILE', 'STOP A FILE', 
        'UPLOAD A FILE', 'RENAME A FILE', 'DELETE A FILE', 
        'VIEW A FILE'
    ]
    markup.add(*[types.KeyboardButton(button) for button in buttons])
    bot.send_message(message.chat.id, 'FILE MANAGER BOT BY RAGHAV ANAND\n', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'VIEW A FILE')
def view_file_command(message):
    """Handles the 'VIEW A FILE' command."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    files_list = list_files()
    if not files_list:
        bot.reply_to(message, 'No files found in the bot directory.')
        return
    file_list_message = '\n'.join([f"{idx + 1}. {file}" for idx, file in enumerate(files_list)])
    bot.send_message(message.chat.id, f"Select a file to view:\n{file_list_message}")
    bot.register_next_step_handler(message, view_file_choice)

def view_file_choice(message):
    """Handles the file choice to view."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    try:
        choice = int(message.text) - 1
        files_list = list_files()
        if 0 <= choice < len(files_list):
            file_name = files_list[choice]
            file_path = os.path.join(BOT_FOLDER, file_name)
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    content = file.read()
                bot.send_message(message.chat.id, f'Content of {file_name}:\n\n{content}')
            else:
                bot.reply_to(message, 'File not found.')
        else:
            bot.reply_to(message, 'Invalid choice. Please choose a valid number.')
            bot.register_next_step_handler(message, view_file_choice)
    except ValueError:
        bot.reply_to(message, 'Please enter a valid number.')
        bot.register_next_step_handler(message, view_file_choice)

@bot.message_handler(func=lambda message: message.text == 'LIST FILES')
def list_files_command(message):
    """Handles the 'LIST FILES' command."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    files_list = list_files()
    if not files_list:
        bot.reply_to(message, 'No files found in the bot directory.')
        return
    file_list_message = '\n'.join([f"{idx + 1}. {file}" for idx, file in enumerate(files_list)])
    bot.send_message(message.chat.id, f"Files in the bot directory:\n{file_list_message}\n\nSend the number of the file you want to download or update.")
    bot.register_next_step_handler(message, file_choice)

def file_choice(message):
    """Handles file choice for download or update."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    try:
        choice = int(message.text) - 1
        files_list = list_files()
        if 0 <= choice < len(files_list):
            chosen_file = files_list[choice]
            bot.send_message(message.chat.id, f"You chose {chosen_file}. Send the file content to update it, or type 'download' to download the file.")
            bot.register_next_step_handler(message, lambda msg: handle_file_action(msg, chosen_file))
        else:
            bot.reply_to(message, 'Invalid choice. Please choose a valid number.')
            bot.register_next_step_handler(message, file_choice)
    except ValueError:
        bot.reply_to(message, 'Please enter a valid number.')
        bot.register_next_step_handler(message, file_choice)

def handle_file_action(message, file_name):
    """Handles the action to perform on the file (download or update)."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    if message.text and message.text.lower() == 'download':
        file_path = os.path.join(BOT_FOLDER, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, 'File not found.')
    elif message.document:
        if message.document.file_name != file_name:
            bot.reply_to(message, 'File name mismatch. Please send the correct file.')
            return
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = os.path.join(BOT_FOLDER, file_name)

        # Replace the file content
        with open(file_path, 'wb') as file:
            file.write(downloaded_file)

        bot.reply_to(message, f'File {file_name} updated successfully.')
        restart_bot()
    else:
        bot.reply_to(message, 'Invalid action. Please send the correct file or type "download" to download the file.')

@bot.message_handler(func=lambda message: message.text == 'START A FILE')
def start_file_command(message):
    """Handles the 'START A FILE' command."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    files_list = list_files()
    if not files_list:
        bot.reply_to(message, 'No files found in the bot directory.')
        return
    file_list_message = '\n'.join([f"{idx + 1}. {file}" for idx, file in enumerate(files_list)])
    bot.send_message(message.chat.id, f"Select a file to start:\n{file_list_message}")
    bot.register_next_step_handler(message, start_file_choice)

def start_file_choice(message):
    """Handles the file choice to start."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    try:
        choice = int(message.text) - 1
        files_list = list_files()
        if 0 <= choice < len(files_list):
            file_name = files_list[choice]
            file_path = os.path.join(BOT_FOLDER, file_name)

            # Start the file
            process = subprocess.Popen(['python3', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes[file_name] = process
            bot.reply_to(message, f'File {file_name} started successfully.')
        else:
            bot.reply_to(message, 'Invalid choice. Please choose a valid number.')
            bot.register_next_step_handler(message, start_file_choice)
    except ValueError:
        bot.reply_to(message, 'Please enter a valid number.')
        bot.register_next_step_handler(message, start_file_choice)

@bot.message_handler(func=lambda message: message.text == 'STOP A FILE')
def stop_file_command(message):
    """Handles the 'STOP A FILE' command."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    if not processes:
        bot.reply_to(message, 'No files are currently running.')
        return
    files_list = list(processes.keys())
    file_list_message = '\n'.join([f"{idx + 1}. {file}" for idx, file in enumerate(files_list)])
    bot.send_message(message.chat.id, f"Select a file to stop:\n{file_list_message}")
    bot.register_next_step_handler(message, stop_file_choice)

def stop_file_choice(message):
    """Handles the file choice to stop."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    try:
        choice = int(message.text) - 1
        files_list = list(processes.keys())
        if 0 <= choice < len(files_list):
            file_name = files_list[choice]
            process = processes.pop(file_name, None)
            if process:
                process.terminate()
                bot.reply_to(message, f'File {file_name} stopped successfully.')
            else:
                bot.reply_to(message, 'Process not found.')
        else:
            bot.reply_to(message, 'Invalid choice. Please choose a valid number.')
            bot.register_next_step_handler(message, stop_file_choice)
    except ValueError:
        bot.reply_to(message, 'Please enter a valid number.')
        bot.register_next_step_handler(message, stop_file_choice)

@bot.message_handler(func=lambda message: message.text == 'UPLOAD A FILE')
def upload_file_command(message):
    """Handles the 'UPLOAD A FILE' command."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    bot.send_message(message.chat.id, 'Send me the file you want to upload.')

@bot.message_handler(func=lambda message: message.document, content_types=['document'])
def handle_document(message):
    """Handles file uploads."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = os.path.join(BOT_FOLDER, message.document.file_name)
    with open(file_path, 'wb') as file:
        file.write(downloaded_file)
    bot.reply_to(message, f'File {message.document.file_name} uploaded successfully.')

@bot.message_handler(func=lambda message: message.text == 'RENAME A FILE')
def rename_file_command(message):
    """Handles the 'RENAME A FILE' command."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    files_list = list_files()
    if not files_list:
        bot.reply_to(message, 'No files found in the bot directory.')
        return
    file_list_message = '\n'.join([f"{idx + 1}. {file}" for idx, file in enumerate(files_list)])
    bot.send_message(message.chat.id, f"Select a file to rename:\n{file_list_message}")
    bot.register_next_step_handler(message, rename_file_choice)

def rename_file_choice(message):
    """Handles the file choice for renaming."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    try:
        choice = int(message.text) - 1
        files_list = list_files()
        if 0 <= choice < len(files_list):
            old_file_name = files_list[choice]
            bot.send_message(message.chat.id, f'You chose {old_file_name}. Send me the new name for the file.')
            bot.register_next_step_handler(message, lambda msg: rename_file(msg, old_file_name))
        else:
            bot.reply_to(message, 'Invalid choice. Please choose a valid number.')
            bot.register_next_step_handler(message, rename_file_choice)
    except ValueError:
        bot.reply_to(message, 'Please enter a valid number.')
        bot.register_next_step_handler(message, rename_file_choice)

def rename_file(message, old_file_name):
    """Renames a file."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    new_file_name = message.text
    old_file_path = os.path.join(BOT_FOLDER, old_file_name)
    new_file_path = os.path.join(BOT_FOLDER, new_file_name)
    if os.path.exists(old_file_path):
        os.rename(old_file_path, new_file_path)
        bot.reply_to(message, f'File renamed from {old_file_name} to {new_file_name} successfully.')
    else:
        bot.reply_to(message, 'File not found.')

@bot.message_handler(func=lambda message: message.text == 'DELETE A FILE')
def delete_file_command(message):
    """Handles the 'DELETE A FILE' command."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    files_list = list_files()
    if not files_list:
        bot.reply_to(message, 'No files found in the bot directory.')
        return
    file_list_message = '\n'.join([f"{idx + 1}. {file}" for idx, file in enumerate(files_list)])
    bot.send_message(message.chat.id, f"Select a file to delete:\n{file_list_message}")
    bot.register_next_step_handler(message, delete_file_choice)

def delete_file_choice(message):
    """Handles the file choice to delete."""
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, 'You are not authorized to perform this action.')
        return
    try:
        choice = int(message.text) - 1
        files_list = list_files()
        if 0 <= choice < len(files_list):
            file_name = files_list[choice]
            file_path = os.path.join(BOT_FOLDER, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                bot.reply_to(message, f'File {file_name} deleted successfully.')
            else:
                bot.reply_to(message, 'File not found.')
        else:
            bot.reply_to(message, 'Invalid choice. Please choose a valid number.')
            bot.register_next_step_handler(message, delete_file_choice)
    except ValueError:
        bot.reply_to(message, 'Please enter a valid number.')
        bot.register_next_step_handler(message, delete_file_choice)

def restart_bot():
    """Restarts the bot."""
    bot.stop_polling()
    os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == '__main__':
    bot.polling(none_stop=True)






