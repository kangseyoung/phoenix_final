# def render_exr(new_version_dir, pub_path, aovs):
#     """
#     씬의 카메라로 EXR 포맷으로 렌더링을 수행하는 함수입니다.
#     Parameters:
#     - new_version_dir (str): 렌더링된 파일을 저장할 디렉토리 경로입니다.
#     - pub_path (str): 출력 파일의 기본 경로를 포함하는 파일 경로입니다.
#     - aovs (list): 렌더링할 AOV의 목록입니다.
#     """
#     print("exr_렌더중...!")
#     file_name = os.path.basename(pub_path)
#     exr_dir = f"{new_version_dir}/exr/{file_name}"
#     exr_path = f"{exr_dir}.####.exr"
#     deep_exr_dir = f"{exr_dir}/exr/deep/"
#     deep_exr_path = f"{deep_exr_dir}deep_####.exr"  # deep AOV 전용 경로
#     # 1. 렌더링에 사용할 카메라 설정
#     camera_name = 'render_cam'  # 사용할 카메라의 이름을 지정
#     print(f"File Name: {file_name}")
#     print(f"EXR Directory: {exr_dir}")
#     print(f"EXR Path: {exr_path}")
#     print(f"Deep EXR Directory: {deep_exr_dir}")
#     print(f"Deep EXR Path: {deep_exr_path}")
#     print(f"Camera Name: {camera_name}")
    
    
#     if not os.path.exists(exr_dir):
#         os.makedirs(exr_dir)
#     if not os.path.exists(deep_exr_dir):
#         os.makedirs(deep_exr_dir)
        
#     # 2. Arnold 렌더러로 설정
#     cmds.setAttr('defaultRenderGlobals.currentRenderer', 'arnold', type='string')
#     print("Arnold renderer set.")
#     # 3. 렌더링 포맷을 EXR로 설정
#     cmds.setAttr('defaultRenderGlobals.imageFormat', 51)  # EXR 포맷 (51 = EXR)
#     print("Image format set to EXR.")
#     # 4. AOV를 합칠 수 있도록 설정
#     cmds.setAttr('defaultArnoldDriver.mergeAOVs', 1)  # AOV 합치기 설정
#     print("AOV merging enabled.")
#     # 5. AOV 리스트를 설정 (이미 설정된 AOV들이 있다고 가정)
#     for aov in aovs:
#         print(aov)
#         if not cmds.ls(aov):
            
#             cmds.createNode('aiAOV', name=aov)
#             print(f"Created AOV node: {aov}")
#             cmds.setAttr(f'aiAOV_{aov}.name', aov, type='string')
#             print(f"Created and set up AOV: {aov}")
#         else:
#             print(f"AOV already exists: {aov}")
#     # 렌더링: 모든 AOV를 합쳐서 기본 EXR 파일로 저장
#     cmds.workspace(fileRule=['images', exr_path])
#     print(f"Workspace path set to: {exr_path}")
#     cmds.render(camera=camera_name, x=1920, y=1080)  # 해상도는 수정 필요
#     print(f"Rendered image with merged AOVs saved to {exr_path}")
#     # `deep` AOV를 별도로 렌더링
#     if 'deep' in aovs:
#         cmds.setAttr('defaultArnoldDriver.mergeAOVs', 0)  # AOV 병합 비활성화
#         print("AOV merging disabled for deep AOV.")
#         cmds.workspace(fileRule=['images', deep_exr_path])
#         print(f"Workspace path set to deep EXR path: {deep_exr_path}")
#         cmds.render(camera=camera_name, x=1920, y=1080)  # 해상도는 수정 필요
#         print(f"Deep image rendered and saved to {deep_exr_path}")
#         return exr_path, deep_exr_path
#     return exr_path
# rener_exr('/home/rapa/phoenix_pipeline_folders/Test_phoenix/Shots/Opening Sequence/OPN_100/lgt/pub/v002','/home/rapa/phoenix_pipeline_folders/Test_phoenix/Shots/Opening Sequence/OPN_100/lgt/pub/OPN_100_lgt_v002.mb',['deep', ' specular', ' diffuse', ' deep'])