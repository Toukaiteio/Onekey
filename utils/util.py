from .initial import get_steam_path
import subprocess
import os
from base64 import b64decode
def stool_add(depot_list):
    steam_path = get_steam_path()
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
def getContent(ori):
    return b64decode(ori['content'])