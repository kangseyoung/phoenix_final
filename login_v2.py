import sys
import subprocess
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtWidgets import QLineEdit, QPushButton, QLabel
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from shotgun_api3 import Shotgun

from Loader import *


class Login(QWidget):
    def __init__(self):
        super().__init__()

        # UI 경로 설정 
        ui_file_path = './ui/login.ui'
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(ui_file, self)
        ui_file.close()

        # 샷그리드 연결
        script_name = "kimgyeoul"
        script_key = "sBwdjezpc&zxhlyr5iqwbkgrn"
        server_url = "https://4thacademy.shotgrid.autodesk.com/"
        self.sg = Shotgun(server_url, script_name, script_key)

        # UI 이벤트 연결
        self.email_input = self.ui.findChild(QLineEdit, 'lineEdit') 
        self.login_button = self.ui.findChild(QPushButton, 'pushButton') 
        self.status_label = self.ui.findChild(QLabel, 'label_3')       
        self.login_button.clicked.connect(self.on_login)

    # 로그인 함수
    def on_login(self):
        email = self.email_input.text()
        user = self.sg.find_one('HumanUser', [['email', 'is', email]], 
                                ['id', 'firstname', 'lastname', 'projects']) 
        
        if user:
            user_name = f"{user.get('firstname', '')} {user.get('lastname', '')}"
            self.status_label.setText(f'{user_name}님으로 로그인되었습니다.')     
 
            user_id = user['id']
            projects = self.sg.find('Project', [['users', 'is', 
                                    {'type': 'HumanUser', 'id': 
                                     user_id}]], ['id', 'name'])
            
            for project in projects:
                print(project['name'])  
                
            
            tasks = self.sg.find('Task', [['project', 'is', project], 
                                ['task_assignees', 'is', 
                                {'type': 'HumanUser', 'id': 
                                user_id}]], ['content','due_date', 'entity', 'id'])
            
            for task in tasks:
                print(task['content'], task['due_date'], task['entity'], task['id'])  
                
##################################################################################################################                
            self.open_loader(email)
        else:
            self.status_label.setText('유저가 없습니다')

 
            
            
    def open_loader(self, email):
        # 새로운 프로세스로 MainWindow 실행
        subprocess.Popen([sys.executable, './Loader/loader_main_v1100.py', email])
        
        # 현재 로그인 창 닫기
        # window.close()
        pass
        

################################################################################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    sys.exit(app.exec())



















