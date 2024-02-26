from .initial import log
from .util import getContent
import requests
from pathlib import Path
import traceback
from multiprocessing.dummy import Lock
from requests.packages import urllib3
urllib3.disable_warnings()
lock = Lock()
def get( path ,repo):
    try:
        r = requests.get(f'https://gitee.com/api/v5/repos/{repo}/contents/{path}',verify=False)
        if r.status_code == 200:
            return r.json()
        
    except requests.exceptions.ConnectionError:
        log.error(f'获取失败: {path}')
def get_manifest(paths, steam_path: Path, repo, app_id=None):
    for path in paths:
        try:
            if path.endswith('.manifest'):
                depot_cache_path = steam_path / 'depotcache'
                depot_cache_path2 = steam_path / 'config' / 'depotcache'
                with lock:
                    if not depot_cache_path.exists():
                        depot_cache_path.mkdir(exist_ok=True)
                    if not depot_cache_path2.exists():
                        depot_cache_path2.mkdir(exist_ok=True)

                save_path = depot_cache_path / path
                save_path2 = depot_cache_path2 / path
                content = getContent(get(f'{app_id}/{path}',repo))
                with lock:
                    log.info(f'清单下载成功: {path}')
                with save_path.open('wb') as f:
                        f.write(content)
                with save_path2.open('wb') as f:
                        f.write(content)
                
                
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
            raise
    return True
def download_st(appid,name,repo):
     return getContent(get(f'{appid}/{name}',repo))
# def check_github_api_rate_limit():
#     config = loadedConfig
#     github_persoal_token = config.get('github_persoal_token', '')
#     headers = {'Authorization': f'{github_persoal_token}'}
#     url = 'https://api.github.com/rate_limit'
#     r = requests.get(url, headers=headers, verify=False)
#     if r.status_code == 200:
#         rate_limit = r.json()['rate']
#         remaining_requests = rate_limit['remaining']
#         reset_time = rate_limit['reset']
#         reset_time_formatted = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reset_time))
#         log.info(f'剩余请求次数: {remaining_requests}')

#     if remaining_requests == 0:
#         log.warning(f'GitHub API 请求数已用尽，将在 {reset_time_formatted} 重置')
#         return True