# * 설정파일 기반으로 설치(파일위치 및 계정/패스워드 등)
# * 설정파일 체크 프로세스 설계(최초 실행 시 intall화면-cmd), 서비스 등록 전/후 테스트
# 1) 설치를 진행하시겠습니까? Y/N
# 2) 파일위치 입력(헷갈리지 않게 )
# 3) 계정 입력
# 4) 패스워드 입력
# 5) 파일경로 입력(/, \ 변경 및 경로 마지막에 /, \ 존재여부 체크)
# 6) 파일명 입력

import json

with open('./conf/config.json', 'r') as f:
    install_config = json.load(f)

def check_install_YN():
    if install_config["installed"] == "N":
        print("설치는 아래 예시를 참고하여 순서대로 입력해주시면 됩니다.")
        # print("1) 세팅 진행여부 선택")
        # print("2) ERP 계정 등록")
        # print("3) 입력한 ERP 계정의 비밀번호 등록")
        print("1) ERP 사용자 이름          : 홍길동")
        print("2) ERP 로그인 계정          : kdhong@hist.co.kr")
        print("3) ERP 로그인 비밀번호      : 5678")
        print("4) 파일경로(*마지막에 / 입력: /User/kdhong/Download/")
        print("5) 파일명(*엑셀만 가능)     : sample.xlsx")
        print("")

        text = input("설치를 진행하시겠습니까?(Y/N) : ")
        # print(text)
        installed = text
        install_config["installed"] = installed

        if text == "Y":
            print("설치를 진행합니다...")

            text = input("ERP 사용자 이름 : ")
            user = text
            print(user)
            install_config["user"] = user

            text = input("ERP 로그인 계정 : ")
            account = text
            print(account)
            install_config["account"] = account
            
            text = input("ERP 로그인 비밀번호 : ")
            password = text
            print(password)
            install_config["password"] = password

            text = input("파일경로 : ")
            filepath = text
            print(filepath)
            install_config["filepath"] = filepath

            text = input("파일명 : ")
            filename = text
            print(filename)
            install_config["filename"] = filename

            with open('./conf/config.json', 'w') as f:
                json.dump(install_config, f, ensure_ascii=False)

            print("설치가 정상적으로 완료되었습니다.")
            
        else :
            print("설치를 종료합니다.")

    elif install_config["installed"] == "Y":
        print("설치가 완료된 상태입니다.")

        text = input("초기화 하시겠습니까?(Y/N) : ")
        installed = text
        install_config["installed"] = installed

        if text == "Y":
            install_config["user"] = "홍길동"
            install_config["account"] = "kdhong@hist.co.kr"
            install_config["password"] = "5678"
            install_config["filepath"] = "/user/kdhong/download/"
            install_config["filename"] = "/sample.xlsx"
            install_config["installed"] = "N"

            with open('./conf/config.json', 'w') as f:
                json.dump(install_config, f, ensure_ascii=False)

            print("초기화가 완료되었습니다.")

        else:
            print("초기화가 취소되었습니다.")


check_install_YN()


# with open('ars.json', 'r') as f:
#     json_data = json.load(f)
#     # json.dump(json_data, f, ensure_ascii=False)
# # print(json_data["name"])
# print(json.dumps(json_data))
