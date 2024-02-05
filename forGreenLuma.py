import os
import vdf
import time
import winreg
import argparse
import requests
import traceback
import requests
import yaml
import colorlog
import logging
from pathlib import Path
from multiprocessing.pool import ThreadPool
from multiprocessing.dummy import Pool, Lock
from requests.packages import urllib3

urllib3.disable_warnings()

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
date = time.strftime('%Y年%m月%d日 %H时%M分%S秒')
print('\033[1;32;40m  _____   __   _   _____   _   _    _____  __    __ \033[0m')
print('\033[1;32;40m /  _  \ |  \ | | | ____| | | / /  | ____| \ \  / /\033[0m')
print('\033[1;32;40m | | | | |   \| | | |__   | |/ /   | |__    \ \/ /\033[0m')
print('\033[1;32;40m | | | | | |\   | |  __|  | |\ \   |  __|    \  /')
print('\033[1;32;40m | |_| | | | \  | | |___  | | \ \  | |___    / /\033[0m')
print('\033[1;32;40m \_____/ |_|  \_| |_____| |_|  \_\ |_____|  /_/\033[0m')
print(f'\033[1;31;40m欢迎使用, 春节将至, 现在是{date}\033[0m')
print('\033[1;32;40m作者ikun\033[0m')
print('\033[1;32;40m当前版本13.1\033[0m')
print("\033[5;31;40m沧海吃老子饭还骂上老子了，光荣榜第一位\033[0m")
print('\033[1;32;40m温馨提示：App ID可以在Steam商店页面或SteamDB找到\033[0m')

default = {
    'github_persoal_token': '' ,
    'github_persoal_token_example': 'Bearer 你生成的Github个人访问Token',
    'customize_steam_path': '',
    'customize_steam_path_example': '填写Steam路径，一般为自动获取,如：C:/Program Files(x86)/steam',
}

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

lock = Lock()

def get(branch, path):
    url_list = [f'https://github.moeyy.xyz/https://raw.githubusercontent.com/{repo}/{branch}/{path}',
                f'https://raw.gitmirror.com/{repo}/{branch}/{path}',
                f'https://fastly.jsdelivr.net/gh/{repo}@{branch}/{path}']

    retry = 3
    while True:
        for url in url_list:
            try:
                r = requests.get(url,verify=False)
                if r.status_code == 200:
                    return r.content
            except requests.exceptions.ConnectionError:
                log.error(f'获取失败: {path}')
                retry -= 1
                if not retry:
                    log.warning(f'超过最大重试次数: {path}')
                    raise


def get_manifest(branch, path, steam_path: Path, app_id=None):
    try:
        if path.endswith('.manifest'):
            depot_cache_path = steam_path / 'depotcache'
            with lock:
                if not depot_cache_path.exists():
                    depot_cache_path.mkdir(exist_ok=True)
            save_path = depot_cache_path / path
            if save_path.exists():
                with lock:
                    log.warning(f'已存在清单: {path}')
                return
            content = get(branch, path)
            with lock:
                log.info(f'清单下载成功: {path}')
            with save_path.open('wb') as f:
                f.write(content)
        if path.endswith('.vdf') and path not in ['appinfo.vdf']:
            if path == 'config.vdf' or 'Key.vdf':
                content = get(branch, path)
            with lock:
                log.info(f'密钥下载成功: {path}')
            depots_config = vdf.loads(content.decode(encoding='utf-8'))
            if greenluma_add([int(i) for i in depots_config['depots'] if i.isdecimal()]):
                log.info('导入Greenluma Depot配置成功')
    except KeyboardInterrupt:
        raise
    except:
        traceback.print_exc()
        raise
    return True

def greenluma_add(depot_id_list):
    steam_path = get_steam_path()
    app_list_path = steam_path / 'AppList'
    if app_list_path.is_file():
        app_list_path.unlink(missing_ok=True)
    if not app_list_path.is_dir():
        app_list_path.mkdir(parents=True, exist_ok=True)
    depot_dict = {}
    for i in app_list_path.iterdir():
        if i.stem.isdecimal() and i.suffix == '.txt':
            with i.open('r', encoding='utf-8') as f:
                app_id_ = f.read().strip()
                depot_dict[int(i.stem)] = None
                if app_id_.isdecimal():
                    depot_dict[int(i.stem)] = int(app_id_)
    for depot_id in depot_id_list:
        if int(depot_id) not in depot_dict.values():
            index = max(depot_dict.keys()) + 1 if depot_dict.keys() else 0
            if index != 0:
                for i in range(max(depot_dict.keys())):
                    if i not in depot_dict.keys():
                        index = i
                        break
            with (app_list_path / f'{index}.txt').open('w', encoding='utf-8') as f:
                f.write(str(depot_id))
            depot_dict[index] = int(depot_id)
    return True

def get_steam_path():
    config = load_config()
    customize_steam_path = config.get('customize_steam_path', '')
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam')
    steam_path = Path(winreg.QueryValueEx(key, 'SteamPath')[0]) or customize_steam_path
    return steam_path

def check_github_api_rate_limit():
    config = load_config()
    github_persoal_token = config.get('github_persoal_token', '')
    headers = {'Authorization': f'{github_persoal_token}'}
    url = 'https://api.github.com/rate_limit'
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        rate_limit = r.json()['rate']
        remaining_requests = rate_limit['remaining']
        reset_time = rate_limit['reset']
        reset_time_formatted = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reset_time))
        log.info(f'剩余请求次数: {remaining_requests}')

    if remaining_requests == 0:
        log.warning(f'GitHub API 请求数已用尽，将在 {reset_time_formatted} 重置')
        return True

def main(app_id):
    app_id_list = list(filter(str.isdecimal, app_id.strip().split('-')))
    app_id = app_id_list[0]
    config = load_config()
    github_persoal_token = config.get('github_persoal_token', '')
    headers = {'Authorization': f'{github_persoal_token}'}

    url = f'https://api.github.com/repos/{repo}/branches/{app_id}'
    try:
            r = requests.get(url, verify=False, headers=headers)
            if 'commit' in r.json():
                branch = r.json()['name']
                url = r.json()['commit']['commit']['tree']['url']
                date = r.json()['commit']['commit']['author']['date']
                r = requests.get(url,verify=False)
                if 'tree' in r.json():
                    greenluma_add([app_id])
                    result_list = []
                    with Pool(32) as pool:
                        pool: ThreadPool
                        for i in r.json()['tree']:
                            result_list.append(pool.apply_async(get_manifest, (branch, i['path'], get_steam_path(), app_id)))
                        try:
                            while pool._state == 'RUN':
                                if all([result.ready() for result in result_list]):
                                    break
                                time.sleep(0.1)
                        except KeyboardInterrupt:
                            with lock:
                                pool.terminate()
                            raise
                    if all([result.successful() for result in result_list]):
                        log.info(f'清单最新更新时间:{date}')
                        log.info(f'入库成功: {app_id}')
                        log.info('重启steam生效')
                        return True
    except KeyboardInterrupt:
        exit()
    except requests.exceptions.RequestException as e:
        log.error(f"An error occurred: {e}")
    log.error(f'入库失败: {app_id}，清单库中可能暂未收录该游戏')
    return False

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--app-id')
parser.add_argument('-r', '--repo', default='Onekey-Project/ManifestAutoUpdate-Cache')
args = parser.parse_args()
repo = args.repo
if __name__ == '__main__':
    try:
        load_config()
        main(args.app_id or input('需要入库的App ID: '))
    except KeyboardInterrupt:
        exit()
    except:
        traceback.print_exc()
    if not args.app_id:
        os.system('pause')