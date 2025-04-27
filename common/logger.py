# https://chuun92.tistory.com/7
import logging
from datetime import datetime
import os
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'filename': record.filename,
            'function': record.funcName,
            'lineno': record.lineno,
            'message': record.getMessage(),
            # 'name': record.name,
        }
        return json.dumps(log_record, ensure_ascii=False)
    
class LoggerFactory(object) :
    _LOGGER = None
    
    # @staticmethod는 전역 함수 선언 시 사용되며 다른 class 및 파일에서도 호출할 수 있다. 
    # 프로그램 시작 시 main() 함수 안에서 create_logger()를 호출하여 logger를 생성해준다. 
    # 이때 logging.getLogger()를 호출하면 Root Logger를 가져올 수 있으며 기본 로그 레벨은 INFO로 설정했다.
    @staticmethod
    def create_logger() :

        # Logger를 전역으로 생성
        LoggerFactory._LOGGER = logging.getLogger()
        
        # Logging Level 설정
        # 설정된 레벨 외의 값을 입력하여 커스텀하게 사용할 수 도 있다.
        # CRITICAL = 50, ERROR = 40, WARNING = 30, INFO = 20, DEBUG = 10, NOTSET = 0
        LoggerFactory._LOGGER.setLevel(logging.INFO)

        # log 폴더 생성
        if not os.path.exists('./log/' + datetime.now().strftime('%Y') + '/' + datetime.now().strftime('%m')): 
            os.makedirs('./log/' + datetime.now().strftime('%Y') + '/' + datetime.now().strftime('%m'))

        # Formatter로 로그 포맷 생성
        # Formatter를 이용하면 기록될 로그의 형식을 기호에 맞게 설정하여 사용할 수 있다. 막일로 값을 받아 작성할 수는 있지만 내장되어있는 style 매개변수를 참조하여 작성하였다. (시간, 로그 레벨, 파일명, 함수, 코드 라인 번호, 메시지 순)
        # formatter = logging.Formatter('[%(asctime)s][%(levelname)s|%(filename)s-%(funcName)s:%(lineno)s] >> %(message)s')    
        # formatter = logging.Formatter('[' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '][%(levelname)s|%(filename)s-%(funcName)s:%(lineno)s] >> %(message)s')    
        # formatter = logging.Formatter('[' + str(datetime.now().strftime('%H:%M:%S')) + '][%(filename)s:%(lineno)s] >> %(message)s')    
        # formatter = logging.Formatter('[%(asctime)s][%(filename)s:%(lineno)s] >> %(message)s')    
        formatter = JsonFormatter()
        # filename = '%(filename)s'
        # Handler 생성
        # StreamHandler를 통해 쉽게 터미널 창에 나타내거나 FileHandler를 통해 log파일에 로그를 기록할 수 있다. 
        # 이를 위해 생성된 Logger에 Handler를 만들어서 AddHandler 해준다. 
        # 각 Handler에 위에서 만들어 두었던 Formatter를 적용한다.
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        file_handler = logging.FileHandler('./log/' + datetime.now().strftime('%Y') + '/' + datetime.now().strftime('%m') + '/' + datetime.now().strftime('%Y%m%d') +'.log')
        file_handler.setFormatter(formatter)
        LoggerFactory._LOGGER.addHandler(stream_handler)
        LoggerFactory._LOGGER.addHandler(file_handler)


    @classmethod
    def get_logger(cls) :
        # return cls._LOGGER
        print("cls._LOGGER : ", cls._LOGGER)
        if cls._LOGGER is None:
            cls.create_logger()
        return cls._LOGGER