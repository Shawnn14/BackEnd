import os
import configparser

def read_config(name_setting: str, name_fie: str = 'config.ini'):
    config_path = (os.getcwd() + '\\BackEnd\\' + name_fie).replace("\\", "/")
    config = configparser.ConfigParser()
    config.read(config_path)
    
    return config[name_setting]