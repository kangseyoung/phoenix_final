import os
import re
import maya.cmds as cmds
from shotgun_api3 import Shotgun

class ShotgunReferenceUpdater:
    def __init__(self):
        self.sg = Shotgun("https://4thacademy.shotgrid.autodesk.com",
                          "kimgyeoul",
                          "sBwdjezpc&zxhlyr5iqwbkgrn")
        self.project_id = self.get_project_id_from_current_file()
        self.sequence_name = self.get_sequence_name_from_path()

    # 현재 파일 경로 가져오기
    def get_current_file_path(self):    
        current_file_path = cmds.file(query=True, sceneName=True)
        print(f"현재 파일 경로: {current_file_path}")
        return current_file_path
    
    # 경로에서 시퀀스 이름 추출
    def get_sequence_name_from_path(self):
        current_file_path = self.get_current_file_path()
        path_parts = current_file_path.split(os.sep)
        if "Shots" in path_parts:
            shots_index = path_parts.index("Shots")
            if shots_index + 1 < len(path_parts):
                sequence_name = path_parts[shots_index + 1] 
                print(f"추출된 시퀀스 이름: {sequence_name}")
                return sequence_name
        print("경로에서 시퀀스 이름을 추출할 수 없습니다.")
        return None

    # 프로젝트 이름 조회
    def get_project_name_from_path(self, current_path):
        root_folder = "/phoenix_pipeline_folders/"
        pattern = re.compile(rf"{root_folder}([^/]+)/")
        match = pattern.search(current_path)
        if match:
            project_name = match.group(1)
            print(f"추출된 프로젝트 이름: {project_name}")
            return project_name
        print("프로젝트 이름을 찾을 수 없습니다.")
        return None
    
    # 프로젝트 ID 조회
    def get_project_id_from_current_file(self):
        current_path = self.get_current_file_path()
        project_name = self.get_project_name_from_path(current_path)
        if project_name:
            project = self.sg.find_one("Project", [["name", "is", project_name]], ["id"])
            if project:
                project_id = project["id"]
                print(f"프로젝트 ID: {project_id}")
                return project_id
            else:
                print("프로젝트를 찾을 수 없습니다.")
                return None
        return None
    
    # 해당 시퀀스의 에셋 정보 조회
    def get_assets_from_sequence(self):
        shots = self.sg.find(
            "Shot",
            [["project", "is", {"type": "Project", "id": self.project_id}],
             ["sg_sequence.Sequence.code", "is", self.sequence_name]],
            ["assets"]
        )
        print(f"프로젝트 ID: {self.project_id}, 시퀀스 코드: {self.sequence_name}")
        if not shots:
            print("해당 시퀀스 코드에 대한 샷이 없습니다.")
            return []
        
        assets = []
        for shot in shots:
            if shot.get("assets"):
                assets.extend(shot["assets"])

        if not assets:
            print("해당 시퀀스 코드에 대한 에셋이 없습니다.")
            return []
        
        return assets
    
    # 최신 파일 경로 찾기
    def get_latest_file_path(self, asset_id):
        latest_version = self.sg.find_one(
            "Version",
            [["project", "is", {"type": "Project", "id": self.project_id}],
             ["entity", "is", {"type": "Asset", "id": asset_id}]],
            ["sg_cache_path", "code", "created_at"],
            order=[{"field_name": "created_at", "direction": "desc"}]
        )
        if latest_version:
            return {
                "asset_id": asset_id,
                "asset_code": latest_version.get("code"),
                "latest_path": latest_version.get("sg_cache_path")
            }
        else:
            return {
                "asset_id": asset_id,
                "asset_code": None,
                "latest_path": None
            }
    
    # 디렉토리 존재 여부와 최신 파일 찾기
    def get_latest_file_in_directory(self, directory_path):
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            print("디렉토리가 존재하지 않거나 디렉토리가 아닙니다.")
            return None
        files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        if not files:
            print("디렉토리에 파일이 없습니다.")
            return None
        latest_file = max(files, key=os.path.getmtime)
        return latest_file

    # 모든 레퍼런스의 파일 경로 조회
    def list_references(self):
        references = cmds.ls(type='reference')
        for ref in references:
            if cmds.referenceQuery(ref, isLoaded=True):
                file_path = cmds.referenceQuery(ref, filename=True)
                print(f"레퍼런스 노드: {ref}, 파일 경로: {file_path}")

    # 레퍼런스를 최신 파일로 업데이트
    def update_reference_with_auto_matching(self, latest_file):
        references = cmds.ls(type='reference')
        for ref in references:
            if cmds.referenceQuery(ref, isLoaded=True):
                file_path = cmds.referenceQuery(ref, filename=True)
                if os.path.basename(file_path).startswith(os.path.basename(latest_file)[:-8]):
                    cmds.file(latest_file, loadReference=ref)
                    print("래퍼런스가 업데이트되었습니다.")
                    return True
        return False

    # 새로운 레퍼런스 노드 생성
    def create_reference(self, latest_file):
        ref_node = cmds.file(latest_file, reference=True)
        print("새 레퍼런스 노드가 생성되었습니다.")

    # 레퍼런스 노드가 있다면 최신 파일로 업데이트 해주고 레퍼런스 노드가 없다면 최신 파일를 레퍼런스로 불러옴
    def get_assets_latest_versions_and_update_references(self):
        assets = self.get_assets_from_sequence()
        latest_versions = []
        for asset in assets:
            asset_id = asset["id"]
            latest_version_info = self.get_latest_file_path(asset_id)
            latest_versions.append(latest_version_info)
            if latest_version_info['latest_path']:
                latest_file = self.get_latest_file_in_directory(latest_version_info['latest_path'])
                if latest_file:
                    print(f"대한 최신 파일: {latest_file}")
                    updated = self.update_reference_with_auto_matching(latest_file)
                    if not updated:
                        self.create_reference(latest_file)
                else:
                    print("경로에 파일이 없습니다.")
        return latest_versions

updater = ShotgunReferenceUpdater()
updater.get_assets_latest_versions_and_update_references()