import os
import re
import configparser 
import logging
from typing import Any, Optional

class ConfigManager:
    """ loader_config.ini(설정 파일)을 관리 """ 
    _instance = None    # 싱글톤 패턴을 위한 클래스 변수(싱글톤 인스턴스를 저장하는 데 사용)

    # 기본 경로 및 대체 경로
    CONFIG_PATH = os.path.join('/home/rapa/_phoenix_/Loader/', 'loader_config_v1100.ini')  # 기본 경로
    ALTERNATE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'loader_config_v1100.ini')    # 대체 경로 겸 테스트용 경로

    def __new__(cls):   # init 전에 호출되는 클래스 메소드! self가 아니라 cls를 인자로 받는다.
        """
        <싱글톤 디자인 패턴>
        클래스 자신의 인스턴스가 하나만 존재하도록 _instance가 None일 때만 인스턴스 생성
        :param cls: 클래스 자신
        :return: ConfigManager 인스턴스
        """
        if cls._instance is None:   # 인스턴스가 없으면
            cls._instance = super().__new__(cls) # 부모 클래스(object)의 __new__ 메소드 호출
            cls._instance._load_config()    # 설정 파일 로드   
        return cls._instance    # 인스턴스 반환

    def _load_config(self): 
        """ 'loader_config.ini'을 읽고 self.config에 저장 """
        self.config = configparser.ConfigParser()   # ConfigParser 객체 생성

        if not os.path.isfile(self.CONFIG_PATH):    # CONFIG_PATH가 파일이 아니면 
            print(f"기본 경로에 파일이 없습니다. 대체 경로를 사용합니다: {self.ALTERNATE_CONFIG_PATH}")
            self.CONFIG_PATH = self.ALTERNATE_CONFIG_PATH # 대체 경로 사용

            if not os.path.isfile(self.ALTERNATE_CONFIG_PATH):    # 대체 경로도 파일이 아니면
                raise FileNotFoundError("설정 파일을 찾을 수 없습니다.")    # FileNotFoundError 발생
        
        self.config.read(self.CONFIG_PATH)  # config 파일 읽기
        print(f"설정 파일 로드됨: {self.CONFIG_PATH}")

    def get_value_as_str(self, section: str, key: str, fallback: Any = None) -> str: 
        """
        설정 값을 str 타입으로 변환해서 가져옵니다.
        :param section: 가져올 섹션 이름
        :param key: 가져올 키 이름
        :param fallback: 디폴트(설정 값이 없을 때 반환할 값)
        :return: 설정 값(섹션, 키에 해당하는 값)
        return type: str
        """
        return self.config.get(section, key, fallback=fallback) 

    def get_value_as_int(self, section: str, key: str, fallback: Optional[int] = None) -> int:
        """
        설정 값을 int 타입으로 변환해서 가져옵니다.
        :param section: 가져올 섹션 이름
        :param key: 가져올 키 이름
        :param fallback: 디폴트(설정 값이 없을 때 반환할 값)
        :return: 설정 값
        :rtype: int
        """
        return self.config.getint(section, key, fallback=fallback)

    def get_value_as_bool(self, section: str, key: str, fallback: Optional[bool] = None) -> bool:
        """
        설정 값을 bool타입으로 변환해서 가져옵니다.
        'true', 'on', 'yes', '1'은 True 값으로, 'false', 'off', 'no', '0'은 False 값으로 변환
        :param section: 가져올 섹션 이름
        :param key: 가져올 키 이름
        :param fallback: 디폴트(설정 값이 없을 때 반환할 값)
        :return: 설정 값
        :rtype: bool
        """
        return self.config.getboolean(section, key, fallback=fallback)
    
    # def get_version_settings(self):
    #     """ 버전 관리 설정을 가져옵니다. """
    #     return {
    #         'pattern': self.get_value_as_str('VersionControl', 'version_pattern', fallback=r'_v\d+'),   
    #         'default': self.get_value_as_str('VersionControl', 'default_version', fallback='_v001')
    # }

# 사용 예시)
# config = ConfigManager() 로 인스턴스 생성 후
# 클래스 메소드 get, getint, getboolean을 사용하여 설정 값을 가져온다.
