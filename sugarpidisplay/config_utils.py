import json

class Cfg():
    data_source = 'data_source'
    ns_url = 'nightscout_url'
    ns_token = 'nightscout_access_token'
    dex_user = 'dexcom_username'
    dex_pass = 'dexcom_password'
    use_animation = 'use_animation'
    time_24hour = 'time_24hour'
    unit_mmol = 'unit_mmolL'
    orientation = 'orientation'
    show_graph = 'show_graph'

def fill_config_gaps(config):
    # fields with defaults
    if Cfg.use_animation not in config:
        config[Cfg.use_animation] = False
    if Cfg.time_24hour not in config:
        config[Cfg.time_24hour] = False
    if Cfg.orientation not in config or config[Cfg.orientation] not in [0,90,180,270]:
        config[Cfg.orientation] = 0
    if Cfg.show_graph not in config:
        config[Cfg.show_graph] = True
    if Cfg.unit_mmol not in config:
        config[Cfg.unit_mmol] = False

def read_config(config, configPath, logger):
    config.clear()
    try:
        # if (not Path(config_full_path).exists()):
        f = open(configPath, "r")
        config.update(json.load(f))
        f.close()
    except:
        if logger is not None:
            logger.error("Error reading config file")
    fill_config_gaps(config)
    if not validateConfig(config):
        if logger is not None:
            logger.error('Invalid config values')
        return False

    if logger is not None:
        logger.info("Loaded config")
    return True


def validateConfig(config):
    # validates the Dexcom or Nightscout settings (which can't be set to defaults)
    if Cfg.data_source not in config:
        return False
    if (config[Cfg.data_source] == "dexcom"):
        if Cfg.dex_user not in config or Cfg.dex_pass not in config:
            return False
    elif (config[Cfg.data_source] == "nightscout"):
        if Cfg.ns_url not in config or Cfg.ns_token not in config:
            return False
    else:
        return False
    return True
