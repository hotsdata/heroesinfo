__author__ = 'Cristian Orellana <crorella@gmail.com>'

import xml.etree.ElementTree as ET
from os import path
import json
import psycopg2ct as pg
import re

BASE_FILES = {"gamestrings": "mods/heroesdata.stormmod/enus.stormdata/LocalizedData/GameStrings.txt",
              "buttondata": "mods/heroesdata.stormmod/base.stormdata/GameData/ButtonData.xml",
              "herodata": "mods/heroesdata.stormmod/base.stormdata/GameData/HeroData.xml",
              "talentdata": "mods/heroesdata.stormmod/base.stormdata/GameData/TalentData.xml",
              "patchdata": "mods/core.stormmod/base.stormdata/DataBuildId.txt"}
HERO_NAMES_FILE = "heroesNames.txt"
PATH = "/Users/crorella/Documents/heroesjson/out/"
HERO_FILES_BASE_PATH = "mods/heroesdata.stormmod/base.stormdata/GameData/Heroes/"
HERO_FILES_ALTERNATE_PATH = "mods/heromods/"
STRING_FILES_ALTERNATE_PATH = "mods/heromods/"
HERO_SPECIFIC_FILES = [
     "ThrallData",
     "AnubarakData",
     "WizardData",
     "WitchDoctorData",
     "UtherData",
     "TinkerData",
     "SylvanasData",
     "StitchesData",
     "RexxarData",
     "NecromancerData",
     "MurkyData",
     "MonkData",
     "MedicData",
     "LostVikingsData",
     "LeoricData",
     "KaelthasData",
     "JainaData",
     "GennData",
     "DryadData",
     "DemonHunterData",
     "CrusaderData",
     "ChenData",
     "ButcherData",
     "AzmodanData",
     "ArtanisData",
     "TassadarData",
     "DiabloData",
     "ZeratulData",
     "ZagaraData",
     "SgtHammerData"
   ]



ALTERNATE_HERO_SPECIFIC_FILES = [
     "thefirelords",
     "zuljin",
     "zarya",
     "varian",
     "valeera",
     "tracer",
     "samuro",
     "probius",
     "medivh",
     "lucio",
     "guldan",
     "dva",
     "dehaka",
     "chromie",
     "chogall",
     "auriel",
     "amazon",
     "alarak",
     "genji",
     "malthael",
    "kelthuzad",
    ]



data = ET.parse(path.join(PATH, BASE_FILES["herodata"]))
icons = ET.parse(path.join(PATH, BASE_FILES["buttondata"]))
names = open(path.join(PATH, BASE_FILES["gamestrings"]))
talent_names = {}
talents = {}
hero_data = {}
patch = None
hero_names = {}


# Get hero names
# with file(path.join(PATH, HERO_NAMES_FILE)) as hero_names_file:
#     build_regex = '([a-zA-Z]+)=([\w\W\'\.\-]+)'
#     for line in hero_names_file:
#         build = re.search(build_regex, line)
#         if build:
#             id = build.group(1)
#             name = build.group(2)
#             hero_names[id] = name
#             #print "%s - %s" % (id, name)

# Get build

with file(path.join(PATH, BASE_FILES['patchdata'])) as build_data:
    build_regex = '[a-zA-Z]+(\d+)'
    for line in build_data:
        build = re.search(build_regex, line)
        patch = build.group(1)
        print "Processing patch: %s" % patch


def get_button_names():
    for name in names:
        if name.startswith('Button/Name/'):
            talent_names[name.split('/')[2].split('=')[0].strip()] = name.split('=')[1].strip()


def get_button_names_heroes(hero):
    with file(path.join(PATH, STRING_FILES_ALTERNATE_PATH, hero + ".stormmod/enus.stormdata/LocalizedData/GameStrings.txt")) as strings:
        for name in strings:
            if name.startswith('Button/Name/'):
                talent_names[name.split('/')[2].split('=')[0].strip()] = name.split('=')[1].strip()


def find_talent_id_by_face(face, hero=None):
    found_talents = []
    for t in talents:
        if face in talents[t]['face']:
            found_talents.append(t)

    return found_talents


def get_talents(hero_root, hero=None):
    heroes = hero_root.findall('CHero')
    # Get talents for those heroes with specific data files
    for h in heroes:
        if h is not None:
            for talent_tree in h.findall('TalentTreeArray'):
                if talent_tree.attrib.get('Talent') not in talents:
                    hero_name = h.attrib.get('Id', None) or h.attrib.get('id', None)
                    talents[talent_tree.attrib.get('Talent')] = {}
                    talents[talent_tree.attrib.get('Talent')][hero_name] = {}
                if h.find('HyperlinkId') is not None:
                    hero_name = h.find('HyperlinkId').attrib.get('value', None)
                else:
                    hero_name = h.attrib.get('Id', None) or h.attrib.get('id', None)
                #print "Assigning %s to %s" % (hero_name, talent_tree.attrib.get('Talent'))
                if hero_name not in talents[talent_tree.attrib.get('Talent')].keys():
                    if len([k for k in talents[talent_tree.attrib.get('Talent')].keys() if k not in ['face', 'icon', 'name']]) == 0:
                        talents[talent_tree.attrib.get('Talent')] = {}
                    talents[talent_tree.attrib.get('Talent')][hero_name] = {}
                talents[talent_tree.attrib.get('Talent')][hero_name]['tier'] = talent_tree.attrib.get('Tier')
                talents[talent_tree.attrib.get('Talent')][hero_name]['column'] = talent_tree.attrib.get('Column')
                talents[talent_tree.attrib.get('Talent')]['face'] = talents[talent_tree.attrib.get('Talent')].get('face', '')

        if hero == 'Alarak':
            for talent_tree in h.findall('TalentTreeArray'):
                if talent_tree.attrib.get('Talent') not in talents or talents[talent_tree.attrib.get('Talent')].get('tier', None) is None:
                    talents[talent_tree.attrib.get('Talent')]['Alarak']['tier'] = talent_tree.attrib.get('Tier')
                    talents[talent_tree.attrib.get('Talent')]['Alarak']['column'] = talent_tree.attrib.get('Column')


def get_talents_faces(hero_root):
    """
    This function retrieves the 'faces' used by the button in the talent selection UI.
    The face is then used to lookup the icon file displayed in the button
    :param hero_root: 
    :return: 
    """
    for talent in hero_root.findall('CTalent'):
        if talent.attrib.get('id') is not None:
            id = talent.attrib.get('id')
            if id not in talents.keys():
                talents[id] = {}
            if talent.find('Face') is not None:
                talents[id]['face'] = talent.find('Face').attrib.get('value', 'NA')


def get_talent_icons(hero_root):
    """
    This function looks for the Buttons associated with the hero and retrieves the icons for those buttons
    used to display talent selection
    :param hero_root: 
    :return: 
    """
    # Some buttons are stored directly in the heroData.xml file, while others in the ButtonData.xml file
    # This for loop is for the buttons stored in the same heroData file
    for button in hero_root.findall('CButton'):
        if button.attrib.get('id') is not None:
            face = button.attrib.get('id')
            if button.find('Icon') is not None:
                found_talents = find_talent_id_by_face(face)
                for t in found_talents:
                    icon = button.find('Icon').attrib.get('value', 'NA').split('\\')[-1].split('.')[0].lower()
                    talents[t]['icon'] = icon + '.png'

    # This for loop is for the buttons stored in the buttonData file
    for icon in icons.findall('CButton'):
        if icon.attrib.get('id') is not None:
            face = icon.attrib.get('id')
            if icon.find('Icon') is not None:
                found_talents = find_talent_id_by_face(face)
                for t in found_talents:
                    icon_image = icon.find('Icon').attrib.get('value', 'NA').split('\\')[-1].split('.')[0].lower()
                    talents[t]['icon'] = icon_image + '.png'


def get_hero_info(hero_root):
    """
    This function retrieves specific hero data, like universe, gender, difficulty, names, and so on.
    :param hero_root: 
    :return: 
    """
    for hero_info in hero_root.findall('CHero'):
        friendly_name = None
        hero_data[hero_info.attrib.get('id', 'Missing')] = {}
        for attribute in ['Role', 'Universe', 'Alignment', 'Rarity', 'SelectScreenButtonImage', 'Gender',
                          'Difficulty', 'AttributeId']:
            if hero_info.find(attribute) is not None:
                hero_data[hero_info.attrib.get('id', 'Missing')][attribute] = hero_info.find(attribute).attrib.get(
                    'value', 'Missing')

        if hero_info.find('Ratings') is not None:
            # print "\tRatings:"
            for rating in ['Damage', 'Utility', 'Complexity', 'Survivability']:
                if hero_info.find('Ratings').attrib.get(rating):
                    hero_data[hero_info.attrib.get('id', 'Missing')][rating] = hero_info.find('Ratings').attrib.get(
                        rating, 'NA')
                elif hero_info.find('Ratings').find(rating) is not None:
                    hero_data[hero_info.attrib.get('id', 'Missing')][rating] = hero_info.find('Ratings').find(
                        rating).attrib.get('value', 'NA')
        if hero_info.find('HyperlinkId') is not None:
            friendly_name = hero_info.find('HyperlinkId').attrib.get('value', None)
        hero_data[hero_info.attrib.get('id', 'Missing')]['friendly_name'] = friendly_name or hero_info.attrib.get(
            'id', 'Missing')


def get_talent_names():
    for name in talent_names:
        found_talents = find_talent_id_by_face(name)
        for t in found_talents:
            talents[t]['name'] = talent_names[name]


def clean_unassigned_talents():
    for talent in talents:
        for hero in [k for k in talents[talent] if k not in ['face', 'icon', 'name']]:
            if 'tier' not in talents[talent][hero].keys():
                del talents[talent][hero]
            #print talents[t]


def validate_talents():
    incomplete_talents = []
    for talent in talents:
        if (talents[talent].get('icon', None) is None \
                and talents[talent].get('hero', None) is None \
                and talents[talent].get('column', None) is None \
                and talents[talent].get('tier', None) is None) \
                or talents[talent].get('face', None) is None \
                or talents[talent].get('name', None) is None:
            incomplete_talents.append(talents[talent])
    try:
        assert len(incomplete_talents) == 0
    except AssertionError, e:
        print "Error, there are %s incomplete talents:" % len(incomplete_talents)
        for talent in incomplete_talents:
            print "\t%s" % talent


# Get hero data to retrieve talent names and icons
def get_hero_data():

    # get hero info for the "Classic" heroes
    hero_root = data.getroot()
    # Get talents for those heroes with specific data files
    get_talents(hero_root)
    # Get talent faces for heroes with specific data files
    get_talents_faces(hero_root)
    # Get talent icons for heroes with specific data files
    get_talent_icons(hero_root)
    get_hero_info(hero_root)


    # First of all, get all the talents in the talentdata.xml file
    heroData = ET.parse(path.join(PATH, BASE_FILES['talentdata']))
    hero_root = heroData.getroot()
    get_talents_faces(hero_root)
    get_talent_icons(hero_root)

    for hero in [h for h in ALTERNATE_HERO_SPECIFIC_FILES if h == 'alarak']:
        # alarak.stormmod / base.stormdata / GameData / AlarakData.xml
        heroData = ET.parse(path.join(PATH, HERO_FILES_ALTERNATE_PATH, hero + ".stormmod", "base.stormdata/GameData/HeroData.xml"))
        hero_root = heroData.getroot()
        # Get talents for those heroes with specific data files
        get_talents(hero_root, 'Alarak')
        # Get talent faces for heroes with specific data files
        get_talents_faces(hero_root)
        # Get talent icons for heroes with specific data files
        get_talent_icons(hero_root)
        get_hero_info(hero_root)

    # then get info for those heroes with a special heroData.xml file
    for hero in HERO_SPECIFIC_FILES:
        heroData = ET.parse(path.join(PATH, HERO_FILES_BASE_PATH, hero, hero + ".xml"))
        hero_root = heroData.getroot()
        h = hero_root.find('CHero')
        # Get talents for those heroes with specific data files5
        get_talents(hero_root)
        # Get talent faces for heroes with specific data files
        get_talents_faces(hero_root)
        # Get talent icons for heroes with specific data files
        get_talent_icons(hero_root)
        # Get hero info
        get_hero_info(hero_root)


    # Then, get info for heroes in the new heromod folder structure
    for hero in ALTERNATE_HERO_SPECIFIC_FILES:
        # populate the talent names
        get_button_names_heroes(hero)

        heroData = ET.parse(path.join(PATH, HERO_FILES_ALTERNATE_PATH, hero + ".stormmod", "base.stormdata/GameData/", hero + "Data.xml"))
        hero_root = heroData.getroot()
        h = hero_root.find('CHero')
        # Get talents for those heroes with specific data files
        get_talents(hero_root)
        # Get talent faces for heroes with specific data files
        get_talents_faces(hero_root)
        # Get talent icons for heroes with specific data files
        get_talent_icons(hero_root)
        get_hero_info(hero_root)

    # Do a final pass to retrieve icons for those heroes where the talent data is
    # distributed between HeroData.xml and TalentData.xml
    for icon in icons.findall('CButton'):
        if icon.attrib.get('id') is not None:
            face = icon.attrib.get('id')

            if icon.find('Icon') is not None:
                found_talents = find_talent_id_by_face(face)
                for t in found_talents:
                    icon_image = icon.find('Icon').attrib.get('value', 'NA').split('\\')[-1].split('.')[0].lower()
                    talents[t]['icon'] = icon_image + '.png'


def save_files():
    with file("heroes.json", "w") as heroes_file:
        json.dump(hero_data, heroes_file)

    with file("talents.json", "w") as talents_file:
        json.dump(talents, talents_file)


# move the data to the database
def save_to_db():
    try:
        rConn = pg.connect(database="hotstats",
                           user="hotstats",
                           password="YOUR_PASS",
                           host="YOUR_SERVER",
                           port="5432")
        cursor = rConn.cursor()
        rConn.autocommit = True
    except Exception, e:
        print "Error while trying to establish connection with database %s" % e

    insert_hero = """
        INSERT INTO heroes (
            id,
            patch,
            name,
            role,
            universe,
            alignment,
            rarity,
            portrait_icon,
            gender,
            difficulty,
            damage,
            utility,
            complexity,
            survivability,
            attrib_name
            )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT hero_pk DO UPDATE SET
            role = excluded.role,
            universe = excluded.universe,
            alignment = excluded.alignment,
            rarity = excluded.rarity,
            portrait_icon = excluded.portrait_icon,
            gender = excluded.gender,
            difficulty = excluded.difficulty,
            damage = excluded.damage,
            utility = excluded.utility,
            complexity = excluded.complexity,
            survivability = excluded.survivability,
            attrib_name = excluded.attrib_name;
        """

    insert_talent = """
        INSERT INTO talents (
            id,
            patch,
            name,
            hero,
            tier,
            position,
            icon
            )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT talents_pk DO UPDATE SET
            name = excluded.name,
            tier = excluded.tier,
            position = excluded.position,
            icon = excluded.icon
        """

    for hero in hero_data:
        cursor.execute(insert_hero, [hero,
                                     patch,
                                     hero_data[hero]['friendly_name'],
                                     hero_data[hero].get('Role'),
                                     hero_data[hero].get('Universe'),
                                     hero_data[hero].get('Alignment'),
                                     hero_data[hero].get('Rarity'),
                                     hero_data[hero].get('SelectScreenButtonImage'),
                                     hero_data[hero].get('Gender'),
                                     hero_data[hero].get('Difficulty'),
                                     hero_data[hero].get('Damage', 0),
                                     hero_data[hero].get('Utility', 0),
                                     hero_data[hero].get('Complexity', 0),
                                     hero_data[hero].get('Survivability', 0),
                                     hero_data[hero].get('AttributeId', '').lower()])

    insert_talent_statements = []
    for talent in talents:
        for hero in [k for k in talents[talent] if k not in ['face', 'icon', 'name']]:
            cursor.execute(insert_talent, [talent,
                                         patch,
                                         talents[talent].get('name'),
                                         hero,
                                         talents[talent][hero]['tier'],
                                         talents[talent][hero]['column'],
                                         talents[talent].get('icon')])

if __name__ == "__main__":
    get_button_names()
    get_hero_data()
    get_talent_names()
    clean_unassigned_talents()
    #validate_talents()
    save_to_db()
