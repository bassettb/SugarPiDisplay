import json

class Cfg(Enum):
    data_source = 'data_source'
    ns_url = 'nightscout_url'
    ns_token = 'nightscout_access_token'
    dex_user = 'dexcom_username'
    dex_pass = 'dexcom_password'
    use_animation = 'use_animation'
    time_24hour = 'time_24hour'
    unit_mmol = 'unit_mmolL'

def loadConfigDefaults():
    configDefaults = {
        Cfg.use_animation: False,
        Cfg.time_24hour: False,
        Cfg.unit_mmol: False
    }
    return configDefaults

def validateConfig(config):
    if Cfg.data_source not in config:
        return False
    if (config[Cfg.data_source] == "dexcom"):
        if Cfg.dex_user not in config or Cfg.dex_pass not in config:
            return False
    elif (config[Cfg.data_source] == "nightscout"):
        if Cfg.ns_url not in config.keys() or Cfg.ns_token not in config.keys():
            return False
    else
        return False
    return True
