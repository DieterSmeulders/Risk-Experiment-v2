from os import environ

SESSION_CONFIGS = [
    dict(
    name='BasicExperiment',
    display_name="Basic Experiment",
    num_demo_participants=2,
    app_sequence=['BaseExperiment'],
    P1_duration_min=1, P1_duration_max=10,
    P1_price_min=1, P1_price_max=1,
    P2_duration_min=1, P2_duration_max=10,
    P2_price_min=1, P2_price_max=1,
    P3_duration_min=1, P3_duration_max=10,
    P3_price_min=1, P3_price_max=1,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False

ROOMS = [dict(
        name='MCCM',
        display_name='Management Control and Cost Management Study',
#        participant_label_file='_rooms/econ101.txt',
    )]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = 'dkz6yndxn3mo9v-ax$1%$0u&_l@$#+ze7-99(_*c5vj@ruy!yz'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
