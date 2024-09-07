from shotgun_api3 import Shotgun
import maya
import os
from Saver.Maya.maya_pub_data_manager import MayaFileSaver

class FileSaver():
    def __init__(self):
        self.sg = Shotgun(
            "https://4thacademy.shotgrid.autodesk.com",
            "kangseyoung",
            "imthtqts8zqqXylfckoiihx-z"
        )
    def save_in_local(self, file_type, file_path):
        import maya.cmds as cmds
        if file_type == "Maya":
            cmds.file(rename=file_path)
            cmds.file(save=True, type='mayaAscii')
            print('파일이 저장되었습니다.')
            print(f'file path : {file_path}')
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # 열린 파일이 누크일 때 로컬에 저장

    
    def upload_to_shotgrid(self, save_info, entity_type,file_path):
        print("샷그리드 업로드 시작")
        print(f"save_info : {save_info}")
        print(f"entity_type : {entity_type}")
        print(f"file_path : {file_path}")
        file_name = file_path.split('/')[-1]
        ver_name = file_name.split('.')[0]
        project_id = save_info['project']['id']
        
        if entity_type == "Shots":
            shot_id = save_info['shot']['id']
            task_id = save_info['task']['id']
            
            created_version = self.sg.create("Version", {
                "project": {"type": "Project", "id": project_id},
                "code": ver_name,
                "sg_path":file_path,
                "sg_status_list": "wip",  
                "entity": {"type": "Shot", "id": shot_id},
                "sg_task": {"type": "Task", "id": task_id}
            })
            print(f"{created_version.get('id')} 버젼이 생성되었습니다.")
            
        elif entity_type == "Assets":
            asset_type_id = save_info['asset_type']['id']
            asset_id = save_info['asset']['id']
            task_id = save_info['task']['id']
            
            created_version = self.sg.create("Version", {
                "project": {"type": "Project", "id": project_id},
                "code": ver_name,
                "sg_path":file_path,
                "sg_status_list": "wip",  
                "entity": {"type": "Asset", "id": asset_id},
                "sg_task": {"type": "Task", "id": task_id},
                "asset_type" : asset_type_id
            })
            print(f"{created_version.get('id')} 버젼이 생성되었습니다.")