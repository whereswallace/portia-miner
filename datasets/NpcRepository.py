{'name': 'NpcRepository',
         'columns': [('Name', Lookup.TRANSLATION, {'label': 'NPC name'}),
                     ('Identity', Lookup.TRANSLATION, {'label': 'Description at first meeting'}),
                     ('Birthday', None, {'label': 'Birthday'}),
                     ('Sex', None, {'label': 'Gender'}),
                     ('date_selecttime', None, {'label': 'Date Times'}),
                     ('LatestTime_Date_new', None, {'label': 'Latest possible date time'}),
                     ('festivaltag', None, {'label': 'Festival participation'}),
                     ('BreakUp', Lookup.FAVOR_RELATION, {'label': 'Can break up if...'}),
                     ('Divorce', Lookup.FAVOR_RELATION, {'label': 'Can divorce if...'}),
                     ('MinFavor', None, {'label': 'Lowest possible Relationship Points'}),
                     ('Initial_Favor', None, {'label': 'Relationship Points at start of game'}),
                     ('des_height', None, {'label': 'Height)'}),
                     ('des_weight', None, {'label': 'Weight'}),
                     ('des_background', Lookup.TRANSLATION, {'regex': r'\d+,(.*)',
                                                             'label': 'Bio'}),
                     ('des_influence', Lookup.FAVOR_RELATION, {'regex': r'(\d+),.*',
                                                               'split': ';',
                                                               'join': '\n',
                                                               'label': 'Relationship'}),
                     ('des_influence', Lookup.TRANSLATION, {'regex': r'\d+,(.*)',
                                                            'split': ';',
                                                            'join': '\n',
                                                            'label': 'Perk'}),
                     ('giftid', Transform.GIFT_ID_EXCELLENT, {'label': 'Love'}),
                     ('giftid', Transform.GIFT_ID_LIKE, {'label': 'Like'}),
                     ('giftid', Transform.GIFT_ID_DISLIKE, {'label': 'Dislike'}),
                     ('giftid', Transform.GIFT_ID_HATE, {'label': 'Hate'}),
                     ('giftid', Transform.GIFT_ID_CONFESSION, {'label': 'Confess'}),
                     ('giftid', Transform.GIFT_ID_PROPOSE, {'label': 'Propose'}),
                     ('giftid', Transform.GIFT_ID_REFUSE, {'label': 'Refuse'}),
                     ('giftid', Transform.GIFT_ID_BREAK_UP, {'label': 'Break Up'}),
                     ('giftid', Transform.GIFT_ID_DIVORCE, {'label': 'Divorce'}),
                     ('giftid', Transform.GIFT_ID_JEALOUS, {'label': 'Jealous'}),
                     ('Hate_List', Lookup.PROP, {'label': 'Possible hated items'}),
                     ('Fame_Need', None),  # for now
                     ('Food_GroupID', Lookup.FOOD_TAG_LIKES, {'label': 'Food Likes'}),
                     ('Food_GroupID', Lookup.FOOD_TAG_DISLIKES, {'label': 'Food Dislikes'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_CONFESS_ACCEPT,
                      {'label': 'Accepts Confession'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_CONFESS_REFUSE,
                      {'label': 'Refuses Confession'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_CONFESS_LACKITEM,
                      {'label': 'Lacks Item For Confession'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_BREAKUP, {'label': 'Breaks up'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PROPOSE_ACCEPT, {'label': 'Accepts Proposal'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PROPOSE_REFUSE, {'label': 'Refuses Proposal'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PROPOSE_LACKITEM,
                      {'label': 'Lacks Item For Proposal'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_START, {'label': 'Play Start'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_MISSEDCONTRACT,
                      {'label': 'Play Missed Contract'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_GIVEUP_HAPPY,
                      {'label': 'Play Gives Up Happy'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_GIVEUP_UNHAPPY,
                      {'label': 'Play Gives Up Unhappy'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_ACTIONVALUE_HAPPY,
                      {'label': 'Play Action Value Happy'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_ACTIONVALUE_UNHAPPY,
                      {'label': 'Play Action Value Unhappy'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_TIMEOUT_HAPPY,
                      {'label': 'Play Time Out Happy'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_TIMEOUT_UNHAPPY,
                      {'label': 'Play Time Out Unhappy'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_MOODVALUE, {'label': 'Play Mood Value'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_JEALOUS, {'label': 'Play Jealous'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_PLAY_INTERRUPT, {'label': 'Play Interrupt'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_DATE_START, {'label': 'Date Start'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_DATE_MISSEDCONTRACT,
                      {'label': 'Date Missed Contract'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_DATE_GIVEUP_HAPPY,
                      {'label': 'Date Give Up Happy'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_DATE_GIVEUP_UNHAPPY,
                      {'label': 'Date Give Up Unhappy'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_DATE_ACTIONVALUE_HAPPY,
                      {'label': 'Date Action Value Happy'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_DATE_ACTIONVALUE_UNHAPPY,
                      {'label': 'Date Action Value Unhappy'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_DATE_TIMEOUT_HAPPY,
                      {'label': 'Date Time Out Happy'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_DATE_TIMEOUT_UNHAPPY,
                      {'label': 'Date Time Out Unhappy'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_DATE_MOODVALUE, {'label': 'Date Mood Value'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_DATE_INTERRUPT, {'label': 'Date Interrupt'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_DATE_JEALOUS, {'label': 'Date Jealous'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_DATE_INVITE, {'label': 'Date Invite'}),
                     ('Date_DialogID', Lookup.DATE_DIALOG_INVITE_REFUSE, {'label': 'Date Invite Refuse'}),
                     ('interact', None, {'label': 'Possible interactions'})]}