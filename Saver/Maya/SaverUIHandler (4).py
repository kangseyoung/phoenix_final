try:
    from PySide6.QtWidgets import *
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtCore import QFile, Qt
    from PySide6.QtGui import QPixmap, QFont
except:
    from PySide2.QtWidgets import *
    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtCore import QFile, Qt
    from PySide2.QtGui import QPixmap, QFont
    
# from shotgun_api3 import Shotgun
import sys
import os
import re
import json
from functools import partial
from data_explorer_json import DataExplorerJson
from file_saver import FileSaver

"""
어떤 프로그램에서 모듈이 실행되는지 확인
"""
# 마야에서 실행되는 경우
if 'maya' in sys.modules:
    try:
        import maya.cmds as cmds  
        from get_maya_current_path import MayaCurrentPathImporter
        current_path_importer = MayaCurrentPathImporter()
        current_path = current_path_importer.show_file_path()
        in_maya = True
    except ImportError:
        in_maya = False
# 누크에서 실행되는 경우
elif 'nuke' in sys.modules:
    try:
        import nuke  
        from get_nuke_path import NukeCurrentPathImporter
        current_path_importer = NukeCurrentPathImporter()
        current_path = current_path_importer.show_file_path()
        print("------------누크에서 열림-------------------")
        in_nuke = True
    except ImportError:
        in_nuke = False

class SaverUIHandler(QWidget):
    def __init__(self):
        super().__init__()
        self.initial_path = current_path
        self.setWindowTitle("Phoenix Save")
        self.explorer_json = DataExplorerJson()
        self.project_json_path = '/home/rapa/phoenix_pipeline_folders/project_json'
        
        self.get_shotgrid_json
        
        self.setting()
        self.events()
        self.first_show()
    """
    이벤트 함수 모음
    """
    def events(self):   # 시그널들 모음
        self.ui.tabWidget_pathtree.currentChanged.connect(self.event_tree_tab_changed)
        # select_btn_list = ["shots_all","shots_none","assets_all","assets_none"]
        # for i in select_btn_list:
        #     getattr(self.ui,f"pushButton_{i}").clicked.connect(partial(self.event_select_btn,i))
        self.ui.checkBox_avaliable_ver.stateChanged.connect(self.set_new_file_ver)
        self.ui.checkBox_avaliable_path.stateChanged.connect(self.select_path)
        self.ui.pushButton_cancel.clicked.connect(self.close_ui)
        self.ui.pushButton_save.clicked.connect(self.save_file)
        self.ui.treeWidget_my_tasks.currentItemChanged.connect(self.show_my_tasks_data)
        self.ui.treeWidget_assets.currentItemChanged.connect(self.show_asset_file_data)
        self.ui.treeWidget_shots.currentItemChanged.connect(self.show_shot_file_data)
        self.ui.spinBox_version.valueChanged.connect(self.event_save_info_changed)
        self.ui.comboBox_filetype.currentIndexChanged.connect(self.event_save_info_changed)
        
    def show_my_tasks_data(self):    # my task 폴더트리 선택시 실행되는 함수들
        if not self.ui.checkBox_avaliable_path.isChecked():
            self.change_current_path('my_task_signal')
        self.change_my_tasks_path()
        self.set_all_table_list('my_task_signal')
        self.set_file_table_list('my_task_signal')
    
    def show_asset_file_data(self):     # asset 폴더트리 선택시 실행되는 함수들
        if not self.ui.checkBox_avaliable_path.isChecked():
            self.change_current_path('asset_signal')
        self.change_asset_path()
        self.set_all_table_list('asset_signal')
        self.set_file_table_list('asset_signal')
    
    def show_shot_file_data(self):   # shot 폴더트리 선택시 실행되는 함수들
        if not self.ui.checkBox_avaliable_path.isChecked():
            self.change_current_path('shot_signal')
        self.change_shot_path()
        self.set_all_table_list('shot_signal')
        self.set_file_table_list('shot_signal')
        
    def event_tree_tab_changed(self,index):    # 폴더트리 탭 변경시 실행되는 함수들
        self.show_path(index)
        if index == 0:
            self.set_all_table_list('my_task_signal')
            self.set_file_table_list('my_task_signal')
        elif index == 1:
            self.set_all_table_list('asset_signal')
            self.set_file_table_list('asset_signal')
        elif index == 2:
            self.set_all_table_list('shot_signal')
            self.set_file_table_list('shot_signal')
        
    def event_save_info_changed(self):  # 사용자가 버전이나 파일 타입 변경시 실행되는 함수들
        self.set_preview()
        self.set_work_area()
        
    def event_select_btn(self, button):   # select 버튼 작동
        shots_list = ["ani", "light", "lookdev", "comp"]
        assets_list = ["mod","texture","rig","character"]
        
        if button == "shots_all":
            for i in shots_list:
                getattr(self.ui,f"checkBox_{i}").setChecked(True)
        elif button == "shots_none":
            for i in shots_list:
                getattr(self.ui,f"checkBox_{i}").setChecked(False)
                
        if button == "assets_all":
            for i in assets_list:
                getattr(self.ui,f"checkBox_{i}").setChecked(True)
        elif button == "assets_none":
            for i in assets_list:
                getattr(self.ui,f"checkBox_{i}").setChecked(False)
        
    """
    외부 정보 불러오기_id로
    """
    def get_project_id(self):   # 프로젝트 데이터 가져오기 
        json_path = '/home/rapa/phoenix_pipeline_folders/pipeline/launcher/loader/data_from_loader/json_from_loader.json'
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        # 254
        project_id = json_data['project_id']
        return project_id
    
    def get_user_id(self):   # 유저 정보 가져오기
        json_path = '/home/rapa/phoenix_pipeline_folders/pipeline/launcher/loader/data_from_loader/json_from_loader.json'
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        # 90
        usr_id = json_data['user_id']
        return usr_id
    
    def get_shotgrid_json(self):    # 시작할 때 샷그리드 정보 가져오기 ★
        project_id = self.get_project_id()
        user_id = self.get_user_id()
        
        self.explorer_json.make_project_user_json(project_id,user_id)
        self.explorer_json.make_assets_json(project_id)
        self.explorer_json.make_shots_json(project_id)
        self.explorer_json.make_user_assigned_work_json(project_id,user_id)
    
    def get_project_name(self): # 프로젝트 이름받기 ★
        project_id = self.get_project_id()
        user_id = self.get_user_id()
        
        json_path = f'{self.project_json_path}/project{project_id}_user{user_id}.json'
        
        with open(json_path, 'r') as f:
            js_data = json.load(f)
        
        project_name = js_data['project']['name']
        return project_name
    
    def get_user_name(self):   # 유저 이름받기 ★
        project_id = self.get_project_id()
        user_id = self.get_user_id()
        
        json_path = f'{self.project_json_path}/project{project_id}_user{user_id}.json'
        
        with open(json_path, 'r') as f:
            js_data = json.load(f)
        
        user_name = js_data['user']['name']
        return user_name
    
    
    """ Asset """
    def get_assets_json_data(self):  # 에셋 json 데이터 가져오기 ★
        project_id = self.get_project_id()
        
        json_path = f'{self.project_json_path}/assets_proj{project_id}.json'
        with open(json_path, 'r') as f:
            js_data = json.load(f)
        
        return js_data
    
    def get_asset_types(self):  # 에셋 타입 데이터 가져오기 ★
        asset_data = self.get_assets_json_data()
        
        asset_type_list = []
        asset_list = asset_data['data']
        for asset in asset_list:
            if not asset['sg_asset_type'] in asset_type_list:
                asset_type_list.append(asset['sg_asset_type'])
            
        return asset_type_list
    
    def get_assets(self):   # 에셋 데이터 가져오기 ★
        asset_data = self.get_assets_json_data()
        assets = asset_data['data']
        
        return assets
    
    def get_asset_tasks(self, asset_id):    # 에셋 테스크 데이터 가져오기 ★
        project_id = self.get_project_id()
        
        json_path = f'{self.project_json_path}/asset_tasks_proj{project_id}.json'
        with open(json_path, 'r') as f:
            js_data = json.load(f)
        
        asset_task_list = js_data['data']
        asset_tasks =[]
        for asset_task in asset_task_list:
            if not asset_task['asset_id'] == asset_id:
                pass
            asset_tasks.append(asset_task)
        
        return asset_tasks
    
    """ Shot """
    def get_sequences(self):    # 시퀀스 데이터 가져오기 ★
        project_id = self.get_project_id()
        
        json_path = f'{self.project_json_path}/sequences_proj{project_id}.json'
        with open(json_path, 'r') as f:
            js_data = json.load(f)
            
        sequences = js_data['data']
        
        return sequences
    
    def get_shots(self, sequence_id):   # 샷 데이터 가져오기 ★
        project_id = self.get_project_id()
        
        json_path = f'{self.project_json_path}/shots_proj{project_id}.json'
        with open(json_path, 'r') as f:
            js_data = json.load(f)
            
        shot_list = js_data['data']
        shots =[]
        
        for shot_data in shot_list:
            if not shot_data['sg_sequence']:
                continue
            if shot_data['sg_sequence']['id'] == sequence_id:
                shots.append(shot_data)
        
        return shots
    
    def get_shot_tasks(self, shot_id):   # 샷 테스크 데이터 가져오기 ★
        project_id = self.get_project_id()
        
        json_path = f'{self.project_json_path}/shot_tasks_proj{project_id}.json'
        with open(json_path, 'r') as f:
            js_data = json.load(f)
            
        shot_task_list = js_data['data']
        shot_tasks =[]
        for shot_task_data in shot_task_list:
            if not shot_task_data['shot_id'] == shot_id:
                pass
            shot_tasks.append(shot_task_data)
        
        return shot_tasks
    
    """ All """
    def get_assigned_work(self, user_id, project_id):   # 유저에게 배정된 작업만 가져오기(wtg,wip,pub) ★
        project_id = self.get_project_id()
        user_id = self.get_user_id()
        
        json_path = f'{self.project_json_path}/user{user_id}_assigned_tasks_proj{project_id}.json'
        with open(json_path, 'r') as f:
            js_data = json.load(f)
            
        shot_list = js_data['shot']
        asset_list = js_data['asset']
        
        return shot_list, asset_list
    
    def get_version(self, task_id): # wip, pub, version 데이터 가져오기 ★
        project_id = self.get_project_id()
    
        shot_ver_path = f'{self.project_json_path}/shot_versions_proj{project_id}.json'
        asset_ver_path = f'{self.project_json_path}/asset_versions_proj{project_id}.json'

        with open(shot_ver_path, 'r') as f:
            shot_task_list = json.load(f)['data']
        with open(asset_ver_path, 'r') as f:
            asset_task_list = json.load(f)['data']

        wip = pub = None
        versions = {'wip': None, 'pub': None}

        for shot_vers in shot_task_list:
            if shot_vers['task_id'] == task_id:
                wip_dic = shot_vers.get('wip', {})
                pub_dic = shot_vers.get('pub', {})

                wip = list(wip_dic.keys()) if wip_dic else None
                pub = list(pub_dic.keys()) if pub_dic else None

                versions = {'entity': 'Shots', 
                            'wip': wip_dic if wip_dic else None, 
                            'pub': pub_dic if pub_dic else None}
                break

        if not wip and not pub:  # 샷 리스트에 version이 없을 경우 에셋 리스트 확인
            for asset_vers in asset_task_list:
                if asset_vers['task_id'] == task_id:
                    wip_dic = asset_vers.get('wip', {})
                    pub_dic = asset_vers.get('pub', {})

                    wip = list(wip_dic.keys()) if wip_dic else None
                    pub = list(pub_dic.keys()) if pub_dic else None

                    versions = {'entity': 'Assets','wip': wip_dic if wip_dic else None, 'pub': pub_dic if pub_dic else None}
                    break
                
        return wip, pub, versions
        
    def get_thumbnail_list(self, task_id):   # 썸네일 가져오기 ★
        """
        주어진 task_id에 대해 썸네일 경로 리스트를 반환합니다.
        """
        proj_id = self.get_project_id()
        
        # JSON 파일 경로 설정
        shot_ver_path = f'{self.project_json_path}/shot_versions_proj{proj_id}.json'
        asset_ver_path = f'{self.project_json_path}/asset_versions_proj{proj_id}.json'

        # JSON 파일 로드
        with open(shot_ver_path, 'r') as f:
            shot_versions = json.load(f)['data']

        with open(asset_ver_path, 'r') as f:
            asset_versions = json.load(f)['data']

        # 버전 정보와 썸네일 경로를 저장할 딕셔너리
        thumbnail_list = []
        
        # 에셋 버전에서 썸네일 정보 찾기
        for asset_version in asset_versions:
            if asset_version['task_id'] == task_id:
                for status, versions in asset_version.items():
                    if status in ['wip', 'pub']:
                        for version_info in versions.values():
                            thumbnail_path = version_info.get('thumbnail', None)
                            version_id = version_info.get('id', None)
                            if version_id:
                                thumbnail_list.append({version_id: thumbnail_path})

        # 샷 버전에서 썸네일 정보 찾기
        for shot_version in shot_versions:
            if shot_version['task_id'] == task_id:
                for status, versions in shot_version.items():
                    if status in ['wip', 'pub']:
                        for version_info in versions.values():
                            thumbnail_path = version_info.get('thumbnail', None)
                            version_id = version_info.get('id', None)
                            if version_id:
                                thumbnail_list.append({version_id: thumbnail_path})

        return thumbnail_list
        
    def get_task_related_info(self, task_id):   # 선택한 테스크와 관련된 정보 가져오기.★
        """
        딕셔너리 형태로 출력
        ex)
        {
        'project_name': 'My Project',
        'project_id': 101,
        'task_name': 'Animation',
        'task_id': 1234,
        'shot_name': 'Shot_001',
        'shot_id': 202,
        'sequence_name': 'Seq_001',
        'sequence_id': 303
        }
        """
        project_id = self.get_project_id()
        project_name = self.get_project_name()

        # JSON 파일 경로 설정
        asset_task_path = os.path.join(self.project_json_path, f'asset_tasks_proj{project_id}.json')
        shot_task_path = os.path.join(self.project_json_path, f'shot_tasks_proj{project_id}.json')
        asset_version_path = os.path.join(self.project_json_path, f'asset_versions_proj{project_id}.json')
        shot_version_path = os.path.join(self.project_json_path, f'shot_versions_proj{project_id}.json')
        asset_file_path = os.path.join(self.project_json_path, f'assets_proj{project_id}.json')
        shot_file_path = os.path.join(self.project_json_path, f'shots_proj{project_id}.json')

        # JSON 파일 로드
        with open(asset_task_path, 'r', encoding='utf-8') as f:
            asset_tasks = json.load(f)['data']
        with open(shot_task_path, 'r', encoding='utf-8') as f:
            shot_tasks = json.load(f)['data']
        with open(asset_version_path, 'r', encoding='utf-8') as f:
            asset_versions = json.load(f)['data']
        with open(shot_version_path, 'r', encoding='utf-8') as f:
            shot_versions = json.load(f)['data']
        with open(asset_file_path, 'r', encoding='utf-8') as f:
            assets = json.load(f)['data']
        with open(shot_file_path, 'r', encoding='utf-8') as f:
            shots = json.load(f)['data']

        # 기본 task 정보
        task_info = {
            'project_name': project_name,
            'project_id': project_id,
            'task_id': task_id
        }

        # task_id에 맞는 에셋 정보 찾기
        asset_task = None
        for at in asset_tasks:
            if at['id'] == task_id:
                asset_task = at
                break
            
        if asset_task:
            asset = None
            for a in assets:
                if a['id'] == asset_task['asset_id']:
                    asset = a
                    break
                
            if asset:
                asset_version = None
                for av in asset_versions:
                    if av['task_id'] == task_id:
                        asset_version = av
                        break
                    
                task_info.update({
                    "task_name": asset_task.get('step_name', 'Unknown Task'),
                    "entity_type": "Asset",
                    "asset_id": asset['id'],
                    "asset_name": asset['code'],
                    "asset_type": asset['sg_asset_type'],
                    "latest_version": self.get_latest_version_code(
                        asset_version.get('wip', {}) if asset_version else {},
                        asset_version.get('pub', {}) if asset_version else {}
                    )
                })
    
        # task_id에 맞는 샷 정보 찾기
        for asset_task in asset_tasks:
            if not asset_task['id'] == task_id:
                continue
            for asset in assets:
                if not asset['id'] == asset_task['asset_id']:
                    continue
                for asset_version in asset_versions:
                    if not asset_version['task_id'] == task_id:
                        continue
                    task_info.update({
                        "task_name": asset_task.get('step_name', 'Unknown Task'),
                        "entity_type": "Asset",
                        "asset_id": asset['id'],
                        "asset_name": asset['code'],
                        "asset_type": asset['sg_asset_type'],
                        "latest_version": self.get_latest_version_code(asset_version.get('wip', {}),
                                                                       asset_version.get('pub', {}))
                    })
                    break
                break
            break
            
        # task_id에 맞는 샷 정보 찾기
        if "entity_type" not in task_info:  # 이미 에셋 정보가 채워졌는지 확인
            for shot_task in shot_tasks:
                if shot_task['id'] != task_id:
                    continue
                for shot in shots:
                    if shot['id'] != shot_task['shot_id']:
                        continue
                    for shot_version in shot_versions:
                        if shot_version['task_id'] != task_id:
                            continue
                        task_info.update({
                            "task_name": shot_task.get('step_name', 'Unknown Task'),
                            "entity_type": "Shot",
                            "shot_id": shot['id'],
                            "shot_name": shot['code'],
                            "sequence_name": shot['sg_sequence']['name'],
                            "sequence_id": shot['sg_sequence']['id'],
                            "latest_version": self.get_latest_version_code(
                                shot_version.get('wip', {}),
                                shot_version.get('pub', {})
                            )
                        })
                        break
                    break
                break
            
        return task_info
   
    def get_latest_version_code(self, wip_versions, pub_versions):  #★
        versions = {**wip_versions, **pub_versions}
        max_version = None
        max_version_number = -1

        for ver_name in versions.keys():
            match = re.search(r'v(\d{3})$', ver_name)
            if match:
                version_number = int(match.group(1))
                if version_number > max_version_number:
                    max_version_number = version_number
                    max_version = ver_name

        return max_version if max_version else 'no_version_v000'
   
    """
    외부 정보 불러오기_name으로
    """
    def get_sequence_id(self, project_id: int, sequence_name: str):    # 시퀀스 이름으로 시퀀스 ID 찾기
        """
        프로젝트 ID와 시퀀스 이름을 사용해 시퀀스의 ID를 가져옵니다.
        :param project_id: 프로젝트 ID
        :param sequence_name: 시퀀스 이름
        :return: 시퀀스 ID
        """
        sequence_file_path = os.path.join(self.project_json_path, f'sequences_proj{project_id}.json')

        with open(sequence_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)['data']

        # 시퀀스 이름에 해당하는 시퀀스 찾기
        for seq in data:
            if seq['code'] == sequence_name:
                sequence_id = seq['id']
                break
        # 시퀀스 ID 반환
        
        return sequence_id
        
    def get_shot_id(self, sequence_id: int, shot_name: str): # 샷 이름으로 샷 ID 찾기 
        """
        시퀀스 ID와 샷 이름을 사용해 샷의 ID를 가져옵니다.
        :param sequence_id: 시퀀스 ID
        :param shot_name: 샷 이름
        :return: 샷 ID (없으면 None 반환)
        """
        project_id = self.get_project_id()
        shot_file_path = os.path.join(self.project_json_path, f'shots_proj{project_id}.json')

        with open(shot_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)['data']

        # 시퀀스 ID와 샷 이름에 해당하는 샷 찾기
        for shot in data:
            if not shot['sg_sequence']:
                continue
            if shot['sg_sequence']['id'] == sequence_id and shot['code'] == shot_name:
                shot_id = shot['id']
                break

        return shot_id
    
    def get_asset_id(self, project_id: int, asset_name: str):   # 에셋 이름으로 에셋 ID 찾기
        """
        프로젝트 ID와 에셋 이름을 사용해 에셋의 ID를 가져옵니다.
        :param project_id: 프로젝트 ID
        :param asset_name: 에셋 이름
        :return: 에셋 ID (없으면 None 반환)
        """
        # 에셋 JSON 파일 경로
        asset_file_path = os.path.join(self.project_json_path, f'assets_proj{project_id}.json')

        # JSON 파일 로드
        with open(asset_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)['data']

        # 에셋 이름에 해당하는 에셋 찾기
        asset_id = None
        for asset in data:
            if asset['code'] == asset_name:
                asset_id = asset['id']
                break

        return asset_id
        
    def get_task_id(self, entity_id: int, entity_type: str ,task_name: str): # 테스크 이름으로 테스크 ID 찾기
        """
        샷 또는 에셋의 ID와 태스크 이름을 사용해 태스크의 ID를 가져옵니다.
        :param entity_id: 샷 또는 에셋의 ID
        :param entity_type: "Shot" 또는 "Asset"
        :param task_name: 태스크 이름
        :return: 태스크 ID (없으면 None 반환)
        """
        project_id = self.get_project_id()
        # 적절한 JSON 파일 경로를 설정
        if entity_type == "Shot":
            task_file_path = os.path.join(self.project_json_path, f'shot_tasks_proj{project_id}.json')
        elif entity_type == "Asset":
            task_file_path = os.path.join(self.project_json_path, f'asset_tasks_proj{project_id}.json')

        with open(task_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)['data']

        # 태스크 ID를 찾기
        for task in data:
            if entity_type == "Shot":
                if task['shot_id'] == entity_id and task['step_name'] == task_name:
                    task_id = task['id']
            elif entity_type == "Asset":
                if task['asset_id'] == entity_id and task['step_name'] == task_name:
                    task_id = task['id']
                
        return task_id
        
    """
    기타 함수
    """
    def check_file_version(self): # 기존 파일들 버전 체크, str 출력
        file_name_with_ver = os.path.basename(current_path)
        
        p = re.compile('v\d{3}')
        p_data = p.search(file_name_with_ver)
        
        if p_data:
            version = p_data.group()
        return version
    
    def check_file_type(self):  # 현재 열린 파일이 어떤 종류인지 체크 
        print(f"현재 경로 : {current_path}")
        ext = None
        if not current_path:
            print("경로가 안잡힘")
            return
        file_name = current_path.split("/")[-1]
        ext = file_name.split(".")[-1]
    
        return ext
    
    def check_shotgrid_version(self):   # 현재 지정된 경로에 따라 샷그리드에서 버전 체크
        save_info,_ = self.store_save_info()
        task_id = save_info['task']['id']
        wips,_,_ = self.get_version(task_id)
        
        now_ver = '000'
        next_ver = '001'
        
        if not wips:
            return now_ver, next_ver
            
        ver_list = []
        for wip in wips:
            p = re.compile("v(\d{3})")
            p_data = p.search(wip)
            if p_data:
                wip_ver = p_data.group(1)
                ver_list.append(wip_ver)
        if ver_list:
            now_ver = sorted(ver_list)[-1]
            next_ver_num = int(now_ver) + 1
            next_ver = str(next_ver_num).zfill(3)
        
        return now_ver, next_ver
        
    def get_shotgrid_directory(self):   # 현재 경로에서 샷그리드 관련 경로 찾기
        # 경로 안바꿀때 
        # 경로 바꿀때 두가지로 작동
        root_folder = "/phoenix_pipeline_folders/"
        p = re.compile(rf"{root_folder}(.+?)/(Shots|Assets)/(.+?)/[^/]+$")
        p_data = p.search(current_path) 
        if p_data:
            extracted_path = os.path.join(p_data.group(1), p_data.group(3))
            entity_type = p_data.group(2)
        return extracted_path, entity_type
    
    def store_save_info(self):  # 저장될 경로에 필요한 정보 저장
        """
        {'project' : {'name' : project_name, 'id' : project_id}, 
        'sequence' : {'name': seq_name, 'id' : seq_id}, 
        'shot' : {'name': shot_name, 'id' : shot_id}, 
        'task' : {'name': task_name,'id':task_id}}
        
        {'project' : {'name' : project_name, 'id' : project_id}, 
        'asset_type' : {'name': asset_type_name}, 
        'asset' : {'name': asset_name, 'id' : asset_id}, 
        'task' : {'name': task_name,'id':task_id}}
        """
        total_dic = {}
        extracted_path,entity_type = self.get_shotgrid_directory()
        project_name = extracted_path.split('/')[0]
        project_id = self.get_project_id()
        
        # 샷 정보
        if entity_type == "Shots":
            seq_name = extracted_path.split('/')[1]
            seq_id = self.get_sequence_id(project_id, seq_name)
            shot_name = extracted_path.split('/')[2]
            shot_id = self.get_shot_id(seq_id, shot_name)
            task_name = extracted_path.split('/')[3]
            task_id = self.get_task_id(shot_id,"Shot",task_name)
            
            total_dic['project'] = {'name' : project_name, 'id' : project_id}
            total_dic['sequence'] = {'name' : seq_name, 'id' : seq_id}
            total_dic['shot'] = {'name' : shot_name, 'id' : shot_id}
            total_dic['task'] = {'name' : task_name, 'id' : task_id}
            
        # 에셋 정보
        if entity_type == "Assets":
            asset_type_name = extracted_path.split('/')[1]
            asset_name = extracted_path.split('/')[2]
            asset_id = self.get_asset_id(project_id, asset_name)
            task_name = extracted_path.split('/')[3]
            task_id = self.get_task_id(asset_id,"Asset",task_name)
            
            total_dic['project'] = {'name' : project_name, 'id' : project_id}
            total_dic['asset_type'] = {'name' : asset_type_name}
            total_dic['asset'] = {'name' : asset_name, 'id' : asset_id}
            total_dic['task'] = {'name' : task_name, 'id' : task_id}
            
        return total_dic, entity_type
    
    def store_changed_path(self):   # 바뀐 경로 저장해두기
        changed_path = current_path
        print(f"---------바뀐 경로 : {changed_path}------------------")
        return changed_path
    
    def select_path(self): # 기존 경로로 할지 바뀐 경로로 할지 정해줌
        global current_path
        index = self.ui.tabWidget_pathtree.currentIndex()
        if not self.ui.checkBox_avaliable_path.isChecked():
            if index == 0:
                self.change_current_path('my_task_signal')
            elif index == 1:
                self.change_current_path('asset_signal')
            elif index == 2:
                self.change_current_path('shot_signal')
        else:
            current_path = self.initial_path
        self.setup_bottom_layer()    
    
    """
    기본 표시 셋팅
    """
    def first_show(self): # 기본 셋팅
        # 유저 이름 넣기
        user_name = self.get_user_name()
        self.ui.label_user_name.setText(user_name)
        # project 이름 넣기
        proj_name = self.get_project_name()
        self.ui.label_project_name.setText(proj_name)
        # 기본 ui 셋팅
        self.ui.stackedWidget_path.setCurrentIndex(0)
        self.ui.tabWidget_pathtree.setCurrentIndex(0)
        self.ui.tabWidget_file_list.setCurrentIndex(0)
        self.ui.comboBox_filter.setCurrentIndex(0)
        self.ui.checkBox_avaliable_ver.setChecked(True)
        self.ui.checkBox_avaliable_path.setChecked(True)
        # 좌측 레이어 셋팅
        self.set_path_filter()
        self.set_my_tasks_tree()
        self.set_asset_path_tree()
        self.set_shot_path_tree()
        # 하단 레이어 셋팅
        self.setup_bottom_layer()
    
    """
    좌 레이어 셋팅
    """
    def show_path(self,index):    # 상단 경로 Tasks, Assets, Shots 별로 바꿔주기
        self.ui.stackedWidget_path.setCurrentIndex(index)
        
    def set_path_filter(self):  # My Tasks 폴더구조 트리 필터
        filter_list = ["All","Duration(Work)"]
        self.ui.comboBox_filter.addItems(filter_list)
        
    """ My Tasks """
    def change_my_tasks_path(self):     #My Tasks 상단 경로 바꿔주기
        selected_item = self.ui.treeWidget_my_tasks.currentItem()
        if selected_item.parent() == None:
            pass
        elif selected_item.parent().parent() == None:
            part = selected_item.text(0)
            self.ui.label_part.setText(part)
            
            self.ui.label_arrow_1.clear()
            self.ui.label_detail.clear()
        else:
            part = selected_item.parent().text(0)
            detail = selected_item.text(0)
            self.ui.label_part.setText(part)
            self.ui.label_arrow_1.setText('▶')
            self.ui.label_detail.setText(detail)
    
    def set_my_tasks_tree(self):    # My Tasks 폴더구조 트리 띄우기
        user_id = self.get_user_id()
        project_id = self.get_project_id()
        shot_list, asset_list = self.get_assigned_work(user_id,project_id)
        
        if shot_list:
            # 'Shots' 항목 추가
            shot_title_item = QTreeWidgetItem(self.ui.treeWidget_my_tasks)
            shot_title_item.setText(0, 'Shots')
            shot_title_item.setExpanded(True)
            
            # Sequence와 Shot을 트리에 추가
            for dic in shot_list:
                seq_name = dic['sequence']['name']
                seq_id = dic['sequence']['id']
                shot_name = dic['shot']['name']
                task_id = dic['task']['id']
                
                
                # Sequence 항목을 찾거나 생성
                seq_item = None
                for i in range(shot_title_item.childCount()):
                    if shot_title_item.child(i).text(0) == seq_name:
                        seq_item = shot_title_item.child(i)
                        break

                if not seq_item:
                    seq_item = QTreeWidgetItem(shot_title_item)
                    seq_item.setText(0, seq_name)
                    seq_item.setData(0, Qt.UserRole, seq_id)
                
                # Shot 항목 추가
                shot_item = QTreeWidgetItem(seq_item)
                shot_item.setText(0, shot_name)
                shot_item.setData(0,Qt.UserRole, task_id)
                
        if asset_list:
            # 'Assets' 항목 추가
            asset_title_item = QTreeWidgetItem(self.ui.treeWidget_my_tasks)
            asset_title_item.setText(0, 'Assets')
            asset_title_item.setExpanded(True)
            
            # Asset Type과 Asset을 트리에 추가
            for dic in asset_list:
                asset_type_name = dic['asset_type']
                asset_name = dic['asset']['name']
                task_id = dic['task']['id']
                
                # Asset Type 항목을 찾거나 생성
                asset_type_item = None
                for i in range(asset_title_item.childCount()):
                    if asset_title_item.child(i).text(0) == asset_type_name:
                        asset_type_item = asset_title_item.child(i)
                        break

                if not asset_type_item:
                    asset_type_item = QTreeWidgetItem(asset_title_item)
                    asset_type_item.setText(0, asset_type_name)
                
                # Asset 항목 추가
                asset_item = QTreeWidgetItem(asset_type_item)
                asset_item.setText(0, asset_name)
                asset_item.setData(0,Qt.UserRole, task_id)
                
    """ Asset """
    def change_asset_path(self): # Asset 상단 경로 바꿔주기 
        selected_item = self.ui.treeWidget_assets.currentItem()
        if selected_item.parent() == None:
            asset_type = selected_item.text(0)
            self.ui.label_asset_type.setText(asset_type)
            
            self.ui.label_arrow_2.clear()
            self.ui.label_asset.clear()
            self.ui.label_arrow_3.clear()
            self.ui.label_asset_task.clear()
        elif selected_item.parent().parent() == None:
            asset_type = selected_item.parent().text(0)
            shot = selected_item.text(0)
            self.ui.label_asset_type.setText(asset_type)
            self.ui.label_arrow_2.setText("▶")
            self.ui.label_asset.setText(shot)
            
            self.ui.label_arrow_3.clear()
            self.ui.label_asset_task.clear()
        else:
            asset_type = selected_item.parent().parent().text(0)
            shot = selected_item.parent().text(0)
            task = selected_item.text(0)
            self.ui.label_asset_type.setText(asset_type)
            self.ui.label_arrow_2.setText("▶")
            self.ui.label_asset.setText(shot)
            self.ui.label_arrow_3.setText("▶")
            self.ui.label_asset_task.setText(task)
        
    def set_asset_path_tree(self):  # Asset 폴더구조 트리 띄우기 ★
        asset_type_list = self.get_asset_types()
        assets = self.get_assets()
        
        for asset_type in asset_type_list:
            asset_type_item = QTreeWidgetItem(self.ui.treeWidget_assets)
            asset_type_item.setText(0, asset_type)
            for asset in assets:
                if not asset['sg_asset_type'] == asset_type:
                    continue
                asset_item = QTreeWidgetItem(asset_type_item)
                asset_item.setText(0,asset['code'])
                asset_item.setData(0, Qt.UserRole, asset['id'])   # item에 데이터 담기
                tasks = self.get_asset_tasks(asset['id'])
                for task in tasks:
                    if task['step_name'] == 'Unknown Step':
                        continue
                    if not task['asset_id'] == asset['id']:
                        continue 
                    task_item = QTreeWidgetItem(asset_item)
                    task_item.setText(0, task['step_name'])
                    task_item.setData(0, Qt.UserRole, task['id'])
            
    
    """ Shot """
    def change_shot_path(self): # Shot 상단 경로 바꿔주기
        selected_item = self.ui.treeWidget_shots.currentItem()
        if selected_item.parent() == None:
            seq = selected_item.text(0)
            self.ui.label_seq.setText(seq)
            
            self.ui.label_arrow_4.clear()
            self.ui.label_shot.clear()
            self.ui.label_arrow_5.clear()
            self.ui.label_shot_task.clear()
        elif selected_item.parent().parent() == None:
            seq = selected_item.parent().text(0)
            shot = selected_item.text(0)
            self.ui.label_seq.setText(seq)
            self.ui.label_arrow_4.setText("▶")
            self.ui.label_shot.setText(shot)
            
            self.ui.label_arrow_5.clear()
            self.ui.label_shot_task.clear()
        else:
            seq = selected_item.parent().parent().text(0)
            shot = selected_item.parent().text(0)
            task = selected_item.text(0)
            self.ui.label_seq.setText(seq)
            self.ui.label_arrow_4.setText("▶")
            self.ui.label_shot.setText(shot)
            self.ui.label_arrow_5.setText("▶")
            self.ui.label_shot_task.setText(task)
        
    def set_shot_path_tree(self):    # Shot 폴더구조 트리 띄우기 ★
        sequences = self.get_sequences()
        
        for seq in sequences:
            seq_item = QTreeWidgetItem(self.ui.treeWidget_shots)
            seq_item.setText(0, seq['code'])
            seq_item.setData(0, Qt.UserRole, seq['id'])
            shots = self.get_shots(seq['id'])
            for shot in shots:
                shot_item = QTreeWidgetItem(seq_item)
                shot_item.setText(0,shot['code'])
                shot_item.setData(0, Qt.UserRole, shot['id'])   # item에 데이터 담기
                tasks = self.get_shot_tasks(shot['id'])
                for task in tasks:
                    if task['step_name'] == 'Unknown Step':
                        continue
                    if not task['shot_id'] == shot['id']:
                        continue 
                    task_item = QTreeWidgetItem(shot_item)
                    task_item.setText(0, task['step_name'])
                    task_item.setData(0, Qt.UserRole, task['id'])
       
        
    """
    우 레이어 셋팅
    """
    def set_thumbnail(self, table_widget, row, ver_id, thumbnail_list): # 썸네일을 테이블 위젯의 특정 셀에 설정
        """
        썸네일을 테이블 위젯의 특정 셀에 설정합니다.
        """
        thumbnail_path = next((thumbnail_dic.get(ver_id, "") for thumbnail_dic in thumbnail_list if ver_id in thumbnail_dic), "")
        thumbnail = QLabel()
        if thumbnail_path == 'No Thumbnail':
            thumbnail.setText("No Image")
            thumbnail.setAlignment(Qt.AlignCenter)
        else:
            pix = QPixmap(thumbnail_path)
            sc_pix = pix.scaledToWidth(100)
            thumbnail.setPixmap(sc_pix)
        table_widget.setCellWidget(row, 0, thumbnail)

    def adjust_table_size(self, table_widget):  # 테이블 위젯 높이 조절
        """
        테이블 위젯의 높이를 데이터에 맞게 자동 조정합니다.
        """
        default_row_height = 71.4
        total_height = table_widget.rowCount() * default_row_height

        # 테이블의 높이를 조정합니다.
        table_widget.setFixedHeight(total_height)
        
    def fill_table_with_data(self, table_widget, status_list, versions, thumbnail_list, entity_type, asset_or_shot):    # 데이터를 테이블 위젯에 채우기
        """
        WIP 또는 Pub 데이터를 테이블 위젯에 채우는 함수입니다.
        """
        if not status_list:
            return
        
        # 테이블 위젯의 행 수를 데이터 목록의 길이로 설정
        table_widget.setRowCount(len(status_list))
        
        row = 0
        for status in status_list:
            version_info = versions.get(entity_type, {}).get(status, {})
            ver_id = version_info.get('id', None)
            artist = version_info.get('artist', 'Unknown')
            date = version_info.get('created_at', 'Unknown')

            # 썸네일 설정
            self.set_thumbnail(table_widget, row, ver_id, thumbnail_list)

            # 텍스트 정보 설정
            info_text = QPlainTextEdit()
            font = QFont()
            font.setPointSize(8)
            info_text.setFont(font)
            info_text.appendPlainText(asset_or_shot)
            info_text.appendPlainText(status)
            info_text.appendPlainText(artist)
            info_text.appendPlainText(date)
            info_text.setFixedHeight(70)
            info_text.setReadOnly(True)
            info_text.setStyleSheet("QPlainTextEdit { border: none; }")
            table_widget.setCellWidget(row, 1, info_text)
            
            # 행 높이 조정
            table_widget.setRowHeight(row, 70)
            
            row += 1
            
        # 테이블 사이즈 조정    
        if table_widget in self.ui.treeWidget_grid_total.findChildren(QTableWidget):
            self.adjust_table_size(table_widget)    
            
    def initialize_table_widget(self, table_widget):    # 테이블 위젯 기본 설정
        """
        테이블 위젯의 기본 설정을 초기화합니다.
        """
        table_widget.setColumnCount(2)
        table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table_widget.horizontalHeader().setVisible(False)
        table_widget.horizontalHeader().setStretchLastSection(True)
        table_widget.verticalHeader().setVisible(False)
        table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # 행 수에 따라 높이 초기화
        table_widget.setRowCount(0)

    def set_all_table_list(self, filter):   #  WIP 및 Pub 파일을 동시에 보여주기 ★
        """
        WIP 및 Pub 파일을 동시에 보여주는 함수입니다.
        """
        # 기존 테이블 위젯의 내용을 초기화
        self.ui.treeWidget_grid_total.clear()

        # 필터에 따라 선택된 항목을 가져오기
        if filter == 'my_task_signal':
            selected_item = self.ui.treeWidget_my_tasks.currentItem()
        elif filter == 'asset_signal':
            selected_item = self.ui.treeWidget_assets.currentItem()
        elif filter == 'shot_signal':
            selected_item = self.ui.treeWidget_shots.currentItem()

        # 선택된 항목 확인
        if selected_item is None or selected_item.childCount() != 0:
            return

        # 선택된 항목에서 정보값들 가져오기
        task_id = selected_item.data(0, Qt.UserRole)
        wips, pubs, versions = self.get_version(task_id)
        thumbnail_list = self.get_thumbnail_list(task_id) or []

        # 'Working' 및 'Publishes' 항목 추가
        working_item = QTreeWidgetItem(self.ui.treeWidget_grid_total)
        working_item.setText(0, 'Working')
        working_item.setExpanded(True)
        publishes_item = QTreeWidgetItem(self.ui.treeWidget_grid_total)
        publishes_item.setText(0, 'Publishes')
        publishes_item.setExpanded(True)
        
        if wips:
            wip_table_item = QTreeWidgetItem(working_item)
            wip_table = QTableWidget()
            self.initialize_table_widget(wip_table)
            self.ui.treeWidget_grid_total.setItemWidget(wip_table_item, 0, wip_table)
            self.fill_table_with_data(wip_table, wips, versions, thumbnail_list, 'wip', selected_item.parent().text(0))

        if pubs:
            pub_table_item = QTreeWidgetItem(publishes_item)
            pub_table = QTableWidget()
            self.initialize_table_widget(pub_table)
            self.ui.treeWidget_grid_total.setItemWidget(pub_table_item, 0, pub_table)
            self.fill_table_with_data(pub_table, pubs, versions, thumbnail_list, 'pub', selected_item.parent().text(0))

    def set_file_table_list(self, filter):  # WIP 및 Pub 파일을 나누어 보여주기 ★
        """
        WIP 및 Pub 파일을 나누어 보여주는 함수입니다.
        """
        # 테이블 위젯 초기화
        self.ui.tableWidget_list_pub.clear()
        self.ui.tableWidget_list_wip.clear()

        # 필터에 따라 선택된 항목 가져오기
        if filter == 'my_task_signal':
            selected_item = self.ui.treeWidget_my_tasks.currentItem()
        elif filter == 'asset_signal':
            selected_item = self.ui.treeWidget_assets.currentItem()
        elif filter == 'shot_signal':
            selected_item = self.ui.treeWidget_shots.currentItem()

        # 선택된 항목 확인
        if selected_item is None or selected_item.childCount() != 0:
            return

        # 선택된 항목에서 정보 가져오기
        task_id = selected_item.data(0, Qt.UserRole)
        wips, pubs, versions = self.get_version(task_id)

        # 테이블 위젯 설정
        self.initialize_table_widget(self.ui.tableWidget_list_wip)
        self.initialize_table_widget(self.ui.tableWidget_list_pub)

        # 썸네일 리스트 한 번만 호출
        thumbnail_list = self.get_thumbnail_list(task_id)

        # WIP와 Pub 데이터를 테이블 위젯에 채우기
        if wips:
            self.fill_table_with_data(self.ui.tableWidget_list_wip, wips, versions, thumbnail_list, 'wip', selected_item.parent().text(0))

        if pubs:
            self.fill_table_with_data(self.ui.tableWidget_list_pub, pubs, versions, thumbnail_list, 'pub', selected_item.parent().text(0))

    
    """
    하단 레이어 셋팅
    """
    
    def setup_bottom_layer(self):   # 하단 레이어 셋팅
        self.set_new_file_name()
        self.set_new_file_ver()
        self.set_file_type()
        self.set_preview()
        self.set_work_area()
    
    def set_new_file_name(self):    # 파일 이름 정보 띄워주기
        file_name_with_ver = os.path.basename(current_path)
        now_version = self.check_file_version()
        file_name = file_name_with_ver.split(f"_{now_version}")[0]
        self.ui.label_new_file_name.setText(file_name)
        return file_name
    
    def set_new_file_ver(self): # 버전 정하기
        _, next_version = self.check_shotgrid_version()
        
        if self.ui.checkBox_avaliable_ver.isChecked():
            self.ui.spinBox_version.setValue(int(next_version))
            version = f"v{next_version}"
            self.ui.spinBox_version.setEnabled(False)
        else:
            self.ui.spinBox_version.setEnabled(True)
            changed_version = self.ui.spinBox_version.value()
            version = f"v{str(changed_version).zfill(3)}"
        return version
    
    def set_file_type(self):    # 열린 프로그램 기준 파일 확장자 정하기
        # 누크일 때, 마야일 때 분리(프로그램별 상이)
        self.ui.comboBox_filetype.clear()
        
        maya = ["ma", "mb"]
        nuke = ["nk", "nknc"]
        if self.check_file_type() in maya:
            self.ui.comboBox_filetype.addItems(maya)
            self.ui.comboBox_filetype.setCurrentText("mb")
        elif self.check_file_type() in nuke:
            self.ui.comboBox_filetype.addItems(nuke)
            self.ui.comboBox_filetype.setCurrentText("nk")
            
    def set_preview(self):  # 저장될 파일 이름 미리 보여주기
        file_name = self.set_new_file_name()
        ver = self.set_new_file_ver()
        ext = self.ui.comboBox_filetype.currentText()
        new_file_name = f"{file_name}_{ver}.{ext}"
        self.ui.label_preview.setText(new_file_name)
        
        return new_file_name
        
    def set_work_area(self):    # 저장될 경로 미리 보여주기
        # 선택이 안됐을 때 경로 정하기
        # 선택이 됐을 때 경로 정하기 
        extracted_path,_ = self.get_shotgrid_directory()
        new_file_name = self.set_preview()
        work_area = f"{extracted_path}/{new_file_name}"
        self.ui.label_work_area.setText(work_area)
        self.store_save_info()
    
    
    
    """
    기타
    """
    def close_ui(self): # 프로그램 닫기
        self.close()
    
    def change_current_path(self, filter):  # 저장될 경로 바꾸기
        global current_path
        root_path = '/home/rapa/phoenix_pipeline_folders/'
        
        # 필터에 따라 선택된 항목 가져오기
        if filter == 'my_task_signal':
            _, entity_type = self.store_save_info()
            selected_item = self.ui.treeWidget_my_tasks.currentItem()
            entity = entity_type
            
        elif filter == 'shot_signal':
            selected_item = self.ui.treeWidget_shots.currentItem()
            entity = 'Shots'
            
        elif filter == 'asset_signal':
            selected_item = self.ui.treeWidget_assets.currentItem()
            entity = 'Assets'
        
        # 선택된 항목 확인
        if selected_item is None:
            return
        if not selected_item.childCount() == 0:
            return
        
        # 선택된 항목에서 정보 가져오기
        task_id = selected_item.data(0, Qt.UserRole)
        task_info = self.get_task_related_info(task_id)
        print('--------task_info-------')
        print(task_info)        
        
        if entity ==  'Shots':
            new_current_path_without_ext = os.path.join(root_path,task_info['project_name'],
                                            entity,task_info['sequence_name'],
                                            task_info['shot_name'],task_info['task_name'],
                                            "wip",task_info['latest_version'])
        elif entity == 'Assets':
            new_current_path_without_ext = os.path.join(root_path,task_info['project_name'],
                                            entity,task_info['asset_type'],
                                            task_info['asset_name'],task_info['task_name'],
                                            "wip",task_info['latest_version'])
            
        ext = self.initial_path.split('.')[-1]
        new_current_path = f"{new_current_path_without_ext}.{ext}"
        current_path = new_current_path
        self.store_changed_path()
        self.setup_bottom_layer()
        
    def make_save_local_path(self): # 로컬에 저장할 경로 만들기
        save_info, entity_type = self.store_save_info()
        
        root_path = "/home/rapa/phoenix_pipeline_folders/"
        project_name = save_info['project']['name']
        if entity_type == "Shots":
            seq_name = save_info['sequence']['name']
            shot_name = save_info['shot']['name']
            task_name = save_info['task']['name']
            file_name = self.set_preview()
            
            local_path = os.path.join(root_path,project_name,entity_type,
                                      seq_name,shot_name,task_name,
                                      "wip",file_name)
            
        elif entity_type == "Assets":
            asset_type_name = save_info['asset_type']['name']
            asset_name = save_info['asset']['name']
            task_name = save_info['task']['name']
            file_name = self.set_preview()
        
            local_path = os.path.join(root_path,project_name,entity_type,
                                      asset_type_name,asset_name,task_name,
                                      "wip",file_name)
        return local_path
    
    def save_file(self):    # 로컬에 파일을 저장하고 샷그리드로 링크 걸어주기
        file_saver = FileSaver()
        file_path = self.make_save_local_path()
        print(f"여기 로컬에 저장할거임 : {file_path}")
        # 로컬에 파일 저장하기
        ext = current_path.split('.')[-1]
        print(f"확장자 : {ext}")
        if ext in ['nk', 'nknc']:
            file_saver.save_in_local('Nuke', file_path)
            print(f'save모듈로 넘어감')
        elif ext in ['ma', 'mb']:
            file_saver.save_in_local('Maya', file_path)
            
        # 샷그리드에 파일경로 업로드
        save_info, entity_type = self.store_save_info()
        file_saver.upload_to_shotgrid(save_info, entity_type, file_path)
        
        self.close()
        
    def setting(self):
        ui_file_path = "/home/rapa/test_project/ui/saver_mockup.ui" 
        ui_file = QFile(ui_file_path)
        self.ui = QUiLoader().load(ui_file,self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SaverUIHandler()
    win.show()
    sys.exit(app.exec())