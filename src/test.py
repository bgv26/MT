from lxml import etree
from enum import Enum


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


class SaleTypeSecond(Enum):
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



print(etree.tostring(to_cian(AdType.RENT.value), pretty_print=True, xml_declaration=True, encoding="utf-8"))
