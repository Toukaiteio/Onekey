from utils.initial import *
from utils.requestor import *
from utils.util import *
import os
import argparse
import requests
import traceback
from requests.packages import urllib3
from json import loads
urllib3.disable_warnings()
print('\033[1;32;40m  _____   __   _   _____   _   _    _____  __    __ \033[0m')
print('\033[1;32;40m /  _  \ |  \ | | | ____| | | / /  | ____| \ \  / /\033[0m')
print('\033[1;32;40m | | | | |   \| | | |__   | |/ /   | |__    \ \/ /\033[0m')
print('\033[1;32;40m | | | | | |\   | |  __|  | |\ \   |  __|    \  /')
print('\033[1;32;40m | |_| | | | \  | | |___  | | \ \  | |___    / /\033[0m')
print('\033[1;32;40m \_____/ |_|  \_| |_____| |_|  \_\ |_____|  /_/\033[0m')
print('\033[1;32;40m作者ikun\033[0m')
print('\033[1;32;40m当前版本 20240225S01 维护:Daiyosei\033[0m')
print('\033[1;32;40m温馨提示：App ID可以在Steam商店页面或SteamDB找到\033[0m')
if isGreenLuma:
    print('\033[1;32;40m找到GreenLuma,GreenLuma模式已启用(提示:GreenLuma模式未经验证)\033[0m')
else:
    print('\033[1;31;40m未找到GreenLuma,GreenLuma模式已禁用\033[0m')
if isSteamTools:
    print('\033[1;32;40m找到SteamTools,SteamTools模式已启用\033[0m')
else:
    print('\033[1;31;40m未找到SteamTools, SteamTools模式已禁用\033[0m')
if not (isGreenLuma or isSteamTools):
    print('\033[1;31;40m请开启SteamTools或GreenLuma以继续使用\033[0m')
    os.system('pause')
    exit()
def main(app_id):
    app_id_list = list(filter(str.isdecimal, app_id.strip().split('-')))
    app_id = app_id_list[0]
    config = load_config()
    # github_persoal_token = config.get('github_persoal_token', '')
    # headers = {'Authorization': f'{github_persoal_token}'}
    headers = {'Authorization': ''}
    url = f'https://gitee.com/api/v5/repos/{repo}/contents/{app_id}/key.json'
    r = loads(getContent(requests.get(url, headers=headers , verify=False).json()).decode('utf-8'))
    try:
        get_manifest(r['manifest'], get_steam_path(),repo, app_id)
        if isSteamTools:
            if r['type']=='luaScript':
                stool_add([(app_id, 1, "None")]+[(r['gameid'][depot_id],1,f"{r['key'][depot_id]}#{r['depotid'][depot_id]}#{r['stage'][depot_id]}") for depot_id in range(len(r['gameid']))]+[(depot_id, '1', 'None') for depot_id in r['dlc_list']])
            elif r['type']=='SteamTools':
                stool_add2(app_id,r['st_files'],repo)
        if isGreenLuma and r['type'] != 'SteamTools':
            greenluma_add([app_id]+[depot_id for depot_id in r['gameid']]+[depot_id for depot_id in r['dlc_list']])
        log.info(f'入库成功: {app_id} 游戏:{r["english"]}')
        log.info('重启steam生效')
        return True
    except KeyboardInterrupt:
        exit()
    except requests.exceptions.RequestException as e:
        log.error(f"An error occurred: {e}")
        log.info('请检查网络连接，或也可能是您入库过于频繁导致的。')
    log.error(f'入库失败: {app_id}，清单库中可能暂未收录该游戏')
    return False

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--app-id')
# parser.add_argument('-r', '--repo', default='Onekey-Project/ManifestAutoUpdate-Cache')
parser.add_argument('-r', '--repo', default='ACGN_weeeee/game-depots')
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