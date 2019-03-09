import sqlite3
import re
import os
import traceback
import json
import sys
import hashlib

DATABASE_FILENAME = 'C:\Program Files (x86)\Steam\steamapps\common\My Time At Portia\Portia_Data\StreamingAssets\CccData\LocalDb.bytes'

CACHED_PROPS = None
CACHED_GIFTS = None
CACHED_FOOD_MENU = None
CACHED_DATE_DIALOG = None
CACHED_GIFT_TAGS = None
CACHED_GIFT_TAGS_NOTRAN = None
CACHED_RECYCLE_TAGS = None

CACHED_QUERIES = {}


def md5_hash(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def load_cache(current_hash):
    global CACHED_QUERIES
    try:
        if os.path.isfile('cached_queries.json'):
            with open('cached_queries.json') as f:
                CACHED_QUERIES = json.load(f)
            previous_hash = CACHED_QUERIES['hash']
            if current_hash != previous_hash:
                print('LOCALDB CHANGED, DELETING CACHE. THIS NEXT RUN WILL BE SLOW BECAUSE THE CACHE NEEDS TO BE REPOPULATED.')
                CACHED_QUERIES = {}
    except Exception:
        print('Failed to load cache file, creating new cache. Error:\n{}'.format(traceback.format_exc()))
        CACHED_QUERIES = {}


def write_cache(current_hash):
    print('Saving query cache, DO NOT EXIT')
    global CACHED_QUERIES
    CACHED_QUERIES['hash'] = current_hash
    with open('cached_queries.json', 'w') as f:
        json.dump(CACHED_QUERIES, f)
    print('Finished saving query cache')


def do_query(query, connection):
    global CACHED_QUERIES
    if query not in CACHED_QUERIES:
        cursor = connection.cursor()
        cursor.execute(query)
        CACHED_QUERIES[query] = []
        for result in cursor:
            CACHED_QUERIES[query].append(result)
    return CACHED_QUERIES[query]


def props_gift_lookup(gift_tagid, connection, gift_id, like_type=None):
    global CACHED_GIFT_TAGS_NOTRAN
    global CACHED_PROPS

    if like_type is not None:
        query = 'SELECT Favor_{} from Gift where Gift_ID="{}"'.format(like_type, gift_id)
        results = do_query(query, connection)
        assert len(results) == 1

        if CACHED_GIFT_TAGS_NOTRAN is None:
            CACHED_GIFT_TAGS_NOTRAN = find_associations('Props_total_table', 'Tag_List', ',',
                                                        ('props_name', None), {}, connection, ignore_multipliers=True)
            CACHED_GIFT_TAGS_NOTRAN = {x: y.split('\n') for x, y in CACHED_GIFT_TAGS_NOTRAN[0]}

        base_value, exceptions_str = results[0]['favor_{}'.format(like_type.lower())].split('|')
        exceptions = {}
        if exceptions_str.strip() != '':
            for exception in exceptions_str.split('$'):
                tag, value = exception.split('_')
                exceptions[tag] = value

    gift_tagid = gift_tagid.split(';')[0]

    if CACHED_PROPS is None:
        CACHED_PROPS = do_query('SELECT props_name, gift_tagid FROM props_total_table', connection)
    all_gifts = []
    for result in CACHED_PROPS:
        if str(gift_tagid) in result['gift_tagid'].split(','):
            prop_name = result['props_name']
            if like_type is not None:
                special_value = None
                for tag, value in exceptions.items():
                    if prop_name in CACHED_GIFT_TAGS_NOTRAN.get(tag, []):
                        special_value = value
                if special_value is None:
                    actual_value = base_value
                else:
                    actual_value = special_value
                all_gifts.append(do_lookup('Translation_hint', prop_name, '<str>id', 'English',
                                           None, connection, {}).strip() + ' ({})'.format(actual_value))
            else:
                all_gifts.append(do_lookup('Translation_hint', prop_name, '<str>id', 'English',
                                           None, connection, {}).strip())

    if len(all_gifts) == 0:
        return 'No gifts for Gift_TagID {}'.format(gift_tagid)
    return ', '.join(all_gifts)


def find_associations(table, column, split_char, name_mapping, tag_names, connection, ignore_multipliers=False):
    column = column.lower()
    name_column = name_mapping[0].lower()
    options = name_mapping[2] if len(name_mapping) > 2 and name_mapping[2] is not None else {}

    all_results = do_query('SELECT {}, {} FROM {}'.format(name_column, column, table), connection)

    all_values = []
    for result in all_results:
        for value in result[column].split(split_char):
            if value not in all_values:
                all_values.append(value)
    mappings = {}
    cached_lookups = {}
    for value in all_values:
        for result in all_results:
            if value in result[column].split(split_char):
                result_conversion = name_mapping[1]
                looked_up_value = result[name_column]
                if looked_up_value not in cached_lookups:
                    if result_conversion is not None:
                        if callable(result_conversion):
                            looked_up_value = result_conversion(result[name_column], connection)
                        elif isinstance(result_conversion, tuple):
                            looked_up_value = do_lookup(
                                result_conversion[1], looked_up_value, result_conversion[0], result_conversion[2], result_conversion[3], connection, options)
                        elif isinstance(result_conversion, list):
                            for conversion in result_conversion:
                                looked_up_value = do_lookup(conversion[1], looked_up_value,
                                                            conversion[0], conversion[2], conversion[3], connection, options)
                                if 'returned no results' not in looked_up_value:
                                    break
                        else:
                            raise Exception('Invalid value of result_conversion: {}'.format(result_conversion))
                    cached_lookups[result[name_column]] = looked_up_value
                if value not in mappings:
                    mappings[value] = []
                mappings[value].append(cached_lookups[result[name_column]])
    extracted = []
    all_ints = True
    for key in mappings.keys():
        if key == '':
            key = '<empty>'
        try:
            int(key)
        except Exception:
            all_ints = False
    for key, values in mappings.items():
        new_values = {}
        for value in values:
            if value not in new_values:
                new_values[value] = 1
            else:
                new_values[value] += 1
        quantified_values = []
        for value, quantity in new_values.items():
            if value == '':
                value = '(empty)'
            if quantity == 1 or ignore_multipliers:
                quantified_values.append(value)
            else:
                quantified_values.append('{} x{}'.format(value, quantity))
        if all_ints:
            key = int(key)
        extracted.append((key, '\n'.join(sorted(quantified_values, key=lambda x: x.lower()))))
    if all_ints:
        extracted.sort()
        extracted = [(tag_names.get(x, x), y) for x, y in extracted]
        extracted = [(str(x), y) for x, y in extracted]
    else:
        extracted.sort(key=lambda x: x[0].lower())
        extracted = [(tag_names.get(x, x), y) for x, y in extracted]

    return [extracted]


def find_npc_from_gift_tagid(gift_tagid, connection):
    global CACHED_GIFTS
    if CACHED_GIFTS is None:
        CACHED_GIFTS = do_query('SELECT Gift_ID, TagID_Excellent, TagID_Like, TagID_Dislike, TagID_Hate, TagID_Confession, '
                                'TagID_Propose, TagID_Refuse, TagID_Breakup, TagID_Divorce, TagID_Jealous, TagID_MarriageCall FROM Gift', connection)
    qualifier = None
    for result in CACHED_GIFTS:
        if gift_tagid in result['tagid_excellent'].split(';'):
            qualifier = 'Excellent'
            break
        elif gift_tagid in result['tagid_like'].split(';'):
            qualifier = 'Like'
            break
        elif gift_tagid in result['tagid_dislike'].split(';'):
            qualifier = 'Dislike'
            break
        elif gift_tagid in result['tagid_hate'].split(';'):
            qualifier = 'Hate'
            break
        elif gift_tagid in result['tagid_confession'].split(';'):
            qualifier = 'Confession'
            break
        elif gift_tagid in result['tagid_propose'].split(';'):
            qualifier = 'Propose'
            break
        elif gift_tagid in result['tagid_refuse'].split(';'):
            qualifier = 'Refuse'
            break
        elif gift_tagid in result['tagid_breakup'].split(';'):
            qualifier = 'Breakup'
            break
        elif gift_tagid in result['tagid_divorce'].split(';'):
            qualifier = 'Divorce'
            break
        elif gift_tagid in result['tagid_jealous'].split(';'):
            qualifier = 'Jealous'
            break
        elif gift_tagid in result['tagid_marriagecall'].split(';'):
            qualifier = 'Marriage Call'
            break

    if qualifier is None:
        return 'No Gift found with tagid {}'.format(gift_tagid)
    npc_name = do_lookup('NPCRepository', result['gift_id'], '<str>GiftID', 'Name', Lookup.TRANSLATION, connection, {'allow_multiple_lookup_results': True,
                                                                                                                     'multiple_lookup_results_join_char': ', '})
    return '{} ({})'.format(npc_name, qualifier)


def foodtag_lookup(tags, connection):
    global CACHED_FOOD_MENU
    if CACHED_FOOD_MENU is None:
        CACHED_FOOD_MENU = do_query('SELECT Food_Name, Food_Tag FROM Food_Menu', connection)
    foods = []
    for tag in tags.split(','):
        for result in CACHED_FOOD_MENU:
            if tag in result['food_tag'].split(','):
                foods.append(do_lookup('Translation_hint', result['food_name'],
                                       '<str>id', 'English', None, connection, {}))
    return '\n'.join(foods)


class Lookup(object):
    TRANSLATION = ('<str>id', 'Translation_hint', 'English', None)
    PROP = ('<str>Props_Id', 'Props_total_table', 'Props_Name', TRANSLATION)
    REPOSITORY = ('<str>Id', 'NPCRepository', 'Name', TRANSLATION)
    CONVERSATION_BASE = ('<str>baseid', 'Conversation_Base', 'TranslationID', TRANSLATION)
    CONVERSATION_SEGMENT_BASE = ('<str>SegmentID', 'Conversation_Segment', 'BaseID', lambda x, connection: '\n'.join([do_lookup(
        'Conversation_Base', split_val, '<str>BaseId', 'TranslationID', Lookup.TRANSLATION, connection, {}) for split_val in (x.split(',') if ',' in x else x.split(';'))]))
    EXHIBIT_SIZE = ('<str>size', 'ExhibitSize', 'name', TRANSLATION)
    EXHIBIT_TYPE_NAME = ('<str>type', 'ExhibitType', 'name', TRANSLATION)
    EXHIBIT_TYPE_DESCRIPTION = ('<str>type', 'ExhibitType', 'description', TRANSLATION)
    EXHIBIT_DATA_SIZE = ('<str>itemId', 'ExhibitData', 'size', EXHIBIT_SIZE)
    EXHIBIT_DATA_TYPE = ('<str>itemId', 'ExhibitData', 'type', EXHIBIT_TYPE_NAME)
    DATE_DIALOG_CONFESS_ACCEPT = ('<str>Date_DialogID', 'Date_Dialog', 'Confess_Accept', lambda val, connection: '\n'.join([do_lookup(
        'Conversation_Base', v, '<str>baseid', 'TranslationID', Lookup.TRANSLATION, connection, {}) for v in val.split(';')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_CONFESS_REFUSE = ('<str>Date_DialogID', 'Date_Dialog', 'Confess_Refuse', lambda val, connection: '\n'.join([do_lookup(
        'Conversation_Base', v, '<str>baseid', 'TranslationID', Lookup.TRANSLATION, connection, {}) for v in val.split(';')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_CONFESS_LACKITEM = ('<str>Date_DialogID', 'Date_Dialog', 'Confess_LackItem', lambda val, connection: '\n'.join([do_lookup(
        'Conversation_Base', v, '<str>baseid', 'TranslationID', Lookup.TRANSLATION, connection, {}) for v in val.split(';')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_BREAKUP = ('<str>Date_DialogID', 'Date_Dialog', 'BreakUp', lambda val, connection: '\n'.join([do_lookup(
        'Conversation_Base', v, '<str>baseid', 'TranslationID', Lookup.TRANSLATION, connection, {}) for v in val.split(';')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PROPOSE_ACCEPT = ('<str>Date_DialogID', 'Date_Dialog', 'Propose_Accept', lambda val, connection: '\n'.join([do_lookup(
        'Conversation_Base', v, '<str>baseid', 'TranslationID', Lookup.TRANSLATION, connection, {}) for v in val.split(';')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PROPOSE_REFUSE = ('<str>Date_DialogID', 'Date_Dialog', 'Propose_Refuse', lambda val, connection: '\n'.join([do_lookup(
        'Conversation_Base', v, '<str>baseid', 'TranslationID', Lookup.TRANSLATION, connection, {}) for v in val.split(';')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PROPOSE_LACKITEM = ('<str>Date_DialogID', 'Date_Dialog', 'Propose_LackItem', lambda val, connection: '\n'.join([do_lookup(
        'Conversation_Base', v, '<str>baseid', 'TranslationID', Lookup.TRANSLATION, connection, {}) for v in val.split(';')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PLAY_START = ('<str>Date_DialogID', 'Date_Dialog', 'Play_Start', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PLAY_MISSEDCONTRACT = ('<str>Date_DialogID', 'Date_Dialog', 'Play_MissedContract', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PLAY_GIVEUP_HAPPY = ('<str>Date_DialogID', 'Date_Dialog', 'Play_Giveup_Happy', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PLAY_GIVEUP_UNHAPPY = ('<str>Date_DialogID', 'Date_Dialog', 'Play_Giveup_UnHappy', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PLAY_ACTIONVALUE_HAPPY = ('<str>Date_DialogID', 'Date_Dialog', 'Play_ActionValue_Happy', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PLAY_ACTIONVALUE_UNHAPPY = ('<str>Date_DialogID', 'Date_Dialog', 'Play_ActionValue_UnHappy', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PLAY_TIMEOUT_HAPPY = ('<str>Date_DialogID', 'Date_Dialog', 'Play_TimeOut_Happy', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PLAY_TIMEOUT_UNHAPPY = ('<str>Date_DialogID', 'Date_Dialog', 'Play_TimeOut_UnHappy', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PLAY_MOODVALUE = ('<str>Date_DialogID', 'Date_Dialog', 'Play_MoodValue', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PLAY_JEALOUS = ('<str>Date_DialogID', 'Date_Dialog', 'Play_Jealous', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_PLAY_INTERRUPT = ('<str>Date_DialogID', 'Date_Dialog', 'Play_Interrupt', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_DATE_START = ('<str>Date_DialogID', 'Date_Dialog', 'Date_Start', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_DATE_MISSEDCONTRACT = ('<str>Date_DialogID', 'Date_Dialog', 'Date_MissedContract', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_DATE_GIVEUP_HAPPY = ('<str>Date_DialogID', 'Date_Dialog', 'Date_Giveup_Happy', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_DATE_GIVEUP_UNHAPPY = ('<str>Date_DialogID', 'Date_Dialog', 'Date_Giveup_UnHappy', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_DATE_ACTIONVALUE_HAPPY = ('<str>Date_DialogID', 'Date_Dialog', 'Date_ActionValue_Happy', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_DATE_ACTIONVALUE_UNHAPPY = ('<str>Date_DialogID', 'Date_Dialog', 'Date_ActionValue_UnHappy', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_DATE_TIMEOUT_HAPPY = ('<str>Date_DialogID', 'Date_Dialog', 'Date_TimeOut_Happy', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_DATE_TIMEOUT_UNHAPPY = ('<str>Date_DialogID', 'Date_Dialog', 'Date_TimeOut_UnHappy', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_DATE_MOODVALUE = ('<str>Date_DialogID', 'Date_Dialog', 'Date_MoodValue', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_DATE_INTERRUPT = ('<str>Date_DialogID', 'Date_Dialog', 'Date_Interrupt', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_DATE_JEALOUS = ('<str>Date_DialogID', 'Date_Dialog', 'Date_Jealous', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_DATE_INVITE = ('<str>Date_DialogID', 'Date_Dialog', 'Date_Invite', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    DATE_DIALOG_INVITE_REFUSE = ('<str>Date_DialogID', 'Date_Dialog', 'InviteRefuse', lambda val, connection: '\n'.join([do_lookup(
        'Translation_Hint', v, '<str>id', 'English', None, connection, {}) for v in val.split(',')])if len(val) > 0 else 'No Date_DialogID yet')
    ITEM_DROP_FIXED = ('<str>id', 'Item_drop', 'FixDrop_ItemList', lambda x, connection: '\n'.join([do_lookup(
        'Props_total_table', y.split(',')[0], '<str>Props_Id', 'Props_Name', Lookup.TRANSLATION, connection, {}) for y in x.split(';')]))
    ITEM_DROP_RANDOM = ('<str>id', 'Item_drop', 'RndDrop_ItemList', lambda x, connection: '\n'.join([do_lookup(
        'Props_total_table', y.split(',')[0], '<str>Props_Id', 'Props_Name', Lookup.TRANSLATION, connection, {}) for y in x.split(';')]) if x.split(';')[0].split(',')[0] != '0' else 'None')
    ITEM_DROP_RANDOM_NUMBER = ('<str>Id', 'Item_drop', 'RndDrop_NumRange', None)
    ITEM_DROP_FIXED_NUMBER = ('<str>Id', 'Item_drop', 'FixDrop_MaxNum', None)
    NPC_ID_TO_NAME = ('<str>Id', 'NPCRepository', 'Name', TRANSLATION)
    GIFT_ID_TO_NAME = ('<str>GiftID', 'NpcRepository', 'Name', TRANSLATION)
    CONVERSATION_SEGMENT_SPEAKER = ('<str>SegmentID', 'Conversation_Segment', 'SpeakerID', NPC_ID_TO_NAME)
    CONVERSATION_SEGMENT_SPEAK_TO_ID = ('<str>SegmentID', 'Conversation_Segment', 'SpeakToId', NPC_ID_TO_NAME)
    WISH_ITEM_GROUP = ('<str>WishItemID', 'WishItem', 'PropsId', PROP)
    PARTS_LIST = ('<str>Part_ID', 'CreationPart_List', 'Item_List', lambda x, connection: do_lookup('Props_total_table', x.split(';')[
                  1].split('_')[0], '<str>Props_ID', 'Props_Name', Lookup.TRANSLATION, connection, {}) + ' x{}'.format(x.split(';')[1].split('_')[1]))
    PROP_ITEM_TYPE = ('<str>Props_Id', 'Props_total_table', 'Item_Type', None)
    FIND_DIFF_GAME_ITEMS = ('<str>id', 'FindDiffGame_Items', 'itemId', PROP)
    MAIL = ('<str>id', 'Mail', 'Content', TRANSLATION)
    PK_DIALOG = ('<str>DialogID', 'PK_Dialog', 'Dialog', TRANSLATION)
    ANIMAL_FARM_HOUSE = ('<str>type', 'AnimalFarm_House', 'ItemId', PROP)
    FAVOR_RELATION = ('<str>Favor_Relation_ID', 'Favor_Relation', 'Relation_Name', TRANSLATION)
    COOK_TAG_NAME = ('<str>Tag', 'Cook_TagName', 'Name', TRANSLATION)
    STORE_ID = ('<str>Store_Id', 'Store_4_0', 'Name_Id', TRANSLATION)
    STORE_PRODUCT = ('<str>product_id', 'Store_product', 'item_id', PROP)
    ACTOR_TYPE = ('<str>ID', 'Actor', 'Name', TRANSLATION)
    DUNGEON_CHEST_FIXED = ('<str>ID', 'Dungeon_Chest', 'Drop_Group', ITEM_DROP_FIXED)
    DUNGEON_CHEST_RANDOM = ('<str>ID', 'Dungeon_Chest', 'Drop_Group', ITEM_DROP_RANDOM)
    DUNGEON_MONSTER = ('<str>ID', 'Trial_Dungeon_Monster', 'ActorID', ACTOR_TYPE)
    RIDABLE_INFO_ID = ('<str>RidableInfoID', 'RidableInfo', 'InitNickName', TRANSLATION)
    FOOD_TAG_LIKES = ('<str>Food_GroupID', 'Food_Group', 'LikeFood_Tag', foodtag_lookup)
    FOOD_TAG_DISLIKES = ('<str>Food_GroupID', 'Food_Group', 'DislikeFood_Tag', foodtag_lookup)
    DATE_PROJECT = ('<str>Date_ProjectID', 'Date_Project_new', 'Project_Name', TRANSLATION)
    GUILD_LEVEL = ('<str>ID', 'GuildLevel', 'Level', None)
    FURNITURE_TABLE_SIZE = ('<str>ID', 'Furniture_Table', 'Size', None)
    FURNITURE_TABLE_FEATURE_TYPE = ('<str>ID', 'Furniture_Table', 'Feature_Type', None)
    EXHIBIT_WORKSHOP_PT = ('<str>itemId', 'ExhibitData', 'workshopPT', None)
    REPAIR_TABLE_PARTS_LIST = ('<str>Item_Id', 'Repair_Table', 'Parts_List', None)  # need to split these up by comma
    REPAIR_TABLE_TIME = ('<str>Item_Id', 'Repair_Table', 'Time', None)
    REPAIR_TABLE_CD_COST = ('<str>Item_Id', 'Repair_Table', 'CD_Cost', None)
    PROPS_ID_TO_USER_LEVEL = ('<str>Props_Id', 'Props_total_table', 'User_Level', None)
    PROPS_ID_TO_PROPS_EXPLAIN_ONE = ('<str>Props_Id', 'Props_total_table', 'Props_Explain_One', TRANSLATION)
    PROPS_ID_TO_EFFECT = ('<str>Props_Id', 'Props_total_table', 'Effect', TRANSLATION)
    PROPS_ID_TO_ATK = ('<str>Equipment_Id', 'Item_equipment', 'ATK', None)
    PROPS_ID_TO_DEFENSE = ('<str>Equipment_Id', 'Item_equipment', 'Defense', None)
    PROPS_ID_TO_HEALTH = ('<str>Equipment_Id', 'Item_equipment', 'Health', None)
    PROPS_ID_TO_CPMAX = ('<str>Equipment_Id', 'Item_equipment', 'CpMax', None)
    PROPS_ID_TO_CRIT = ('<str>Equipment_Id', 'Item_equipment', 'Crit', None)
    PROPS_ID_TO_MELEE_CRITICAL = ('<str>Equipment_Id', 'Item_equipment', 'MeleeCriticalAmount', None)
    PROPS_ID_TO_RANGE_CRITICAL = ('<str>Equipment_Id', 'Item_equipment', 'RangeCriticalAmount', None)
    PROPS_ID_TO_ANTICRITICAL = ('<str>Equipment_Id', 'Item_equipment', 'AntiCritical', None)
    PROPS_ID_TO_DATE_FORCE = ('<str>Equipment_Id', 'Item_equipment', 'Date_Force', None)
    ITEM_FOOD_HP_VALUE = ('<str>Food_Id', 'Item_food', 'hp_Value', None)
    ITEM_FOOD_COMFORT_VALUE = ('<str>Food_Id', 'Item_food', 'Comfort_Value', None)
    ITEM_FOOD_ADD_HP_MAX = ('<str>Food_Id', 'Item_food', 'Add_HpMax', None)
    ITEM_FOOD_ADD_CP_MAX = ('<str>Food_Id', 'Item_food', 'Add_CpMax', None)
    ITEM_FOOD_ADD_ATTACK = ('<str>Food_Id', 'Item_food', 'Add_Attack', None)
    ITEM_FOOD_ADD_DEFENCE = ('<str>Food_Id', 'Item_food', 'Add_Defence', None)
    ITEM_FOOD_ADD_CRIT = ('<str>Food_Id', 'Item_food', 'Add_Crit', None)
    ITEM_FOOD_ADD_ANTICRIT = ('<str>Food_Id', 'Item_food', 'Add_AntiCrit', None)
    ITEM_FOOD_BUFF_ID = ('<str>Food_Id', 'Item_food', 'Buff_Id', None)
    ITEM_FOOD_REMOVE_BUFF_ID = ('<str>Food_Id', 'Item_food', 'Remove_Buff_Id', None)
    RECYCLE_TABLE_DROP_ID = ('<str>Item_Id', 'Recycle_Table', 'Drop_Id', ITEM_DROP_FIXED)
    FARM_COMMON_SUITABLE_FLOOR = ('<str>ID', 'Farm_Common', 'SuitableFloor', None)
    FARM_COMMON_AREA = ('<str>ID', 'Farm_Common', 'Area', None)
    FARM_COMMON_UNABLE_FACE_TO_WALL = ('<str>ID', 'Farm_Common', 'UnableFaceToWall', None)
    STORE_PRODUCT_GENERAL = ('<str>product_id', 'Store_product', 'item_id', None)
    FOOD_DIALOG = ('<str>FoodTag_ID', 'Food_Dialog', 'FoodTag_Name', TRANSLATION)
    CABINET_TYPE_LIST = ('<str>Type', 'Cabinet_TypeList', 'Name', TRANSLATION)
    ABILITY_TREE_NEW = ('<str>Id', 'Ability_Tree_New', 'Name', TRANSLATION)
    ITEM_FROM = ('<str>Id', 'ItemFrom', 'Des', TRANSLATION)
    PLAYER_INTEND_NO_TARGET = ('<str>Type', 'Player_Intend', 'NoTarget', None)
    PLAYER_INTEND_HOME_REGION = ('<str>Type', 'Player_Intend', 'HomeRegion', None)
    IN_MISSION_DIALOG = ('<str>MissionID', 'InMission_Dialog', 'Dialog', CONVERSATION_BASE)  # split by semicolon
    TASK_DIALOGUE = ('<str>Dialogue', 'Task_dialogue', 'Id', CONVERSATION_BASE)
    ORDER_REQ_ITEM = ('<str>OrderID', 'Order_Req', 'ItemReq', PROP)  # for now
    ORDER_REQ_GOLD = ('<str>OrderID', 'Order_Req', 'Gold', None)
    ORDER_REQ_RELATIONSHIP = ('<str>OrderID', 'Order_Req', 'Relationship', None)
    ORDER_REQ_WORKSHOP_PT = ('<str>OrderID', 'Order_Req', 'WorkshopPT', None)
    ORDER_REQ_EXP = ('<str>OrderID', 'Order_Req', 'Exp', None)
    ORDER_REQ_LEVEL = ('<str>OrderID', 'Order_Req', 'Level', GUILD_LEVEL)
    ORDER_REQ_WEIGHT = ('<str>OrderID', 'Order_Req', 'Weight', None)
    ORDER_REQ_DEADLINE = ('<str>OrderID', 'Order_Req', 'Deadline', None)
    ORDER_REQ_MISSION = ('<str>OrderID', 'Order_Req', 'MissionID', None)
    ORDER_REQ_SEASON = ('<str>OrderID', 'Order_Req', 'Season', None)
    ORDER_REQ_WEATHER = ('<str>OrderID', 'Order_Req', 'Weather', None)
    TRIAL_DUNGEON_MONSTER = ('<str>ID', 'Trial_Dungeon_Monster', 'ActorID', ACTOR_TYPE)
    REQ_TYPE = ('<str>TypeID', 'Req_Type', 'Order_Rewards', None)  # for now, need to split by ','
    # for now, need to split by ';' and quantity_post '_'
    RESEARCH_LIST_ITEM_LIST = ('<str>ID', 'Research_List', 'Item_List', PROP)
    RESEARCH_LIST_RESEARCH_SPEED = ('<str>ID', 'Research_List', 'Research_Speed', None)
    SWING_ID_TO_NAME = ('<str>SwingGame_ID', 'NpcRepository', 'Name', TRANSLATION)
    TEETER_ID_TO_NAME = ('<str>TeeterGame_ID', 'NpcRepository', 'Name', TRANSLATION)
    RANDOM_HERBS_ITEM_DROP_FIXED = ('<str>ID', 'random_herbs', 'Drop_Group', ITEM_DROP_FIXED)
    RANDOM_HERBS_ITEM_DROP_FIXED_NUMBER = ('<str>ID', 'random_herbs', 'Drop_Group', ITEM_DROP_FIXED_NUMBER)
    RANDOM_HERBS_ITEM_DROP_RANDOM = ('<str>ID', 'random_herbs', 'Drop_Group', ITEM_DROP_RANDOM)
    RANDOM_HERBS_ITEM_DROP_RANDOM_NUMBER = ('<str>ID', 'random_herbs', 'Drop_Group', ITEM_DROP_RANDOM_NUMBER)
    EMOTION_DATA = ('<str>emotionId', 'emotion_data', 'nameId', TRANSLATION)
    SLOT_RATE_TYPE = ('<str>Type', 'Slot_Rate', 'Index_List', None)
    SLOT_RATE_RATE = ('<str>Type', 'Slot_Rate', 'Rate', None)
    COOK_BOOK_QUALITY_COST = ('<str>Quality', 'Cook_BookQuality', 'Cost', None)
    COOK_BOOK_QUALITY_WEIGHT = ('<str>Quality', 'Cook_BookQuality', 'Weight', None)
    DEE_FLAG_NAME = ('<str>id', 'SceneItemTransformBinding', 'flagName', None)
    FOOD_TAG_MAXIMUM = ('<str>Food_GroupID', 'Food_Group', 'Food_Maximum', None)
    FOOD_TAG_MINIMUM = ('<str>Food_GroupID', 'Food_Group', 'Food_Minimum', None)
    ORDER_REQ_GROUP_REQ = ('<str>id', 'Order_ReqGroup', 'req', lambda x, connection: '\n'.join([do_lookup(
        'Order_Req', y.split(',')[0], '<str>OrderID', 'ItemReq', Lookup.PROP, connection, {}) for y in x.split(',')]))


class Transform(object):
    @staticmethod
    def FACTION(x, connection):
        return {'11': 'Person',
                '-1': 'Monster',
                '0': '0 (Unknown)',
                '1': '1 (Unknown)',
                '2': '2 (Unknown)',
                '3': '3 (Unknown)',
                '4': '4 (Unknown)',
                '5': '5 (Unknown)',
                '6': '6 (Unknown)',
                '7': '7 (Unknown)',
                '8': '8 (Unknown)',
                '9': '9 (Unknown)',
                '10': '10 (Unknown)',
                '15': '15 (Unknown)'}[x]

    @staticmethod
    def BOOL(x, connection):
        return {'0': 'False', '1': 'True'}[x]

    @staticmethod
    def EMPTY(x, connection):
        return {'-1': 'n/a'}[x]

    @staticmethod
    def RELATION_TYPE(x, connection):
        return {'1': 'Not Romanceable',
                '2': 'Bachelor/Bachelorette',
                '3': 'Spouse'}[x]

    @staticmethod
    def GIFT_TAGID(x, connection):
        results = []
        tags = x.split(',')
        for tag in tags:
            if tag == '0':
                results.append('No tag')
            elif tag in ['1', '2', '3', '4']:
                results.append({'1': 'Universal love',
                                '2': 'Universal like',
                                '3': 'Universal dislike',
                                '4': 'Universal hate'}[tag])
            else:
                results.append(find_npc_from_gift_tagid(tag, connection))
        return '\n'.join(results)

    @staticmethod
    def TRANSLATION_UNDERSCORE_SPLIT(x, connection):
        results = []
        for q_and_a in x.split(','):
            print(q_and_a)
            q, a = q_and_a.split('_')
            q_and_a_str = 'Question: {}\nAnswer: {}'.format(
                do_lookup('Translation_hint', q, '<str>id', 'English', None, connection, {}),
                do_lookup('Translation_hint', a, '<str>id', 'English', None, connection, {}))
            results.append(q_and_a_str)
        return '\n\n'.join(results)

    @staticmethod
    def SOCIAL_DIALOG(x, connection):
        if x == '-1':
            return 'None'
        results = []
        for dialog in x.split('|'):
            hearts, options = dialog.split('=')
            dialogs = []
            for option in options.split(';'):
                dialogs.append(do_lookup('Conversation_Base', option, '<str>baseid',
                                         'TranslationID', Lookup.TRANSLATION, connection, {}))
            results.append('{0:>3}: {1}'.format(hearts, '\n     '.join(dialogs)))
        return '\n'.join(results)

    @staticmethod
    def PRODUCT_SEASON(x, connection):
        season, products = x.split('=')
        results = []
        for product in products.split(','):
            product, quantity = product.split('_')
            product = do_lookup('Store_product', product, '<str>product_id',
                                'item_id', Lookup.PROP, connection, {})
            results.append('{} x{}'.format(product, quantity))
        season = ['Spring', 'Summer', 'Autumn', 'Winter'][int(season)]
        return '{} -- {}'.format(season, '\n          '.join(results))

    @staticmethod
    def PRODUCT_WEATHER(x, connection):
        weather, products = x.split('=')
        results = []
        for product in products.split(','):
            product, quantity = product.split('_', maxsplit=1)
            product = do_lookup('Store_product', product, '<str>product_id',
                                'item_id', Lookup.PROP, connection, {})
            results.append('{} x{}'.format(product, quantity))
        weather = ['Weather 0', 'Weather 1', 'Weather 2', 'Weather 3'][int(weather)]
        return '{} -- {}'.format(weather, '\n          '.join(results))

    @staticmethod
    def GIFT_ID(x, connection):
        if str(x) == '1':
            return 'ALL'
        results = do_query('SELECT Name FROM NPCRepository where GiftID="{}"'.format(x), connection)
        if len(results) == 0:
            return '<No NPC with GiftID {}>'.format(x)
        name = do_lookup('Translation_hint', results[0]['name'], '<str>id', 'English', None, connection, {})
        if name.strip() == '':
            return '<Empty name, GiftID is {}>'.format(x)
        return name

    @staticmethod
    def FAVOR(x, connection):
        global CACHED_GIFT_TAGS
        if CACHED_GIFT_TAGS is None:
            CACHED_GIFT_TAGS = find_associations('Props_total_table', 'Tag_List', ',',
                                                 ('props_name', Lookup.TRANSLATION), {}, connection)
            CACHED_GIFT_TAGS = {x: y for x, y in CACHED_GIFT_TAGS[0]}
        base_value, exceptions = x.split('|')
        if exceptions.strip() == '':
            return 'Value {}\nExceptions:None'.format(base_value)
        exceptions_translated = []
        for exception in exceptions.split('$'):
            tag, value = exception.split('_')
            items_str = CACHED_GIFT_TAGS.get(tag)
            if items_str is None:
                exceptions_translated.append('{}: {}'.format(value, '<Unknown gift with tag {}>'.format(tag)))
            else:
                items = items_str.split('\n')
                exceptions_translated.append('{}: {}'.format(value, ', '.join(items)))
        return 'Value {}\nExceptions: {}'.format(base_value, '\n            '.join(exceptions_translated))

    @staticmethod
    def REWARDS(x, connection):
        points, mail, drop = x.split(',')
        return 'Points: {}\n  Mail: {}\n'.format(
            points,
            do_lookup('Mail', mail, '<str>id', 'Content', Lookup.TRANSLATION, connection, {}).replace('\n\n', ' ').replace('\n', ' '))
        """
        return 'Points: {}\nReward: {}\n  Mail: {}\n'.format(
            points,
            do_lookup('Item_drop', drop, '<str>id', 'FixDrop_ItemList', lambda x, connection: ', '.join([do_lookup(
                'Props_total_table', y.split(',')[0], '<str>Props_Id', 'Props_Name', Lookup.TRANSLATION, connection, {}) for y in x.split(';')]), connection, {}),
            do_lookup('Mail', mail, '<str>id', 'Content', Lookup.TRANSLATION, connection, {}).replace('\n\n', ' ').replace('\n', ' '))
        """

    @staticmethod
    def GIFT_ID_EXCELLENT(x, connection):
        return do_lookup('Gift', x, '<str>Gift_ID', 'TagID_Excellent', lambda val,
                         connection: props_gift_lookup(val, connection, x, 'Excellent') if len(val.strip()) > 0 else 'No Gift_TagID yet', connection, {})

    @staticmethod
    def GIFT_ID_LIKE(x, connection):
        return do_lookup('Gift', x, '<str>Gift_ID', 'TagID_Like', lambda val,
                         connection: props_gift_lookup(val, connection, x, 'Like') if len(val.strip()) > 0 else 'No Gift_TagID yet', connection, {})

    @staticmethod
    def GIFT_ID_DISLIKE(x, connection):
        return do_lookup('Gift', x, '<str>Gift_ID', 'TagID_Dislike', lambda val,
                         connection: props_gift_lookup(val, connection, x, 'Dislike') if len(val.strip()) > 0 else 'No Gift_TagID yet', connection, {})

    @staticmethod
    def GIFT_ID_HATE(x, connection):
        return do_lookup('Gift', x, '<str>Gift_ID', 'TagID_Hate', lambda val,
                         connection: props_gift_lookup(val, connection, x, 'Hate') if len(val.strip()) > 0 else 'No Gift_TagID yet', connection, {})

    @staticmethod
    def GIFT_ID_CONFESSION(x, connection):
        return do_lookup('Gift', x, '<str>Gift_ID', 'TagID_confession', lambda val,
                         connection: props_gift_lookup(val, connection, x) if len(val.strip()) > 0 else 'No Gift_TagID yet', connection, {})

    @staticmethod
    def GIFT_ID_PROPOSE(x, connection):
        return do_lookup('Gift', x, '<str>Gift_ID', 'TagID_propose', lambda val,
                         connection: props_gift_lookup(val, connection, x) if len(val.strip()) > 0 else 'No Gift_TagID yet', connection, {})

    @staticmethod
    def GIFT_ID_REFUSE(x, connection):
        return do_lookup('Gift', x, '<str>Gift_ID', 'TagID_refuse', lambda val,
                         connection: props_gift_lookup(val, connection, x) if len(val.strip()) > 0 else 'No Gift_TagID yet', connection, {})

    @staticmethod
    def GIFT_ID_BREAK_UP(x, connection):
        return do_lookup('Gift', x, '<str>Gift_ID', 'TagID_breakup', lambda val,
                         connection: props_gift_lookup(val, connection, x) if len(val.strip()) > 0 else 'No Gift_TagID yet', connection, {})

    @staticmethod
    def GIFT_ID_DIVORCE(x, connection):
        return do_lookup('Gift', x, '<str>Gift_ID', 'TagID_divorce', lambda val,
                         connection: props_gift_lookup(val, connection, x) if len(val.strip()) > 0 else 'No Gift_TagID yet', connection, {})

    @staticmethod
    def GIFT_ID_JEALOUS(x, connection):
        return do_lookup('Gift', x, '<str>Gift_ID', 'TagID_jealous', lambda val,
                         connection: props_gift_lookup(val, connection, x) if len(val.strip()) > 0 else 'No Gift_TagID yet', connection, {})

    @staticmethod
    def PROPS_RECYCLE_TAG(x, connection):
        global CACHED_RECYCLE_TAGS
        if CACHED_RECYCLE_TAGS is None:
            CACHED_RECYCLE_TAGS = {}
            results = do_query('SELECT props_name, Recycle_Tag FROM props_total_table', connection)
            for result in results:
                tags = result['recycle_tag'].split(',')
                for tag in tags:
                    if tag not in CACHED_RECYCLE_TAGS:
                        CACHED_RECYCLE_TAGS[tag] = []
                    CACHED_RECYCLE_TAGS[tag].append(result['props_name'])
        if x not in CACHED_RECYCLE_TAGS:
            return 'Did not find any props with recycle tag {}'.format(x)

        props = []
        for prop in CACHED_RECYCLE_TAGS[x]:
            props.append(do_lookup('Translation_hint', prop, '<str>id', 'English', None, connection, {}))
        return '\n'.join(props)

    @staticmethod
    def ORDER_CAN_REQUEST(x, connection):
        if x == '-1':
            return 'None'
        requestables = []
        groups = x.split('#')
        for i, group in enumerate(groups):
            commisions = group.split('|')[0].split(',')
            for commision in commisions:
                results = do_query('SELECT req FROM Order_ReqGroup WHERE id="{}"'.format(commision), connection)
                assert len(results) == 1
                order_ids = results[0]['req'].split(',')
                for order_id in order_ids:
                    results = do_query(
                        'SELECT * FROM Order_Req WHERE OrderId="{}"'.format(order_id), connection)
                    assert len(results) == 1
                    info = results[0]
                    quantity = info['itemreq'].split('_')[1]
                    if len(set(quantity.split('-'))) == 1:
                        quantity = quantity.split('-')[0]
                    name = do_lookup('Props_total_table', info['itemreq'].split('_')[0], '<str>Props_Id',
                                     'Props_Name', Lookup.TRANSLATION, connection, {}) + ' (x{})'.format(quantity)
                    gold = info['gold']
                    if len(set(gold.split('-'))) == 1:
                        gold = gold.split('-')[0]
                    relationship = info['relationship']
                    if len(set(relationship.split('-'))) == 1:
                        relationship = relationship.split('-')[0]
                    workshop_pt = info['workshoppt']
                    if len(set(workshop_pt.split('-'))) == 1:
                        workshop_pt = workshop_pt.split('-')[0]
                    workshop_pt = info['workshoppt']
                    if len(set(workshop_pt.split('-'))) == 1:
                        workshop_pt = workshop_pt.split('-')[0]
                    requestables.append('{}: {}'.format(i + 1, name) +
                                        '\n     Gold: {}'.format(gold) +
                                        '\n     Relationship: {}'.format(relationship) +
                                        '\n     Workshop Pts: {}'.format(workshop_pt) +
                                        '\n     Exp: {}'.format(info['exp']) +
                                        '\n     Level: {}'.format(info['level']) +
                                        '\n     Weight: {}'.format(info['weight']) +
                                        '\n     Mission ID: {}'.format('None' if info['missionid'] == '-1' else info['missionid']) +
                                        '\n     Season: {}'.format('None' if info['season'] == '' else info['season']) +
                                        '\n     Weather: {}'.format('None' if info['weather'] == '' else info['weather']) +
                                        '\n     Deadline: {} Days'.format(info['deadline']))
        return '\n'.join(requestables)

    @staticmethod
    def ORDER_MISSION_DIALOGUE(x, connection):
        if x == '-1':
            return 'None'
        groups = x.split('#')
        dialogues = []
        for group in groups:
            dialogue = do_lookup('Translation_hint', group.split('|')[1], '<str>id', 'English', None, connection, {})
            dialogues.append(dialogue)
        return '\n'.join(dialogues)

    @staticmethod
    def ORDER_CAN_DELIVER_TO(x, connection):
        groups = x.split('#')
        npcs = []
        for group in groups:
            for subgroup in group.split('|')[2:]:
                npc_id = subgroup.split('=')[0]
                npc_name = do_lookup('NPCRepository', npc_id, '<str>Id', 'Name', Lookup.TRANSLATION, connection, {})
            npcs.append(npc_name)
        return '\n'.join(npcs)

    @staticmethod
    def ITEM_DROP_FIXED(x, connection):
        reward_id = x.split(',')[-1]
        return do_lookup('Item_drop', reward_id, '<str>id', 'FixDrop_ItemList',
                         lambda x, connection: '\n'.join([do_lookup('Props_total_table', y.split(',')[0], '<str>Props_Id', 'Props_Name', Lookup.TRANSLATION, connection, {}) for y in x.split(';')]), connection, {})

    @staticmethod
    def ITEM_DROP_RANDOM(x, connection):
        reward_id = x.split(',')[-1]
        return do_lookup('Item_drop', reward_id, '<str>id', 'RndDrop_ItemList',
                         lambda x, connection: '\n'.join([do_lookup('Props_total_table', y.split(',')[0], '<str>Props_Id', 'Props_Name', Lookup.TRANSLATION, connection, {}) for y in x.split(';')]) if x.split(';')[0].split(',')[0] != '0' else 'None', connection, {})

    @staticmethod
    def ITEM_DROP_RANDOM_NUMBER(x, connection):
        reward_id = x.split(',')[-1]
        return do_lookup('Item_drop', reward_id, '<str>id', 'RndDrop_NumRange', None, connection, {})

    @staticmethod
    def ITEM_DROP_FIXED_NUMBER(x, connection):
        reward_id = x.split(',')[-1]
        return do_lookup('Item_drop', reward_id, '<str>id', 'FixDrop_MaxNum', None, connection, {})


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0].lower()] = row[idx]
    return d


def do_lookup(lookup_table, source_value, lookup_column, result_column, result_conversion, connection, options):
    multiplier = None
    if 'quantity_pre' in options or 'quantity_post' in options:
        quantity_indicator = options.get('quantity_pre', None)
        quantity_indicator = options.get('quantity_post', quantity_indicator)
        assert quantity_indicator is not None
        if quantity_indicator in source_value:
            split_values = source_value.split(quantity_indicator)
            if len(split_values) > 2:
                return 'Unsure how to handle source value with multiple quantity indicators: quantity indicator is {}, value is {}'.format(quantity_indicator, source_value)
            if 'quantity_pre' in options and 'quantity_post' not in options:
                multiplier, source_value = split_values
            elif 'quantity_post' in options and 'quantity_pre' not in options:
                source_value, multiplier = split_values
            else:
                assert False, 'Invalid quantity options combination: {}'.format(options)
    if lookup_column.startswith('<str>'):
        lookup_column = lookup_column[5:]
        query = 'SELECT {} FROM {} where {}="{}"'.format(
            result_column, lookup_table, lookup_column, source_value)
        results = do_query(query, connection)
    else:
        query = 'SELECT {} FROM {} where {}={}'.format(
            result_column, lookup_table, lookup_column, source_value)
        results = do_query(query, connection)
    looked_up_values = []
    for result in results:
        looked_up_values.append(result[result_column.lower()])
    if len(looked_up_values) == 0:
        return 'Query {} returned no results'.format(query)
    if len(looked_up_values) > 1:
        assert options.get('allow_multiple_lookup_results', True), \
            'Multiple results returned for query {} :o'.format(query)
    final_values = []
    for looked_up_value in looked_up_values:
        values_to_process = [looked_up_value]
        if 'lookup_split' in options:
            values_to_process = looked_up_value.split(options['lookup_split'])
        results = []
        for looked_up_value in values_to_process:
            if result_conversion is not None:
                if callable(result_conversion):
                    looked_up_value = result_conversion(looked_up_value, connection)
                elif isinstance(result_conversion, tuple):
                    looked_up_value = do_lookup(
                        result_conversion[1], looked_up_value, result_conversion[0], result_conversion[2], result_conversion[3], connection, options)
                elif isinstance(result_conversion, list):
                    for conversion in result_conversion:
                        looked_up_value = do_lookup(conversion[1], looked_up_value,
                                                    conversion[0], conversion[2], conversion[3], connection, options)
                        if 'returned no results' not in looked_up_value:
                            break
                else:
                    raise Exception('Invalid value of result_conversion: {}'.format(result_conversion))
            if multiplier is not None:
                looked_up_value = looked_up_value + ' x{}'.format(multiplier)
            results.append(looked_up_value)
        final_values.append(options.get('lookup_split_join_char', '\n').join(results))
    return options.get('multiple_lookup_results_join_char', ', ').join(final_values)


def extract_table(name, columns, connection):
    extracted = []
    results = do_query('SELECT {} FROM {}'.format(','.join([x[0] for x in columns]), name), connection)
    for result in results:
        single_extracted = []
        for i in range(len(columns)):
            options = {}
            if len(columns[i]) > 2:
                options = columns[i][2]
                col_name = columns[i][0]
                conversion = columns[i][1]
            elif len(columns[i]) == 2:
                col_name, conversion = columns[i]
            col_values = []

            field_label = options.get('label', col_name)

            if 'split' in options:
                values = result[col_name.lower()].split(options['split'])
            else:
                values = [result[col_name.lower()]]
            for value in values:
                if 'ignore_if_equals' in options and value in options['ignore_if_equals']:
                    col_values.append('(n/a)')
                    continue
                if value == '':
                    col_values.append('(empty)')
                    continue
                if 'regex' in options:
                    match = re.search(options['regex'], value)
                    assert match is not None, 'Regex {} does not match value "{}"'.format(options['regex'], value)
                    value = match.group(1)
                if isinstance(conversion, tuple):
                    col_value = do_lookup(conversion[1], value, conversion[0],
                                          conversion[2], conversion[3], connection, options)
                elif isinstance(conversion, list):
                    for single_conversion in conversion:
                        col_value = do_lookup(
                            single_conversion[1], value, single_conversion[0], single_conversion[2], single_conversion[3], connection, options)
                        if 'returned no results' not in col_value:
                            break
                elif callable(conversion):
                    col_value = conversion(value, connection)
                elif conversion is None:
                    col_value = value
                else:
                    raise Exception('Unexpected conversion type {}'.format(conversion))
                col_values.append(col_value)
            join_string = options.get('join', '\n')
            single_extracted.append((field_label, join_string.join(col_values)))
        extracted.append(single_extracted)
    extracted.sort(key=lambda x: x[0][1].lower())
    return extracted


def main(mappings):
    connection = sqlite3.connect(DATABASE_FILENAME)
    connection.row_factory = dict_factory

    with open('all.txt', 'w', encoding='utf-8') as f_all:
        for filepath, mapping in mappings.items():
            with open(filepath[:-2] + 'txt', 'w', encoding='utf-8') as f:
                try:
                    if 'association' in mapping:
                        column = mapping['association']['column']
                        lookup = None
                        if isinstance(column, tuple):
                            column, lookup = column
                        extracted = find_associations(mapping['name'], column, mapping['association'].get(
                            'split', ','), mapping['association']['name'], mapping['association'].get('tag_names', {}), connection)
                        if lookup is not None:
                            new_extracted = [[]]
                            for i in extracted:
                                for key, value in i:
                                    new_extracted[0].append((do_lookup(
                                        lookup[1], key, lookup[0], lookup[2], lookup[3], connection, {}), value))
                            extracted = new_extracted
                    elif 'columns' in mapping:
                        extracted = extract_table(mapping['name'], mapping['columns'], connection)
                    print(mapping['name'])
                    print('\n')
                    for single in extracted:
                        maxlen = 0
                        for field, _ in single:
                            maxlen = max(len(field), maxlen)
                        multiple_values_in_list = False
                        for field, value in single:
                            if '\n' in value:
                                multiple_values_in_list = True
                        # Does weird things to name column, disable for now
                        multiple_values_in_list = False
                        for field, value in single:
                            if '\n' in value:
                                all_values = value.split('\n')
                                index_length = len(str(len(all_values)))
                                all_values = ['{0:>{1}}: {2}'.format(i + 1, index_length, all_values[i])
                                              for i in range(len(all_values))]
                                value = '\n{0:>{1}}'.format(' ', maxlen + 2).join(all_values)
                            elif multiple_values_in_list:
                                value = '1: {}'.format(value)
                            line = '{0:>{1}}: {2}'.format(field, maxlen, value)
                            try:
                                print(line)
                            except UnicodeEncodeError:
                                print('{0:>{1}}: {2}'.format(field, maxlen,
                                                             value.encode('cp437', 'replace').decode('cp437')))
                            f.write(line + '\n')
                            f_all.write(line + '\n')
                            f.flush()
                            f_all.flush()
                        f.write('\n')
                        f_all.write('\n')
                        print('')
                except Exception:
                    err = 'Failed to evaluate mapping for {} due to the following error:\n\n{}'.format(
                        filepath, traceback.format_exc())
                    print(err)
                    f.write(err)
                    f_all.write(err)


if __name__ == '__main__':
    folder = os.path.join('datasets')
    files = []
    if len(files) == 0:
        for root, _, filenames in os.walk(folder):
            for filename in filenames:
                if filename.endswith('.py'):
                    files.append(os.path.join(root, filename))
    else:
        for i, filepath in enumerate(files):
            if not filepath.endswith('.py'):
                filepath += '.py'
            files[i] = os.path.join(folder, filepath)
    files.sort()
    mappings = {}
    for filepath in files:
        with open(filepath) as f:
            try:
                mapping = eval(f.read())
            except Exception:
                print('Failed to evaluate file {}:\n{}'.format(filepath, traceback.format_exc()))
                exit(1)
        mappings[filepath] = mapping

    if not os.path.isfile(DATABASE_FILENAME):
        print('Please update DATABASE_FILENAME to point to LocalDb.bytes')
    else:
        current_hash = md5_hash(DATABASE_FILENAME)
        load_cache(current_hash)
        initial_size = sys.getsizeof(CACHED_QUERIES)
        main(mappings)
        post_run_size = sys.getsizeof(CACHED_QUERIES)
        if post_run_size - initial_size > 500:
            write_cache(current_hash)
