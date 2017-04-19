#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime as dt

# definitions
HOME_DIR_MT = r'/home/xml/export/cian'
HOME_DIR_NIRLAN = r'/home/xml/export/n_cian'

# Директории
DIRECTORIES = (
    # r'C:\Devel\PyCharmProject\MT\src',
    # r'D:\Devel\MT\src',
    os.path.join(HOME_DIR_MT, 'tem'),
    os.path.join(HOME_DIR_MT, 'soc'),
    os.path.join(HOME_DIR_MT, 'bud'),
    os.path.join(HOME_DIR_MT, 'sev'),
    os.path.join(HOME_DIR_MT, 'zap'),
    os.path.join(HOME_DIR_MT, 'vos'),
    os.path.join(HOME_DIR_MT, 'str'),
    os.path.join(HOME_DIR_MT, 'bat'),
    # HOME_DIR_NIRLAN,
    os.path.join(HOME_DIR_NIRLAN, 'centr'),
    os.path.join(HOME_DIR_NIRLAN, 'sever'),
    os.path.join(HOME_DIR_NIRLAN, 'zapad'),
)

# Имена файлов с выгрузками bn для ЦИАНа
IN_FILE = 'bncat.xml'
IN_FILE_COMMERCE = 'bncat_comnedv.xml'

# Имя выходного файла с выгрузками для ЦИАНа
OUT_FILE = 'cian.xml'

# Имя файла с журналом
LOG_FILE = '{}.log'.format(dt.today().strftime('%d %B %Y %H-%M-%S'))

# "Новый" префикс объявлений
ID_PREFIX = "1508"

# Список блокирующих выражений
BLOCK_PHRASES = (
    'ена 1',
    'ена 2',
    'ена: 1',
    'ена: 2',
    'найти',
    'Продажа квартир',
    'омощь',
    'оможем',
    'омогу',
    'выбрать квартиру',
    'выбор квартир',
    'квартир мало',
    'родажа',
    'квартир ',
    'варианты',
    '1-комнатные',
    '2х-комнатные',
    '1-2-3 комнатные',
    '1-2 комнатные',
    'Есть варианты по этажам',
    'квартиры на других этажах',
    'выбор квартир',
    'торговые площади',
)

# Список офисов с названиями и телефонами для ЦИАНа
OFFICES = {
    '8(863)2-270-500': {'office': 'ДОНМТ офис Центральный 1', 'phone': '9381361278'},
    '8(863)2-990-707': {'office': 'ДОНМТ офис Центральный 2', 'phone': '9604434798'},
    '8(863)2-270-909': {'office': 'ДОНМТ офис Центральный 3', 'phone': '9286216057'},
    '8(863)200-67-67': {'office': 'ДОНМТ офис Западный', 'phone': '9298174480'},
    '8(863)2-300-909': {'office': 'ДОНМТ офис Северный', 'phone': '9885669794'},
    '8(863)200-85-85': {'office': 'ДОНМТ офис Стройгородок', 'phone': '9034067095'},
    '8(863)300-24-00': {'office': 'ДОНМТ офис Восточный', 'phone': '9045033362'},
    '8(863)2-500-400': {'office': 'ДОНМТ офис Батайск', 'phone': '9281879795'},
    '8(863)250-27-27': {'office': 'ДОНМТ офис Коммерческая недвижимость', 'phone': '9081719005'},
}
