<div align="center">

![Onekey](https://socialify.git.ci/ikun0014/Onekey/image?description=1&font=Inter&forks=1&issues=1&language=1&name=1&owner=1&pulls=1&stargazers=1&theme=Auto)
![GitHub Repo Size](https://img.shields.io/github/repo-size/ikun0014/Onekey?style=for-the-badge)
[![GitHub Release (with filter)](https://img.shields.io/github/v/release/ikun0014/Onekey?style=for-the-badge)](https://github.com/ikun0014/Onekey/releases/latest)
[![GitHub All Releases](https://img.shields.io/github/downloads/ikun0014/Onekey/total?style=for-the-badge&color=violet)](https://github.com/ikun0014/Onekey/releases)
[![GitHub License](https://img.shields.io/github/license/ikun0014/Onekey?style=for-the-badge)](https://github.com/ikun0014/Onekey/blob/main/LICENSE)

</div>

# Onekey
Steam收费游戏体验(无法享受官方的任何在线权益)  

## 备注
### 本项目中可能会出现以下优秀代码

1. 三角形具有稳定性
```python
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
    log.error(f'入库失败: {app_id}')
    return False
```

2. 能多行写完那就坚决不一行
```python
    url_list = [f'https://github.moeyy.xyz/https://raw.githubusercontent.com/BlankTMing/ManifestAutoUpdate/{branch}/{path}',
                f'https://gh.api.99988866.xyz/https://raw.githubusercontent.com/BlankTMing/ManifestAutoUpdate/{branch}/{path}',
                f'https://raw.staticdn.net/https://raw.githubusercontent.com/BlankTMing/ManifestAutoUpdate/{branch}/{path}',
                f'https://github.moeyy.xyz/https://raw.githubusercontent.com/lls7890/Repository/{branch}/{path}',
                f'https://gh.api.99988866.xyz/https://raw.githubusercontent.com/lls7890/Repository/{branch}/{path}',
                f'https://raw.staticdn.net/https://raw.githubusercontent.com/lls7890/Repository/{branch}/{path}',
                f'https://github.moeyy.xyz/https://raw.githubusercontent.com/isKoi/Manifest-AutoUpdate/{branch}/{path}',
                f'https://gh.api.99988866.xyz/https://raw.githubusercontent.com/isKoi/Manifest-AutoUpdate/{branch}/{path}',
                f'https://raw.staticdn.net/https://raw.githubusercontent.com/isKoi/Manifest-AutoUpdate/{branch}/{path}',
                f'https://github.moeyy.xyz/https://raw.githubusercontent.com/qwq-xinkeng/awaqwqmain/{branch}/{path}',
                f'https://raw.staticdn.net/https://raw.githubusercontent.com/qwq-xinkeng/awaqwqmain/{branch}/{path}',
                f'https://gh.api.99988866.xyz/https://raw.githubusercontent.com/qwq-xinkeng/awaqwqmain/{branch}/{path}',
                f'https://github.moeyy.xyz/https://raw.githubusercontent.com/Onekey-Project/Manifest-AutoUpdate/{branch}/{path}',
                f'https://gh.api.99988866.xyz/https://raw.githubusercontent.com/Onekey-Project/Manifest-AutoUpdate/{branch}/{path}',
                f'https://raw.staticdn.net/https://raw.githubusercontent.com/Onekey-Project/Manifest-AutoUpdate/{branch}/{path}']
```

# 项目协议
本项目基于 MIT 许可证发行，以下协议是对于 MIT 原协议的补充，如有冲突，以以下协议为准。

词语约定：“使用者”指签署本协议的使用者;“版权数据”指包括但不限于图像、音频、名字等在内的他人拥有所属版权的数据。

本项目的数据来源原理是从Steam官方的CDN服务器中拉取游戏清单数据，经过对数据简单地筛选与合并后进行展示，因此本项目不对数据的准确性负责。
使用本项目的过程中可能会产生版权数据，对于这些版权数据，本项目不拥有它们的所有权，为了避免造成侵权，使用者务必在24 小时内清除使用本项目的过程中所产生的版权数据。
由于使用本项目产生的包括由于本协议或由于使用或无法使用本项目而引起的任何性质的任何直接、间接、特殊、偶然或结果性损害（包括但不限于因商誉损失、停工、计算机故障或故障引起的损害赔偿，或任何及所有其他商业损害或损失）由使用者负责。
本项目完全免费，且开源发布于 GitHub 面向全世界人用作对技术的学习交流，本项目不对项目内的技术可能存在违反当地法律法规的行为作保证，禁止在违反当地法律法规的情况下使用本项目，对于使用者在明知或不知当地法律法规不允许的情况下使用本项目所造成的任何违法违规行为由使用者承担，本项目不承担由此造成的任何直接、间接、特殊、偶然或结果性责任。
若你使用了本项目，将代表你接受以上协议。

Steam正版平台不易，请尊重版权，支持正版。  
本项目仅用于对技术可行性的探索及研究，不接受任何商业（包括但不限于广告等）合作。  
若对此有疑问请 mail to:  
ikun0014+qq.com  
(请将+替换成@)

## Star 趋势图

[![Stargazers over time](https://starchart.cc/ikun0014/Onekey.svg)](https://starchart.cc/ikun0014/Onekey)

## 贡献者

<a href="https://github.com/ikun0014/Onekey/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ikun0014/Onekey" />
</a>

## 交流群
[Telegram](https://t.me/OnekeyProject)  
[QQ](https://qm.qq.com/cgi-bin/qm/qr?k=LIGCgexM7pKDdAzOYYt48-q3MKEJ86zQ&jump_from=webapi&authKey=phTpxY5oXbshlXPnxvgE1fgEq5jORww2Z77Wytdlfzc+gllkXNOq8SZYXgdVWjLU)

## 赞赏
如果您觉得本项目对您有帮助，可以适当的打赏一下
![微信](https://github.com/Onekey-Project/Onekey/blob/main/wx.png)]
![支付宝](https://github.com/Onekey-Project/Onekey/blob/main/zfb.jpg)