import os
import sys
import re
import json
from functools import partial
from importlib import reload

# Set custom site-packages path
sys.path.append("/home/rapa/_phoenix_/lib/site-packages")

# Shotgun API import
from shotgun_api3 import Shotgun

# Conditional imports for PySide6, fallback to PySide2 if not available
try:
    from PySide6.QtWidgets import *
    from PySide6.QtUiTools import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
except:
    from PySide2.QtWidgets import *
    from PySide2.QtUiTools import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *


script_name = "kangseyoung"

with open('/home/rapa/script_key.key', 'rb') as key_file:
    key = key_file.read()

with open('/home/rapa/script_key.bin', 'rb') as enc_file:
    encrypted_data = enc_file.read()

# 2. Fernet 객체를 사용하여 복호화
cipher_suite = Fernet(key)
decrypted_data = cipher_suite.decrypt(encrypted_data)
decoded_key = decrypted_data.decode()

# Import custom Maya and Publisher modules
from Publisher.Maya.get_maya_current_path import MayaCurrentPathImporter
from Publisher.Maya.maya_pub_data_manager import MayaOutlinerInfoCatcher, MayaFileSaver
from Publisher.Maya.maya_messageBox import MayaMessageBoxPrompter
from Publisher.Maya.maya_playblast_scene_setter import PlayblastSceneSetter
from Publisher.Maya.data_explorer_sj import DataExplorer
from Publisher.Maya.ValidationCheckForMaya import ValidateByTask, ValidationCheckForMaya

# Main class to handle publish functionality
class PublishHandler(QMainWindow, DataExplorer):
    def __init__(self):
        super().__init__()
        self.root_path = "/home/rapa"  # Define root path
        self.set_information()  # Set ShotGrid and Maya information
        self.setting()  # Load UI settings
        self.first_show()  # Load file data and show it in UI
        
        # Initialize Maya-related classes
        self.infocatcher = MayaOutlinerInfoCatcher()
        self.file_saver = MayaFileSaver()
        self.selected_items = self.get_outliner_items()  # Store outliner items
        self.publish_button_event()  # Connect publish button to functionality
        self.outliner_warning()  # Check for potential outliner issues

        self.cache_path = False
        self.camera_path = False
        self.pub_path = self.get_publish_path()  # Generate publish path
        print(f"Publish path: {self.pub_path}")

    # Function to set initial information including ShotGrid connection
    def set_information(self):
        # Initialize Shotgun instance with authentication
        self.sg = Shotgun(
            "https://4thacademy.shotgrid.autodesk.com/",  
            script_name="kangseyoung",
            api_key=decoded_key
        )
        # Initialize other components
        self.infocatcher = MayaOutlinerInfoCatcher()
        self.file_saver = MayaFileSaver()
        maya_importer = MayaCurrentPathImporter()
        self.path = maya_importer.show_file_path()  # Get current Maya file path
        self.version = self.check_existence_of_version()  # Check ShotGrid for the file version
        self.task_step = self.get_user_task()  # Get user task
        self.validate_checker = ValidateByTask()
        self.validate_checklist = self.validate_checker.check_validation_list_for_task(self.task_step)
        print(f"Validation checklist: {self.validate_checklist}")

    # Function to load and configure the UI
    def setting(self):
        ui_file_path = f"{self.root_path}/_phoenix_/ui/publisher.ui"
        ui_file = QFile(ui_file_path)
        print("Loading UI...")
        self.ui = QUiLoader().load(ui_file, self)  # Load UI from file

        # Screenshot functionality
        self.label_thum_img = self.ui.findChild(QLabel, "label_thum_img")
        QTimer.singleShot(0, self.make_screenshot)  # Make screenshot on startup
        self.capture = Screen_Capture(self.ui.label_thum_img, parent=self.ui)

    # Handle close event for UI
    def closeEvent(self, event):
        if hasattr(self, 'capture') and self.capture:
            self.capture.close()  # Close capture if active
        QApplication.restoreOverrideCursor()  # Restore cursor
        event.accept()  # Accept the close event

    # Connect publish button event
    def publish_button_event(self):
        self.ui.pushButton_publish.clicked.connect(self.collect_selected_files)

    # Connect validation button event
    def validation_button_event(self):
        self.ui.pushButton_validate.clicked.connect(self.validate)

    # Placeholder for validation function
    def validate(self):
        pass  # Add validation logic if needed

    # Load project data from a JSON file
    def get_project_id_one(self):
        json_path = f'{self.root_path}/_phoenix_/Launcher/Loader/data_from_loader/json_from_loader.json'
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        project_id = json_data['project_id']
        return project_id

    # Load user data from a JSON file
    def get_user_id(self):
        json_path = f'{self.root_path}/_phoenix_/Launcher/Loader/data_from_loader/json_from_loader.json'
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        user_id = json_data['user_id']
        return user_id

    # Retrieve the user task from ShotGrid
    def get_user_task(self):
        try:
            task_entity_in_version = self.version.get("sg_task")
            if not task_entity_in_version:
                print("Task entity not found in version.")
                return None
            task_id = task_entity_in_version.get("id")
            if not task_id:
                print("Task ID not found in Task entity.")
                return None
            task_step = self.get_task_step_by_id(task_id)
            if not task_step:
                print("Task step not found for Task ID.")
                return None
            return task_step
        except Exception as e:
            print(f"Error fetching task step: {e}")
            return None

    # Initialize and show file info in UI
    def first_show(self):
        project_id = self.get_project_id_one()
        user_id = self.get_user_id()
        self.project_name = self.get_project_name(project_id)
        self.ui.label_username.setText(self.get_user_name(user_id))
        self.ui.label_project_name.setText(self.project_name)
        
        self.tree_widget = self.ui.findChild(QTreeWidget, "treeWidget_main")
        self.label_file_name = self.ui.findChild(QLabel, "label_file_name")
        self.label_icon = self.ui.findChild(QLabel, "label_icon")
        self.label_file_type = self.ui.findChild(QLabel, "label_file_type")
        self.text_description = self.ui.findChild(QTextEdit, "text_description")
        
        self.load_file(self.path)  # Load file and display in UI

    # Load and display file information in the tree widget
    def load_file(self, *file_paths):
        for file_path in file_paths:
            if os.path.exists(file_path) and file_path.endswith(('.mb', '.ma', '.nknc', '.nk')):
                file_name = os.path.basename(file_path)
                tree_item = QTreeWidgetItem(self.tree_widget)
                tree_item.setText(0, file_name)
                tree_item.setToolTip(0, file_path)
                tree_item.setExpanded(True)

                outliner_items = self.get_outliner_items()
                if outliner_items:
                    self.add_outliner_items(tree_item, outliner_items, "Outliner")
                self.add_outliner_items(tree_item, self.validate_checklist, "Validation List")

    # Display file type and related icons in the UI
    def get_file_info(self, item, column):
        selected_file_name = item.text(column)
        self.label_file_name.setText(selected_file_name)

        file_extension = os.path.splitext(selected_file_name)[-1].lower()
        if file_extension in ['.mb', '.ma']:
            pixmap = QPixmap(f"{self.root_path}/_phoenix_/ui/image_source/maya.png")
            file_type = "Maya Session"
        elif file_extension in ['.nk', '.nknc']:
            pixmap = QPixmap(f"{self.root_path}/_phoenix_/ui/image_source/Nuke.png")
            file_type = "Nuke Session"
        else:
            pixmap = QPixmap()
            file_type = "Unknown File Type"

        self.label_icon.setPixmap(pixmap)
        self.label_icon.setScaledContents(True)
        self.label_file_type.setText(file_type)

    # Synchronize checkbox states
    def sync_checkboxes(self, state, checkboxes):
        for checkbox in checkboxes:
            checkbox.setCheckState(Qt.CheckState(state))

    # Function to collect and upload selected files to ShotGrid
    def collect_selected_files(self):
        self.upload_to_shotgrid()

    # Check for potential warnings related to the outliner
    def outliner_warning(self):
        self.task_step = self.get_user_task()
        warn_list_task = ['rig', 'mod']
        if self.task_step in warn_list_task:
            if len(self.get_outliner_items()) > 1:
                self.ui.label_validation_error.setText("There are more than two objects in the Outliner.")
                self.ui.label_validation_error.setStyleSheet("""
                    QLabel {
                        color: #e74c3c;
                        background-color: #f9e6e6;
                        border: 2px solid #e74c3c;
                        padding: 5px;
                        font-size: 12px;
                        font-weight: bold;
                        text-align: center;
                    }
                """)

    # Function to check if a version exists in ShotGrid for the current file
    def check_existence_of_version(self):
        project_id = self.get_project_id_one()
        basename = os.path.basename(self.path)
        file_name = basename.split(".")[0]
        version = self.sg.find_one('Version', [['project.Project.id', 'is', project_id], ['code', 'is', file_name]], ['sg_task', 'entity'])
        if version:
            self.find_version_number(version)
            return version
        else:
            MayaMessageBoxPrompter().show_version_not_saved_warning()
            return None

    # Core upload function to publish the files to ShotGrid
    def upload_to_shotgrid(self):
        self.save_checked_data()

        print(f"Upload path: {self.pub_path}")
        if not self.pub_path:
            print("퍼블리시할 경로가 지정되지 않았습니다.")
            return

        user_id = self.get_user_id()
        pub_file = os.path.basename(self.pub_path)
        code = pub_file.split(".")[0]
        task = self.version.get("sg_task")
        task_id = task.get("id")
        entity = self.version.get('entity')
        description = self.ui.description.toPlainText()

        # ShotGrid 버전 생성
        try:
            new_version = self.sg_uploader.create_version(
                entity=entity,
                task_id=task_id,
                code=code,
                description=description,
                project_id=191,
                pub_path=self.pub_path,
                file_type="Maya Scene",  # 퍼블리시 파일 타입 (예: 'Maya Scene')
                user_id=user_id
            )
            # 파일 업로드
            self.sg_uploader.upload_file(new_version['id'], self.pub_path)
        except Exception as e:
            print(f"ShotGrid 업로드 중 오류 발생: {e}")
    # Helper function to manage selected items for publishing
    def save_checked_data(self):
        print("file_saver 실행중..")
        self.mayafilesaver = MayaFileSaver()
        cache_data_task = ["mod", "ly", "mm", "ani", "cmp"]
        if not self.selected_items:
            print("Publish 할 아이템을 선택해주세요.")
            return
        if not self.pub_path:
            print("Publish 할 경로가 지정되지 않았습니다.")
            return
        if self.task_step == "lkd":
            self.json_path, self.ma_path = self.mayafilesaver.export_shader_ma_json(self.pub_path)
            print(self.json_path, self.ma_path)

        elif self.task_step == "lgt":
            print("saving lgt...")
            aovs = self.get_standard_aov_info(191)
            print("aovs", aovs)
            cache_mb_exr_path = self.get_version_dir(self.pub_path)
            self.exr_path = self.mayafilesaver.render_exr(cache_mb_exr_path, self.pub_path, aovs, self.selected_items)
            print("exr_path")
            self.mb_path = self.mayafilesaver.save_selected_items_as_mb(self.get_outliner_items(), self.pub_path)
            print(self.exr_path, self.mb_path)

        elif self.task_step == "rig":
            self.mayafilesaver.save_selected_items_as_mb(self.selected_items, self.pub_path)
            print(self.selected_items)
            print(self.pub_path)

        elif self.task_step == "mm":  # Handle mm task (caching paths)
            cache_mb_path = self.get_version_dir(self.pub_path)
            print(cache_mb_path)
            self.cache_path, self.mb_path = self.mayafilesaver.export_selected_items_as_alembic_and_mb(self.selected_items, cache_mb_path, self.pub_path)
            self.camera_path = self.get_camera_cache_path(self.cache_path)

        elif self.task_step == "ani":
            cache_mb_path = self.get_version_dir(self.pub_path)
            print(cache_mb_path)
            self.cache_path, self.mb_path = self.mayafilesaver.export_selected_items_as_alembic_and_mb(self.selected_items, cache_mb_path, self.pub_path)
            self.camera_path = self.get_camera_cache_path(self.cache_path)
            print(self.selected_items)

        elif self.task_step in cache_data_task:
            cache_mb_path = self.get_version_dir(self.pub_path)
            print(cache_mb_path)
            self.cache_path, self.mb_path = self.mayafilesaver.export_selected_items_as_alembic_and_mb(self.selected_items, cache_mb_path, self.pub_path)
            print(self.selected_items)

    # Generate the publish path by incrementing the version number
    def get_publish_path(self):
        pattern = r'v(\d{3})'
        new_version_number = self.find_version_number(self.version)
        new_path = self.path.replace("wip", "pub")
        if 'v' in new_path:
            new_path = re.sub(pattern, f'v{new_version_number}', new_path)  # Replace with new version
        print(new_path)
        return new_path

    # Helper function to get version directory for caching
    def get_version_dir(self, pub_path):
        project_name = self.get_project_name(self.get_project_id_one())
        dir_path = os.path.dirname(pub_path)
        print("dir_path", dir_path)
        pattern = rf"({project_name})(/)"
        cache_dir = re.sub(pattern, r"\1/cache\2", dir_path)
        print("cache_dir", cache_dir)
        return cache_dir

    # Function to find the next available version number for publishing
    def find_version_number(self, version):
        task = version['sg_task']
        pub_versions = self.get_pub_version_code(task)
        if not pub_versions:
            return str(int(1)).zfill(3)
        version_codes = []
        pattern = r'v(\d{3})'
        for version in pub_versions:
            version_code = version.get("code")
            match = re.search(pattern, version_code)
            if match:
                version_codes.append(match.group(1))
        version_codes.sort()
        new_version_number = str(int(version_codes[-1]) + 1).zfill(3)
        print(new_version_number)
        return new_version_number

    # Function to take a screenshot and display it in the UI
    def make_screenshot(self):
        self.capture = Screen_Capture(self.label_thum_img)
        self.capture.show()

    # Helper function to get camera cache path
    def get_camera_cache_path(self, abc_paths):
        for abc_path in abc_paths:
            if "camera" in os.path.basename(abc_path):
                return abc_path

##################################################################################################
# Screen Capture widget class to handle taking and displaying screenshots
class Screen_Capture(QWidget):
    def __init__(self, label_thum_img, parent=None):
        super().__init__(parent)
        self.start_pos = None
        self.end_pos = None
        self.label_thum_img = label_thum_img
        QApplication.setOverrideCursor(Qt.CrossCursor)  # Override cursor to crosshair
        self.setWindowFlag(Qt.FramelessWindowHint)  # Remove window frame
        self.setWindowOpacity(0.3)  # Set window opacity to 30%
        self.setAttribute(Qt.WA_TranslucentBackground)  # Enable transparent background
        self.showFullScreen()  # Show in fullscreen mode

    # Capture the mouse press event for selecting the area
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = self.start_pos
            self.update()

    # Track mouse movement to adjust the selection area
    def mouseMoveEvent(self, event):
        if self.start_pos:
            self.end_pos = event.pos()
            self.update()

    # Finalize the screenshot capture
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_pos = event.pos()
            self.capture_screen()
            QApplication.restoreOverrideCursor()
            self.start_pos = None
            self.end_pos = None
            self.close()

    # Actual screenshot capture logic
    def capture_screen(self):
        if self.start_pos and self.end_pos:
            x = min(self.start_pos.x(), self.end_pos.x())
            y = min(self.start_pos.y(), self.end_pos.y())
            w = abs(self.start_pos.x() - self.end_pos.x())
            h = abs(self.start_pos.y() - self.end_pos.y())
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0, x, y, w, h)
            base_path = os.path.dirname("/home/rapa/.thumbnail")
            self.capture_folder_path = os.path.join(base_path, "capture")
            if not os.path.exists(self.capture_folder_path):
                os.makedirs(self.capture_folder_path)
            screenshot_file_path = os.path.join(self.capture_folder_path, "screenshot.jpg")
            screenshot.save(screenshot_file_path, "jpg", quality=100)
            print(f"{screenshot_file_path}에 스크린샷이 저장되었습니다.")
            pixmap = QPixmap(screenshot_file_path)
            self.label_thum_img.setPixmap(pixmap)
            self.label_thum_img.setScaledContents(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PublishHandler()
    window.show()
    sys.exit(app.exec())
