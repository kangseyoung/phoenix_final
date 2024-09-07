

from Publisher.Maya.data_explorer_sj import DataExplorer
from Publisher.Maya.maya_pub_data_manager import MayaFileSaver
class UploadDataToShotGrid(DataExplorer):
    
    def __init__(self,project_name,task_step) -> None:
        super(DataExplorer).__init__()
        publish_file_type = self.get_file_type()
        self.file_saver = MayaFileSaver()

    def get_file_type(self):
        published_file_type = self.sg.find_one("PublishedFileType", [["code", "is", "Maya Scene"]], ["id"])
        
        return published_file_type
    def upload_to_shotgrid(self,task_step,pub_path,project_name):
        print("#"*10)
        
        if task_step in ['mod','rig','lkd']:
            maya_slate_path = self.file_saver.asset_make_slate(pub_path, project_name)
            
        elif task_step == "ani":
            maya_slate_path = self.file_saver.shot_make_slate(pub_path, project_name)
        
        # elif task_step == "lgt":
        #     maya_slate_path = 

        print("#"*10)
        import re # 프로젝트의 퍼블리쉬 될 경로
        print("pub_path는..",pub_path)

        if not published_file_type:
                print("'Maya Scene'이 없습니다.")
                return
        print(pub_path)
        
        if pub_path:
            pub_file = os.path.basename(pub_path)
            print(pub_file)
            code = pub_file.split(".")[0]
            task = version.get("sg_task")
            task_id = task.get("id")
            entity = version.get('entity')
            entity_id = entity.get('id')
            entity_type = entity.get('type')
            

            
        #[{'type': 'Version', 'id': 7687, 'sg_task': {'id': 6869, 'name': 'teapot_mod_v001 Task', 'type': 'Task'}, 'entity': {'id': 1735, 'name': 'teapot_mod_v001', 'type': 'Asset'}}]
        
        
        if task_step == "lkd":
            maya_slate_path = file_saver.asset_make_slate(pub_path, get_project_name())
            new_version = self.sg.create('Version', {
            'entity': entity,
            'sg_task': {'type': 'Task', 'id': task_id},
            'code': f'{code}',
            'description':  ui.description.toPlainText() , ###########고쳐야함
            'project': {'type': 'Project', 'id': 254},
            'sg_path': ma_path, #이게 두번 올라감..?
            'sg_status_list': 'pub', #user 정보 올라가야함
            'sg_shader_json_path': f"{json_path}",
            'sg_version_file_type': published_file_type
            
            
                
            })
            
            published_file_type = self.sg.find_one("PublishedFileType", [["code", "is", "Maya Scene"]], ["id"])
            if not published_file_type:
                print("'Maya Scene'이 없습니다.")
                return
            created_published_file = self.sg.create("PublishedFile",{
                "project": {"type": "Project", "id": 254},
                "entity": entity,
                "task": {"type": "Task", "id": task_id}, 
                "path": {"local_path": ma_path}, 
                "description": ui.description.toPlainText(),   #UI에 입력된 description 사용
                'path_cache':json_path,
                'sg_status_list':'ip',
                'published_file_type': published_file_type
            })
                        
            print(f"{created_published_file['id']}가 퍼블리쉬 되었습니다.")  
                
            print(pub_path)
            print(new_version)
            print("version_created")
        
                
        #리깅일 경우.. mb 파일로만 나감
        elif task_step == "rig":
            maya_slate_path = file_saver.asset_make_slate(pub_path, get_project_name())
            new_version = self.sg.create('Version', {
            'entity': entity,
            'sg_task': {'type': 'Task', 'id': task_id},
            'code': f'{code}',
            'description':  ui.description.toPlainText() , ###########고쳐야함
            'project': {'type': 'Project', 'id': 254},
            'sg_path': pub_path,
            'sg_status_list': 'pub', #user 정보 올라가야함,
            'sg_version_file_type': published_file_type
            
                
            })
            
            created_published_file = self.sg.create("PublishedFile",{
                    "project": {"type": "Project", "id": 254},
                    "entity": entity,
                    "task": {"type": "Task", "id": task_id}, 
                    "path": {"local_path": pub_path}, 
                    "description": ui.description.toPlainText(),   #UI에 입력된 description 사
                    'published_file_type': published_file_type
            })   
            
        elif task_step == "mod":
            maya_slate_path = file_saver.asset_make_slate(pub_path, get_project_name())
            new_version = self.sg.create('Version', {
            'entity': entity,
            'sg_task': {'type': 'Task', 'id': task_id},
            'code': f'{code}',
            'description':  ui.description.toPlainText() , ###########고쳐야함
            'project': {'type': 'Project', 'id': 254},
            'sg_path': mb_path,
            'sg_status_list': 'pub', #user 정보 올라가야함   
            'sg_cache_path':f"{cache_path}",
            'sg_version_file_type': published_file_type
            
        })
            created_published_file = self.sg.create("PublishedFile",{
                "project": {"type": "Project", "id": 254},
                "entity": entity,
                "task": {"type": "Task", "id": task_id}, 
                "path": {"local_path": mb_path }, 
                "description": ui.description.toPlainText(),   #UI에 입력된 description 사용
                'path_cache':f"{cache_path}",
                'published_file_type': published_file_type
            })
            #lighting은 exr 렌더 후, 이미지의 경로 + 
            #mb,cache 나가야함.
        elif task_step == "lgt":
            
            new_version = self.sg.create('Version', {
            'entity': entity,
            'sg_task': {'type': 'Task', 'id': task_id},
            'code': f'{code}',
            'description':  ui.description.toPlainText() , ###########고쳐야함
            'project': {'type': 'Project', 'id': 254},
            'sg_path': pub_path,
            'sg_status_list': 'pub', #user 정보 올라가야함,
            'sg_version_file_type': published_file_type,
            'sg_exr_path': exr_path
            })
            
            created_published_file = self.sg.create("PublishedFile",{
                    "project": {"type": "Project", "id": 254},
                    "entity": entity,
                    "task": {"type": "Task", "id": task_id}, 
                    "path": {"local_path": pub_path}, 
                    "description": ui.description.toPlainText(),   #UI에 입력된 description 사
                    'published_file_type': published_file_type,
                    'sg_exr_path': exr_path
            })   
            print(f"{created_published_file['id']}가 퍼블리쉬 되었습니다.")  
                
            print(pub_path)
            print(new_version)
            print("version_created")
            
        
        
        elif task_step == "ani": #카메라 캐쉬 나가줘야하나?
            new_version = self.sg.create('Version', {
            'entity': entity,
            'sg_task': {'type': 'Task', 'id': task_id},
            'code': f'{code}',
            'description':  ui.description.toPlainText() , ###########고쳐야함
            'project': {'type': 'Project', 'id': 254},
            'sg_path': mb_path,
            'sg_status_list': 'pub', #user 정보 올라가야함   
            'sg_cache_path':f"{cache_path}",
            'sg_version_file_type': published_file_type
            
        })
            created_published_file = self.sg.create("PublishedFile",{
                "project": {"type": "Project", "id": 254},
                "entity": entity,
                "task": {"type": "Task", "id": task_id}, 
                "path": {"local_path": mb_path }, 
                "description": ui.description.toPlainText(),   #UI에 입력된 description 사용
                'path_cache':f"{cache_path}",
                'published_file_type': published_file_type
            })
            
            
            
            print(f"{created_published_file['id']}가 퍼블리쉬 되었습니다.")  
                
            print(pub_path)
            print(new_version)
            print("version_created")
            
        elif task_step == "ani": #카메라 캐쉬 나가줘야하나?
            new_version = self.sg.create('Version', {
            'entity': entity,
            'sg_task': {'type': 'Task', 'id': task_id},
            'code': f'{code}',
            'description':  ui.description.toPlainText() , ###########고쳐야함
            'project': {'type': 'Project', 'id': 254},
            'sg_path': mb_path,
            'sg_status_list': 'pub', #user 정보 올라가야함   
            'sg_cache_path':f"{cache_path}",
            'sg_version_file_type': published_file_type
            
        })
            created_published_file = self.sg.create("PublishedFile",{
                "project": {"type": "Project", "id": 254},
                "entity": entity,
                "task": {"type": "Task", "id": task_id}, 
                "path": {"local_path": mb_path }, 
                "description": ui.description.toPlainText(),   #UI에 입력된 description 사용
                'path_cache':f"{cache_path}",
                'published_file_type': published_file_type
            })
            
            
            
            print(f"{created_published_file['id']}가 퍼블리쉬 되었습니다.")  
                
            print(pub_path)
            print(new_version)
            print("version_created")
                
        version_id = new_version.get("id")
        version_code = new_version.get("code")
        slate_path = maya_slate_path
        print("slate_path",slate_path)
        self.sg.upload("Version",version_id, slate_path, field_name= "sg_uploaded_movie")
        
        print(f"{version_code} 슬레이트가 업로드되었습니다.")           