from utils.initial import steam_path
from pathlib import Path
from os import getcwd,mkdir,system
from vdf import loads
from shutil import copyfile
from json import dump
steamApps=[steam_path / "steamapps"]
appMap={}
finalMap={}
steamUserConfig=None
if not (steam_path / "config" / "config.vdf").is_file():
    print("未找到Steam用户配置文件。")
    system("pause")
    exit()
with open(steam_path / "config" / "config.vdf","r",encoding="utf-8") as f:
    steamUserConfig=loads(f.read())['InstallConfigStore']
try:
    if steamUserConfig:
        if 'Software' in steamUserConfig.keys(): steamUserConfig=steamUserConfig['Software']
        else: steamUserConfig=steamUserConfig['software']
        if 'Valve' in steamUserConfig.keys(): steamUserConfig=steamUserConfig['Valve']
        else: steamUserConfig=steamUserConfig['valve']
        if 'steam' in steamUserConfig.keys(): steamUserConfig=steamUserConfig['steam']
        else: steamUserConfig=steamUserConfig['Steam']
        if 'depots' in steamUserConfig: steamUserConfig=steamUserConfig['depots']
        else: steamUserConfig=steamUserConfig['Depots']
except KeyError:
    print('Steam用户配置文件错误!')
    system("pause")
    exit()
except:
    print("程序出错!")
    system("pause")
    exit()
def loadAppManifest(fp,givenIndex):
    _app=loads(fp.read())['AppState']
    finalMap[givenIndex]={}
    finalMap[givenIndex]['name']=_app['name']
    finalMap[givenIndex]['appid']=_app['appid']
    finalMap[givenIndex]['depots']={}
    for i in _app['InstalledDepots'].keys():
        finalMap[givenIndex]['depots'][i]={}
        finalMap[givenIndex]['depots'][i]['manifest']=_app['InstalledDepots'][i]['manifest']
        finalMap[givenIndex]['depots'][i]['stage']=_app['InstalledDepots'][i]['size']
    print(f"{givenIndex} - {_app['name']}")
def gatherManifest(givenIndex):
    for i in finalMap[givenIndex]['depots']:
        fullPath=steam_path / "depotcache" / f"{i}_{finalMap[givenIndex]['depots'][i]['manifest']}.manifest"
        output=Path(getcwd()) / "depot_output"
        sub_output=output / f"{finalMap[givenIndex]['appid']}"
        if not fullPath.is_file():
            print("游戏文件不完整，提取失败。")
            raise
        if not output.is_dir():
            mkdir(output)
        if not sub_output.is_dir():
            mkdir(sub_output)
        if (sub_output / f"{i}_{finalMap[givenIndex]['depots'][i]['manifest']}.manifest").is_file():
            continue
        copyfile(fullPath,sub_output / f"{i}_{finalMap[givenIndex]['depots'][i]['manifest']}.manifest")
    genrateKeyFile(givenIndex,sub_output / "key.json")
def genrateKeyFile(givenIndex,output):
    oriDict={
        "type":"luaScript",
        "key":[steamUserConfig[i]["DecryptionKey"] for i in finalMap[givenIndex]['depots'].keys()],
        "appid":finalMap[givenIndex]["appid"],
        "gameid":[i for i in finalMap[givenIndex]['depots'].keys()],
        "stage":[finalMap[givenIndex]['depots'][i]['stage'] for i in finalMap[givenIndex]['depots'].keys()],
        "depotid":[finalMap[givenIndex]['depots'][i]['manifest'] for i in finalMap[givenIndex]['depots'].keys()],
        "english":finalMap[givenIndex]["name"],
        "dlc_list":[],
        "manifest":[f"{i}_{finalMap[givenIndex]['depots'][i]['manifest']}.manifest" for i in finalMap[givenIndex]['depots'].keys()]
    }
    with open(output,"w") as f:
        dump(oriDict,f)
steamLibraries=[
    steam_path / "config" / "libraryfolders.vdf",
    steam_path / "steamapps" / "libraryfolders.vdf"
]
loadedConfig=None
for i in steamLibraries:
    if i.is_file():
        with open(i,"r",encoding="utf-8") as library:
            loadedConfig=loads(library.read())
            break
if loadedConfig:
    _=loadedConfig['libraryfolders']
    for i in _.keys():
        if (Path(_[i]['path']) / "steamapps")!=steamApps[0] and (Path(_[i]['path']) / "steamapps").is_dir():
            steamApps.append(Path(_[i]['path']) / "steamapps")
        if (Path(_[i]['path']) / "steamapps").is_dir():
            appMap[i]=list(_[i]['apps'].keys())
_prefix="appmanifest_"
for i,lib in enumerate(steamApps):
    for j,app in enumerate(appMap[str(i)]):
        fullPath=lib / (_prefix + app + ".acf")
        if fullPath.is_file():
            if(j>9998):
                i+=27
            try:
                with open(fullPath,'r',encoding="utf-8") as f: loadAppManifest(f,f"{(i+1)*10000 + j}")
            except:
                system("pause")
                exit()
print("如果你未找到你拥有的游戏，可能是由于你未下载该游戏。")
print("对于未下载的游戏，需要您提供steam通行凭证。")
print("使用# + APPID来尝试获取未列出的游戏。 如 #1203620 。其中 APPID 可在SteamDB中获取。")
print("之后您还需要给出DepotID，同样能够从steamDB获取")
while(True):
    try:
        find=input("输入游戏前序号，提取游戏表单密钥:")
        int(find)
    except KeyboardInterrupt:
        exit()
    except:
        print("不是有效的数字!")
        continue
    if (find in finalMap.keys()):
        gatherManifest(find)
        print("提取完成!")
    else:
        print("未找到该序号对应的游戏")
