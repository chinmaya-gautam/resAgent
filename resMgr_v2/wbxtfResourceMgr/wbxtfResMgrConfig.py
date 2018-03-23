__author__ = 'huajin2'
PFTserverIP = "10.1.8.88"
PFTserverPort = "8393"
PFTBaseURL = "http://%s:%s" % (PFTserverIP,PFTserverPort)
### Resource Manager Version
RMC_AutoUpdateURL = r"http://%s:%s/wbxtfResourceService/wbxtfResMgrVersion" % (PFTserverIP,PFTserverPort)#r"http://192.168.22.11:7777/api/v1/pf_agents/wbxtfresmgr"
RMC_AutoUpdateCheckIntervalSec = 60
RMC_TempFolder = r"c:\tmpWBXTFResMgr"

### Master center server information
MASTER_MACHINE_IP = PFTserverIP
MASTER_REST_URL = "http://%s:%s/api/v1/machines" % (MASTER_MACHINE_IP,PFTserverPort)
WBXTF_PING_SERVER_INTERVAL = 60*30


