import os
import random
import json
import urllib.request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neural_network import MLPClassifier
import nest_asyncio
nest_asyncio.apply()
#  Update - информация полученная с сервера (новые сообщения, новые контакты)
#  С сервера регулярно регулярно приходят Update'ы с новой информацией
from telegram import Update 
from telegram.ext import ApplicationBuilder #  Инструмент чтобы создавать и настраивать приложение (телеграм бот)
from telegram.ext import MessageHandler #  Handler (обработчик) - создать реакцию (функцию) на действие

from  telegram.ext import filters

# Загружаем файл с диалогами для обучения модели
url = "https://drive.google.com/uc?export==view&id=1_g0fLSHqAEuRnk-shY3KSspzCMPvHKpO"
filename = "dataset.json"
#filename = "intents_dataset.json"
urllib.request.urlretrieve(url, filename)

# Считываем файл в словарь
with open(filename, 'r', encoding='UTF-8') as file:
    data = json.load(file)

# Создаем массивы фраз и интентов для обучения
X = []
y = []

for name in data:
    for phrase in data[name]['examples']:
        X.append(phrase)
        y.append(name)
    for phrase in data[name]['responses']:
        X.append(phrase)
        y.append(name)

# Векторизуем наши фразы X
vectorizer = CountVectorizer()
vectorizer.fit(X)
X_vec = vectorizer.transform(X)

# Создаем и обучаем модель
model_mlp = MLPClassifier()
model_mlp.fit(X_vec, y)

MODEL = model_mlp

def get_intent(text):
    # сначала преобразуем текст в числа
    text_vec = vectorizer.transform([text])
    # берем элемент номер 0 - для того, чтобы избавиться от формата "список", который необходим для векторизации и машинного обучения
    return model_mlp.predict(text_vec)[0] 

def get_response(intent):
    return random.choice(data[intent]['responses'])

def bot(text):
 intent=''
 while intent !='exit':
   intent = get_intent(text)
   answer = get_response(intent)
   return answer
try:
    with open('secret_file.txt', 'r') as f:
        TOKEN = f.read()
except:
    print('Это файл с токеном спикера. Вам нужно вставить свой токен в ячейку ниже')

    TOKEN = '5574299276:AAEz_wilDYwtQ9e6anjd78aRLWTEWiMCegE'
# Функция для MessageHandler'а, вызывать ее при каждом сообщении боту
async def reply(update: Update, context) -> None:
    user_text = update.message.text
    reply = bot(user_text)
    print('<', user_text)
    print('>', reply)

    await update.message.reply_text(reply)  # Ответ пользователю в чат ТГ

# Создаем объект приложения - связываем его с токеном
app = ApplicationBuilder().token(TOKEN).build()

# Создаем обработчик текстовых сообщений
handler = MessageHandler(filters.Text(), reply)

# Добавляем обработчик в приложение
app.add_handler(handler)

# Запускаем приложение: бот крутится, пока крутится колесико выполнения слева ячейки)
app.run_polling()
