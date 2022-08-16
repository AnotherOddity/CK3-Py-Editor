import pathlib
import platform

# CK3 relative to the steam library directory
CK3_GAMEDIR = "steamapps/common/Crusader Kings III/game"
CK3_APP_ID = "1158310"

STEAM_LINUX = "~/.local/share/Steam/steamapps"
STEAM_MAC = "~/Library/Application Support/Steam/steamapps"

# Return Steam's steamapps/ directory, or None if not found.
def find_steamapps_directory():
    path = None
    if platform.system() == "Windows":
        import winreg
        # TODO: figure out if I can do all subkeys in one call
        key1 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE")
        key2 = winreg.OpenKey(key1, "Wow6432Node")
        key3 = winreg.OpenKey(key2, "Valve")
        key4 = winreg.OpenKey(key3, "Steam")
        (path, type) = winreg.QueryValueEx(key4, "InstallPath")
        if type == winreg.REG_EXPAND_SZ:
            path = winreg.ExpandEnvironmentStrings(path.joinpath("steamapps"))
        winreg.CloseKey(key4)
        winreg.CloseKey(key3)
        winreg.CloseKey(key2)
        winreg.CloseKey(key1)
        path = pathlib.Path(path)
    elif platform.system() == "Linux":
        path = pathlib.Path(STEAM_LINUX).expanduser()
    elif platform.system() == "Darwin":
        path = pathlib.Path(STEAM_MAC).expanduser()
    if path and path.is_dir():
        return path
    return None

# Return CK3's game directory, or None if not found.
def find_ck3_game_directory():
    steam_lib = find_steamapps_directory()
    if steam_lib is None:
        return None

    # Rudimentary libraryfolders.vdf parsing.
    # We're looking for a subsection with a "path" setting that has
    # our app (CK3) listed in its "apps" list.
    with open(steam_lib.joinpath("libraryfolders.vdf")) as infile:
        current_path = None
        for line in infile.readlines():
            try:
                key, value = line.split()
                key = key.strip('"')
                value = value.strip('"')
            except ValueError:
                continue
            if key == 'path':
                current_path = pathlib.Path(value)
            elif key == CK3_APP_ID and current_path is not None:
                ck3_path = current_path.joinpath(CK3_GAMEDIR)
                if ck3_path.is_dir():
                    return ck3_path
    return None
