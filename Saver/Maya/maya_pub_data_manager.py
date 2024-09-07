
from Publisher.Maya.maya_playblast_scene_setter import PlayblastSceneSetter
import maya.cmds as cmds
import os
import maya.mel as mel
# 마야에서 퍼블리시 할 때 필요한 정보들을 관리하는 모듈
# 기능별로 클래스 구분함.
#[주요기능]
# 1. 아웃라이너 오브젝트 조사 
# 2. abc,shader,shader_json,mb 파일 저장


class MayaOutlinerInfoCatcher():
    """
    마야의 아웃라이너에 있는 오브젝트들의 이름을 ui에 띄우기 위해 
    조사하고, 간결화하는 클래스
    """
    def __init__(self, exclude_views=None):
        if exclude_views is None:
            exclude_views = ['persp', 'top', 'front', 'side']
        self.exclude_views = exclude_views

    def get_all_objects(self):
        """Maya 씬에서 모든 객체를 가져옵니다."""
        return cmds.ls(assemblies=True)
        
    def filter_objects(self,objects):
        """카메라와 제외할 뷰포트를 필터링합니다."""
        objs = []

        for obj in objects:
            if not obj in self.exclude_views:
                objs.append(obj)
            from importlib import reload
        return objs



    def simplify_object_name(self, name):
        """객체 경로에서 마지막 부분만 추출하여 단순화합니다."""
        if 'Shape' in name:
            return None
        return name.rpartition('|')[-1]

    def get_filtered_and_simplified_objects(self):
        """필터링과 단순화를 적용한 객체 리스트를 반환합니다."""
        all_objects = self.get_all_objects()
        filtered_objects = self.filter_objects(all_objects)
        
        print(filtered_objects)
        return filtered_objects
    
    def warn_file_path_messsage(self):
        import maya.cmds as cmds

        cmds.confirmDialog(
                title='Warning!',
                message="There's no file path",
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel'
                    )


class MayaFileSaver(): 
    def save_selected_items_as_mb(self, selected_text_items, file_path):
        #선택된 오브젝트를 제외한 모든 정보들을 제거함
        # 새 신을 만들고, 카피함.
        all_objects = cmds.ls(assemblies = True )

        # 유효한 오브젝트들을 저장할 리스트
        valid_items = []
        
        for item in selected_text_items:
            # 각 오브젝트 이름이 DAG 경로의 일부일 수 있으므로, 전체 경로에서 일치 항목을 찾습니다.
            if item in all_objects:
                valid_items.append(item)
                if not valid_items:
                    print("선택된 유효한 오브젝트가 없습니다. 작업을 종료합니다.")
                    return None
            
        # 선택된 오브젝트들을 새로 선택합니다.
        cmds.select(valid_items, replace=True)
        print(f"유효한 오브젝트가 선택되었습니다: {valid_items}")
        
        # 선택되지 않은 모든 오브젝트를 제거합니다.
        all_objects = cmds.ls(assemblies = True)
        objects_to_delete = [obj for obj in all_objects if obj not in valid_items]
        
        if objects_to_delete:
            cmds.delete(objects_to_delete)
            print(f"선택되지 않은 오브젝트가 제거되었습니다: {objects_to_delete}")
        else:
            print("제거할 오브젝트가 없습니다.")
        
        # 파일 경로가 절대 경로인지 확인합니다. 절대 경로가 아니면 기본 작업 디렉토리와 결합합니다.
        if not os.path.isabs(file_path):
            directory = cmds.workspace(query=True, rootDirectory=True)
            file_path = os.path.join(directory, file_path)

        # 디렉토리가 존재하지 않으면 생성합니다.
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # MB 파일로 저장합니다.
        try:
            cmds.file(rename=file_path)
            cmds.file(save=True, type='mayaBinary')
            print(f"MB 파일이 {file_path}에 저장되었습니다.")
        except RuntimeError as e:
            print(f"파일 저장에 실패했습니다. 오류: {e}")
    
    def export_selected_items_as_alembic_and_mb(self, selected_text_items, new_version_dir,pub_path):
        """
        선택된 오브젝트들만 Alembic 파일과 Maya Binary 파일로 저장합니다.
        나머지 오브젝트는 제거합니다.

        :param selected_text_items: 선택된 오브젝트의 이름 목록
        :param export_abc_file_dir: Alembic 파일이 저장될 디렉토리 경로
        :param mb_file_path: Maya Binary 파일이 저장될 경로
        """
        print("newversion_dir",new_version_dir)
        file_name = os.path.basename(pub_path)
        all_objects = cmds.ls(assemblies = True)

        # 유효한 오브젝트들을 저장할 리스트
        valid_items = []
        
        for item in selected_text_items:
            # 각 오브젝트 이름이 DAG 경로의 일부일 수 있으므로, 전체 경로에서 일치 항목을 찾습니다.
            if item in all_objects:
                valid_items.append(item)
                if not valid_items:
                    print("선택된 유효한 오브젝트가 없습니다. 작업을 종료합니다.")
                    return None
        if not valid_items:
            print("선택된 유효한 오브젝트가 없습니다. 작업을 종료합니다.")
            return

        # 선택된 오브젝트들을 새로 선택합니다.
        cmds.select(valid_items, replace=True)
        print(f"유효한 오브젝트가 선택되었습니다: {valid_items}")

        # 선택되지 않은 모든 오브젝트를 제거합니다.
        objects_to_delete = [obj for obj in all_objects if obj not in valid_items]

        if objects_to_delete:
            cmds.delete(objects_to_delete)
            print(f"선택되지 않은 오브젝트가 제거되었습니다: {objects_to_delete}")
        else:
            print("제거할 오브젝트가 없습니다.")

        # Alembic 내보내기
        start_frame = int(cmds.playbackOptions(query=True, min=True))
        end_frame = int(cmds.playbackOptions(query=True, max=True))
        
        #샷그리드에 올라갈 알렘빅 경로 리스트 
        abc_cache_paths = []
        
        
        
        for vaild_item in valid_items:
            # Alembic 파일 경로를 설정합니다.
            file_basename = os.path.basename(vaild_item) ###
            abc_path = f"{new_version_dir}/{file_basename}.abc" #변수 네이밍..
            print(abc_path)
            abc_cache_paths.append(abc_path)
            # Alembic 내보내기 옵션을 설정합니다.
            alembic_args = [
                "-renderableOnly",
                "-writeFaceSets",
                "-uvWrite",
                "-worldSpace",
                "-eulerFilter",
                f"-fr {start_frame} {end_frame}",
                f"-file '{abc_path}'",
                f"-root {vaild_item}"
            ]

            # Alembic 내보내기 명령을 실행합니다.
            abc_export_cmd = 'AbcExport -j "%s"' % " ".join(alembic_args)

            try:
                # Alembic 파일 디렉토리가 존재하지 않으면 생성합니다.
                if not os.path.exists(new_version_dir):
                    os.makedirs(new_version_dir)

                mel.eval(abc_export_cmd)
                print(f"Alembic 파일이 성공적으로 저장되었습니다: {abc_path}")
            except RuntimeError as e:
                    print(f"Alembic 내보내기에 실패했습니다. 오류: {e}")
        # Maya Binary 파일로 저장하기
        # 파일 경로가 절대 경로인지 확인합니다. 절대 경로가 아니면 기본 작업 디렉토리와 결합합니다.
        mb_file_path = f"{new_version_dir}/{file_name}" #경로는 알렘빅이랑 똑같이 되서, 이미 확인됨,.
        
        try:
            cmds.file(rename=mb_file_path)
            cmds.file(save=True, type='mayaBinary')
            print(f"MB 파일이 {mb_file_path}에 저장되었습니다.") #필요한거>> END_001_v001 파일의 base 네임..
            
            
        except RuntimeError as e:
            print(f"MB 파일 저장에 실패했습니다. 오류: {e}")
        return abc_cache_paths,mb_file_path
            
    def shader_collector(self):
       
        """
        룩뎁일경우에만
        셰이더와 오브젝트들을 컬렉션하는 함수.
        셰이더 딕셔너리..
        """
        shader_dictionary = {}
        shading_groups = cmds.ls(type="shadingEngine")
        for shading_group in shading_groups:
            shader = cmds.ls(cmds.listConnections(shading_group + ".surfaceShader"), materials=True)    
            if not shader:
                continue
            objects = cmds.sets(shading_group, q=True)
            shader_name = shader[0]
            if objects:
                if shader_name not in shader_dictionary:
                    shader_dictionary[shader_name] = []
                shader_dictionary[shader_name].extend(objects)
        return shader_dictionary
    
    def export_shader_ma_json(self,path):
        """
        maya에서 오브젝트에 어싸인된 셰이더들을 ma 파일로 익스포트하고,
        그 정보들을 json 파일로 익스포트 하는 함수이다.
        """
        import json
        import re
        pattern = r'v(\d{3})'
        match = re.search(pattern, path)
        version= match.group(0) #001 v떼고
        pub_dir = os.path.dirname(path)
        shader_dictionary = self.shader_collector()
        


        for shader, _ in shader_dictionary.items():
            cmds.select(shader, add=True)    

        ma_file_path = f"{pub_dir}/{version}/shader.ma"
        json_file_path = f"{pub_dir}/{version}/shader.json"
        
        if not os.path.exists(f"{pub_dir}/{version}/"):
            os.makedirs(f"{pub_dir}/{version}/")
        
        cmds.file(ma_file_path, exportSelected=True, type="mayaAscii")
        
        with open(json_file_path, 'w') as f:
            json.dump(shader_dictionary, f)

        cmds.select(clear=True)
        return json_file_path, ma_file_path
    
    def make_slate(self,path,project):
        """ 
        마야의 플레이 블라스트 기능을 이용해서 뷰포트를 이미지로 렌더링하고,
        슬레이트 정보를 삽입하여 동영상을 인코딩한다.
        image : jpg
        mov codec : h264
        """ 
        scene_setter = PlayblastSceneSetter()
        scene_setter.run_playblast_setup()
        
        pub_dir = os.path.dirname(path)
        proxy_path = f"{pub_dir}/.proxy"
        proxy_format = "jpg"
        image_path = os.path.join(proxy_path, 'proxy.%04d.' + proxy_format) #playblast에서 만든이미지 경로
        mov_path = f"{pub_dir}/.slate/slate.mov"
        
        if not os.path.exists(f"{pub_dir}/.slate"):
            os.makedirs(f"{pub_dir}/.slate")
        if not os.path.exists(f"{pub_dir}/.proxy"):
            os.makedirs(f"{pub_dir}/.proxy")
        
        start_frame = 1
        last_frame = 200
        render_width = 1920
        render_height = 1080

        # PLAYBLAST MAYA API
        cmds.playblast(filename=os.path.join(proxy_path, 'proxy'), format='image', compression=proxy_format,
                    startTime=start_frame, endTime=last_frame, forceOverwrite=True,
                    widthHeight=(render_width, render_height), percent=100,
                    showOrnaments=True, framePadding=4, quality=100, viewer=False) #
        
        # FFMPEG 명령어 생성 및 실행
        first = 1
        frame_rate = 24 
        ffmpeg = "ffmpeg"
        slate_size = 60
        font_path = "/home/rapa/phoenix/phoenix_pipeline/maya/playblast/font/Courier Regular/Courier Regular.ttf"
        font_size = 40
        frame_count = last_frame - start_frame
        text_x_padding = 10
        text_y_padding = 20

        top_left = ""
        top_center = project
        top_right = datetime.date.today().strftime("%Y/%m/%d")
        bot_left = "SIZE : 1920x1080"
        bot_center = ""        # split = file_basename.split(".")
        # abc = split[0]
        # abc_name = f"{abc}.abc" #abc 파일이름

        frame_cmd = "'Frame \: %{eif\:n+"
        frame_cmd += "%s\:d}' (%s)"  % (first, frame_count+1)
        bot_right = frame_cmd

        cmd = '%s -framerate %s -y -start_number %s ' % (ffmpeg, frame_rate, first)
        cmd += '-i %s' % (image_path)
        cmd += ' -vf "drawbox=y=0 :color=black :width=iw: height=%s :t=fill, ' % (slate_size)
        cmd += 'drawbox=y=ih-%s :color=black :width=iw: height=%s :t=fill, ' % (slate_size, slate_size)
        cmd += 'drawtext=fontfile=%s :fontsize=%s :fontcolor=white@0.7 :text=%s :x=%s :y=%s,' % (font_path, font_size, top_left, text_x_padding, text_y_padding)
        cmd += 'drawtext=fontfile=%s :fontsize=%s :fontcolor=white@0.7 :text=%s :x=(w-text_w)/2 :y=%s,' % (font_path, font_size, top_center, text_y_padding)
        cmd += 'drawtext=fontfile=%s :fontsize=%s :fontcolor=white@0.7 :text=%s :x=w-tw-%s :y=%s,' % (font_path, font_size, top_right, text_x_padding, text_y_padding)
        cmd += 'drawtext=fontfile=%s :fontsize=%s :fontcolor=white@0.7 :text=%s :x=%s :y=h-th-%s,' % (font_path, font_size, bot_left, text_x_padding, text_y_padding)
        cmd += 'drawtext=fontfile=%s :fontsize=%s :fontcolor=white@0.7 :text=%s :x=(w-text_w)/2 :y=h-th-%s,' % (font_path, font_size, bot_center, text_y_padding)
        cmd += 'drawtext=fontfile=%s :fontsize=%s :fontcolor=white@0.7 :text=%s :x=w-tw-%s :y=h-th-%s' % (font_path, font_size, bot_right, text_x_padding, text_y_padding)
        cmd += '"'
        cmd += ' -c:v prores_ks -profile:v 3 -colorspace bt709 %s' % mov_path
        
        subprocess.call(cmd, shell=True)
        
        return mov_path  # 동영상 경로를 반환




if __name__ == "__main__":
    filter = MayaOutlinerInfoCatcher()
