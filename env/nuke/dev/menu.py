print("*" *30)
print("menu.py")
print("메뉴 스크립트가 실행됨")
print("*" *30)

import sys
sys.path.append("/home/rapa/_phoenix_")
import nuke
from Saver.Nuke import SaverUIHandler


def show_saver_handler():
    # # script_dir = "/home/rapa/_phoenix_/env/nuke/dev/python"
    # if script_dir not in sys.path:
    #     # sys.path.append(script_dir)
    # # reload(SaverUIHandler)
    
    script_dir = "/home/rapa/env/nuke/dev/python/"
    if script_dir not in sys.path:
        sys.path.append(script_dir)
    from importlib import reload
    import SaverUIHandler
    # import FileSaver
    # import DataExplorerJson
    # import NukeCurrentPathImporter
    reload(SaverUIHandler)
    # reload(FileSaver)
    # reload(DataExplorerJson)
    # reload(NukeCurrentPathImporter)
    
    global win
    win = SaverUIHandler.SaverUIHandler()
    win.show()
    
menu_bar = nuke.menu("Nuke")
menu_4th = menu_bar.addMenu("4th_Academy")
pheonix_menu = menu_bar.addMenu("pheonix")

# addCommand(라벨(메뉴이름), 명령, 바로가기, 순서)_바로가기와 순서는 없어도 실행이 됨
# menu_4th.addCommand("make mov", pipeline_script.set_outpath, "F8")
# menu_4th.addCommand("mini button", pipeline_script.button, "F9")
# menu_4th.addCommand("write read", pipeline_script.write_read, "Alt+R")
# menu_4th.addCommand("copy path", pipeline_script.copy_win_path, "Ctrl+M")
# menu_4th.addCommand("loader", pipeline_script.show_loader)
pheonix_menu.addCommand("File save", show_saver_handler)
# pheonix_menu.addCommand("Publish",show_publish_handler())
