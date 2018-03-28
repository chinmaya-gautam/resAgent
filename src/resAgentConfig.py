ONE_DAY_IN_SECONDS = 60 * 60 * 24

# For auto update
PFT_SERVER_IP = "10.1.8.88"
PFT_SERVER_PORT = "8393"
RES_AGENT_VERSION = "1.0.0"

RES_AGENT_UPDATE_URL = r"http://%s:%s/wbxtfResourceService/resAgentVersion" % (PFT_SERVER_IP, PFT_SERVER_PORT)
RES_AGENT_TEMP_FOLDER = r"c:\tmpResAgent"
RES_AGENT_UPDATE_CHECK_INTERVAL = 60

# For vm booking
DEFAULT_RES_ADMIN_SERVER_IP = "localhost" #"10.1.8.88" # localhost for testing, 10.1.8.88 for actual use
DEFAULT_RES_ADMIN_SERVER_PORT = "11830"
DEFAULT_RES_ADMIN_SERVER_ADDR = "%s:%s" % (DEFAULT_RES_ADMIN_SERVER_IP,DEFAULT_RES_ADMIN_SERVER_PORT)

POLL_DURATION = 5
CACHE_SIZE = 6

# For vm monitor
DB_USER = 'amtbot'
DB_PASSWORD = 'amtbot'
DB_HOST='10.1.11.0'
DB_NAME='meetingMgr'