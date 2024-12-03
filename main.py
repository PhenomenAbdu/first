import json
from difflib import get_close_matches

# Загрузка базы знаний из файла
def load_knowledge_base():
    with open('knowledge_base.json', 'r') as file:
        return json.load(file)

# Сохранение базы знаний в файл
def save_knowledge_base(data):
    with open('knowledge_base.json', 'w') as file:
        json.dump(data, file, indent=2)

# Нахождение самого похожего вопроса
def find_best_match(user_question, questions):
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.8)
    return matches[0] if matches else None

# Чат-бот
def chat_bot():
    knowledge_base = load_knowledge_base()

    print('Напиши "quit", чтобы выйти.')

    while True:
        user_input = input("Ты: ")

        if user_input.lower() == 'quit':
            break

        # Поиск ответа
        questions = [q["question"] for q in knowledge_base["questions"]]
        best_match = find_best_match(user_input, questions)

        if best_match:
            for q in knowledge_base["questions"]:
                if q["question"] == best_match:
                    print(f'Бот: {q["answer"]}')
                    break
        else:
            print("Бот: Я не знаю ответа. Научи меня!")
            new_answer = input('Напиши ответ или пропусти, написав "skip": ')

            if new_answer.lower() != "skip":
                knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
                save_knowledge_base(knowledge_base)
                print('Бот: Спасибо!')

if __name__ == '__main__':
    chat_bot()

import json
from difflib import get_close_matches
import telebot

bot = telebot.TeleBot('7398307830:AAGbzR1-9XGTJ3NXw9fBwrbHaYby3WU-kKk')

# Хранилище для текущего вопроса
pending_questions = {}

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
    return None

knowledge_base: dict = load_knowledge_base('knowledge_base.json')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Задай мне любой вопрос.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    best_match = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])

    if best_match:
        answer = get_answer_for_question(best_match, knowledge_base)
        bot.reply_to(message, answer)
    else:
        bot.reply_to(message, "Я не знаю ответа. Можешь научить меня? Напиши ответ на этот вопрос или 'skip', чтобы пропустить.")
        pending_questions[message.chat.id] = user_input  # Сохраняем вопрос
        bot.register_next_step_handler(message, handle_learning)

def handle_learning(message):
    chat_id = message.chat.id
    if chat_id in pending_questions:
        question = pending_questions.pop(chat_id)  # Получаем сохраненный вопрос
        if message.text.lower() != "skip":
            answer = message.text
            knowledge_base["questions"].append({"question": question, "answer": answer})
            save_knowledge_base('knowledge_base.json', knowledge_base)
            bot.reply_to(message, "Спасибо! Я запомнил.")
        else:
            bot.reply_to(message, "Хорошо, может быть в следующий раз.")
    else:
        bot.reply_to(message, "Что-то пошло не так. Попробуй задать вопрос заново.")

if __name__ == '__main__':
    bot.polling()


