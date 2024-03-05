from utils.initial import *
from utils.requestor import *
from utils.util import *
import os
import argparse
import requests
import traceback
from json import loads
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
print('\033[1;33m输入的APP ID加上#前缀可仅解锁其DLC(需要拥有本体，且确保网络能够访问steam商店，仅支持SteamTools)\033[0m')
def unlockGame(app_id):
    app_id_list = list(filter(str.isdecimal, app_id.strip().split('-')))
    app_id = app_id_list[0]
    # config = loadedConfig
    # github_persoal_token = config.get('github_persoal_token', '')
    # headers = {'Authorization': f'{github_persoal_token}'}
    headers = {'Authorization': ''}
    url = f'https://gitee.com/api/v5/repos/{repo}/contents/{app_id}/key.json'
    try:
        __r=requests.get(url, headers=headers , verify=False).json()
        # print(__r,type(__r)==type([1]),'content' not in __r.keys())
        if type(__r)==type([1]) or 'content' not in __r.keys():
            raise
        r = loads(getContent(__r).decode('utf-8'))
        get_manifest(r['manifest'], get_steam_path(),repo, app_id)
        if isSteamTools:
            if r['type']=='luaScript':
                stoolAdd([(app_id, 1, "None")]+[(r['gameid'][depot_id],1,f"{r['key'][depot_id]}#{r['depotid'][depot_id]}#{r['stage'][depot_id]}") for depot_id in range(len(r['gameid']))]+[(depot_id, '1', 'None') for depot_id in r['dlc_list']])
            elif r['type']=='SteamTools':
                stoolAdd2(app_id,r['st_files'],repo)
        if isGreenLuma and r['type'] != 'SteamTools':
            greenlumaAdd([app_id]+[depot_id for depot_id in r['gameid']]+[depot_id for depot_id in r['dlc_list']])
        log.info(f'入库成功: {app_id} 游戏:{r["english"]}')
        log.info('重启steam生效')
        return True
    except KeyboardInterrupt:
        exit()
    except requests.exceptions.RequestException as e:
        log.error(f"An error occurred: {e}")
        log.info('请检查网络连接，或也可能是您入库过于频繁导致的。')
    except:
        # traceback.print_exc()
        log.error(f'入库失败: {app_id}，清单库中可能暂未收录该游戏')
        return False
    return False
def unlockDLC(app_id):
    app_id_list = list(filter(str.isdecimal, app_id.strip().split('-')))
    app_id = app_id_list[0]
    config = loadedConfig
    url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
    try:
        r=None
        dlc_proxy=config.get('github_persoal_token', '')
        if dlc_proxy:
            r=requests.get(url , verify=False).json()[app_id]
        else: r=requests.get(url , verify=False,proxies=dlc_proxy).json()[app_id]
        if (not r['success']) or (r['data']['type']!='game'):
            log.error("App ID 并不指向一个 游戏！")
            raise
        else:
            dlcList=[]
            try:
                dlcList+=list(r['data']['dlc'])
            except KeyError:
                pass
            except:
                raise
            if(len(dlcList)==0):
                log.info("未找到该游戏DLC")
                raise
            if stoolUnlockDLC(dlcList):
                log.info(f'解锁DLC成功: {app_id} 游戏:{ r["data"]["name"] }')
                log.info('重启steam生效')
                return True
    except KeyboardInterrupt:
        exit()
    except requests.exceptions.RequestException as e:
        log.error(f"An error occurred: {e}")
        log.info('请检查网络连接。')
    return False

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--app-id')
# parser.add_argument('-r', '--repo', default='Onekey-Project/ManifestAutoUpdate-Cache')
parser.add_argument('-r', '--repo', default='ACGN_weeeee/game-depots')
args = parser.parse_args()
repo = args.repo
if __name__ == '__main__':
    try:
        _appid=args.app_id or input('需要入库的App ID: ')
        if _appid.startswith('#'):
            _appid = _appid[1:]
            unlockDLC(_appid)
        else:
            unlockGame(_appid)
    except KeyboardInterrupt:
        exit()
    except:
        traceback.print_exc()
    if not args.app_id:
        os.system('pause')