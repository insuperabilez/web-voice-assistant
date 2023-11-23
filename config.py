import pandas as pd
import re
from copy import copy
from number_to_text import num2text
from fuzzywuzzy import fuzz
def get_key_by_value(dictionary, value):
    keys = list(dictionary.keys())
    if value in dictionary.values():
        index = list(dictionary.values()).index(value)
        return keys[index]
    return None  # Если значение не найдено
def convert_numbers_to_words(sentence):
    sentence = str(sentence)
    sentence = sentence.replace('.',' . ')
    sentence = sentence.replace(',', ' . ')
    sentence = sentence.replace('.', 'точка')

    words = sentence.split()  # разделение предложения на отдельные слова
    converted_words = []  # список для хранения преобразованных слов

    for word in words:
        if word.isdigit():  # проверка, является ли слово числом
            converted_word = num2text(int(word))  # преобразование числа в слово
            converted_words.append(converted_word)
        else:
            converted_words.append(word)  # оставляем слово без изменений

    converted_sentence = ' '.join(converted_words)  # объединение слов обратно в предложение
    return converted_sentence

df = pd.read_excel('table.xlsx',decimal=',')
items=[]
sootvetstvie={}
dwords = ['пао','оао','ао','ооо']
for item in pd.array(df['Заказчик']):
    converted = convert_numbers_to_words(item)
    converted = converted.replace('"','')
    converted = converted.replace('-', ' ')
    converted = converted.replace(':', ' ')
    converted=converted.lower()
    converted = converted.split()
    words = [x for x in converted if x not in dwords]
    converted=' '.join(words)
    items.append(converted)
    sootvetstvie[item] = converted
VA_ALIAS = ['алиса','алис']
VA_TBR = ('для')
VA_CMDS = {
    'show1':('выполнение договоров'),
    'show2':('отгрузки товаров'),
}
def recognize_company(cmd: str):
    rc = {'item': '', 'percent': 0}
    for x in items:
        vrt = fuzz.ratio(cmd, x)
        if vrt > rc['percent']:
            rc['item'] = x
            rc['percent'] = vrt
    if rc['percent']>50:
        print(f'Распознан заказчик {rc["item"]} с уверенностью {rc["percent"]} процентов.')
        return rc['item']
    else:
        return ''
def recognize_cmd(cmd: str):
    rc = {'cmd': '', 'percent': 0}
    for c, v in VA_CMDS.items():
        vrt = fuzz.ratio(cmd, v)
        if vrt > rc['percent']:
            rc['cmd'] = c
            rc['percent'] = vrt
    print(f'Команда {cmd}  распознана как {rc["cmd"]} с уверенностью {rc["percent"]} процентов.')
    if rc['percent']>50:
        return rc['cmd']
    else:
        return 'None'