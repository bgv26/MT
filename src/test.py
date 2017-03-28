from lxml import etree
from enum import Enum

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
    PARCEL = 'A'
    TOWNHOUSE = 'T'


class LandType(Enum):
    SNT = 1
    IGS = 2
    PROM = 3
    FARM = 4
    DNP = 5
    INVEST = 6


def to_cian(ad_type):
    root = etree.Element(ad_type)
    offer = etree.SubElement(root, 'offer')
    ad_id = etree.SubElement(offer, 'id')

    if ad_type == 'commerce':  # for commerce only
        commerce_type = etree.SubElement(offer, 'commerce_type')
        contract_type = etree.SubElement(offer, 'contract_type')
        building = etree.SubElement(offer, 'building')
        building_dict = building.attrib
        building_dict['floor'] = ''
        building_dict['floor_total'] = ''
        business_shopping_center = etree.SubElement(offer, 'business_shopping_center')

    if ad_type.startswith('flats'):  # for rent and sale
        rooms_num = etree.SubElement(offer, 'rooms_num')
        floor = etree.SubElement(offer, 'floor')
        floor_dict = floor.attrib
        floor_dict['total'] = ''
        composition = etree.SubElement(offer, 'composition')

    if ad_type == 'suburbian':  # for suburbian only
        deal_type = etree.SubElement(offer, 'deal_type')
        realty_type = etree.SubElement(offer, 'realty_type')
        land_type = etree.SubElement(offer, 'land_type')
        floor_total = etree.SubElement(offer, 'floor_total')
        bedroom_total = etree.SubElement(offer, 'bedroom_total')

    area = etree.SubElement(offer, 'area')
    area_dict = area.attrib
    if ad_type == 'suburbian':
        area_dict['region'] = ''
        area_dict['living'] = ''
    else:
        area_dict['total'] = ''

    price = etree.SubElement(offer, 'price')
    phone = etree.SubElement(offer, 'phone')
    address = etree.SubElement(offer, 'address')
    address_dict = address.attrib
    address_dict['admin_area'] = str(39)
    address_dict['locality'] = ''
    address_dict['street'] = ''

    note = etree.SubElement(offer, 'note')
    options = etree.SubElement(offer, 'options')
    com = etree.SubElement(offer, 'com')
    photo = etree.SubElement(offer, 'photo')
    promotions = etree.SubElement(offer, 'promotions')
    special_offer_id = etree.SubElement(offer, 'special_offer_id')
    if ad_type == 'flats_for_sale':  # for sale only
        residential_complex = etree.SubElement(offer, 'residential_complex')
        project_declaration = etree.SubElement(offer, 'project_declaration')
    return root


def gen_new_id(text):
    return ID_PREFIX + text[4:]


def get_node_value(parent, node):
    return parent.xpath(node).pop().text.strip()


def is_block(text):
    for block in BLOCK_PHRASES:
        if block in text:
            return True
    return False


def get_city_by_place(text):
    for key, value in LOCATIONS.items():
        if text in value:
            return key
    return ''


def get_lot_number(text):
    # symbols from 4 length 5 + '-8' + char value from three last digits in text
    return text[4:9] + '-8' + bytes([int(text[9:])]).decode('cp1251')

def from_bn(item):
    info = dict()
    ad_id = get_node_value(item, 'id')
    info['ad_id'] = gen_new_id(ad_id)
    lot_number = get_lot_number(ad_id)
    info['rooms_num'] = get_node_value(item, 'rooms-total')
    info['floor-total'] = get_node_value(item, 'floors')
    info['floor'] = get_node_value(item, 'floor')

    description = get_node_value(item, 'description/full')
    if is_block(description):
        print('Blocked: [{}]'.format(description))
        return

    place = get_node_value(item, 'locality/place')
    city = get_node_value(item, 'location/city')
    street = get_node_value(item, 'locality/street')
    if get_city_by_place(place) == '' and get_city_by_place(street) == '' and city != '':
        print('Fix this:[{}]'.format(place))

    info['address-locality'] = city
    info['address-street'] = street


doc = etree.parse('format_new.xml')
objects = doc.xpath('bn-object')

sales = [o for o in objects
         if o.xpath('type[text() = "квартира" or text() = "комната"] and action[text() = "продажа"]')]
print(len(sales))
rents = [o for o in objects
         if o.xpath('type[text() = "квартира" or text() = "комната"] and action[text()="аренда"]')]
print(len(rents))
suburbians = [o for o in objects
              if o.xpath('type[text() = "коттедж" or contains(text(), "дом")]')]
print(len(suburbians))
commerce = [o for o in objects
            if o.xpath('type[not(text() = "квартира" or text() = "комната" or '
                       'text() = "коттедж" or contains(text(), "дом"))]')]
print(len(commerce))
# objects = doc.xpath('bn-object/action [text()="продажа"]')
# for obj in objects:
#     info = dict()
#     info['ad_id'] = obj.xpath('id').pop().text
#     obj_type = obj.xpath('type').pop().text
#     obj_action = obj.xpath('action').pop().text
#     if obj_type in ('квартира', 'комната'):
#         if obj_action == 'аренда':
#             info['ad_type'] = AdType.RENT.value
#         if  obj_action == 'продажа':
#             info['ad_type'] = AdType.SALE.value
#
#     obj_url = obj.xpath('url').pop().text
#     obj_location_area = obj.xpath('location/area').pop().text
#     obj_location_city = obj.xpath('location/city').pop().text
#     obj_location_ctar = obj.xpath('location/ctar').pop().text
#     obj_location_district = obj.xpath('location/district').pop().text
#     obj_location_place = obj.xpath('location/place').pop().text
#     obj_location_street = obj.xpath('location/street').pop().text
#     obj_location_house = obj.xpath('location/house').pop().text
#     obj_location_address = obj.xpath('location/address').pop().text
#     obj_price_value = obj.xpath('price/value').pop().text
#     obj_price_currency = obj.xpath('price/currency').pop().text
#     obj_price_period = obj.xpath('price/period').pop().text
#     obj_price_unit = obj.xpath('price/unit').pop().text
#     obj_add_terms = obj.xpath('price/additional-terms')
#     for term in obj_add_terms:
#         if part
#     if obj_type in ('квартира', 'комната'):


# print(etree.tostring(doc, pretty_print=True, xml_declaration=True, encoding="utf-8"))
# print(etree.tostring(to_cian(AdType.RENT.value), pretty_print=True, xml_declaration=True, encoding="utf-8"))
