import sqlite3
import re

DATABASE_FILENAME = 'C:\Program Files (x86)\Steam\steamapps\common\My Time At Portia\Portia_Data\StreamingAssets\CccData\LocalDb.bytes'

CACHED_PROPS = None
CACHED_GIFTS = None
CACHED_FOOD_MENU = None
CACHED_DATE_DIALOG = None
CACHED_GIFT_TAGS = None
CACHED_GIFT_TAGS_NOTRAN = None


def props_gift_lookup(gift_tagid, connection, gift_id, like_type=None):
    global CACHED_GIFT_TAGS_NOTRAN
    global CACHED_PROPS

    if like_type is not None:
        query = 'SELECT Favor_{} from Gift where Gift_ID="{}"'.format(like_type, gift_id)
        cursor = connection.cursor()
        cursor.execute(query)
        results = []
        for result in cursor:
            results.append(result)
        assert len(set([str(x) for x in results])) == 1

        if CACHED_GIFT_TAGS_NOTRAN is None:
            CACHED_GIFT_TAGS_NOTRAN = find_associations('Props_total_table', 'Tag_List', ',',
                                                        ('props_name', None), {}, connection, ignore_multipliers=True)
            CACHED_GIFT_TAGS_NOTRAN = {x: y.split('\n') for x, y in CACHED_GIFT_TAGS_NOTRAN[0]}

        base_value, exceptions_str = result['favor_{}'.format(like_type.lower())].split('|')
        exceptions = {}
        if exceptions_str.strip() != '':
            for exception in exceptions_str.split('$'):
                tag, value = exception.split('_')
                exceptions[tag] = value

    gift_tagid = gift_tagid.split(';')[0]

    if CACHED_PROPS is None:
        CACHED_PROPS = []
        cursor = connection.cursor()
        cursor.execute('SELECT props_name, gift_tagid FROM props_total_table')
        for result in cursor:
            CACHED_PROPS.append(result)
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
    cursor = connection.cursor()
    cursor.execute('SELECT {}, {} FROM {}'.format(name_column, column, table))
    all_results = []
    for result in cursor:
        all_results.append(result)

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
        CACHED_GIFTS = []
        cursor = connection.cursor()
        cursor.execute('SELECT Gift_ID, TagID_Excellent, TagID_Like, TagID_Dislike, TagID_Hate, TagID_Confession, '
                       'TagID_Propose, TagID_Refuse, TagID_Breakup, TagID_Divorce, TagID_Jealous, TagID_MarriageCall FROM Gift')
        for result in cursor:
            CACHED_GIFTS.append(result)
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
        CACHED_FOOD_MENU = []
        cursor = connection.cursor()
        cursor.execute('SELECT Food_Name, Food_Tag FROM Food_Menu')
        for result in cursor:
            CACHED_FOOD_MENU.append(result)
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
    STORE_ID = ('<str>Store_Id', 'Store_4_0', 'name_id', TRANSLATION)
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
    STORE_PRODUCT_GENERAL = ('<str>product_id', 'Store_product', 'item_id', )
    FOOD_DIALOG = ('<str>FoodTag_ID', 'Food_Dialog', 'FoodTag_Name', TRANSLATION)
    CABINET_TYPE_LIST = ('<str>Type', 'Cabinet_TypeList', 'Name', TRANSLATION)
    ABILITY_TREE_NEW = ('<str>Id', 'Ability_Tree_New', 'Name', TRANSLATION)
    ITEM_FROM = ('<str>Id', 'ItemFrom', 'Des', TRANSLATION)
    PLAYER_INTEND_NO_TARGET = ('<str>Type', 'Player_Intend', 'NoTarget', None)
    PLAYER_INTEND_HOME_REGION = ('<str>Type', 'Player_Intend', 'HomeRegion', None)
    IN_MISSION_DIALOG = ('<str>MissionID', 'InMission_Dialog', 'Dialog', CONVERSATION_BASE)  # split by semicolon
    TASK_DIALOGUE = ('<str>Dialogue', 'Task_dialogue', 'Id', CONVERSATION_BASE)
    ORDER_REQ_ITEM = ('<str>OrderID', 'Order_Req', 'ItemReq', None)  # for now
    ORDER_REQ_GOLD = ('<str>OrderID', 'Order_Req', 'Gold', None)
    ORDER_REQ_RELATIONSHIP = ('<str>OrderID', 'Order_Req', 'Relationship', None)
    ORDER_REQ_WORKSHOP_PT = ('<str>OrderID', 'Order_Req', 'WorkshopPT', None)
    ORDER_REQ_EXP = ('<str>OrderID', 'Order_Req', 'Exp', None)
    ORDER_REQ_LEVEL = ('<str>OrderID', 'Order_Req', 'Level', GUILD_LEVEL)
    ORDER_REQ_WEIGHT = ('<str>OrderID', 'Order_Req', 'Weight', None)
    ORDER_REQ_DEADLINE = ('<str>OrderID', 'Order_Req', 'Deadline', None)
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
    KINSHIP_DATA = ('<str>kinshipId', 'kinship_data', 'nameId', TRANSLATION)
    EMOTION_DATA = ('<str>emotionId', 'emotion_data', 'nameId', TRANSLATION)


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
        cursor = connection.cursor()
        cursor.execute('SELECT Name FROM NPCRepository where GiftID="{}"'.format(x))
        result = cursor.fetchone()
        if result is None:
            return '<No NPC with GiftID {}>'.format(x)
        name = do_lookup('Translation_hint', result['name'], '<str>id', 'English', None, connection, {})
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
        return 'Points: {}\nReward: {}\n  Mail: {}\n'.format(
            points,
            do_lookup('Item_drop', drop, '<str>id', 'FixDrop_ItemList', lambda x, connection: ', '.join([do_lookup(
                'Props_total_table', y.split(',')[0], '<str>Props_Id', 'Props_Name', Lookup.TRANSLATION, connection, {}) for y in x.split(';')]), connection, {}),
            do_lookup('Mail', mail, '<str>id', 'Content', Lookup.TRANSLATION, connection, {}).replace('\n\n', ' ').replace('\n', ' '))

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


MAPPINGS = [
    #     {'name': 'mission_require',
    #      'columns': [('missionId', Lookup.IN_MISSION_DIALOG, {'label': 'Mission'}),
    #                  ('missionId', None, {'label': 'Mission ID'}),
    #                  ('requireItems', Lookup.PROP, {'split': ',',
    #                                                 'label': 'Mission items'})]},
    #     #     PLAYER
    #     {'name': 'Ability_Tree',
    #      'columns': [('Branch', None, {'label': 'Battle|Gather|Social'}),
    #                  ('Class', None, {'label': 'Row +1'}),
    #                  ('Number', None, {'label': 'Row position +1'}),
    #                  ('name', Lookup.TRANSLATION, {'label': 'Skill'}),
    #                  ('description', Lookup.TRANSLATION, {'label': 'Description'}),
    #                  ('Upper_Limit', None, {'label': 'Max points you can apply'})]},
    #     {'name': 'Ability_Tree_New',
    #      'columns': [('Branch', None, {'label': 'Battle|Gather|Social'}),
    #                  ('Class', None, {'label': 'Row +1'}),
    #                  ('Number', None, {'label': 'Row position +1'}),
    #                  ('Name', Lookup.TRANSLATION),
    #                  ('Description', Lookup.TRANSLATION),
    #                  ('Upper_Limit', None, {'label': 'Max points you can apply'})]},
    #     {'name': 'Achievement',
    #      'columns': [('name', Lookup.TRANSLATION, {'label': 'Achievement'}),
    #                  ('description', Lookup.TRANSLATION, {'label': 'Description'}),
    #                  ('type', None, {'label': 'Action required'}),
    #                  ('checkType', None, {'label': 'Check for...'}),
    #                  ('mainpara', None, {'label': '...what'})]},
    #     {'name': 'Player_Operate',
    #      'columns': [('operate_type', None, {'label': 'Player action'}),
    #                  ('cp_cost', None, {'label': 'Stamina cost'}),
    #                  ('money_cost', None, {'label': 'Gol cost'}),
    #                  ('Ability_Exp', None, {'label': 'Ability experience earned*'}),
    #                  ('exp', None, {'label': 'Experience earned'})]},
    #     {'name': 'BookItem',
    #      'columns': [('title', Lookup.TRANSLATION, {'label': 'Book title'}),
    #                  ('content', Transform.TRANSLATION_UNDERSCORE_SPLIT, {'label': 'Book contents'})]},
    #     # NPC INTERACTIONS
    #     #     {'name': 'Actor',
    #     #      'columns': [('faction', Transform.FACTION, {'label': 'Character type'}),
    #     #                  ('name', Lookup.TRANSLATION, {'label': 'Character'}),
    #     #                  ('Lv', None, {'label': 'Character level'}),
    #     #                  ('IsBoss', Transform.BOOL, {'label': 'Is a boss?'})]},
    #     {'name': 'CloseInteract',
    #      'columns': [('ID', None, {'label': 'Interaction type 0=Hug?|1=Kiss?|2=Pet?|3=?|4=?'}),
    #                  ('Favor_Level', Lookup.FAVOR_RELATION, {'label': 'Friendship required'}),
    #                  ('CpCost', None, {'label': 'SP cost'}),
    #                  ('Favor_Value', None, {'label': 'Relationship Points earned'}),
    #                  ('TimesPerDay', None, {'label': 'Max interactions per day'}),
    #                  ('IsJealous', None, {'label': 'Cannot do if jealous*'}),
    #                  ('JealousStart', None, {'label': 'Causes jealousy*'})]},
    #     {'name': 'LoveDate',
    #      'columns': [('place', None, {'label': 'Date location'}),
    #                  ('time', None, {'label': 'Date time'}),
    #                  ('LikeAbilityNeed', None, {'label': 'Friendship required*'})]},
    #     {'name': 'PK_Multi',
    #      'columns': [('Name', Lookup.TRANSLATION, {'label': 'Character name'}),
    #                  ('Is_NPC', None, {'label': 'Is an NPC?'}),
    #                  ('HPPercentage', None, {'label': 'HP percentage*'}),
    #                  ('Buff_Player', None, {'label': 'Player buff*'}),
    #                  ('Buff_Npc', None, {'label': 'NPC buff*'}),
    #                  ('Fail_Favor', None, {'label': 'Player Victory RP'}),
    #                  ('Win_Favor', None, {'label': 'NPC Victory'}),
    #                  ('Begin_Dialog', Lookup.PK_DIALOG, {'lookup_split': ',',
    #                                                      'label': 'Start Line'}),
    #                  ('Win_Dialog', Lookup.PK_DIALOG, {'lookup_split': ',',
    #                                                    'label': 'Win Line'}),
    #                  ('Fail_Dialog', Lookup.PK_DIALOG, {'lookup_split': ',',
    #                                                     'label': 'Lose Line'}),
    #                  ('Defeated_Dialog', Lookup.PK_DIALOG, {'lookup_split': ',',
    #                                                         'label': 'Defeated Line'}),
    #                  ('PK_Drop', Lookup.ITEM_DROP_FIXED, {'label': 'Item Dropped'}),
    #                  ('PK_PlayerDropGold', None, {'label': 'Gols Dropped'}),
    #                  ('is_surrender', Transform.BOOL, {'label': 'Surrenders'}),
    #                  ('Surrender_Dialog', Lookup.PK_DIALOG, {'lookup_split': ',',
    #                                                          'label': 'Surrender Line'})]},
    #     {'name': 'Date_Event_new',
    #      'columns': [('event_name', Lookup.TRANSLATION, {'label': 'Date Activity'}),
    #                  ('is_date', Transform.BOOL, {'label': 'Is Date?'}),
    #                  ('RemoveWeather', None, {'label': 'Weather available'}),
    #                  ('RemoveInfo', None),
    #                  ('project_id', Lookup.DATE_PROJECT, {'label': 'Location',
    #                                                       'split': ","}),
    #                  ('MapIcon_Point', None, {'label': 'Map coordinates'}),
    #                  ('time', None, {'split': ",",
    #                                  'label': 'Hours'})]},
    #     {'name': 'Npc_resource_table',
    #      'columns': [('Id', Lookup.NPC_ID_TO_NAME, {'label': 'NPC name'}),
    #                  ('Coordinate', None, {'label': 'Map coordinates'}),
    #                  ('Rotation', None, {'label': 'Rotation'}),
    #                  ('Scene_name', None, {'label': 'Location'})]},
    #     # STORY
    #     {'name': 'Tips',
    #      'columns': [('translate_id', Lookup.TRANSLATION, {'label': 'Loading Screen Tips'})]},
    #     {'name': 'Newsstand_Content',
    #      'columns': [('Content_ID', None),
    #                  ('title_id', Lookup.TRANSLATION, {'label': 'Newspaper Title'}),
    #                  ('body_id', Lookup.TRANSLATION, {'label': 'Newspaper Content'})]},
    #     {'name': 'Mail',
    #      'columns': [('Title', Lookup.TRANSLATION, {'label': 'Mail title'}),
    #                  ('Content', Lookup.TRANSLATION, {'label': 'Mail message'}),
    #                  ('Attachment', Lookup.PROP, {'split': ':',
    #                                               'label': 'Attached item'}),
    #                  ('missionid', None, {'label': 'Related mission'}),
    #                  ('MissionAutoReceive', None, {'label': 'Mission attached'}),
    #                  ('appear', None, {'label': 'Envelope type'})]},
    #     {'name': 'SystemCaptureData',
    #      'columns': [('describe', Lookup.TRANSLATION, {'label': 'Photo cutscene caption'})]},
    #     {'name': 'SystemCaptureCollection',
    #      'columns': [('describe', Lookup.TRANSLATION, {'label': 'Photo collection caption'})]},
    #     # COMMISSIONS
    #     {'name': 'Order_Rewards',
    #      'columns': [('itemreq', Lookup.PROP, {'label': 'Item ordered',
    #                                            'quantity_post': '_', }),
    #                  ('gold', None, {'label': 'Gol reward'}),
    #                  ('relationship', None, {'label': 'RP reward'}),
    #                  ('workshoppt', None, {'label': 'Rank reward'}),
    #                  ('exp', None, {'label': 'Experience reward'}),
    #                  ('level', Lookup.GUILD_LEVEL, {'label': 'Commission level'}),
    #                  ('Deadline', None, {'label': 'Commission deadline'})]},
    #     {'name': 'Order_Req',
    #      'columns': [('ItemReq', Lookup.PROP, {'quantity_post': '_',
    #                                            'label': 'Requested item'}),
    #                  ('OrderID', None, {'label': 'Order ID'}),
    #                  ('Gold', None, {'label': 'Gols earned'}),
    #                  ('Relationship', None, {'label': 'Relationship Points earned'}),
    #                  ('WorkshopPT', None, {'label': 'Workshop Points earned'}),
    #                  ('Exp', None, {'label': 'Experience earned'}),
    #                  ('Level', None, {'label': 'Commission level'}),
    #                  ('Weight', None, {'label': 'Weight*'}),
    #                  ('Deadline', None, {'label': 'Commission deadline'})]},
    #     {'name': 'Order_ReqGroup',
    #      'columns': [('type', Lookup.REQ_TYPE, {'label': 'Order type*'}),
    #                  ('ID', None, {'label': 'ID'}),
    #                  ('req', Lookup.ORDER_REQ_ITEM, {'split': '_',
    #                                                  'label': 'Possible order items'})]},
    #     {'name': 'Order_Rewards',
    #      'columns': [('ItemReq', Lookup.PROP, {'quantity_post': '_',
    #                                            'label': 'Requested items'}),
    #                  ('OrderID', None, {'label': 'Order ID'}),
    #                  ('Gold', None, {'label': 'Gols earned'}),
    #                  ('Relationship', None, {'label': 'Relationship Points earned'}),
    #                  ('WorkshopPT', None, {'label': 'Workshop Points earned'}),
    #                  ('Exp', None, {'label': 'Experience earned'}),
    #                  ('Level', None, {'label': 'Commission level'}),
    #                  ('Weight', None, {'label': 'Weight*'}),
    #                  ('Deadline', None, {'label': 'Commission deadline'})]},
    #     {'name': 'Mission_Rewards',
    #      'columns': [('missionId', None, {'label': 'Mission ID'}),
    #                  ('missionId', Lookup.IN_MISSION_DIALOG, {'label': 'Mission dialogue'}),
    #                  ('money', None, {'label': 'Gol earned'}),
    #                  ('itemList', Lookup.PROP, {'split': ',',
    #                                             'quantity_post': '_',
    #                                             'label': 'Item earned'}),
    #                  ('favor', Lookup.NPC_ID_TO_NAME, {'split': ',',
    #                                                    'quantity_post': '_',
    #                                                    'label': 'Relationship Points earned'}),
    #                  ('Exp', None, {'label': 'Experience earned'}),
    #                  ('reputation', None, {'label': 'Workshop Points earned'})]},
    #     {'name': 'PlayerMission',  # player commissions from Civil Corps?
    #      'columns': [('Type', None),
    #                  ('Level', None),
    #                  ('Title', Lookup.TRANSLATION),
    #                  ('Des', Lookup.TRANSLATION),
    #                  ('Cost', None),
    #                  ('Count', None),
    #                  ('Time', None),
    #                  ('Rewards', Lookup.PROP),
    #                  ('DungeonName', None),
    #                  ('DungeonLevel', None),
    #                  ('Icon', None)]},
    #     {'name': 'mission_require',
    #      'columns': [('missionId', Lookup.IN_MISSION_DIALOG, {'label': 'Mission'}),
    #                  ('missionId', None, {'label': 'Mission ID'}),
    #                  ('requireItems', Lookup.PROP, {'split': ',',
    #                                                 'label': 'Mission items'})]},
    #     # RELATIONSHIP STATUS
    #     {'name': 'Favor_Grade',
    #      'columns': [('favor_grade_id', None, {'label': 'Favor Grade ID'}),
    #                  ('favor_range', None, {'label': 'Points'}),
    #                  ('grade_name', Lookup.TRANSLATION, {'label': 'Relationship Label'})]},
    #     #     {'name': 'Favor_Relation',
    #     #      'columns': [('Favor_Relation_ID', None, {'label': 'Relationship Label ID'}),
    #     #                  ('relation_name', Lookup.TRANSLATION, {'label': 'Relationship Label'}),
    #     #                  ('type', Transform.RELATION_TYPE, {'label': 'Romanceable?'}),
    #     #                  ('canplay', None, {'label': 'Play?'}),
    #     #                  ('canexpress', None, {'label': 'Confess?'}),
    #     #                  ('canpropose', None, {'label': 'Propose'}),
    #     #                  ('askbirthday', Transform.BOOL, {'label': 'Birthday Available?'}),
    #     #                  ('attendBirthdayParty', None),
    #     #                  ('askstory', Transform.BOOL, {'label': 'Bio Available?'})]},
    #     {'name': 'Favor_Influence',
    #      'columns': [('npc_id', Lookup.REPOSITORY, {'label': 'Name'}),
    #                  ('benefit', None, {'label': 'Perks'})]},
    #             NPC SPECIFIC INFO
    {'name': 'NpcRepository',
     'columns': [('Name', Lookup.TRANSLATION, {'label': 'NPC name'}),
                 #                  ('Identity', Lookup.TRANSLATION, {'label': 'Description at first meeting'}),
                 #                  ('Birthday', None, {'label': 'Birthday'}),
                 #                  ('Sex', None, {'label': 'Gender'}),
                 #                  ('date_selecttime', None, {'label': 'Date Times'}),
                 #                  ('LatestTime_Date_new', None, {'label': 'Latest possible date time'}),
                 #                  ('festivaltag', None, {'label': 'Festival participation'}),
                 #                  ('BreakUp', Lookup.FAVOR_RELATION, {'label': 'Can break up if...'}),
                 #                  ('Divorce', Lookup.FAVOR_RELATION, {'label': 'Can divorce if...'}),
                 #                  ('MinFavor', None, {'label': 'Lowest possible Relationship Points'}),
                 #                  ('Initial_Favor', None, {'label': 'Relationship Points at start of game'}),
                 #                  ('des_height', None, {'label': 'Height)'}),
                 #                  ('des_weight', None, {'label': 'Weight'}),
                 #                  ('des_background', Lookup.TRANSLATION, {'regex': r'\d+,(.*)',
                 #                                                          'label': 'Bio'}),
                 #                  ('des_influence', Lookup.FAVOR_RELATION, {'regex': r'(\d+),.*',
                 #                                                            'split': ';',
                 #                                                            'join': '\n',
                 #                                                            'label': 'Relationship'}),
                 #                  ('des_influence', Lookup.TRANSLATION, {'regex': r'\d+,(.*)',
                 #                                                         'split': ';',
                 #                                                         'join': '\n',
                 #                                                         'label': 'Perk'}),
                 ('giftid', Transform.GIFT_ID_EXCELLENT, {'label': 'Love'}),
                 ('giftid', Transform.GIFT_ID_LIKE, {'label': 'Like'}),
                 ('giftid', Transform.GIFT_ID_DISLIKE, {'label': 'Dislike'}),
                 ('giftid', Transform.GIFT_ID_HATE, {'label': 'Hate'}),
                 #                      ('giftid', Transform.GIFT_ID_CONFESSION, {'label': 'Confess'}),
                 #                      ('giftid', Transform.GIFT_ID_PROPOSE, {'label': 'Propose'}),
                 #                      ('giftid', Transform.GIFT_ID_REFUSE, {'label': 'Refuse'}),
                 #                      ('giftid', Transform.GIFT_ID_BREAK_UP, {'label': 'Break Up'}),
                 #                      ('giftid', Transform.GIFT_ID_DIVORCE, {'label': 'Divorce'}),
                 #                      ('giftid', Transform.GIFT_ID_JEALOUS, {'label': 'Jealous'}),
                 #                  ('Hate_List', Lookup.PROP, {'label': 'Possible hated items'}),
                 #                  ('Fame_Need', None),  # for now
                 #                  ('Food_GroupID', Lookup.FOOD_TAG_LIKES, {'label': 'Food Likes'}),
                 #                  ('Food_GroupID', Lookup.FOOD_TAG_DISLIKES, {'label': 'Food Dislikes'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_CONFESS_ACCEPT, {'label': 'Accepts Confession'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_CONFESS_REFUSE, {'label': 'Refuses Confession'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_CONFESS_LACKITEM,
                 #                   {'label': 'Lacks Item For Confession'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_BREAKUP, {'label': 'Breaks up'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PROPOSE_ACCEPT, {'label': 'Accepts Proposal'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PROPOSE_REFUSE, {'label': 'Refuses Proposal'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PROPOSE_LACKITEM,
                 #                   {'label': 'Lacks Item For Proposal'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_START, {'label': 'Play Start'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_MISSEDCONTRACT,
                 #                   {'label': 'Play Missed Contract'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_GIVEUP_HAPPY, {'label': 'Play Gives Up Happy'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_GIVEUP_UNHAPPY,
                 #                   {'label': 'Play Gives Up Unhappy'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_ACTIONVALUE_HAPPY,
                 #                   {'label': 'Play Action Value Happy'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_ACTIONVALUE_UNHAPPY,
                 #                   {'label': 'Play Action Value Unhappy'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_TIMEOUT_HAPPY, {'label': 'Play Time Out Happy'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_TIMEOUT_UNHAPPY,
                 #                   {'label': 'Play Time Out Unhappy'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_MOODVALUE, {'label': 'Play Mood Value'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_JEALOUS, {'label': 'Play Jealous'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_INTERRUPT, {'label': 'Play Interrupt'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_DATE_START, {'label': 'Date Start'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_DATE_MISSEDCONTRACT,
                 #                   {'label': 'Date Missed Contract'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_DATE_GIVEUP_HAPPY, {'label': 'Date Give Up Happy'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_DATE_GIVEUP_UNHAPPY,
                 #                   {'label': 'Date Give Up Unhappy'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_DATE_ACTIONVALUE_HAPPY,
                 #                   {'label': 'Date Action Value Happy'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_DATE_ACTIONVALUE_UNHAPPY,
                 #                   {'label': 'Date Action Value Unhappy'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_DATE_TIMEOUT_HAPPY, {'label': 'Date Time Out Happy'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_DATE_TIMEOUT_UNHAPPY,
                 #                   {'label': 'Date Time Out Unhappy'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_DATE_MOODVALUE, {'label': 'Date Mood Value'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_DATE_INTERRUPT, {'label': 'Date Interrupt'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_DATE_JEALOUS, {'label': 'Date Jealous'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_DATE_INVITE, {'label': 'Date Invite'}),
                 #                  ('Date_DialogID', Lookup.DATE_DIALOG_INVITE_REFUSE, {'label': 'Date Invite Refuse'}),
                 ('interact', None, {'label': 'Possible interactions'})]},
    {'name': 'Npc_relation_network',
     'columns': [('npc_Id', Lookup.NPC_ID_TO_NAME, {'split': ',',
                                                    'quantity_pre': '_',
                                                    'label': 'Name'}),
                 ('kinship', Lookup.NPC_ID_TO_NAME, {'split': ',',
                                                     'quantity_pre': '_',
                                                     'label': 'Family Name'}),
                 ('kinship', Lookup.KINSHIP_DATA, {'split': ',',
                                                   'quantity_post': '_',
                                                   'label': 'Family Relationship'}),
                 ('friendship', Lookup.NPC_ID_TO_NAME, {'split': ',',
                                                        'quantity_pre': '_',
                                                        'label': 'Friend Name'}),
                 ('friendship', Lookup.FAVOR_RELATION, {'split': ',',
                                                        'quantity_post': '_',
                                                        'label': 'Friendship'}),
                 ('emotion', Lookup.NPC_ID_TO_NAME, {'split': ',',
                                                     'quantity_pre': '_',
                                                     'label': 'Emotion Toward Name'}),
                 ('emotion', Lookup.EMOTION_DATA, {'split': ',',
                                                   'quantity_post': '_',
                                                   'label': 'Emotion'})]},
    #     {'name': 'Credits',
    #      'columns': [('IdentityEN', None, {'label': 'Character'}),
    #                  ('NameEN', None, {'label': 'Voice Actor'})]},
    #     # SHOPS
    #     {'name': 'Open_close_Door',
    #      'columns': [('ShopID', Lookup.STORE_ID, {'label': 'Shop'}),
    #                  ('OpenTime', None, {'label': 'Hours'}),
    #                  ('MappingScene', None, {'label': 'Location'})]},
    #     {'name': 'Store',
    #      'columns': [('Name_Id', Lookup.TRANSLATION, {'label': 'Shop Name'}),
    #                  ('Store_Id', Lookup.STORE_ID, {'label': 'Shop ID'}),
    #                  ('Goods_Id_Num', Lookup.PROP, {'split': ';',
    #                                                 'quantity_post': ',',
    #                                                 'label': 'Goods'}),
    #                  ('Currency', None, {'label': 'Shop Cash on Hand'}),
    #                  ('Goods_Spring', Lookup.PROP, {'split': ';',
    #                                                 'quantity_post': ',',
    #                                                 'label': 'Spring Goods'}),
    #                  ('Goods_Summer', Lookup.PROP, {'split': ';',
    #                                                 'quantity_post': ',',
    #                                                 'label': 'Summer Goods'}),
    #                  ('Goods_Autumn', Lookup.PROP, {'split': ';',
    #                                                 'quantity_post': ',',
    #                                                 'label': 'Autumn Goods'}),
    #                  ('Goods_Winter', Lookup.PROP, {'split': ';',
    #                                                 'quantity_post': ',',
    #                                                 'label': 'Winter Goods'}),
    #                  ('Goods_Weather', Lookup.PROP, {'split': ';',
    #                                                  'quantity_post': ',',
    #                                                  'label': 'Weather-Based Goods Sunny|Cloudy|RainDay|SnowDay|Overcast|HeavySnowDay'}),
    #                  ('OpenTime', None, {'label': 'Hours'})]},
    #     #     {'name': 'Store_product',
    #     #      'columns': [('product_id', None, {'label': 'Product ID'}),
    #     #                  ('item_id', Lookup.PROP, {'label': 'Shop item'}),
    #     #                  ('currency', Lookup.PROP, {'label': 'Non-gol currency required'}),
    #     #                  ('exchange_rate', None, {'label': 'Exchange rate'}),
    #     #                  ('require_mission', None, {'label': 'Prerequisite mission'})]},  # for now
    #     {'name': 'Research_Choice',
    #      'columns': [('ID', None, {'label': 'Research ID'}),
    #                  ('CD_Count', None, {'label': 'Data Discs turned in'}),
    #                  ('CD_Extra', None, {'label': 'CD extra*'}),
    #                  ('Creation_List', Lookup.RESEARCH_LIST_ITEM_LIST, {'split': ',',
    #                                                                     'quantity_post': '_',
    #                                                                     'label': 'Items to research'}),
    #                  ('Creation_List', Lookup.RESEARCH_LIST_RESEARCH_SPEED, {'split': ',',
    #                                                                          'quantity_post': '_',
    #                                                                          'label': 'Speed of research'})]},
    #     # ANIMALS
    #     {'name': 'AnimalFarm_Food',
    #      'columns': [('id', Lookup.PROP, {'label': 'Farm food'}),
    #                  ('growpoint', None, {'label': 'Growth Points'})]},
    #     {'name': 'AnimalFarm_Animal',
    #      'columns': [('farmtype', Lookup.ANIMAL_FARM_HOUSE, {'label': 'Animal building'}),
    #                  ('CubId', Lookup.PROP, {'label': 'Baby animal'}),
    #                  ('Name', Lookup.TRANSLATION, {'label': 'Adult animal'}),
    #                  ('TotalPoint', None, {'label': 'Total point*'}),
    #                  ('StandardPoint', None, {'label': 'Standard point*'}),
    #                  ('ProductionCycle', None, {'label': 'Production cycle*'}),
    #                  ('touchcoef', None, {'label': 'Effect of petting animal*'}),
    #                  ('FoodRalation', Lookup.PROP, {'split': ';',
    #                                                 'quantity_post': ',',
    #                                                 'label': 'Favorite food*'}),
    #                  ('FoodCanEat', None, {'label': 'Food eaten per day'}),
    #                  ('ShitNum', None, {'label': 'Feces made per day'}),
    #                  ('SpeedRegion', None, {'label': 'Movement speed of animal*'}),
    #                  ('Price', None, {'label': 'Market price'}),
    #                  ('Product', Lookup.ITEM_DROP_FIXED, {'label': 'Daily animal drops'}),
    #                  ('Product_Extra', Lookup.ITEM_DROP_FIXED, {'label': 'Extra animal drops'})]},
    #     {'name': 'AnimalFarm_House',
    #      'columns': [('ItemId', Lookup.PROP, {'label': 'Animal building'}),
    #                  ('CapacityAnimal', None, {'label': 'Animal capacity'}),
    #                  ('CapacityFood', None, {'label': 'Food trough capactiy'}),
    #                  ('CapacityProduct', None, {'label': 'Animal product capacity'}),
    #                  ('CapacityShit', None, {'label': 'Feces capacity'}),
    #                  ('ShitReducePoint', None, {'label': 'Happiness reduced by feces*'}),
    #                  ('ShitScale', None, {'label': 'Feces size scale'})]},
    #     {'name': 'RidableCommodity',
    #      'columns': [('RidableInfoID', Lookup.RIDABLE_INFO_ID, {'label': 'Purchaseable animal'}),
    #                  ('SpeedPercentage', None, {'label': 'Speed %'}),
    #                  ('VpRecoverPercentage', None, {'label': 'VP recovery %'}),
    #                  ('VpConsumeJumpPercentage', None, {'label': 'VP used by jump %'}),
    #                  ('VpConsumeFastRunPercentage', None, {'label': 'VP used by sprint %'}),
    #                  ('Price', None, {'label': 'Market price'}),
    #                  ('Day', None, {'label': 'Rental length'}),
    #                  ('loyalty', None, {'label': 'Loyalty to player'})]},
    #     {'name': 'RidableFoodData',
    #      'columns': [('Id', Lookup.PROP, {'label': 'Possible food for mounts'})]},
    #     {'name': 'RidableInfo',
    #      'columns': [('RidableInfoID', Lookup.RIDABLE_INFO_ID, {'label': 'Mountable animal'}),
    #                  ('InitNickName', Lookup.TRANSLATION, {'label': 'Inital nickname'}),
    #                  ('InitialSpeed', None, {'label': 'Initial speed'}),
    #                  ('SpeedGrowthLimit', None, {'label': 'Best trained speed'}),
    #                  ('InitialVpRecover', None, {'label': 'Initial VP recovery'}),
    #                  ('VpRecoverLimit', None, {'label': 'Best trained VP recovery'}),
    #                  ('InitialVpConsumeJump', None, {'label': 'Initial VP used by jump'}),
    #                  ('JumpingPowerLimit', None, {'label': 'Best trained VP used by jump'}),
    #                  ('InitialVpConsumeFastRun', None, {'label': 'Initial VP used by sprint'}),
    #                  ('VpConsumeFastRunLimit', None, {'label': 'Best trained VP used by sprint'}),
    #                  ('FoodFillingDegree', Lookup.PROP, {'split': ';',
    #                                                      'quantity_post': ',',
    #                                                      'label': 'Hunger satisfaction from food'}),
    #                  ('FeedDegree', None, {'label': 'Feed degree*'}),
    #                  ('ShitNum', None, {'label': 'Feces made per day'}),
    #                  ('PassScore', None, {'label': 'Score required to capture*'}),
    #                  ('Bait', Lookup.PROP, {'split': ';',
    #                                         'quantity_post': ',',
    #                                         'label': 'Required bait to capture'}),
    #                  ('BasePrice', None, {'label': 'Value*'})]},
    #     #     FOOD
    #     {'name': 'Cook_Book',
    #      'columns': [('Food', Lookup.PROP, {'label': 'Recipe'}),
    #                  ('Material', [Lookup.PROP, Lookup.STORE_PRODUCT, Lookup.COOK_TAG_NAME], {'quantity_post': '_',
    #                                                                                           'split': ';',
    #                                                                                           'label': 'Ingredients'})]},
    #     {'name': 'Cook_TagList',
    #      'association': {'column': 'Tag',
    #                      'split': ',',
    #                      'name': ('ID', Lookup.PROP),
    #                      'tag_names': {0: 'Random Ingredients',
    #                                    1: 'Fish',
    #                                    2: 'Meat',
    #                                    3: 'Grains',
    #                                    4: 'Fruits',
    #                                    102: 'Fruits',
    #                                    5: 'Vegetables',
    #                                    6: 'Sides',
    #                                    7: 'Spicy Seasoning',
    #                                    8: 'TBD',
    #                                    9: 'Sweet Seasoning',
    #                                    10: 'Salty Seasoning',
    #                                    100: 'Light Seasoning',
    #                                    101: 'Any Seasoning',
    #                                    103: 'Sugary Ingredients',
    #                                    104: 'TBD',
    #                                    105: 'Mushrooms'}}},
    #     {'name': 'Food_Menu',
    #      'columns': [('food_type_name', None, {'label': 'Restaurant course'}),
    #                  ('food_name', Lookup.TRANSLATION, {'label': 'Food name'}),
    #                  ('Food_Season', None, {'label': 'Season available'}),
    #                  ('Food_Sale', None, {'label': 'Market price'}),
    #                  ('food_score', None, {'label': 'Mood Points on dates if neutral*'}),
    #                  ('Like_Coefficient', None, {'label': 'Mood Points on dates if liked*'}),
    #                  ('DisLike_Coefficient', None, {'label': 'Mood points on dates if disliked*'}),
    #                  ('Food_Tag', Lookup.FOOD_DIALOG, {'split': ',',
    #                                                    'label': 'Food tags'}),
    #                  ('Icon', None, {'label': 'Food image name'})]},
    #     {'name': 'Cook_AckList',
    #      'columns': [('Food', Lookup.PROP, {'label': 'Recipe owned by Ack'}),
    #                  ('Material', Lookup.PROP, {'split': ';',
    #                                             'quantity_post': '_',
    #                                             'label': 'Required ingredients'})]},
    #     {'name': 'Item_food',
    #      'columns': [('Food_Id', Lookup.PROP, {'label': 'Food'}),
    #                  ('hp_Value', None, {'label': 'Restores HP',
    #                                      'ignore_if_equals': ['0']}),
    #                  ('Comfort_Value', None, {'label': 'Restores SP',
    #                                           'ignore_if_equals': ['0']}),
    #                  ('Add_HpMax', None, {'label': 'HP Max +',
    #                                       'ignore_if_equals': ['0']}),
    #                  ('Add_CpMax', None, {'label': 'SP Max +',
    #                                       'ignore_if_equals': ['0']}),
    #                  ('Add_Attack', None, {'label': 'Attack +',
    #                                        'ignore_if_equals': ['0']}),
    #                  ('Add_Defence', None, {'label': 'Defense +',
    #                                         'ignore_if_equals': ['0']}),
    #                  ('Add_Crit', None, {'label': 'Critical Chance +',
    #                                      'ignore_if_equals': ['0']}),
    #                  ('Add_AntiCrit', None, {'label': 'Resilience +',
    #                                          'ignore_if_equals': ['0']}),
    #                  ('Buff_Id', None, {'label': 'Adds Other Buff?'}),  # need to define these!
    #                  ('Remove_Buff_Id', None, {'label': 'Removes Other Buff?'})]},
    #     {'name': 'Cook_TagList',
    #      'association': {'column': ('Tag', Lookup.COOK_TAG_NAME),
    #                      'split': ',',
    #                      'name': ('ID', Lookup.PROP)}},
    #     {'name': 'Cook_TagList',
    #      'columns': [('ID', Lookup.PROP, {'label': 'Cooked food'}),
    #                  ('Tag', Lookup.COOK_TAG_NAME, {'split': ',',
    #                                                 'label': 'Associated tags'})]},
    #     # ASSEMBLY
    #     {'name': 'CreationFactory_Upgrade',
    #      'columns': [('item_id', Lookup.PROP, {'label': 'Assembly Station'}),
    #                  ('Level', None, {'label': 'Assembly Station level'}),
    #                  ('money_cost', None, {'label': 'Gols'}),
    #                  ('item_cost', Lookup.PROP, {'label': 'Materials',
    #                                              'quantity_post': ',',
    #                                              'split': ";"}),
    #                  ('farm_level_need', None, {'label': 'Farm Level Required'}),
    #                  ('des', Lookup.TRANSLATION, {'label': 'Description'})]},
    #     {'name': 'Creation_List',
    #      'columns': [('Item_ID', Lookup.PROP, {'label': 'Assembled item'}),
    #                  ('Level', None, {'label': 'Assembly level required (add +1)'}),
    #                  ('Name', Lookup.TRANSLATION, {'label': 'Assembled item'}),
    #                  ('Time', None, {'label': 'Crafting time'}),
    #                  ('Exp', None, {'label': 'Experience reward'}),
    #                  ('PartList', Lookup.PARTS_LIST, {'split': ',',
    #                                                   'label': 'Parts required'})]},
    #     # WORKTABLE
    #     {'name': 'Synthesis_Machines',
    #      'columns': [('Name', Lookup.TRANSLATION, {'label': 'Crafting station'}),
    #                  ('Level', None, {'label': 'Level related to similar stations (+1)'}),
    #                  ('FactoryCapacity', None, {'label': 'Factory capacity*'}),
    #                  ('fuel_id', Lookup.PROP, {'label': 'Fuel required'}),
    #                  ('fuel_max', None, {'label': 'Fuel Max'}),
    #                  ('minutes', None, {'label': 'Minutes of fuel at max*'}),
    #                  ('itemcount_max', None, {'label': 'Maximum items queued'}),
    #                  ('Weather_Coef', None, {'label': 'Effect of weather on production*'}),
    #                  ('Season_Coef', None, {'label': 'Effect of season on production*'})]},
    #     {'name': 'Synthesis_Upgrade',
    #      'columns': [('Item_ID', Lookup.PROP, {'label': 'Crafting station'}),
    #                  ('Level', None, {'label': 'Worktable level (+1)'}),
    #                  ('Item_Cost', Lookup.PROP, {'split': ';',
    #                                              'quantity_post': ',',
    #                                              'label': 'Required materials to upgrade'}),
    #                  ('Money_Cost', None, {'label': 'Gol cost of upgrade'})]},
    #     {'name': 'Synthesis_table',
    #      'columns': [('Name', Lookup.TRANSLATION, {'label': 'Item name'}),
    #                  ('Item_Id', Lookup.PROP, {'label': 'Item ID'}),
    #                  ('Item_Id', Lookup.PROP_ITEM_TYPE, {'label': 'Item Type'}),
    #                  ('Furniture_Id', Lookup.PROP, {'label': 'Furniture ID'}),
    #                  ('Data_one_id', Lookup.PROP, {'label': '1st ingredient'}),
    #                  ('Data_one_number', None, {'label': '1st ingredient amount'}),
    #                  ('Data_two_id', Lookup.PROP, {'label': '2nd ingredient'}),
    #                  ('Data_two_number', None, {'label': '2nd ingredient amount'}),
    #                  ('Data_three_id', Lookup.PROP, {'label': '3rd ingredient'}),
    #                  ('Data_three_number', None, {'label': '3rd ingredient amount'}),
    #                  ('NotAutomable', None, {'label': 'Can be automated in factory?'}),
    #                  ('Product_list', Lookup.ITEM_DROP_FIXED, {'split': ':',
    #                                                            'label': 'Product list fixed*'}),
    #                  ('Product_list', Lookup.ITEM_DROP_RANDOM, {'split': ':',
    #                                                             'label': 'Product list random*'}),
    #                  ('Extra_props_id', Lookup.PROP, {'label': 'Extra products*'}),
    #                  ('Additional_item_probability_and_number', None, {
    #                      'label': 'Probability and amount of extra products*'}),
    #                  ('Time', None, {'label': 'Crafting time'}),
    #                  ('Exp', None, {'label': 'Experience earned'}),
    #                  ('Cost', None, {'label': 'Cost*'}),
    #                  ('Unlock_Level', None, {'label': 'Required crafting station level'}),
    #                  ('Plug_In_Type', None, {'label': 'Plug In Type*'}),
    #                  ('Item_Label', None, {'label': 'Item label*'})]},
    #     {'name': 'Farm_Machine',
    #      'columns': [('Type', None, {'label': 'Type*'}),
    #                  ('Name', Lookup.TRANSLATION, {'label': 'Crafting station/machine'}),
    #                  ('Time_Max', None, {'label': 'Maximum time running*'}),
    #                  ('Load_Number', None, {'label': 'Maximum orders placed*'}),
    #                  ('Buff_Coef', None, {'label': 'Buff coefficient*'})]},
    #     {'name': 'Farm_NormalItem',
    #      'columns': [('FarmNormalItemType', None, {'label': 'Item type: 0=no effect, 1=crafting'}),
    #                  ('ID', Lookup.PROP, {'label': 'Item name'}),
    #                  ('CanUsePower', None, {'label': 'Uses fuel/power?*'})]},
    #     # FACTORY
    #     {'name': 'Factory_PerformanceLevel',
    #      'columns': [('Level', None, {'label': 'Level of performance efficiency'}),
    #                  ('Speed', None, {'label': 'Speed of factory performance'}),
    #                  ('Cost', Lookup.PROP, {'quantity_post': ',',
    #                                         'label': 'Upgrade cost'})]},
    #     {'name': 'Factory_TransmissionLevel',
    #      'columns': [('Level', None, {'label': 'Level of transmission efficiency'}),
    #                  ('Speed', None, {'label': 'Speed of factory transmission'}),
    #                  ('Cost', Lookup.PROP, {'quantity_post': ',',
    #                                         'label': 'Upgrade cost'})]},
    #     # RANK
    #     {'name': 'GuildLevel',
    #      'columns': [('Exp', None, {'label': 'Total Workshop Points required*'}),
    #                  ('Level', None, {'label': 'Overall Workshop Level'})]},
    #     {'name': 'GuildRank',
    #      'columns': [('Name', Lookup.TRANSLATION, {'label': 'Workshop name'}),
    #                  ('Owner', Lookup.TRANSLATION, {'label': 'Builder name'}),
    #                  ('Point_Day', None, {'label': 'Workshop Points earned per day'}),
    #                  ('Origin_Point', None, {'label': 'Initial Workshop Points'})]},
    #     {'name': 'GuildRewards',
    #      'columns': [('ID', None, {'label': 'ID*'}),
    #                  ('RewardsID', [Lookup.ITEM_DROP_FIXED, Lookup.ITEM_DROP_RANDOM], {'split': ',',
    #                                                                                    'label': 'End of season rewards'}),
    #                  ('AnnualRewardsID', [Lookup.ITEM_DROP_FIXED, Lookup.ITEM_DROP_RANDOM], {'split': ',',
    #                                                                                          'label': 'Annual rewards'})]},
    # MUSEUM
    {'name': 'ExchangeReq',
     'columns': [('npcId', Lookup.REPOSITORY, {'label': 'NPC'}),
                 ('supplyPool', Lookup.PROP, {'split': ',',
                                              'label': 'Offers'}),
                 ('reqPool', Lookup.PROP, {'split': ',',
                                           'label': 'Requests'}),
                 ('exhibitPool', Lookup.PROP, {'split': ',',
                                               'label': 'Favorite donations'})]},
    #     {'name': 'ExchangeFragment',
    #      'columns': [('itemId', Lookup.PROP, {'label': 'Requested relic piece'}),
    #                  ('value', None, {'label': 'Value*'}),
    #                  ('existDays', None, {'label': 'Days posted'}),
    #                  ('favorReward', None, {'label': 'RP reward'})]},
    #     {'name': 'ExhibitData',
    #      'columns': [('itemId', Lookup.PROP, {'label': 'Exhibit item'}),
    #                  ('size', Lookup.EXHIBIT_SIZE, {'label': 'Size of exhibit'}),
    #                  ('type', Lookup.EXHIBIT_TYPE_NAME, {'label': 'Type of exhibit'}),
    #                  ('type', Lookup.EXHIBIT_TYPE_DESCRIPTION, {'label': 'Description of exhibit type'}),
    #                  ('description', Lookup.TRANSLATION, {'label': 'Item description'}),
    #                  ('workshopPT', None, {'label': 'Rank reward'})]},
    #     {'name': 'ExhibitReward',
    #      'columns': [('Count', None, {'label': 'Donations made'}),
    #                  ('Rewards', Lookup.PROP, {'split': ',',
    #                                            'quantity_post': '_',
    #                                            'label': 'Donation Rewards'})]},
    #     {'name': 'Repair_Table',
    #      'columns': [('Item_Id', Lookup.PROP, {'label': 'Item to recover'}),
    #                  ('Parts_List', Lookup.PROP, {'split': ',',
    #                                               'label': 'Required pieces'}),
    #                  ('Time', None, {'label': 'Crafting time'}),
    #                  ('CD_Cost', None, {'label': 'Data Disc cost for recovery'})]},
    #     #     HOLIDAYS
    #     {'name': 'Festival_Gift',
    #      'columns': [('npc_name', Lookup.TRANSLATION, {'label': 'NPC gift giver'}),
    #                  ('translationid', Lookup.TRANSLATION, {'label': 'Note from NPC'}),
    #                  ('gift_drop', Lookup.PROP, {'label': 'Gift',
    #                                              'quantity_post': '_'}),
    #                  ('Gift_Model_Path', None, {'label': 'Present type*'})]},
    #     {'name': 'Festival_HotPot',
    #      'columns': [('HotPot_ID', None, {'label': 'NPC name'}),
    #                  ('ItemGroup', Lookup.PROP, {'split': ';',
    #                                              'quantity_post': ',',
    #                                              'label': 'Wanted hotpot ingredients'}),
    #                  ('MaxHotValue', None, {'label': 'Spicyness quota*'})]},
    #     {'name': 'HarvestDayMelon',
    #      'columns': [('Props_Id', Lookup.PROP, {'label': 'Harvest Day item*'}),
    #                  ('Weight', None, {'label': 'Weight*'})]},
    #     {'name': 'Item_PutDown',
    #      'columns': [('ID', Lookup.PROP, {'label': 'Day of Memories item*'})]},
    #     {'name': 'SnowBallMatchReward',
    #      'columns': [('Rank', None, {'label': 'Rank in Snowball Fight'}),
    #                  ('Reward_Day1', Lookup.PROP, {'split': ',',
    #                                                'quantity_post': '_',
    #                                                'label': 'Day 1 rewards'}),
    #                  ('Reward_Day2', Lookup.PROP, {'split': ',',
    #                                                'quantity_post': '_',
    #                                                'label': 'Day 2 rewards'})]},
    #     {'name': 'StageItemList',  # don't know what this is yet
    #      'columns': [('Type', None),
    #                  ('ID', Lookup.PROP),
    #                  ('Quantity', None),
    #                  ('PriceBase', None),
    #                  ('ExtraRewards', None)]},
    #     {'name': 'StagePrice',  # don't know what this is yet
    #      'columns': [('Type', None),
    #                  ('PriceStart2', None),
    #                  ('PriceIncrease', None),
    #                  ('NumLimit', None)]},
    #     # MINIGAMES
    #     {'name': 'Draw_Pattern',
    #      'columns': [('model_path', None, {'label': 'Pattern name'}),
    #                  ('name', Lookup.TRANSLATION, {'label': 'Pattern ID'}),
    #                  ('Score', None, {'label': 'Score for success'}),
    #                  ('timelimit', None, {'label': 'Time limit'})]},
    #     {'name': 'FindDiffGame_Items',
    #      'columns': [('itemid', Lookup.PROP, {'label': 'Item to inspect'}),
    #                  ('diffcount', None, {'label': 'Number of differences to find'}),
    #                  ('operatelimit', None, {'label': 'Tries'}),
    #                  ('timelimit', None, {'label': 'Time limit'}),
    #                  ('Difficulty', Lookup.GUILD_LEVEL, {'label': 'Difficulty'}),
    #                  ('workshoppt', None, {'label': 'Workshop points'})]},
    #     {'name': 'FireBalloon',
    #      'columns': [('pathname', Lookup.TRANSLATION, {'label': 'Ride route'}),
    #                  ('needtime', None, {'label': 'Trip length'}),
    #                  ('Cost', None, {'label': 'Gol cost'}),
    #                  ('SeasonLimit', None, {'label': 'Seasons available'}),
    #                  ('RemoveWeather', None, {'label': 'Weather available'}),
    #                  ('addmood', None, {'label': 'Mood Points earned'}),
    #                  ('addcp', None, {'label': 'SP restored'})]},
    #     {'name': 'GameRewards_Dart',
    #      'columns': [('score', None, {'label': 'Darts score'}),
    #                  ('Mood', None, {'label': 'Mood points earned'}),
    #                  ('rewards', Lookup.ITEM_DROP_RANDOM, {'label': 'Random rewards dropped',
    #                                                        'quantity_post': ','}),
    #                  ('rewards', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of random rewards dropped'})]},
    #     {'name': 'GameRewards_ShootBalloon',
    #      'columns': [('Score', None, {'label': 'Balloon score'}),
    #                  ('Mood', None, {'label': 'Mood Points earned'}),
    #                  ('Rewards', Lookup.ITEM_DROP_RANDOM, {'label': 'Random rewards dropped',
    #                                                        'quantity_post': ','}),
    #                  ('Rewards', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of random rewards dropped'})]},
    #     {'name': 'GameRewards_CatchCow',
    #      'columns': [('cow', Lookup.PROP, {'quantity_post': ',',
    #                                        'label': 'Reward for catching a Cow'}),
    #                  ('smallcow', Lookup.PROP, {'quantity_post': ',',
    #                                             'label': 'Reward for catching a Calf'}),
    #                  ('horse', Lookup.PROP, {'quantity_post': ',',
    #                                          'label': 'Reward for catching a Horse'}),
    #                  ('sheep', Lookup.PROP, {'quantity_post': ',',
    #                                          'label': 'Reward for catching a Sheep'})]},
    #     {'name': 'LookStar_Constellation',
    #      'columns': [('Name', Lookup.TRANSLATION, {'label': 'Constellation name'}),
    #                  ('startime', None, {'label': 'Time limit'}),
    #                  ('completefavor', None, {'label': 'Mood Points earned'})]},
    #     {'name': 'Slot_Rewards',
    #      'columns': [('Type', None, {'label': 'Image'}),
    #                  ('Rewards_1', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Bet 5 Badges reward'}),
    #                  ('Rewards_2', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Bet 10 Badges reward'}),
    #                  ('Rewards_3', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Bet 50 Badges reward'}),
    #                  ('Mood', None, {'label': 'Mood Points earned'})]},
    #     {'name': 'Slot_Rate',
    #      'columns': [('Index_List', None, {'label': 'Matches'}),
    #                  ('Type', None, {'label': 'Wheel image ID'}),  # for now
    #                  ('Rate', None, {'label': 'Wheel spin rate'})]},
    #     {'name': 'FindDiffGame_Rules',
    #      'columns': [('workshopLevel', Lookup.GUILD_LEVEL, {'label': 'Player Workshop Level'}),
    #                  ('diffItemId', Lookup.FIND_DIFF_GAME_ITEMS, {'split': ',',
    #                                                               'label': 'Items can inspect'}),
    #                  ('rewards', Transform.REWARDS, {'split': ';',
    #                                                  'label': 'Rewards*'})]},
    #     {'name': 'SwingGame',
    #      'columns': [('SwingGame_ID', Lookup.SWING_ID_TO_NAME, {'label': 'NPC name'}),
    #                  ('ForceMin', None, {'label': 'Force min*'}),
    #                  ('ForceMax', None, {'label': 'Force max*'}),
    #                  ('MatchTime', None, {'label': 'Time for player action*'}),
    #                  ('GameTime', None, {'label': 'Time to play minigame'})]},
    #     {'name': 'TeeterGame',
    #      'columns': [('TeeterGame_ID', Lookup.TEETER_ID_TO_NAME, {'label': 'NPC name'}),
    #                  ('HeightRange', None, {'label': 'Height range*'}),
    #                  ('HeightFavor', None, {'label': 'Desired height*'}),
    #                  ('HeightFly', None, {'label': 'How high NPC can fly*'}),
    #                  ('HeightFlyRate', None, {'label': 'Rate at which NPC will fly*'})]},
    #     # FISH
    #     {'name': 'FishList',
    #      'columns': [('id', Lookup.PROP, {'label': 'Fish species'}),
    #                  ('score', None, {'label': 'Score*'}),
    #                  ('TakeUpTime', None, {'label': 'Time taken to catch*'}),
    #                  ('ComplianceAbility', None, {'label': 'Difficulty to catch*'}),
    #                  ('Exp', None, {'label': 'Experience earned'}),
    #                  ('weight_range', None, {'label': 'Weight of fish'}),
    #                  ('length_range', None, {'label': 'Length of fish'})]},
    #     {'name': 'Fish_Att',
    #      'columns': [('itemid', Lookup.PROP, {'label': 'Fish type'}),
    #                  ('hpmax', None, {'label': 'Maximum HP'}),
    #                  ('survivaldays', None, {'label': 'Lifespan in tank*'}),
    #                  ('productioncycle', None, {'label': 'Production cycle*'})]},
    #     {'name': 'Fish_Food',
    #      'columns': [('itemid', Lookup.PROP, {'label': 'Fish food'}),
    #                  ('hpmax', None, {'label': 'HP restored by food'})]},
    #     {'name': 'Fish_Jar',
    #      'columns': [('itemid', Lookup.PROP, {'label': 'Fish tank'}),
    #                  ('fishamount', None, {'label': 'Fish capacity*'}),
    #                  ('fishamount_max', None, {'label': 'Fish capacity*'})]},
    #     {'name': 'Fish',
    #      'columns': [('ID', None, {'label': 'Fishing spot'}),
    #                  ('Rub_Drop', Lookup.PROP, {'split': ';',
    #                                             'quantity_post': ',',
    #                                             'label': 'Rubbish dropped'}),
    #                  ('Fish_Drop', Lookup.PROP, {'split': ';',
    #                                              'quantity_post': ',',
    #                                              'label': 'Fish available on normal days'}),
    #                  ('Match_Fish_Drop', Lookup.PROP, {'split': ';',
    #                                                    'quantity_post': ',',
    #                                                    'label': 'Fish available during Fishing Day'})]},
    #     {'name': 'FishMatchRewards',
    #      'columns': [('FishMatchRange', None, {'label': 'Rank on Fishing Day'}),
    #                  ('Rewards', Lookup.PROP, {'quantity_post': '_',
    #                                            'label': 'Rewards'})]},
    #     {'name': 'FishingMatchReward',
    #      'columns': [('Rank', None, {'label': 'Rank on Fishing Day'}),
    #                  ('Reward', Lookup.PROP, {'split': ',',
    #                                           'quantity_post': '_',
    #                                           'label': 'Rewards'})]},
    #     {'name': 'Fish_Ability',
    #      'columns': [('NPCID', Lookup.NPC_ID_TO_NAME, {'label': 'Competitor on Fishing Day'}),
    #                  ('FishingAbility', None, {'label': 'Talent in fishing'})]},
    #     # HAZARDOUS RUINS
    #     {'name': 'The_Chest',
    #      'columns': [('scene_name', None, {'label': 'Location'}),
    #                  ('Coordinate', None, {'label': 'Map coordinates'}),
    #                  ('drop_group', Lookup.ITEM_DROP_FIXED, {'label': 'Chest Items',
    #                                                          'quantity_post': ','}),
    #                  ('drop_group', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Items inside chest'}),
    #                  ('ID', None, {'label': 'Chest ID'}),
    #                  ('Model_Path', None, {'label': 'Type of chest'})]},
    #     {'name': 'Dungeon_Chest',
    #      'columns': [('drop_group', [Lookup.ITEM_DROP_FIXED, Lookup.ITEM_DROP_RANDOM], {'label': 'Chest Items',
    #                                                                                     'split': ';',
    #                                                                                     'quantity_post': ','})]},
    #     {'name': 'Trial_Dungeon',
    #      'columns': [('Description', Lookup.TRANSLATION, {'label': 'Ruin name'}),
    #                  ('ID', None, {'label': 'Level'}),
    #                  ('Spend_Time', None, {'label': 'Time required to complete level'}),
    #                  ('Grade', None, {'label': 'Recommended player level'}),
    #                  ('Little_MonsterID', Lookup.DUNGEON_MONSTER, {'split': ';',
    #                                                                'quantity_post': ',',
    #                                                                'label': 'Common enemies'}),
    #                  ('Boss_ID', Lookup.DUNGEON_MONSTER, {'split': ';',
    #                                                       'quantity_post': ',',
    #                                                       'label': 'Boss enemies'}),
    #                  ('Common_ChestID', Lookup.DUNGEON_CHEST_FIXED, {'split': ';',
    #                                                                  'quantity_post': ',',
    #                                                                  'label': 'Common chest fixed drops'}),
    #                  ('Common_ChestID', Lookup.DUNGEON_CHEST_RANDOM, {'split': ';',
    #                                                                   'quantity_post': ',',
    #                                                                   'label': 'Common chest random drops'}),
    #                  ('Best_ChestID', Lookup.DUNGEON_CHEST_FIXED, {'split': ';',
    #                                                                'quantity_post': ',',
    #                                                                'label': 'Special chest fixed drops'}),
    #                  ('Best_ChestID', Lookup.DUNGEON_CHEST_RANDOM, {'split': ';',
    #                                                                 'quantity_post': ',',
    #                                                                 'label': 'Special chest random drops'}),
    #                  ('First_Reward', Lookup.PROP, {'split': ',',
    #                                                 'quantity_post': '_',
    #                                                 'label': 'Reward for first time through'}),
    #                  ('Reward', Lookup.PROP, {'split': ',',
    #                                           'quantity_post': '_',
    #                                           'label': 'Reward after first time'}),
    #                  ('Life', None)]},
    #     {'name': 'Trial_DungeonN',
    #      'columns': [('Description', Lookup.TRANSLATION, {'label': 'Ruin name'}),
    #                  ('Level', None, {'label': 'Level'}),
    #                  ('Spend_Time', None, {'label': 'Time required to complete level'}),
    #                  ('Grade', None, {'label': 'Recommended player level'}),
    #                  ('Little_MonsterID', Lookup.DUNGEON_MONSTER, {'split': ';',
    #                                                                'quantity_post': ',',
    #                                                                'label': 'Common enemies'}),
    #                  ('Boss_ID', Lookup.DUNGEON_MONSTER, {'split': ';',
    #                                                       'quantity_post': ',',
    #                                                       'label': 'Boss enemies'}),
    #                  ('Common_ChestID', Lookup.DUNGEON_CHEST_FIXED, {'split': ';',
    #                                                                  'quantity_post': ',',
    #                                                                  'label': 'Common chest fixed drops'}),
    #                  ('Common_ChestID', Lookup.DUNGEON_CHEST_RANDOM, {'split': ';',
    #                                                                   'quantity_post': ',',
    #                                                                   'label': 'Common chest random drops'}),
    #                  ('Best_ChestID', Lookup.DUNGEON_CHEST_FIXED, {'split': ';',
    #                                                                'quantity_post': ',',
    #                                                                'label': 'Special chest fixed drops'}),
    #                  ('Best_ChestID', Lookup.DUNGEON_CHEST_RANDOM, {'split': ';',
    #                                                                 'quantity_post': ',',
    #                                                                 'label': 'Special chest random drops'}),
    #                  ('First_Reward', Lookup.PROP, {'split': ',',
    #                                                 'quantity_post': '_',
    #                                                 'label': 'Reward for first time through'}),
    #                  ('Reward', Lookup.PROP, {'split': ',',
    #                                           'quantity_post': '_',
    #                                           'label': 'Reward after first time'}),
    #                  ('Life', None)]},
    #     {'name': 'Trial_Dungeon_Monster',
    #      'columns': [('ActorID', Lookup.ACTOR_TYPE, {'label': 'Monster name'}),
    #                  ('Add_Time', None, {'label': 'Defeated time bonus in time trial*'})]},
    #     {'name': 'Random_Dungeon',
    #      'columns': [('ID', None),
    #                  ('Lv', None),
    #                  ('Type', None),
    #                  ('LittleMonsterID', Lookup.TRIAL_DUNGEON_MONSTER, {'split': ';',  # for now
    #                                                                     'quantity_post': ','}),  # for now
    #                  ('BossID', Lookup.TRIAL_DUNGEON_MONSTER, {'split': ';',  # for now
    #                                                            'quantity_post': ','}),  # for now
    #                  ('LeadID', Lookup.TRIAL_DUNGEON_MONSTER, {'split': ';',  # for now
    #                                                            'quantity_post': ','}),  # for now
    #                  ('SpecialMonsterID', Lookup.TRIAL_DUNGEON_MONSTER, {'split': ';',  # for now
    #                                                                      'quantity_post': ','})]},  # for now
    #     #  HOUSE
    #     {'name': 'Furniture_Table',
    #      'columns': [('id', Lookup.PROP, {'label': 'Furniture Item'}),
    #                  ('Size', None, {'label': 'Size'}),
    #                  ('X_size', None, {'label': 'X-size'}),
    #                  ('Y_size', None, {'label': 'Y-size'}),
    #                  ('Z_size', None, {'label': 'Z-size/height'}),
    #                  ('On_Wall', None, {'label': 'Placed on wall?'}),
    #                  ('feature_des', Lookup.TRANSLATION, {'label': 'Stat Description'}),
    #                  ('feature_type', None, {'label': 'Stat Boost'})]},
    #     {'name': 'InteractItem',
    #      'columns': [('ID', Lookup.PROP, {'label': 'Item that can be interacted with*'})]},
    #     {'name': 'Farm_Item',
    #      'columns': [('ID', Lookup.PROP, {'label': 'Item that can remove placed items'}),
    #                  ('Area', None, {'label': 'Range of item'})]},
    #     {'name': 'Item_StorageBox',
    #      'columns': [('id', Lookup.PROP, {'label': 'Item'}),
    #                  ('Count', None, {'label': 'Storage spaces available'}),
    #                  ('npcinteract', None, {'label': 'NPCs  can use it?'})]},
    #     {'name': 'Item_Floor',
    #      'columns': [('ID', Lookup.PROP, {'label': 'Flooring item'}),
    #                  ('Type', None, {'label': 'Type'})]},
    #     {'name': 'HomeConstruction',
    #      'columns': [('Type', None, {'label': 'Building type'}),
    #                  ('Level', None, {'label': 'Building level'}),
    #                  ('Name', Lookup.TRANSLATION, {'label': 'Building name'}),
    #                  ('ItemId', Lookup.PROP, {'split': ',',
    #                                           'label': 'Building Item ID'}),
    #                  ('costitemlist', Lookup.PROP, {'label': 'Supplies Needed',
    #                                                 'split': ';',
    #                                                 'quantity_post': ','}),
    #                  ('costgol', None, {'label': 'Gol Cost'}),
    #                  ('ModifyCostItemList', Lookup.PROP, {'split': ';',
    #                                                       'quantity_post': ',',
    #                                                       'label': 'Items required to modify*'}),
    #                  ('ModifyCostGol', None, {'label': 'Cost to modify*'})]},
    #     {'name': 'HomeLevel',
    #      'columns': [('Level', None, {'label': 'Home Level'}),
    #                  ('Item_ID', Lookup.PROP, {'label': 'Home ID'}),
    #                  ('money_cost', None, {'label': 'Gol Cost'}),
    #                  ('item_cost', Lookup.PROP, {'label': 'Supplies Needed'}),
    #                  ('attr_max', None, {'label': 'Attribute Max',
    #                                      'split': ';'}),
    #                  ('extra_des', Lookup.TRANSLATION, {'label': 'Additional Desc'})]},
    #     {'name': 'HomeMaterial',
    #      'columns': [('Id', Lookup.PROP, {'label': 'Home design item name'}),
    #                  ('Type', None, {'label': 'Type of item'}),
    #                  ('Level', None, {'label': 'House level required'}),
    #                  ('Item_Cost', Lookup.PROP, {'split': ';',
    #                                              'quantity_post': ',',
    #                                              'label': 'Item cost'}),
    #                  ('Money', None, {'label': 'Gol cost'})]},
    #     {'name': 'HomePlugin',
    #      'columns': [('Name', Lookup.TRANSLATION, {'label': 'Special building name'}),
    #                  ('Desc', Lookup.TRANSLATION, {'label': 'Description'}),
    #                  ('Unlock_Level', None, {'label': 'House level required*'}),
    #                  ('Item_Need', Lookup.PROP, {'split': ';',
    #                                              'quantity_post': ',',
    #                                              'label': 'Items required'}),
    #                  ('Item_Recycle', Lookup.PROP, {'split': ';',
    #                                                 'quantity_post': ',',
    #                                                 'label': 'Recycled products*'}),
    #                  ('Gold_Need', None, {'label': 'Gol cost'})]},
    #     # GENERAL ITEMS
    #     {'name': 'Props_total_table',
    #      'association': {'column': 'Tag_List',
    #                      'split': ',',
    #                      'name': ('props_name', Lookup.TRANSLATION),
    #                      'tag_names': {55: 'Universal Hates',
    #                                    54: 'Universal Dislikes',
    #                                    101: 'Universal Likes',
    #                                    116: 'Universal Likes',
    #                                    117: 'Universal Likes',
    #                                    49: 'Universal Exceptions',
    #                                    113: 'Universal Exceptions',
    #                                    63: 'Pinky Likes',
    #                                    64: 'Pinky Likes',
    #                                    65: 'Pinky Likes',
    #                                    67: 'Scraps Likes',
    #                                    6: 'Special Likes',
    #                                    7: 'Special Likes',
    #                                    9: 'Special Likes',
    #                                    10: 'Special Likes',
    #                                    11: 'Special Likes',
    #                                    13: 'Special Likes',
    #                                    14: 'Special Likes',
    #                                    15: 'Special Likes',
    #                                    16: 'Special Likes',
    #                                    17: 'Special Likes',
    #                                    19: 'Special Likes',
    #                                    22: 'Special Likes',
    #                                    24: 'Special Likes',
    #                                    39: 'Special Likes',
    #                                    42: 'Special Likes',
    #                                    43: 'Special Likes',
    #                                    45: 'Special Likes/Loves',
    #                                    46: 'Special Likes',
    #                                    47: 'Special Likes',
    #                                    102: 'Special Likes',
    #                                    109: 'Special Likes',
    #                                    110: 'Special Likes',
    #                                    111: 'Special Likes',
    #                                    112: 'Special Likes',
    #                                    114: 'Special Likes',
    #                                    12: 'Special Loves',
    #                                    32: 'Special Loves',
    #                                    41: 'Special Loves',
    #                                    57: 'Special Loves',
    #                                    62: 'Special Loves',
    #                                    70: 'Special Loves',
    #                                    71: 'Special Loves',
    #                                    72: 'Special Loves',
    #                                    104: 'Special Loves',
    #                                    105: 'Special Loves',
    #                                    106: 'Special Loves',
    #                                    107: 'Special Loves',
    #                                    108: 'Special Loves',
    #                                    300: 'Special Loves',
    #                                    301: 'Special Loves',
    #                                    302: 'Special Loves',
    #                                    303: 'Special Loves',
    #                                    304: 'Special Loves',
    #                                    305: 'Special Loves',
    #                                    401: 'Relationship - Break Up',
    #                                    400: 'Relationship - Confession',
    #                                    402: 'Relationship - Divorce',
    #                                    404: 'Relationship - Jealous',
    #                                    405: 'Relationship - Pet Name',
    #                                    2: 'Items - Swords',
    #                                    3: 'Items - Pickaxes',
    #                                    5: 'Items - Axes',
    #                                    18: 'Items - Tea',
    #                                    21: 'Items - Drinks',
    #                                    25: 'Items - Fishing',
    #                                    26: 'Items - Bouquets',
    #                                    27: 'Items - Enemy Drops',
    #                                    28: 'Items - Furs',
    #                                    29: 'Items - Bones',
    #                                    31: 'Items - Seasonings',
    #                                    33: 'Items - Fiber/Thread',
    #                                    36: 'Items - Ores',
    #                                    44: 'Items - Fruits',
    #                                    48: 'Items - Tree Drops',
    #                                    50: 'Items - Vegetables',
    #                                    58: 'Items - Paintings',
    #                                    66: 'Items - Rare Fish', }}},
    #     {'name': 'Props_total_table',
    #      'columns': [('Item_Type', None, {'label': 'Item Type'}),
    #                  ('Intend_Type', [Lookup.PLAYER_INTEND_NO_TARGET,
    #                                   Lookup.PLAYER_INTEND_HOME_REGION], {'label': 'Used for'}),
    #                  ('Props_Id', Lookup.PROP, {'label': 'Item'}),
    #                  ('Props_Explain_One', Lookup.TRANSLATION, {'label': 'Description'}),
    #                  ('Effect', Lookup.TRANSLATION, {'label': 'Additional Description'}),
    #                  ('User_Level', None, {'label': 'Armor Level'}),
    #                  ('Buy_Price', None, {'label': 'Market Price'}),
    #                  ('Sell_Price', None, {'label': 'Value'}),
    #                  ('SourceDes', Lookup.ITEM_FROM, {'split': ',',
    #                                                   'label': 'Obtained from'}),
    #                  ('InVersion', None, {'label': 'Version It Appeared In'}),
    #                  ('Skill_List', Lookup.ABILITY_TREE_NEW, {'split': ',',
    #                                                           'label': 'Related Skill'}),
    #                  ('Energy', None, {'label': 'Energy*'}),
    #                  ('HotValue', None, {'label': 'Spicyness'}),
    #                  ('IsGift', Transform.BOOL, {'label': 'Is a gift?'}),
    #                  ('gift_tagid', Transform.GIFT_TAGID, {'label': 'Gift Tag'}),
    #                  ('Rare_Lv', None, {'label': 'Rare Level*'}),
    #                  ('Tag_List', None, {'split': ',',
    #                                      'label': 'Prop Tags'}),
    #                  ('Props_Id', Lookup.FARM_COMMON_SUITABLE_FLOOR, {'label': 'Suitable Flooring'}),
    #                  ('Props_Id', Lookup.FARM_COMMON_AREA, {'label': 'Common Area*'}),
    #                  ('Props_Id', Lookup.FARM_COMMON_UNABLE_FACE_TO_WALL, {'label': 'Unable to face wall*'}),
    #                  ('Props_Id', Lookup.FURNITURE_TABLE_SIZE, {'label': 'Size*'}),
    #                  ('Props_Id', Lookup.FURNITURE_TABLE_FEATURE_TYPE, {'label': 'Placed Bonus'}),
    #                  ('Props_Id', Lookup.EXHIBIT_DATA_SIZE, {'label': 'Exhibit Size'}),
    #                  ('Props_Id', Lookup.EXHIBIT_DATA_TYPE, {'label': 'Exhibit Type'}),
    #                  ('Props_Id', Lookup.EXHIBIT_WORKSHOP_PT, {'label': 'Museum Rank Points'}),
    #                  ('Props_Id', Lookup.REPAIR_TABLE_PARTS_LIST, {'label': 'Recovery Parts',
    #                                                                'split': ','}),
    #                  ('Props_Id', Lookup.REPAIR_TABLE_TIME, {'label': 'Recovery Time'}),
    #                  ('Props_Id', Lookup.REPAIR_TABLE_CD_COST, {'label': 'Recovery Cost'}),
    #                  ('Props_Id', Lookup.ITEM_FOOD_HP_VALUE, {'label': 'HP Restored'}),
    #                  ('Props_Id', Lookup.ITEM_FOOD_COMFORT_VALUE, {'label': 'Stamina Restored'}),
    #                  ('Props_Id', Lookup.ITEM_FOOD_ADD_HP_MAX, {'label': 'HP Max +'}),
    #                  ('Props_Id', Lookup.ITEM_FOOD_ADD_ATTACK, {'label': 'Attack +'}),
    #                  ('Props_Id', Lookup.ITEM_FOOD_ADD_DEFENCE, {'label': 'Defense +'}),
    #                  ('Props_Id', Lookup.ITEM_FOOD_ADD_CRIT, {'label': 'Critical Chance +'}),
    #                  ('Props_Id', Lookup.ITEM_FOOD_ADD_ANTICRIT, {'label': 'Resilience +'}),
    #                  ('Props_Id', Lookup.ITEM_FOOD_BUFF_ID, {'label': 'Adds Other Buff?'}),
    #                  ('Props_Id', Lookup.ITEM_FOOD_REMOVE_BUFF_ID, {'label': 'Removes Other Buff?'}),
    #                  ('Props_Id', Lookup.RECYCLE_TABLE_DROP_ID, {'split': ';',
    #                                                              'quantity_post': ',',
    #                                                              'label': 'Recycle Drops'})]},
    #     {'name': 'Props_total_table',
    #      'association': {'column': 'Recycle_Tag',
    #                      'split': ',',
    #                      'name': ('Props_Id', Lookup.PROP),
    #                      'tag_names': {0: 'TBD'}}},
    #     {'name': 'Item_Box',
    #      'columns': [('ID', Lookup.PROP),
    #                  ('DropID', Lookup.ITEM_DROP_FIXED, {'label': 'Fixed Drop',
    #                                                      'ignore_if_equals': ['0']}),
    #                  ('DropID', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Fixed Drop #',
    #                                                             'ignore_if_equals': ['0']}),
    #                  ('DropID', Lookup.ITEM_DROP_RANDOM, {'label': 'Random Drop',
    #                                                       'ignore_if_equals': ['0']}),
    #                  ('DropID', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Random Drop #',
    #                                                              'ignore_if_equals': ['0']})]},
    #     {'name': 'Item_equipment',
    #      'columns': [('Equipment_Id', Lookup.PROP, {'label': 'Gift tag'}),
    #                  ('Equipment_Type', None),  # for now
    #                  ('ATK', None, {'label': 'Attack'}),
    #                  ('Defense', None),
    #                  ('Health', None, {'label': 'HP'}),
    #                  ('CpMax', None, {'label': 'SP'}),
    #                  ('Crit', None, {'label': 'Critical Chance'}),
    #                  ('MeleeCriticalAmount', None, {'label': 'Melee Critical Damage*'}),
    #                  ('RangeCriticalAmount', None, {'label': 'Ranged Critical Damage*'}),
    #                  ('Move_Speed', None, {'label': 'Movement speed'}),
    #                  ('AntiCritical', None, {'label': 'Resilience'}),
    #                  ('Attack_Distance', None, {'label': 'Attack distance*'}),
    #                  ('Dig_Range', None, {'label': 'Digging range*'}),
    #                  ('DigIntensity', None, {'label': 'Digging intensity*'}),
    #                  ('Cp_Cost', None, {'label': 'Stamina cost'}),
    #                  ('Date_Force', None, {'label': 'Extra Action Points'})]},
    #     {'name': 'Cabinet',
    #      'columns': [('ID', Lookup.PROP, {'label': 'Cabinet type'}),
    #                  ('MaxCount', None, {'label': 'Capacity'}),
    #                  ('TypeList', Lookup.CABINET_TYPE_LIST, {'label': 'Type of contents'})]},
    #     {'name': 'Cabinet_ItemList',
    #      'columns': [('ID', Lookup.PROP, {'label': 'Cabinet item'}),
    #                  ('Type', Lookup.CABINET_TYPE_LIST, {'label': 'Cabinet content type'})]},
    #     {'name': 'Herbs',
    #      'columns': [('Drop_Model_Path', None, {'label': 'Item type*'}),
    #                  ('ID', None, {'label': 'Herb ID'}),
    #                  ('Drop_Group', Lookup.ITEM_DROP_FIXED, {'label': 'Fixed herbs dropped'}),
    #                  ('Drop_Group', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of fixed herbs dropped'}),
    #                  ('Drop_Group', Lookup.ITEM_DROP_RANDOM, {'label': 'Random herbs dropped'}),
    #                  ('Drop_Group', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of random herbs dropped'}),
    #                  ('Scene', None, {'label': 'Area found'}),
    #                  ('Season', None, {'label': 'Season found'}),
    #                  ('DayorNight', None, {'label': 'Time found'}),
    #                  ('Weather', None, {'label': 'Weather found'})]},
    #     {'name': 'random_herbs',
    #      'columns': [('Drop_Item_ID', Lookup.PROP, {'label': 'Items dropped'}),
    #                  ('Drop_Group', Lookup.ITEM_DROP_FIXED, {'label': 'Fixed herbs dropped'}),
    #                  ('Drop_Group', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of fixed herbs dropped'}),
    #                  ('Drop_Group', Lookup.ITEM_DROP_RANDOM, {'label': 'Random herbs dropped'}),
    #                  ('Drop_Group', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of random herbs dropped'})]},
    #     {'name': 'Place_Item',
    #      'columns': [('Prefab_Path', None, {'label': 'Location*'}),
    #                  ('Defence', None, {'label': 'Defense'}),
    #                  ('HP_Max', None, {'label': 'Max HP'}),
    #                  ('Drop_ID', Lookup.ITEM_DROP_FIXED, {'label': 'Fixed drops'}),
    #                  ('Drop_ID', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of fixed drops'}),
    #                  ('Drop_ID', Lookup.ITEM_DROP_RANDOM, {'label': 'Random drops'}),
    #                  ('Drop_ID', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of random drops'}),
    #                  ('Extra_ID', None, {'label': 'Extra item drops'}),
    #                  ('Extra_Rate', None, {'label': 'Rate of extra items dropped'}),
    #                  ('Extra_DropID', Lookup.ITEM_DROP_FIXED, {'label': 'Other extra item fixed drops'}),
    #                  ('Extra_DropID', Lookup.ITEM_DROP_FIXED_NUMBER, {
    #                      'label': 'Number of other extra item fixed drops'}),
    #                  ('Extra_DropID', Lookup.ITEM_DROP_RANDOM, {'label': 'Other extra item random drops'}),
    #                  ('Extra_DropID', Lookup.ITEM_DROP_RANDOM_NUMBER, {
    #                      'label': 'Number of other extra item random drops'}),
    #                  ('Extra_DropRate', None, {'label': 'Rate of other extra items dropped'})]},
    #     # GARDEN
    #     {'name': 'Item_seed',
    #      'columns': [('ID', Lookup.PROP, {'label': 'Seed name'}),
    #                  ('Plant_Name', Lookup.TRANSLATION, {'label': 'Crop or tree name'}),
    #                  ('Food_Point', None, {'label': 'Food Points*'}),
    #                  ('Food_Happy', None, {'label': 'Fertilizer required to be happy*'}),
    #                  ('Drop_Happy', Lookup.ITEM_DROP_RANDOM, {'label': 'Crops dropped when well fertilized'}),
    #                  ('Drop_Happy', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of well fertilized drops'})]},
    #     {'name': 'PlantBox_Data',
    #      'columns': [('ID', Lookup.PROP, {'label': 'Planter box name'}),
    #                  ('Fuel_Max', None, {'label': 'Fuel capacity'}),
    #                  ('size', None, {'label': 'Size of planter box'})]},
    #     {'name': 'PlantBox_Food',
    #      'columns': [('ID', Lookup.PROP, {'label': 'Fertilizer item'}),
    #                  ('Food_Point', None, {'label': 'Food Points given to plants per fertilizer'})]},
    #     # RECYCLE MACHINE
    #     {'name': 'Recycle_Table',
    #      'columns': [('Item_Id', Lookup.PROP, {'label': 'Item to be recycled'}),
    #                  ('Drop_Id', Lookup.ITEM_DROP_FIXED, {'label': 'Recycle drops*'}),
    #                  ('Drop_Id', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of drops*'}),
    #                  ('Time', None, {'label': 'Recycling time'})]},
    #     # WORLD LOCATIONS
    #     {'name': 'SceneItemTransformBinding',
    #      'columns': [('id', None, {'label': 'ID'}),
    #                  ('Type', None, {'label': 'Type of map object'}),
    #                  ('sceneName', None, {'label': 'Region of map object'}),
    #                  ('flagName', None, {'label': 'Map object name'})]},
    #     {'name': 'GameConfig',
    #      'columns': [('scenenameid', Lookup.TRANSLATION, {'label': 'Location name'}),
    #                  ('UnitySceneName', None, {'label': 'Unity name (behind the scenes)'}),
    #                  ('Radius', None, {'label': 'Radius of area'}),
    #                  ('PosinWorldMap', None, {'label': 'Position on world map'}),
    #                  ('PortalinPos', None, {'label': 'PortalinPos*'}),
    #                  ('PortalinRot', None, {'label': 'PortalinRot*'}),
    #                  ('PortalOutRot', None, {'label': 'PortalOutRot*'}),
    #                  ('OpenTime', None, {'label': 'Open Hours'}),
    #                  ('MapCenter', None, {'label': 'MapCenter*'}),
    #                  ('PortalOutPos', None, {'label': 'PortalOutPos*'})]},
    #     {'name': 'MapIcon',
    #      'columns': [('Text', Lookup.TRANSLATION, {'label': 'Location name'}),
    #                  ('Building_Pos', None, {'label': 'Map coordinates'})]},
    #     {'name': 'MapIconData',
    #      'columns': [('MapIconName', None, {'label': 'Map icon name'}),
    #                  ('MapIconID', None, {'label': 'Map icon ID'}),
    #                  ('SpritePath', None, {'label': 'Name of icon image sprite'}),
    #                  ('Layer', None, {'label': 'Map layer on which icon is located'})]},
    #     # CLOTHING MODIFICATIONS
    #     {'name': 'SewingList',
    #      'columns': [('Id', Lookup.PROP, {'label': 'Clothing name'}),
    #                  ('Id', Lookup.PROPS_ID_TO_USER_LEVEL, {'label': 'Armor level'}),
    #                  ('Id', Lookup.PROPS_ID_TO_ATK, {'label': 'Attack'}),
    #                  ('Id', Lookup.PROPS_ID_TO_DEFENSE, {'label': 'Defense'}),
    #                  ('Id', Lookup.PROPS_ID_TO_HEALTH, {'label': 'HP'}),
    #                  ('Id', Lookup.PROPS_ID_TO_CPMAX, {'label': 'SP'}),
    #                  ('Id', Lookup.PROPS_ID_TO_CRIT, {'label': 'Critical Chance'}),
    #                  ('Id', Lookup.PROPS_ID_TO_MELEE_CRITICAL, {'label': 'Melee Critical Damage*'}),
    #                  ('Id', Lookup.PROPS_ID_TO_RANGE_CRITICAL, {'label': 'Ranged Critical Damage*'}),
    #                  ('Id', Lookup.PROPS_ID_TO_ANTICRITICAL, {'label': 'Resilience'}),
    #                  ('Id', Lookup.PROPS_ID_TO_DATE_FORCE, {'label': 'Action Points'}),
    #                  ('Type', None, {'label': '1=Head|2=Torso|3=Legs'}),
    #                  ('CostList', Lookup.PROP, {'quantity_post': '_',
    #                                             'label': 'Cost to upgrade'})]},
    #     # DIALOGUE
    #     {'name': 'Conversation_Talk',
    #      'columns': [('SegmentID', None, {'label': 'Segment ID'}),
    #                  ('SegmentID', Lookup.CONVERSATION_SEGMENT_SPEAKER, {'ignore_if_equals': ['-1', '-2', '-3'],
    #                                                                      'label': 'NPC speaking'}),
    #                  ('SegmentID', Lookup.CONVERSATION_SEGMENT_BASE, {'split': ',',
    #                                                                   'label': 'Spoken line'})]},
    #     {'name': 'Conversation_list',
    #      'columns': [('dialogue_id', None, {'label': 'Dialogue ID'}),
    #                  ('dialogue_id', Lookup.CONVERSATION_BASE, {'split': ',',
    #                                                             'label': 'Dialogue (split by ,)'}),
    #                  ('dialogue_id', Lookup.CONVERSATION_BASE, {'split': ';',
    #                                                             'label': 'Dialogue (split by ;)'}),
    #                  ('Task_id', None, {'label': 'Task ID'})]},
    #     {'name': 'Task_dialogue',
    #      'columns': [('Id', None, {'label': 'Task dialogue ID'}),
    #                  ('dialogue', Lookup.TRANSLATION, {'label': 'Dialogue'})]},
    #     {'name': 'InMission_Dialog',
    #      'columns': [('Dialog', None, {'label': 'Dialog ID'}),
    #                  ('MissionID', None, {'label': 'Mission ID'}),
    #                  ('Dialog', Lookup.CONVERSATION_BASE, {'split': ';',
    #                                                        'label': 'Dialogue when in middle of mission'})]},
    #     {'name': 'Conversation_Segment',
    #      'columns': [('SegmentID', None, {'label': 'Segment ID'}),
    #                  ('BaseID', Lookup.CONVERSATION_BASE, {'split': ',',
    #                                                        'label': 'Dialogue'}),
    #                  ('SpeakerID', Lookup.NPC_ID_TO_NAME, {'ignore_if_equals': ['-1', '-2', '-3'],
    #                                                        'label': 'NPC speaking'})]},
    #     # BEHIND THE SCENES
    #     {'name': 'Changlist',
    #      'columns': [('Time', None, {'label': 'Date of change'}),
    #                  ('ID', Lookup.TRANSLATION, {'label': 'Change list'})]},
    #     {'name': 'ItemFrom',
    #      'columns': [('Id', None),
    #                  ('Des', Lookup.TRANSLATION)]},
    #     {'name': 'Weather',
    #      'columns': [('ID', None, {'label': 'Sunny|Cloudy|RainDay|SnowDay|Overcast|HeavySnowDay'}),
    #                  ('Week1', None, {'split': ',',
    #                                   'quantity_post': '_'}),
    #                  ('Week2', None, {'split': ',',
    #                                   'quantity_post': '_'}),
    #                  ('Week3', None, {'split': ',',
    #                                   'quantity_post': '_'}),
    #                  ('Week4', None, {'split': ',',
    #                                   'quantity_post': '_'})]},
    #     {'name': 'Translation_hint',
    #      'columns': [('ID', None),
    #                  ('English', None)]},
    #     {'name': 'Gift',
    #      'columns': [('Gift_ID', Transform.GIFT_ID),
    #                  ('Favor_Excellent', Transform.FAVOR),
    #                  ('Favor_Like', Transform.FAVOR),
    #                  ('Favor_Dislike', Transform.FAVOR),
    #                  ('Favor_Hate', Transform.FAVOR),
    #                  ('Favor_Neutral', Transform.FAVOR)]},
]


# MAPPINGS = [
#     {'name': 'Wish',  # I need wishitemgroup to also list the needrelation and addfavor. Right now the number listed with it represents how much they like that item, ish. Might need "value" from wishitem too.
#      'columns': [('npcid', Lookup.NPC_ID_TO_NAME),
#                  ('wishitemgroup', Lookup.WISH_ITEM_GROUP, {'label': 'Wish Items',
#                                                             'split': ';',
#                                                             'quantity_post': ','})]},
#     # I'd like to show the range in the quantity for
#     # ITEM_DROP... the thing where you said you need to count how many commas
#     # there are. See the very last cell in row 26 of Item_drop table
#     {'name': 'Quarrying',
#      'columns': [('Defence', None, {'label': 'Rock defense'}),
#                  ('HP_Max', None, {'label': 'Rock max HP'}),
#                  ('Drop_ID', Lookup.ITEM_DROP_FIXED, {'label': 'Fixed drops from rocks'}),
#                  ('Drop_ID', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of fixed drops from rocks'}),
#                  ('Drop_ID', Lookup.ITEM_DROP_RANDOM, {'label': 'Random drops from rocks'}),
#                  ('Drop_ID', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of random drops from rocks'})]},
#     {'name': 'TreeChop',
#      'columns': [('TreeID', None, {'label': 'Tree name'}),
#                  ('Tree_Prefab', None),
#                  ('Act_Type', None),
#                  ('Tree_Radius', None, {'label': 'Tree radius'}),
#                  ('Defence', None, {'label': 'Tree defense'}),
#                  ('HP_Min', None, {'label': 'Tree min HP'}),
#                  ('HP_Max', None, {'label': 'Tree max HP'}),
#                  ('Chop_DropID', Lookup.ITEM_DROP_FIXED, {'label': 'Drops from chopping'}),
#                  ('Chop_DropID', Lookup.ITEM_DROP_FIXED_NUMBER),
#                  ('Chop_DropID', Lookup.ITEM_DROP_RANDOM),
#                  ('Chop_DropID', Lookup.ITEM_DROP_RANDOM_NUMBER),
#                  ('Extra_ChopDropRate', None, {'label': 'Rate of extra chop drops',
#                                                'ignore_if_equals': ['0']}),
#                  ('Extra_ChopDropID', Lookup.ITEM_DROP_FIXED, {'label': 'Extra chop drops',
#                                                                'ignore_if_equals': ['0']}),
#                  ('Extra_ChopDropID', Lookup.ITEM_DROP_FIXED_NUMBER),
#                  ('Extra_ChopDropID', Lookup.ITEM_DROP_RANDOM),
#                  ('Extra_ChopDropID', Lookup.ITEM_DROP_RANDOM_NUMBER),
#                  ('Stub_DropID', Lookup.ITEM_DROP_FIXED, {'label': 'Drops from ?stub'}),
#                  ('Stub_DropID', Lookup.ITEM_DROP_FIXED_NUMBER),
#                  ('Stub_DropID', Lookup.ITEM_DROP_RANDOM),
#                  ('Stub_DropID', Lookup.ITEM_DROP_RANDOM_NUMBER),
#                  ('Extra_StubDropRate', None, {'label': 'Rate of extra ?stub drops',
#                                                'ignore_if_equals': ['0']}),
#                  ('Extra_StubDropID', Lookup.ITEM_DROP_FIXED, {'label': 'Extra ?stub drops',
#                                                                'ignore_if_equals': ['0']}),
#                  ('Extra_StubDropID', Lookup.ITEM_DROP_FIXED_NUMBER),
#                  ('Extra_StubDropID', Lookup.ITEM_DROP_RANDOM),
#                  ('Extra_StubDropID', Lookup.ITEM_DROP_RANDOM_NUMBER),
#                  ('Kick_DropID', Lookup.ITEM_DROP_FIXED, {'label': 'Drops from kicking trees'}),
#                  ('Kick_DropID', Lookup.ITEM_DROP_FIXED_NUMBER),
#                  ('Kick_DropID', Lookup.ITEM_DROP_RANDOM),
#                  ('Kick_DropID', Lookup.ITEM_DROP_RANDOM_NUMBER)]},
#     {'name': 'Part_List',
#      'columns': [('Part_ID', Lookup.PARTS_LIST),  # what is the difference between this table and CreationPart_List?
#                  ('Part_Des', Lookup.TRANSLATION),
#                  ('Item_List', None)]},
#     {'name': 'General_Dialog',
#      'columns': [('NPCid', Lookup.REPOSITORY, {'label': 'NPC name',
#                                                'ignore_if_equals': ['-1']}),
#                  ('First_Dialog', Lookup.CONVERSATION_BASE, {
#                      'label': 'Dialogue upon first meeting', 'ignore_if_equals': ['-1']}),
#                  #                  ('Area_Dialog', Transform.DIALOG, {'label': 'Area'}), # need transform here
#                  #                  ('Weather_Dialog', Transform.DIALOG, {'label': 'Weather'}), # need transform here
#                  #                  ('Season_Dialog', Transform.DIALOG, {'label': 'Season'}), # need transform here
#                  ('Social_Dialog', Transform.SOCIAL_DIALOG, {'label': 'Typical day dialogue'}),
#                  #                  ('Festival_Dialog', Transform.DIALOG, {'label': 'Festival'}), # need transform here
#                  ('Jealous_Dialog', Lookup.CONVERSATION_BASE, {'label': 'Jealous dialogue',
#                                                                'ignore_if_equals': ['-1']}),
#                  ('Unhappy_Dialog', Lookup.CONVERSATION_BASE, {'label': 'Unhappy dialogue',
#                                                                'split': ';',
#                                                                'ignore_if_equals': ['-1']})]},
#     {'name': 'Store_4_0',
#      'columns': [('name_id', Lookup.TRANSLATION, {'label': 'Shop name'}),
#                  ('product_general', Lookup.STORE_PRODUCT, {'split': ',',
#                                                             'quantity_post': '_',
#                                                             'allow_multiple_lookup_results': True,
#                                                             'label': 'General products'}),  # how to handle a range of quantities?
#                  ('product_season', Transform.PRODUCT_SEASON, {'split': ';',
#                                                                'label': 'Seasonal products'}),
#                  ('product_weather', Transform.PRODUCT_WEATHER, {'split': ';',
#                                                                  'label': 'Weather-limited products Sunny|Cloudy|RainDay|SnowDay|Overcast|HeavySnowDay'}),
#                  ('text_welcome', Lookup.TRANSLATION, {'label': 'Greeting dialogue'}),
#                  ('text_buy', Lookup.TRANSLATION, {'label': 'Successful purchase dialogue'}),
#                  ('text_buy_fail', Lookup.TRANSLATION, {'label': 'Out of stock dialogue'}),
#                  ('text_recycle', Lookup.TRANSLATION, {'label': 'Successful buyback'}),
#                  ('text_limited', Lookup.TRANSLATION, {'label': 'Failed buyback (no money, overstocked)'}),
#                  ('text_dislike', Lookup.TRANSLATION, {'label': 'Failed buyback (not interested)'}),
#                  ('open_time', None, {'label': 'Shop hours'}),
#                  ('add_money', None, {'label': 'Add money*'}),
#                  ('start_money', None, {'label': 'New day cash on hand*'})]},
#     {'name': 'Res_Point',
#      'columns': [('Area', None, {'label': 'Resource Box shop*'}),
#                  ('Lv', None, {'label': 'Level of resources desired'}),
#                  ('Cost', None, {'label': 'Cost of upgrade'}),
#                  ('PriceLimit', None, {'label': 'Price limit*'}),
#                  ('ProductsId', Lookup.PROP, {'split': ';',
#                                               'label': 'Resources delivered'}),
#                  ('Products_Ratio', Lookup.PROP, {'split': ';',  # how to consider range in quantity
#                                                   'quantity_post': '_',
#                                                   'label': 'Ratio of products'}),
#                  ('Products_Extra', Lookup.PROP, {'split': ',',  # ignore what's in front of semicolon
#                                                   'quantity_post': '_',
#                                                   'label': 'Extra products'}),
#                  ('Capacity', None, {'label': 'Capacity*'})]},
# ]


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
    cursor = connection.cursor()
    if lookup_column.startswith('<str>'):
        lookup_column = lookup_column[5:]
        query = 'SELECT {} FROM {} where {}="{}"'.format(result_column, lookup_table, lookup_column, source_value)
        cursor.execute(query)
    else:
        query = 'SELECT {} FROM {} where {}={}'.format(result_column, lookup_table, lookup_column, source_value)
        cursor.execute(query)
    looked_up_values = []
    for result in cursor:
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

    cursor = connection.cursor()
    cursor.execute('SELECT {} FROM {}'.format(','.join([x[0] for x in columns]), name))
    for result in cursor:
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


def main():
    connection = sqlite3.connect(DATABASE_FILENAME)
    connection.row_factory = dict_factory

    with open('portia.txt', 'w', encoding='utf-8') as f:
        for mapping in MAPPINGS:
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
            f.write(mapping['name'] + '\n\n\n')
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
                        print('{0:>{1}}: {2}'.format(field, maxlen, value.encode('cp437', 'replace').decode('cp437')))
                    f.write(line + '\n')
                    f.flush()
                f.write('\n')
                print('')
        print('\n')


if __name__ == '__main__':
    main()
