{'name': 'RidableInfo',
 'columns': [('RidableInfoID', Lookup.RIDABLE_INFO_ID, {'label': 'Type of mount'}),
             ('InitNickName', Lookup.TRANSLATION, {'label': 'Initial nickname'}),
             ('InitialSpeed', None, {'label': 'Initial speed'}),
             ('SpeedGrowthLimit', None, {'label': 'Best trained speed'}),
             ('InitialVpRecover', None, {'label': 'Initial VP recovery'}),
             ('VpRecoverLimit', None, {'label': 'Best trained VP recovery'}),
             ('InitialVpConsumeJump', None, {'label': 'Initial VP used by jump'}),
             ('JumpingPowerLimit', None, {'label': 'Best trained VP used by jump'}),
             ('InitialVpConsumeFastRun', None, {'label': 'Initial VP used by dash'}),
             ('VpConsumeFastRunLimit', None, {'label': 'Best trained VP used by dash'}),
             ('PassScore', None, {'label': 'Score required to tame'}),
             ('Bait', Lookup.PROP, {'split': ';',
                                    'quantity_post': ',',
                                    'label': 'Bait required to trap'}),
             ('BasePrice', None, {'label': 'Purchase Price'}),
             ('FoodFillingDegree', Lookup.PROP, {'split': ';',
                                                 'quantity_post': ',',
                                                 'label': '**Food_Filling_Degree**'}),
             ('FeedDegree', None, {'label': '**Feed_Degree**'}),
             ('ShitNum', None, {'label': '**Shit_Num**'})]}