from .initial import steam_path
from .requestor import download_st
import subprocess
import os

def stool_add2(appid,st_files,repo):
    writeTo=steam_path / "config" / "stplug-in"
    for i in range(len(st_files)):
        with open(writeTo / f"{appid}_{i}.st","wb") as f:
            f.write(download_st(appid,st_files[i],repo))
def stool_add(depot_list):
    lua_content = ""
    appid=None
    for depot_id, type_, _orikey in depot_list:
        if not appid:
            appid=depot_id
        if(_orikey != "None"):
            depot_key=_orikey.split("#")
        else:
            depot_key=[_orikey,_orikey,_orikey]
        lua_content += f"""addappid({depot_id}, {type_}, "{depot_key[0]}")"""
        if(depot_key!='None'):
            lua_content += f"""setManifestid({depot_id},"{depot_key[1]}",{depot_key[2]})"""
    lua_filename = f"Onekey_unlock_{appid}.lua"
    lua_filepath = steam_path / "config" / "stplug-in" / lua_filename
    with open(lua_filepath, "w", encoding="utf-8") as lua_file:
        lua_file.write(lua_content)
    luapacka_path = steam_path / "config" / "stplug-in" / "luapacka.exe"
    subprocess.run([str(luapacka_path), str(lua_filepath)])
    os.remove(lua_filepath)
    return True
def greenluma_add(depot_list):
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
    for depot_id, type_, _orikey in depot_list:
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

