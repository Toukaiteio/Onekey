import os
import vdf
import time
import shutil
import winreg
import argparse
import requests
import traceback
import subprocess
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
print('\033[0;32;40m  _____   __   _   _____   _   _    _____  __    __  _____   _____    _____  \033[0m')
print('\033[0;32;40m /  _  \ |  \ | | | ____| | | / /  | ____| \ \  / / |  _  \ |  _  \  /  _  \ \033[0m')
print('\033[0;32;40m | | | | |   \| | | |__   | |/ /   | |__    \ \/ /  | |_| | | |_| |  | | | | \033[0m')
print('\033[0;32;40m | | | | | |\   | |  __|  | |\ \   |  __|    \  /   |  ___/ |  _  /  | | | | ')
print('\033[0;32;40m | |_| | | | \  | | |___  | | \ \  | |___    / /    | |     | | \ \  | |_| | \033[0m')
print('\033[0;32;40m \_____/ |_|  \_| |_____| |_|  \_\ |_____|  /_/     |_|     |_|  \_\ \_____/ \033[0m')
log.info('作者ikun')
log.info('当前版本12.7')
log.info('本程序Github仓库:https://github.com/Onekey-Project/Onekey')
log.info('温馨提示：App ID可以在Steam商店页面或SteamDB找到')

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
    url_list = [f'https://github.moeyy.xyz/https://raw.githubusercontent.com/Onekey-Project/Manifest-AutoUpdate/{branch}/{path}',
                f'https://raw.gitmirror.com/Onekey-Project/Manifest-AutoUpdate/{branch}/{path}']

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
            if depotkey_merge(steam_path / 'config' / 'config.vdf', depots_config):
                log.info('合并密钥成功')
            if stool_add(
                    [(depot_id, '1', depots_config['depots'][depot_id]['DecryptionKey'])
                     for depot_id in depots_config['depots']]):
                log.info('导入Steamtools Depot成功')    
            if greenluma_add([int(i) for i in depots_config['depots'] if i.isdecimal()]):
                log.info('导入Greenluma Depot配置成功')
    except KeyboardInterrupt:
        raise
    except:
        traceback.print_exc()
        raise
    return True


def depotkey_merge(config_path, depots_config):
    if not config_path.exists():
        with lock:
            log.error('密钥文件不存在')
        return
    with open(config_path, encoding='utf-8') as f:
        config = vdf.load(f)
    software = config['InstallConfigStore']['Software']
    valve = software.get('Valve') or software.get('valve')
    steam = valve.get('Steam') or valve.get('steam')
    if 'depots' not in steam:
        steam['depots'] = {}
    steam['depots'].update(depots_config['depots'])
    with open(config_path, 'w', encoding='utf-8') as f:
        vdf.dump(config, f, pretty=True)
    return True

def stool_add(depot_list):
    steam_path = get_steam_path()
    lua_content = ""
    for depot_id, type_, depot_key in depot_list:
        lua_content += f"""addappid({depot_id}, {type_}, "{depot_key}")"""
    lua_filename = f"Onekey_unlock_{depot_id}.lua"
    lua_filepath = steam_path / "config" / "stplug-in" / lua_filename
    with open(lua_filepath, "w", encoding="utf-8") as lua_file:
        lua_file.write(lua_content)
    luapacka_path = steam_path / "config" / "stplug-in" / "luapacka.exe"
    subprocess.run([str(luapacka_path), str(lua_filepath)])
    os.remove(lua_filepath)
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
    config = load_config()
    github_persoal_token = config.get('github_persoal_token', '')
    headers = {'Authorization': f'{github_persoal_token}'}
    latest_date = None
    selected_repo = None
    if check_github_api_rate_limit():
        log.info('检查Github请求数完成')
    for repo in repos:
        url = f'https://api.github.com/repos/{repo}/branches/{app_id}'
        try:
            r = requests.get(url, headers=headers, verify=False)
            if 'commit' in r.json():
                date = r.json()['commit']['commit']['author']['date']
                if latest_date is None or date > latest_date:
                    latest_date = date
                    selected_repo = repo
        except KeyboardInterrupt:
            exit()
        except requests.exceptions.RequestException as e:
            log.error(f"An error occurred: {e}")
    if selected_repo:
        log.info(f'选择清单仓库: {selected_repo}')
        url = f'https://api.github.com/repos/{selected_repo}/branches/{app_id}'
        try:
            r = requests.get(url, verify=False)
            if 'commit' in r.json():
                branch = r.json()['name']
                url = r.json()['commit']['commit']['tree']['url']
                date = r.json()['commit']['commit']['author']['date']
                r = requests.get(url,verify=False)
                if 'tree' in r.json():
                    stool_add([(app_id, 1, "None")])
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

def app(app_path):
    app_path = Path(app_path)
    if not app_path.is_dir():
        raise NotADirectoryError(app_path)
    steam_path = get_steam_path()
    app_id_list = list(filter(str.isdecimal, app_path.name.strip().split('-')))
    if app_id_list:
        app_id = app_id_list[0]
        stool_add([(app_id, 1, "None")])
    else:
        raise Exception('目录名称不是app_id')
    for file in app_path.iterdir():
        if file.is_file():
            if file.suffix == '.manifest':
                depot_cache_path = steam_path / 'depotcache'
                shutil.copy(file, depot_cache_path)
                log.info(f'导入清单成功: {file.name}')
            elif file.name == 'config.vdf' or 'Key.vdf':
                with file.open('r', encoding='utf-8') as f:
                    depots_config = vdf.loads(f.read())
                if depotkey_merge(steam_path / 'config' / 'config.vdf', depots_config):
                    log.info('合并config.vdf成功')
                if stool_add([(depot_id, '1',
                               depots_config['depots'][depot_id]['DecryptionKey']) for depot_id in
                              depots_config['depots']]):
                    log.info('导入Steamtools Depot配置成功')
                if greenluma_add([int(i) for i in depots_config['depots'] if i.isdecimal()]):
                    log.info('导入GreenLuma Depot配置成功')

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--app-id')
parser.add_argument('-p', '--app-path')
args = parser.parse_args()
repos = ['Onekey-Project/Manifest-AutoUpdate']
if __name__ == '__main__':
    try:
        load_config()
        if args.app_path:
            app(args.app_path)
        else:
            main(args.app_id or input('appid: '))
    except KeyboardInterrupt:
        exit()
    except:
        traceback.print_exc()
    if not args.app_id and not args.app_path:
        os.system('pause')