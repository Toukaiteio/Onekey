import winreg
from pathlib import Path
import logging
import colorlog
import yaml
import os
logging.captureWarnings(True)
default = {
    'customize_steam_path': '',
    'customize_steam_path_example': '填写Steam路径，一般为自动获取,如：C:/Program Files(x86)/steam',
    'dlc_proxy':'',
    'dlc_proxy_example':'使用解锁DLC功能时使用的代理',
}
def init_log():
    logger = logging.getLogger('Onekey')
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    fmt_string = '%(log_color)s[%(name)s][%(levelname)s]%(message)s'
    # black red green yellow blue purple cyan 和 white
    log_colors = {
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'purple'
        }
    fmt = colorlog.ColoredFormatter(fmt_string, log_colors=log_colors)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)
    return logger
log = init_log()
def gen_config():
    with open("./appsettings.yaml", "w", encoding="utf-8") as f:
        f.write(yaml.dump(default, allow_unicode=True))
        f.close()
        if (not os.getenv('build')):
            log.warning('首次启动或配置文件被删除，已创建默认配置文件')
        return gen_config
    
def load_config():
    if os.path.exists('appsettings.yaml'):
        with open('appsettings.yaml', 'r', encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
    else:
        gen_config()
        with open('appsettings.yaml', 'r', encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

    return config
loadedConfig=load_config()
def get_steam_path():
    config = loadedConfig
    customize_steam_path = config.get('customize_steam_path', '')
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam')
    steam_path = Path(winreg.QueryValueEx(key, 'SteamPath')[0]) or customize_steam_path
    return steam_path
steam_path=get_steam_path()
isGreenLuma = (steam_path / 'AppList').is_dir()
isSteamTools = (steam_path / 'config' / 'stplug-in').is_dir()
