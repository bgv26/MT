#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum

from lxml import etree

# definitions
ID_PREFIX = "1508"

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

LOCATIONS = {
    'Аксай': ('Аксай',
              'Водники', 'Военный городок',
              'Поле чудес №2',
              'Стекольный завод'),
    'Батайск': ('Авиагородок',
                'Батайск', 'Булгакова',
                'ВЖМ', 'Ворошилова',
                'Гайдара',
                'Дачный', 'Железнодорожный тупик',
                'Залесье', 'Залесье/Остановка', 'Западный Батайск', 'Заря',
                'Кирова', 'Коваливского', 'Комсомольская', 'Книжный', 'Красный сад', 'Крупской',
                'Крупской/Парк',
                'Куйбышева',
                'Луначарского', 'Лунева',
                'Наливная',
                'Огородная', 'Октябрьская',
                'Парковый', 'Половинко',
                'РДВС', 'Ростовский',
                'Северная Звезда', 'Северный массив', 'Соленое озеро', 'Солнечный', 'Стадионный',
                'Старый город',
                'Урицкого', 'Ушинского',
                'Энгельса'),
    'Ростов-на-Дону': ('1 Орджоникидзе', '2 Орджоникидзе', '1 Пламенный',
                       'Автосборочный', 'Александровка', 'Ашан, Леге-Артис, СЖМ', 'Аэропорт',
                       'Берберовка, Аэропорт', 'Болгарстрой', 'Ботанический сад (ЖДР)',
                       'ВЖМ', 'Военвед',
                       'Доватора (ЖДР, ЗЖМ)',
                       'ЖДР',
                       'Западная промзона (ЗЖМ)', 'Заречная промзона, Левый берег', 'ЗЖМ (Западный)', 'Зоопарк',
                       'Каменка', 'Каратаево', 'Комсомольская площадь', 'Красный Аксай, Нахичевань',
                       'Красный Маяк (ЗЖМ)', 'Красный сад', 'Кумженская роща',
                       'Левенцовка (ЗЖМ)', 'Левый берег', 'Леге-Артис, СЖМ', 'Ленина', 'Лесополоса, Болгарстрой',
                       'Мирный, Чкаловский', 'Мясниковань, СЖМ',
                       'Нариманова', 'Нахичевань', 'Новое поселение',
                       'площадь Ленина', 'Портовая (ЖДР, ЗЖМ)',
                       'Рабочий городок', 'РИИЖТ', 'Ростовское море',
                       'Сельмаш', 'СЖМ', 'СЖМ (Северный)', 'совхоз СКВО, СЖМ', 'Старый автовокзал, Нахичевань',
                       'Стройгородок', 'Суворовский',
                       'Темерник', 'Темерницкий',
                       'Фрунзе',
                       'Центр',
                       'Чкаловский')
}

OFFICES = {
    '8(863)2-270-500': {'office': 'ДОНМТ офис Центральный 1', 'phone': '9381361278'},
    '8(863)2-990-707': {'office': 'ДОНМТ офис Центральный 2', 'phone': '9604434798'},
    '8(863)2-270-909': {'office': 'ДОНМТ офис Центральный 3', 'phone': '9286216057'},
    '8(863)200-67-67': {'office': 'ДОНМТ офис Западный', 'phone': '9298174480'},
    '8(863)2-300-909': {'office': 'ДОНМТ офис Северный', 'phone': '9885669794'},
    '8(863)2-500-400': {'office': 'ДОНМТ офис Северный', 'phone': '9885669794'},
    '8(863)200-85-85': {'office': 'ДОНМТ офис Стройгородок', 'phone': '9034067095'},
    '8(863)300-24-00': {'office': 'ДОНМТ офис Восточный', 'phone': '9045033362'},
    '8(863)2-417-423': {'office': 'ДОНМТ офис Батайск', 'phone': '9281879795'}
}

DEAL_TYPE = {
    'аренда': 'R',
    'продажа': 'S'
}

REALTY_TYPE = {
    'дом': 'K',
    'коттедж': 'K',
    'участок': 'A'
}

PROPORTIONS = (
    (100,),
    (60, 40),
    (40, 30, 30),
    (30, 25, 25, 20),
    (25, 20, 20, 20, 15),
    (20, 20, 15, 15, 15, 15)
)


class AdType(Enum):
    RENT = 'flats_rent'
    SALE = 'flats_for_sale'
    COMMERCE = 'commerce'
    SUBURBIAN = 'suburbian'


class ForDay(Enum):
    UNLIM = 0
    FOR_DAY = 1
    FOR_MONTH = 2


class CommerceType(Enum):
    OFFICE = 'O'
    WAREHOUSE = 'W'
    TRADE_PLACE = 'T'
    FOR_FOOD_PLACE = 'F'
    FREE_PLACE = 'FP'
    GARAGE = 'G'
    AUTOSERVICE = 'AU'
    BUILDING = 'B'
    LEGAL_ADDRESS = 'UA'
    SALE_OF_BUSINESS = 'SB'
    DOMESTIC_SERVICES = 'BU'


class ContractType(Enum):
    RENT = 1
    SUBRENT = 2
    RENT_RIGHT_SALE = 3
    OBJECT_SALE = 4
    SHARE_BUSINESS = 5


class BuildingType(Enum):
    NONLIVING = 1
    LIVING = 2


class BuildingEnter(Enum):
    FREE = 1
    PERMISSION = 2


class BuildingStatus(Enum):
    SATISFACTORY = 1
    GOOD = 2
    PERFECT = 3


class BuildingClass(Enum):
    A = 1
    APLUS = 2
    B = 3
    BPLUS = 4
    C = 5
    CPLUS = 6


class HouseType(Enum):
    PANEL = 1
    BRICK = 2
    MONOLITH = 3
    BRICK_MONOLITH = 4
    BLOCK = 5
    WOOD = 6
    STALIN = 7
    OLD_FOND = 9


class SaleTypeFirst(Enum):
    FREE = 'free'
    ALTERNATE = 'alt'
    INVEST = 'invest'
    PDKP = 'pdkp'
    PEREUSTUPKA = 'pereustupka'
    ZHSK = 'zhsk'
    DDU = 'ddu'


class RoomNum(Enum):
    ROOM = 0
    SINGLE_ROOM = 1
    DOUBLE_ROOM = 2
    TRIPLE_ROOM = 3
    FORTH_ROOM = 4
    FIVE_ROOM = 5
    MULTI_ROOM = 6
    FREE = 7
    STUDIO = 9
    BED = 10


class Windows(Enum):
    YARD = 1
    STREET = 2
    MIX = 3


class Ipoteka(Enum):
    YES = 1
    NO = 0


class Repair(Enum):
    COSMETIC = 1
    EURO = 2
    DESIGN = 3
    ABSENT = 4


class Finishing(Enum):
    YES = 1
    NO = 0


class SaleTypeUsed(Enum):
    FREE = 'F'
    ALTERNATE = 'A'


class Deposit(Enum):
    YES = 0
    NO = 1


class Composition(Enum):
    ANY = 1
    FAMILY = 2
    FEMALE = 3
    MALE = 4


class RealityType(Enum):
    HOUSE = 'K'
    PART_OF_HOUSE = 'P'
    STEAD = 'A'
    TOWNHOUSE = 'T'


class LandType(Enum):
    SNT = 1
    IGS = 2
    PROM = 3
    FARM = 4
    DNP = 5
    INVEST = 6


class BlockedRecordException(Exception):
    pass


class EmptyRequiredFieldException(Exception):
    pass


class EmptyResult(Exception):
    pass


# def to_cian(ad_type):
#     root = etree.Element(ad_type)
#     offer = etree.SubElement(root, 'offer')
#     ad_id = etree.SubElement(offer, 'id')
#
#     if ad_type == 'commerce':  # for commerce only
#         commerce_type = etree.SubElement(offer, 'commerce_type')
#         contract_type = etree.SubElement(offer, 'contract_type')
#         building = etree.SubElement(offer, 'building')
#         building_dict = building.attrib
#         building_dict['floor'] = ''
#         building_dict['floor_total'] = ''
#         business_shopping_center = etree.SubElement(offer, 'business_shopping_center')
#
#     if ad_type.startswith('flats'):  # for rent and sale
#         rooms_num = etree.SubElement(offer, 'rooms_num')
#         floor = etree.SubElement(offer, 'floor')
#         floor_dict = floor.attrib
#         floor_dict['total'] = ''
#         composition = etree.SubElement(offer, 'composition')
#
#     if ad_type == 'suburbian':  # for suburbian only
#         deal_type = etree.SubElement(offer, 'deal_type')
#         realty_type = etree.SubElement(offer, 'realty_type')
#         land_type = etree.SubElement(offer, 'land_type')
#         floor_total = etree.SubElement(offer, 'floor_total')
#         bedroom_total = etree.SubElement(offer, 'bedroom_total')
#
#     area = etree.SubElement(offer, 'area')
#     area_dict = area.attrib
#     if ad_type == 'suburbian':
#         area_dict['region'] = ''
#         area_dict['living'] = ''
#     else:
#         area_dict['total'] = ''
#
#     price = etree.SubElement(offer, 'price')
#     phone = etree.SubElement(offer, 'phone')
#     address = etree.SubElement(offer, 'address')
#     address_dict = address.attrib
#     address_dict['admin_area'] = str(39)
#     address_dict['locality'] = ''
#     address_dict['street'] = ''
#
#     note = etree.SubElement(offer, 'note')
#     options = etree.SubElement(offer, 'options')
#     com = etree.SubElement(offer, 'com')
#     photo = etree.SubElement(offer, 'photo')
#     promotions = etree.SubElement(offer, 'promotions')
#     special_offer_id = etree.SubElement(offer, 'special_offer_id')
#     if ad_type == 'flats_for_sale':  # for sale only
#         residential_complex = etree.SubElement(offer, 'residential_complex')
#         project_declaration = etree.SubElement(offer, 'project_declaration')
#     return root
#

def gen_new_id(offer_id):
    return ID_PREFIX + offer_id[4:]


def get_node_value(parent, node, required=False):
    try:
        value = parent.xpath(node)
        return value.pop().text.strip()
    except IndexError:
        ad_id = get_node_value(parent, 'id', True)
        if required:
            raise EmptyRequiredFieldException(
                'Blocked: empty required field ({}) in advert id [{}]'.format(node, ad_id))
        print('Fix this: field {} in advert id: [{}] is  empty.'.format(node, ad_id))
        return ''


def is_block(text):
    for block in BLOCK_PHRASES:
        if block in text:
            return True
    return False


def get_rooms_areas(rooms, area):
    # split living area to room's areas in fixed PROPORTIONS
    areas = [round(area * room / 100, 1) for room in PROPORTIONS[rooms - 1][:-1]]
    areas.append(round(area - sum(areas), 1))
    return ' '.join(map(str, areas))


def get_city_by_place(text):
    for key, value in LOCATIONS.items():
        if text in value:
            return key
    return ''


def get_office_suffix(offer_id):
    return bytes([int(offer_id[9:])]).decode('cp1251')


def get_lot_number(offer_id):
    # symbols from 4 length 5 + '-8' + char value from three last digits in text
    return offer_id[4:9] + '-8' + get_office_suffix(offer_id)


def get_ipoteka(item):
    ad_terms = get_node_value(item, 'additional-terms')
    return 1 if ad_terms == 'Ипотека' else 0


def from_bn(item):
    description = get_node_value(item, 'description/full')
    ad_id = get_node_value(item, 'id', True)

    if is_block(description):
        raise BlockedRecordException('Blocked: bad description "{}" in advert id [{}]'.format(description, ad_id))

    info = dict()

    info['ad_id'] = gen_new_id(ad_id)

    price = int(get_node_value(item, 'price/value', True))
    if get_office_suffix(ad_id) != '*':
        if price * 0.025 < 10000:
            price -= price * 0.025
        else:
            price -= 90123
    info['price'] = str(price)

    agent_phone = get_node_value(item, 'agent/phone', True)
    info['phone'] = OFFICES[agent_phone]['phone']

    place = get_node_value(item, 'location/place')
    city = get_node_value(item, 'location/city', True)
    street = get_node_value(item, 'location/street', True)
    if get_city_by_place(place) == '' and get_city_by_place(street) == '' and city != '':
        print('Fix this:[{}]'.format(place))

    info['address_locality'] = city
    info['address_street'] = street

    info['photo'] = [photo.text for photo in item.xpath('files/image')]

    office = OFFICES[agent_phone]['office']
    lot_number = get_lot_number(ad_id)
    info['note'] = "{}\nПри звонке в {} укажите лот: {}".format(description, office, lot_number)

    return info, ad_id


def from_bn_flats_and_rooms(item, sell=True):
    try:
        info, ad_id = from_bn(item)

        object_type = get_node_value(item, 'type', True)
        if object_type == 'квартира':
            if sell:
                info['options_ipoteka'] = get_ipoteka(item)
            rooms_num = int(get_node_value(item, 'rooms-total', True))
            info['rooms_num'] = str(rooms_num)
        else:
            rooms_num = int(get_node_value(item, 'rooms-offer', True))
            info['rooms_num'] = str(0)

        info['floor_total'] = get_node_value(item, 'floors', True)
        info['floor'] = get_node_value(item, 'floor', True)

        area_living = get_node_value(item, 'living/value')
        info['area_living'] = area_living
        info['area_kitchen'] = get_node_value(item, 'kitchen/value')
        info['area_total'] = get_node_value(item, 'total/value', True)
        info['options_object_type'] = int(get_node_value(item, 'new-building')) + 1

        if area_living:
            info['area_rooms'] = get_rooms_areas(rooms_num, float(area_living))
        else:
            print('Fix this (area living is empty) for advert id: [{}]'.format(ad_id))

        return info

    except (EmptyRequiredFieldException, BlockedRecordException) as e:
        print(e)
        raise EmptyResult()


def from_bn_suburbians(item):
    try:
        info, _ = from_bn(item)

        deal_type = get_node_value(item, 'action', True)
        info['deal_type'] = DEAL_TYPE[deal_type]
        object_type = get_node_value(item, 'type', True)
        info['realty_type'] = REALTY_TYPE[object_type]

        info['area_region'] = get_node_value(item, 'lot/value', True)

        if object_type in ('дом', 'коттедж'):
            info['area_living'] = get_node_value(item, 'total/value', True)
            info['floor_total'] = get_node_value(item, 'floors')
            info['options_year'] = get_node_value(item, 'building/year')

        return info

    except (EmptyRequiredFieldException, BlockedRecordException) as e:
        print(e)
        raise EmptyResult()


def to_cian_flats_and_rooms(root_node, data):
    offer = etree.SubElement(root_node, 'offer')
    ad_id = etree.SubElement(offer, 'id')
    ad_id.text = data['ad_id']
    rooms_num = etree.SubElement(offer, 'rooms_num')
    rooms_num.text = data['rooms_num']
    area = etree.SubElement(offer, 'area', total=data['area_total'])
    if 'area_rooms' in data:
        area.set('rooms', data['area_rooms'])
    if 'area_living' in data:
        area.set('living', data['area_living'])
    if 'area_kitchen' in data:
        area.set('kitchen', data['area_kitchen'])
    price = etree.SubElement(offer, 'price', currency='RUB')
    price.text = data['price']
    floor = etree.SubElement(offer, 'floor', total=data['floor_total'])
    floor.text = data['floor']
    phone = etree.SubElement(offer, 'phone')
    phone.text = data['phone']
    etree.SubElement(offer, 'address', area='39', locality=data['address_locality'], street=data['address_street'])
    options = etree.SubElement(offer, 'options', object_type=str(data['options_object_type']))
    if 'options_ipoteka' in data:
        options.set('ipoteka', str(data['options_ipoteka']))
    note = etree.SubElement(offer, 'note')
    note.text = etree.CDATA(data['note'])
    for p in data['photo']:
        photo = etree.SubElement(offer, 'photo')
        photo.text = p


def to_cian_suburbians(root_node, data):
    offer = etree.SubElement(root_node, 'offer')
    ad_id = etree.SubElement(offer, 'id')
    ad_id.text = data['ad_id']
    deal_type = etree.SubElement(offer, 'deal_type')
    deal_type.text = data['deal_type']
    realty_type = etree.SubElement(offer, 'realty_type')
    realty_type.text = data['realty_type']
    area = etree.SubElement(offer, 'area', region=data['area_region'])
    if realty_type.text in ('дом', 'коттедж'):
        area.set('living', data['area_living'])
    land_type = etree.SubElement(offer, 'land_type')
    land_type.text = '2'
    price = etree.SubElement(offer, 'price', currency='RUB')
    price.text = data['price']
    phone = etree.SubElement(offer, 'phone')
    phone.text = data['phone']
    etree.SubElement(offer, 'address', area='39', locality=data['address_locality'], street=data['address_street'])
    if 'options_year' in data and data['options_year']:
        etree.SubElement(offer, 'options', year=data['options_year'])
    for p in data['photo']:
        photo = etree.SubElement(offer, 'photo')
        photo.text = p
    if 'floor_total' in data and data['floor_total']:
        floor_total = etree.SubElement(offer, 'floor_total')
        floor_total.text = data['floor_total']
    note = etree.SubElement(offer, 'note')
    note.text = etree.CDATA(data['note'])


doc = etree.parse('bncat.xml')
objects = doc.xpath('bn-object')
f = open('cian_new.xml', 'w+', encoding='utf-8')
flats_rooms_sales = [o for o in objects
                     if o.xpath('type[text() = "квартира" or text() = "комната"] and action[text() = "продажа"]')]
if len(flats_rooms_sales):
    root = etree.Element('flats_for_sale')
    for sale in flats_rooms_sales:
        try:
            to_cian_flats_and_rooms(root, from_bn_flats_and_rooms(sale))
        except EmptyResult:
            pass
    f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8').decode('utf-8'))
flats_rooms_rents = [o for o in objects
                     if o.xpath('type[text() = "квартира" or text() = "комната"] and action[text()="аренда"]')]
if len(flats_rooms_rents):
    root = etree.Element('flats_rent')
    for sale in flats_rooms_rents:
        try:
            to_cian_flats_and_rooms(root, from_bn_flats_and_rooms(sale))
        except EmptyResult:
            pass
    if len(flats_rooms_sales):
        f.write(etree.tostring(root, pretty_print=True, encoding='utf-8').decode('utf-8'))
    else:
        f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8').decode('utf-8'))
suburbians = [o for o in objects
              if o.xpath('type[text() = "дом" or text() = "коттедж" or text() = "участок"]')]
if len(suburbians):
    root = etree.Element('suburbian')
    for sale in suburbians:
        try:
            to_cian_suburbians(root, from_bn_suburbians(sale))
        except EmptyResult:
            pass
    if len(flats_rooms_sales) or len(flats_rooms_rents):
        f.write(etree.tostring(root, pretty_print=True, encoding='utf-8').decode('utf-8'))
    else:
        f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8').decode('utf-8'))
# commerce = [o for o in objects
#             if o.xpath('type[not(text() = "квартира" or text() = "комната" or '
#                        'text() = "коттедж" or contains(text(), "дом"))]')]
f.close()
