from typing import List, Dict, Any
from datetime import datetime
import shotgun_api3
import requests
import shutil
import json
import os

class DataExplorerJson:
    def __init__(self):
        self.sg = shotgun_api3.Shotgun("https://4thacademy.shotgrid.autodesk.com",
                                       "kangseyoung",
                                       "imthtqts8zqqXylfckoiihx-z")
        self.make_json_path()
        

    def make_json_path(self):   # JSON파일이 저장될 경로 설정
        root_path = '/home/rapa/phoenix_pipeline_folders/'
        file_path = os.path.join(root_path, 'project_json')
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        self.json_path = file_path
    
    def make_project_user_json(self, project_id: int, user_id: int):    # 프로젝트와 유저 정보 JSON만들기
        """
        주어진 프로젝트 ID로 프로젝트 정보와 유저 정보를 찾아 JSON 형식으로 파일로 저장합니다.
        """
        print('project_user_json 실행')
        # 프로젝트 정보 가져오기
        project = self.sg.find_one('Project', [['id', 'is', project_id]], ['name'])
        
        # 유저 정보 가져오기
        user = self.sg.find_one('HumanUser', [['id', 'is', user_id]], ['name'])
        
        project_filename = f'project{project_id}_user{user_id}.json'
        project_file_path = os.path.join(self.json_path, project_filename)
        
        if project and user:
            # 프로젝트 및 유저 정보를 JSON 형식으로 변환
            project_info = {'id': project_id, 'name': project['name']}
            user_info = {'id': user_id, 'name': user['name']}
            json_data = {'timestamp': datetime.now().isoformat(), 
                         'project': project_info,
                         'user': user_info}
            
            # JSON 데이터를 파일에 저장
            with open(project_file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
        else:
            if not project:
                raise ValueError(f"프로젝트 ID {project_id}에 해당하는 프로젝트를 찾을 수 없습니다.")
            if not user:
                raise ValueError(f"유저 ID {user_id}에 해당하는 유저를 찾을 수 없습니다.")
    
    def download_thumbnail(self, task_id, save_path=None):  # 썸네일 다운로드하기
        if not save_path:
            save_path = '/home/rapa/thumbnail'
        path_list = {}

        versions = self.sg.find("Version", [['sg_task', 'is', {'type': 'Task', 'id': task_id}]], 
                                ['image', 'sg_status_list', 'code'])

        for version in versions:
            version_id = version['id']
            version_code = version['code']

            if not version.get('image'):
                print(f"Version {version_code}에 대한 썸네일이 없습니다.")
                continue  # 다음 버전으로 건너뜀
            
            thumbnail_url = version['image']

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            try:
                with requests.get(thumbnail_url, stream=True) as response:
                    response.raise_for_status()

                    file_path = f'{save_path}/version_{version_code}_thumbnail.jpg'
                    with open(file_path, 'wb') as file:
                        shutil.copyfileobj(response.raw, file)
                        path_list[version_id] = file_path
            except requests.exceptions.RequestException as e:
                print(f"Failed to download thumbnail for version {version_code}: {e}")
                continue  # 현재 버전은 건너뛰고 다음 버전으로 이동
            
        # if not path_list:
        #     print(f"No thumbnails found for task_id {task_id}.")

        return path_list
    
    def make_assets_json(self, project_id: int):    # 에셋 목록 JSON만들기
        """
        지정된 프로젝트의 에셋, 에셋 테스크, 에셋 버전 정보를 개별 JSON 파일로 만듭니다.
        """
        # 에셋 Json 만들기
        assets = self.sg.find("Asset", [['project', 'is', {'type': 'Project', 'id': project_id}]], 
                            ["code", "sg_asset_type"])
        
        asset_filename = f'assets_proj{project_id}.json'
        asset_file_path = os.path.join(self.json_path, asset_filename)

        with open(asset_file_path, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'data': assets}, f, ensure_ascii=False, indent=4)

        # 에셋 테스크 Json 만들기
        asset_tasks_all = []
        for asset in assets:
            asset_tasks = self.sg.find("Task", [['entity', 'is', {'type': 'Asset', 'id': asset['id']}]], 
                            ["step"])
            for asset_task in asset_tasks:
                # Step 필드가 없거나 None일 경우를 처리
                step_name = 'Unknown Step' if asset_task.get('step') is None else asset_task['step'].get('name', 'Unknown Step')
                asset_tasks_all.append({'id': asset_task['id'], 'asset_id': asset['id'], 'step_name': step_name})

        asset_task_filename = f'asset_tasks_proj{project_id}.json'
        asset_task_file_path = os.path.join(self.json_path, asset_task_filename)

        with open(asset_task_file_path, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'data': asset_tasks_all}, f, ensure_ascii=False, indent=4)

        # 에셋 버전 Json 만들기
        asset_versions_all = []
        for asset in assets:
            asset_tasks = self.sg.find("Task", [['entity', 'is', {'type': 'Asset', 'id': asset['id']}]], 
                            ["id"])
            for asset_task in asset_tasks:
                versions = self.sg.find("Version", [['sg_task', 'is', {'type': 'Task', 'id': asset_task['id']}]], 
                            ["id", "code", "sg_status_list", "created_at", "user"])
                wip = {}
                pub = {}
                
                # 썸네일 다운로드
                thumbnail_paths = self.download_thumbnail(asset_task['id'])
                
                for version in versions:
                    version_info = {
                        'id' : version['id'],
                        'created_at' : version.get('created_at').isoformat() if version.get('created_at') else 'No Date',
                        'artist' : version.get('user', {}).get('name', 'Unknown Artist')
                    }
                    if version['sg_status_list'] == 'wip':
                        version_info['thumbnail'] = thumbnail_paths.get(version['id'], 'No Thumbnail')
                        wip[version['code']] = version_info
                    if version['sg_status_list'] == 'pub':
                        version_info['thumbnail'] = thumbnail_paths.get(version['id'], 'No Thumbnail')
                        pub[version['code']] = version_info
                
                asset_versions_all.append({
                    'task_id': asset_task['id'],
                    'wip': wip,
                    'pub': pub
                })

        asset_version_filename = f'asset_versions_proj{project_id}.json'
        asset_version_file_path = os.path.join(self.json_path, asset_version_filename)

        with open(asset_version_file_path, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'data': asset_versions_all}, f, ensure_ascii=False, indent=4)

    def make_shots_json(self, project_id: int): # 샷 목록 JSON만들기
        """
        지정된 프로젝트의 시퀀스, 샷, 샷 테스크, 샷 버전 정보를 개별 JSON 파일로 만듭니다.
        """
        # 시퀀스 Json 만들기
        sequences = self.sg.find("Sequence", [['project', 'is', {'type': 'Project', 'id': project_id}]], 
                                ["code"])

        sequence_filename = f'sequences_proj{project_id}.json'
        sequence_file_path = os.path.join(self.json_path, sequence_filename)

        with open(sequence_file_path, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'data': sequences}, f, ensure_ascii=False, indent=4)

        # 샷 Json 만들기
        shots = self.sg.find("Shot", [['project', 'is', {'type': 'Project', 'id': project_id}]], 
                            ["code", "sg_sequence"])

        shot_filename = f'shots_proj{project_id}.json'
        shot_file_path = os.path.join(self.json_path, shot_filename)

        with open(shot_file_path, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'data': shots}, f, ensure_ascii=False, indent=4)

        # 샷 테스크 Json 만들기
        shot_tasks_all = []
        for shot in shots:
            shot_tasks = self.sg.find("Task", [['entity', 'is', {'type': 'Shot', 'id': shot['id']}]], 
                            ["step"])
            for shot_task in shot_tasks:
                # Step 필드가 없거나 None일 경우를 처리
                step_name = 'Unknown Step' if shot_task.get('step') is None else shot_task['step'].get('name', 'Unknown Step')
                shot_tasks_all.append({'id': shot_task['id'], 'shot_id': shot['id'], 'step_name': step_name})

        shot_task_filename = f'shot_tasks_proj{project_id}.json'
        shot_task_file_path = os.path.join(self.json_path, shot_task_filename)

        with open(shot_task_file_path, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'data': shot_tasks_all}, f, ensure_ascii=False, indent=4)

        # 샷 버전 Json 만들기
        shot_versions_all = []
        for shot in shots:
            shot_tasks = self.sg.find("Task", [['entity', 'is', {'type': 'Shot', 'id': shot['id']}]], 
                            ["id"])
            for shot_task in shot_tasks:
                versions = self.sg.find("Version", [['sg_task', 'is', {'type': 'Task', 'id': shot_task['id']}]], 
                            ["id", "code", "sg_status_list", "created_at", "user"])
                wip = {}
                pub = {}
                
                # 썸네일 다운로드
                thumbnail_paths = self.download_thumbnail(shot_task['id'])
                
                for version in versions:
                    version_info = {
                        'id': version['id'],
                        'created_at': version.get('created_at').isoformat() if version.get('created_at') else 'No Date',
                        'artist': version.get('user', {}).get('name', 'Unknown Artist')
                    }
                    if version['sg_status_list'] == 'wip':
                        version_info['thumbnail'] = thumbnail_paths.get(version['id'], 'No Thumbnail')
                        wip[version['code']] = version_info
                    if version['sg_status_list'] == 'pub':
                        version_info['thumbnail'] = thumbnail_paths.get(version['id'], 'No Thumbnail')
                        pub[version['code']] = version_info

                shot_versions_all.append({
                    'task_id': shot_task['id'],
                    'wip': wip,
                    'pub': pub
                })

        shot_version_filename = f'shot_versions_proj{project_id}.json'
        shot_version_file_path = os.path.join(self.json_path, shot_version_filename)

        with open(shot_version_file_path, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'data': shot_versions_all}, f, ensure_ascii=False, indent=4)

    def make_user_assigned_work_json(self, project_id: int, user_id: int):  # 유저에게 할당된 task JSON 만들기
        filters = [['task_assignees', 'is', {'type': 'HumanUser', 'id': user_id}],
                ['project', 'is', {'type': 'Project', 'id': project_id}]]
            
        fields = ['step', 'entity', 'sg_status_list']
        tasks = self.sg.find('Task', filters, fields)
        
        shot_list = []
        asset_list = []
        
        for task in tasks:
            if task['sg_status_list'] not in ['wip','wtg','pub']:
                continue
            if not task['entity']:
                continue
            
            task_id = task['id']
            if task.get('step'):
                task_name = task['step']['name']
            else:
                task_name = 'Unknown Step'
            entity_type = task['entity']['type']
            entity_id = task['entity']['id']
            entity_name = task['entity']['name']
            
            if entity_type == 'Shot':
                seq_dic = self.sg.find_one('Shot',[['id', 'is', entity_id]], ['sg_sequence'])
                seq_data = seq_dic.get('sg_sequence', {})
                
                # Sequence 정보가 있는지 확인하고 seq_name과 seq_id를 설정
                if seq_data:
                    seq_name = seq_data.get('name', 'Unknown Sequence')
                    seq_id = seq_data.get('id', None)
                else:
                    seq_name = 'Unknown Sequence'
                    seq_id = None
                
                shot_list.append({'task' : {'id': task_id ,"name": task_name},
                                  'shot' : {'id': entity_id,'name' : entity_name}, 
                                  'sequence' : {'id' : seq_id, 'name' : seq_name}})
                
            if entity_type == 'Asset':
                asset_dic = self.sg.find_one('Asset', [['id', 'is', entity_id]], ['sg_asset_type'])
                if asset_dic:
                    asset_type = asset_dic.get('sg_asset_type', 'Unknown Asset Type')
                else:
                    asset_type = 'Unknown Asset Type'
                    
                asset_list.append({'task' : {'id': task_id,"name": task_name},
                                   'asset_type' : asset_type,
                                   'asset' : {'id' : entity_id, 'name' : entity_name}})
        
        filename = f'user{user_id}_assigned_tasks_proj{project_id}.json'
        file_path = os.path.join(self.json_path, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'shot': shot_list, 'asset': asset_list}, f, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    test = DataExplorerJson()
    # test.make_user_assigned_work_json(254,90)
    # test.make_project_user_json(254,90)
    # test.make_assets_json(254)
    test.make_shots_json(254)

