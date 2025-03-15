class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    API_ID = 
    API_HASH = ""

    CASH_API_KEY = ""  # Get this value for currency converter from https://www.alphavantage.co/support/#api-key

    DATABASE_URL = ""  # A sql database url from elephantsql.com

    EVENT_LOGS = ()  # Event logs channel to note down important bot level events

    MONGO_DB_URI = ""  # Get ths value from cloud.mongodb.com

    # Telegraph link of the image which will be shown at start command.
    START_IMG = "https://files.catbox.moe/1u9rd3.jpg"

    SUPPORT_CHAT = "InfoRobotCalvin"  # Your Telegram support group chat username where your users will go and bother you

    TOKEN = ""  # Get bot token from @BotFather on Telegram

    TIME_API_KEY = ""  # Get this value from https://timezonedb.com/api

    OWNER_ID = 5510539512  # User id of your telegram account (Must be integer)

    # Optional fields
    BL_CHATS = [5510539512]  # List of groups that you want blacklisted.
    DRAGONS = [5510539512]  # User id of sudo users
    DEV_USERS = [5510539512]  # User id of dev users
    DEMONS = [5510539512]  # User id of support users
    TIGERS = [5510539512]  # User id of tiger users
    WOLVES = [5510539512]  # User id of whitelist users

    ALLOW_CHATS = True
    ALLOW_EXCL = True
    DEL_CMDS = True
    INFOPIC = True
    LOAD = []
    NO_LOAD = []
    STRICT_GBAN = True
    TEMP_DOWNLOAD_DIRECTORY = "./"
    WORKERS = 8


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
