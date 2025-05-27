# prompt:
# 아래와 같이 5초마다 DB Select해서 결과를 print하는 스케줄러를 만들었는데 처음 돌자마자 바로 멈추고 있어. 혹시 원인알아?
import schedule
import time
from datetime import datetime, date
import psycopg2
# from flask import Flask, request, jsonify, Blueprint, make_response # Flask 관련 임포트 제거
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

# from common import getEnv
# DB_HOST     = getEnv.get_environment_variable('DB_HOST')
# DB_USER     = getEnv.get_environment_variable('DB_USER')
# DB_PASSWORD = getEnv.get_environment_variable('DB_PASSWORD')
# DB_NAME     = getEnv.get_environment_variable('DB_NAME')
# DB_PORT     = getEnv.get_environment_variable('DB_PORT')
DB_HOST     = "34.22.105.246"
DB_USER     = "usecase-public"
DB_PASSWORD = "usecase12#$"
DB_NAME     = "postgres"
DB_PORT     = 5432

def connect_db():
    """PostgreSQL 데이터베이스에 연결합니다."""
    conn = None
    try:
        # DB_PORT를 명시적으로 지정
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)

    except psycopg2.Error as e:
        print(f"데이터베이스 연결 오류: {e}")

    return conn


def fetch_all_user_info(conn, account):
    print("fetch_all_user_info : ", account)
    """user_info 테이블의 모든 데이터를 조회합니다."""
    cursor = conn.cursor()

    query = """
        SELECT user_name, account, password, restart_count, display_yn FROM user_info WHERE account = %s;
    """

    try:
        cursor.execute(query, (account,))
        records = cursor.fetchall()
        results = []

        for row in records:
            results.append({
                "user_name": row[0],
                "account": row[1],
                "password": row[2],
                "restart_count": row[3],
                "display_yn": row[4]
            })
        
        print("results : ", results)

        return results
    
    except psycopg2.Error as e:
        print(f"ar_job 데이터 조회 실패: {e}")
        return None
    
    finally:
        cursor.close()


def fetch_all_ar_jobs(conn):
    """ar_job 테이블의 모든 데이터를 조회합니다."""
    cursor = conn.cursor()

    # query = """
    #     SELECT job_id, title, user_name, account, created_at, updated_at, job_status, complete_yn
    #     FROM ar_job ORDER BY job_id DESC;
    # """
    query = """
        SELECT job_id, account, job_status FROM ar_job WHERE job_status = 'SCHEDULED' ORDER BY job_id ASC LIMIT 1;
    """

    try:
        cursor.execute(query)
        records = cursor.fetchall()
        results = []

        for row in records:
            # results.append({
            #     "job_id": row[0],
            #     "title": row[1],
            #     "user_name": row[2],
            #     "account": row[3],
            #     "created_at": row[4].isoformat() if row[4] else None,
            #     "updated_at": row[5].isoformat() if row[5] else None,
            #     "job_status": row[6],
            #     "complete_yn": row[7]
            # })
            results.append({
                "job_id": row[0],
                "account": row[1],
                "job_status": row[2]
            })

        return results
    
    except psycopg2.Error as e:
        print(f"ar_job 데이터 조회 실패: {e}")
        return None
    
    finally:
        cursor.close()


# prompt:
# 아래는 postgres db 내 ar_info와 ar_info_detail 테이블에서 데이터를 select해오는 프로세스야.
# 1개의 ar_info에는 여러개의 ar_info_detail row가 포함될 수 있는데
# 1) 먼저 job_id와 기준으로 registered_yn = 'N'을 기준으로 ar_info 데이터를 가져와서 json으로 변환해줘.
# * 이 때 InvoiceDetails라는 배열타입의 변수를 생성해줘.
# 2) 다음은 앞에서 가져온 ar_info에서 ar_info_id와 ar_issued_yn = 'N' 기준으로 ar_info_detail 데이터를 '모두' 가져와서 json으로 변환 후 InvoiceDetails에 저장해줘.
# ar_info_detail에 데이터가 여러개인 경우를 대비해 InvoiceDetails는 반드시 배열로 선언해야해.
# 3) 마지막으로 ar_info와 ar_info_detail를 return 해줘.
def fetch_ar_data(job_id):
    """
    주어진 job_id와 registered_yn='N' 기준으로 ar_info 데이터를 가져오고,
    각 ar_info에 연결된 ar_info_detail 데이터를 ar_issued_yn='N' 기준으로 가져와
    InvoiceDetails 배열에 포함하여 반환합니다.
    """
    conn = None
    try:
        conn = connect_db()
        if not conn:
            print("데이터베이스 연결 실패.")
            return []

        cursor = conn.cursor()

        # 1) job_id와 registered_yn = 'N'을 기준으로 ar_info 데이터 가져와서 JSON으로 변환
        # * 이 때 InvoiceDetails라는 배열타입의 변수를 생성
        ar_info_query = """
            SELECT ar_info_id, job_id, user_name, account, business_unit, transaction_source, 
                   transaction_type, transaction_number, transaction_date, accounting_date, 
                   bill_to_name, payment_terms, structured_payment_reference, tax_proof_type, 
                   business_number, email, reverse_issue_yn, registered_yn
            FROM ar_info 
            WHERE job_id = %s AND registered_yn = 'N';
        """

        cursor.execute(ar_info_query, (job_id,))
        ar_info_records = cursor.fetchall()
        
        results = []

        for row in ar_info_records:
            ar_info_id = row[0] # ar_info_id는 ar_info_detail을 조회할 때 사용

            ar_info_data = {
                "ar_info_id": row[0],
                "job_id": row[1],
                "user_name": row[2],
                "account": row[3],
                "business_unit": row[4],
                "transaction_source": row[5],
                "transaction_type": row[6],
                "transaction_number": row[7],
                "transaction_date": row[8].isoformat() if isinstance(row[8], (datetime, date)) else str(row[8]),
                "accounting_date": row[9].isoformat() if isinstance(row[9], (datetime, date)) else str(row[9]),
                "bill_to_name": row[10],
                "payment_terms": row[11],
                "structured_payment_reference": row[12],
                "tax_proof_type": row[13],
                "business_number": row[14],
                "email": row[15],
                "reverse_issue_yn": row[16],
                "registered_yn": row[17],
                "InvoiceDetails": [] # InvoiceDetails 배열 생성
            }

            # 2) 앞에서 가져온 ar_info에서 ar_info_id와 ar_issued_yn = 'N' 기준으로
            # ar_info_detail 데이터를 '모두' 가져와서 JSON으로 변환 후 InvoiceDetails에 저장
            ar_info_detail_query = """
                SELECT ar_info_detail_id, ar_info_id, memo_line, description, quantity, unit_price,
                       tax_classification, revenue, transaction_business_category, cost_center, 
                       account, project, ar_issued_yn 
                FROM ar_info_detail 
                WHERE ar_info_id = %s AND ar_issued_yn = 'N';
            """
            cursor.execute(ar_info_detail_query, (ar_info_id,))
            ar_info_detail_records = cursor.fetchall()

            # 파이썬 소스코드 중 일부인데 unit_price 부분에 데이터가 "unit_price": Decimal("463305600.0000") 이런 식으로 나와서 오류가 발생하고 있어.
            # 혹시 463305600값만 가져오게 할 수 있어?
            for detail_row in ar_info_detail_records:
                ar_info_data["InvoiceDetails"].append({
                    "ar_info_detail_id": detail_row[0],
                    "ar_info_id": detail_row[1],
                    "memo_line": detail_row[2],
                    "description": detail_row[3],
                    "quantity": detail_row[4],
                    # "unit_price": detail_row[5],
                    "unit_price": int(detail_row[5]), # Decimal 객체를 int으로 변환
                    "tax_classification": detail_row[6],
                    "revenue": detail_row[7],
                    "transaction_business_category": detail_row[8],
                    "cost_center": detail_row[9],
                    "account_detail": detail_row[10], # 컬럼명 충돌 방지: ar_info에도 'account'가 있어서 'account_detail'로 변경
                    "project": detail_row[11],
                    "ar_issued_yn": detail_row[12]
                })
            
            results.append(ar_info_data)
        
        # 3) 마지막으로 ar_info와 ar_info_detail를 return 해줘.
        return results

    except psycopg2.Error as e:
        print(f"데이터 조회 실패: {e}")
        return [] # 오류 발생 시 빈 리스트 반환
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        return []
    finally:
        if conn:
            conn.close()


def processing_ERP_AR_Transaction(name):
    """실제로 수행할 작업 함수"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Hello, {name}! This job is running.")

    conn = connect_db()

    if conn is None:
        print("데이터베이스 연결 실패. 작업을 건너뜝니다.")
        return # 데이터베이스 연결 실패 시 함수 종료

    try:
        ar_jobs = fetch_all_ar_jobs(conn)

        if ar_jobs:
            print("--- 조회된 AR Jobs ---")

            for job in ar_jobs:
                print(f"Job ID: {job['job_id']}, Account(email): {job['account']}, Status: {job['job_status']}")

                user_info = fetch_all_user_info(conn, job['account'])

                # for user_info in user_infos:

                user_name     = user_info[0]['user_name']
                account       = user_info[0]['account']
                password      = user_info[0]['password']
                restart_count = user_info[0]['restart_count']
                displayYN     = user_info[0]['display_yn']
                print("user_name     : ", user_name)
                print("account       : ", account)
                print("password      : ", password)
                print("restart_count : ", restart_count)
                print("displayYN     : ", displayYN)

                try:
                    # print('else - else - 3rd try')
                    # logger.LoggerFactory._LOGGER.info('--------------------------------------------------')
                    # logger.LoggerFactory._LOGGER.info('--------------------------------------------------')
                    # logger.LoggerFactory._LOGGER.info('1) 설치여부 확인 및 사용자 정보 가져오기')
                    # logger.LoggerFactory._LOGGER.info('2) 엑셀에 등록된 데이터 기반 json 데이터 생성')
                    # logger.LoggerFactory._LOGGER.info('3) ERP 로그인 및 Receivables > Billing 이동 <<< [현재위치]')
                    # logger.LoggerFactory._LOGGER.info('4) Transaction 생성 및 General Information 등록')
                    # logger.LoggerFactory._LOGGER.info('5) Invoice Lines 및 Distribution 등록')

                    # dev
                    # url = 'https://efuw-test.fa.ap1.oraclecloud.com/'

                    # live
                    url = 'https://efuw.login.ap1.oraclecloud.com/'

                    # account = job['account']
                    # password = job['job_status']

                    if displayYN == 'N':                    
                        # 1) 화면출력 안함
                        options = webdriver.ChromeOptions()
                        # options.add_experimental_option("detach", True) # 화면꺼짐 방지
                        options.add_argument('headless')
                        driver = webdriver.Chrome(options=options)
                        wait = WebDriverWait(driver, 20)
                        driver.get(url)
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info('ERP 페이지 이동 완료(화면출력 안함)')

                    else:
                        # 2) 화면출력 함
                        driver = webdriver.Chrome()
                        wait = WebDriverWait(driver, 20)

                        driver.get(url)
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info('ERP 페이지 이동 완료(화면출력 함)')

                    # 로그인
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnActive"]')))
                    displayOK = driver.find_element(By.XPATH, '//*[@id="btnActive"]').is_displayed()
                    # logger.LoggerFactory._LOGGER.info('displayOK : {}'.format(displayOK))
                    # driver.find_element(By.XPATH, '//*[@id="userid"]').send_keys(account)
                    driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div/main/form/input[1]').send_keys(account)
                    time.sleep(1)
                    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(password)
                    time.sleep(1)
                    driver.find_element(By.XPATH, '//*[@id="btnActive"]').click()
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('로그인 완료')
                    # logger.LoggerFactory._LOGGER.info('{} : {}'.format(account, password))

                    # logger.LoggerFactory._LOGGER.info('AR Transaction 이동')
                    # 햄버거 버튼 클릭
                    time.sleep(10)
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pt1:_UISmmLink::icon"]'))) # dev
                    # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="groupNode_my_information"]'))) # live - 화면이 모두 로딩되고 나서
                    driver.find_element(By.XPATH, '//*[@id="pt1:_UISmmLink::icon"]').click()
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('햄버거 버튼 클릭 완료')

                    # Receivables 메뉴 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pt1:_UISnvr:0:nvgpgl2_groupNode_receivables"]')))
                    driver.find_element(By.XPATH, '//*[@id="pt1:_UISnvr:0:nvgpgl2_groupNode_receivables"]').click()
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Receivables 메뉴 클릭 완료')

                    # Billing 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pt1:_UISnvr:0:nv_itemNode_receivables_billing"]')))
                    driver.find_element(By.XPATH, '//*[@id="pt1:_UISnvr:0:nv_itemNode_receivables_billing"]').click()
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Billing 클릭 완료')


                    ar_info = fetch_ar_data(job['job_id'])
                    print("ar_info and ar_info_detail : ", ar_info)

                    # Tasks 이미지 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH,
                                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTsdi__TransactionsWorkArea_itemNode__FndTasksList::icon"]')))
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTsdi__TransactionsWorkArea_itemNode__FndTasksList::icon"]').click()
                    # time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Tasks 이미지 클릭 완료')

                    # Create Transaction 클릭
                    wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTRaT:0:RAtl1"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTRaT:0:RAtl1"]').click()
                    # logger.LoggerFactory._LOGGER.info('Create Transaction 클릭 완료')

                    # 데이터 입력
                    # Transaction Source
                    wait.until(EC.element_to_be_clickable(
                        (By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:batchSourceId::content"]')))
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:batchSourceId::content"]').send_keys(
                        ar_info[0]['transaction_source'])
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:batchSourceId::content"]').send_keys(
                        Keys.ENTER)
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Transaction Source 입력 완료')

                    # Transaction Type : 매출유형
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:transactionTypeId::content"]').send_keys(
                        ar_info[0]['transaction_type'])
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:transactionTypeId::content"]').send_keys(
                        Keys.ENTER)
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Transaction Type : 매출유형 입력 완료')

                    # Transaction Number : 전표번호(ARTyymmdd이름hhmm)
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:inputText2::content"]').send_keys(
                        ar_info[0]['transaction_number'])
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Transaction Number : 전표번호 입력 완료')

                    # Transaction Date : 계산서 발행일자(yyyy-mm-10) - 사용익월 10일
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:tdt::content"]').clear()
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:tdt::content"]').send_keys(
                        ar_info[0]['transaction_date'])
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Transaction Date : AR 작성일자 입력 완료')

                    # Accounting Date : 계산서 발행일자(yyyy-mm-10) - 사용익월 10일
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:inputDate9::content"]').clear()
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:inputDate9::content"]').send_keys(
                        ar_info[0]['accounting_date'])
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Accounting Date : 계산서 발행일자 입력 완료')

                    # Bill-to Name
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:billToNameId::content"]').send_keys(
                        ar_info[0]['bill_to_name'])
                    # driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:billToNameId::content"]').send_keys(Keys.ENTER)
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Bill-to Name	입력 완료')

                    # Payment Terms	: 수금조건
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:paymentTermId::content"]').send_keys(
                        ar_info[0]['payment_terms'])
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:paymentTermId::content"]').send_keys(
                        Keys.ENTER)
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Payment Terms : 수금조건 입력 완료')

                    # Show More 클릭
                    wait.until(EC.element_to_be_clickable(
                        (By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:showMore"]')))
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:showMore"]').click()
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Show More 클릭 완료')

                    # Miscellaneous 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH,
                                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:showDetailItem5::disAcr"]')))
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:showDetailItem5::disAcr"]').click()
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Miscellaneous 클릭 완료')

                    # Structured Payment Reference : 적요 입력 필수
                    wait.until(EC.element_to_be_clickable(
                        (By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:it20::content"]')))
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:it20::content"]').send_keys(
                        ar_info[0]['structured_payment_reference'])
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Structured Payment Reference : 적요 입력 완료')

                    # 세무 증빙 유형(TaxProofType)	
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:df1_TransactionHeaderDFF2IteratorslipTypeHXSlipType::content"]').send_keys(
                        ar_info[0]['tax_proof_type'])
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('세무 증빙 유형 입력 완료')

                    # 역발행여부(ReverseIssue)
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:df1_TransactionHeaderDFF2IteratorinverseIssueHXSlipType::content"]').send_keys(
                        ar_info[0]['reverse_issue_yn'])
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('역발행여부 입력 완료')

                    # 작성자 E-Mail
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:df1_TransactionHeaderDFF2IteratoruserEmailHXSlipType::content"]').send_keys(
                        ar_info[0]['email'])
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('작성자 E-Mail 입력 완료')


                    ids_count = 0

                    # Invoice Lines
                    while ids_count < len(ar_info[0]['InvoiceDetails']):
                        # logger.LoggerFactory._LOGGER.info('{}번째 ids_count'.format(ids_count + 1))

                        # Memo Line
                        driver.find_element(By.XPATH,
                                            '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:{}:memoLineNameId::content"]'.format(ids_count)).send_keys(
                            ar_info[0]['InvoiceDetails'][ids_count]['memo_line'])
                        driver.find_element(By.XPATH,
                                            '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:{}:memoLineNameId::content"]'.format(ids_count)).send_keys(
                            Keys.ENTER)
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info('Memo Line 입력 완료')

                        # Description
                        # Memo Line보다 먼저 입력하면 나중에 Memo Line 내용으로 바뀜
                        driver.find_element(By.XPATH,
                                            '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:{}:descriptionId::content"]'.format(ids_count)).clear()
                        driver.find_element(By.XPATH,
                                            '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:{}:descriptionId::content"]'.format(ids_count)).send_keys(
                            ar_info[0]['InvoiceDetails'][ids_count]['description'])
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info('Description 입력 완료')

                        # Quantity
                        driver.find_element(By.XPATH,
                                            '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:{}:quantity::content"]'.format(ids_count)).send_keys(
                            ar_info[0]['InvoiceDetails'][ids_count]['quantity'])
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info('Quantity 완료')

                        # Unit Price
                        driver.find_element(By.XPATH,
                                            '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:{}:sellingPrice::content"]'.format(ids_count)).send_keys(
                            ar_info[0]['InvoiceDetails'][ids_count]['unit_price'])
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info('Unit Price 완료')

                        # Tax Classification : 과세유형
                        driver.find_element(By.XPATH,
                                            '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:{}:taxClassificationCodeId::content"]'.format(ids_count)).send_keys(
                            ar_info[0]['InvoiceDetails'][ids_count]['tax_classification'])
                        driver.find_element(By.XPATH,
                                            '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:{}:taxClassificationCodeId::content"]'.format(ids_count)).send_keys(
                            Keys.ENTER)
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info('Tax Classification 완료')

                        ids_count = ids_count + 1


                    # save
                    wait.until(EC.element_to_be_clickable((By.XPATH,
                                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:saveMenu"]/table/tbody/tr/td[1]/a/span')))
                    # time.sleep(30)
                    driver.find_element(By.XPATH,
                                        '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:saveMenu"]/table/tbody/tr/td[1]/a/span').click()
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Save 완료')

                    # 만약 AR 문서가 등록되어 있는 경우 삭제프로세스 진행
                    if driver.find_element(By.XPATH, '//*[@id="_FOd1::msgDlg::cancel"]').is_displayed(): 
                        # logger.LoggerFactory._LOGGER.info('AR 문서가 등록된 상태')

                        # 오류 AR 삭제프로세스
                        # 1) Billing 화면으로 이동 : refresh
                        # 2) AR 검색화면으로 이동 : 돋보기 클릭
                        # 3) Transaction Number 입력
                        # 4) Transaction Number Search
                        # 5) 해당 AR 클릭
                        # 6) 삭제
                        # 7) Done

                        # This transaction number already exists. Enter a unique transaction number. (AR-855040)
                        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOd1::msgDlg::cancel"]')))
                        driver.find_element(By.XPATH, '//*[@id="_FOd1::msgDlg::cancel"]').click()
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info("1 - This transaction number already exists. Enter a unique transaction number. (AR-855040)")

                        # Cancel
                        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:commandToolbarButton2"]/a')))
                        driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:commandToolbarButton2"]/a').click()
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info("1 - Cancel")

                        # Your changes aren''t saved. If you leave this page, then your changes will be lost. Do you want to continue?
                        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:dialogCancel::yes"]')))
                        driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:dialogCancel::yes"]').click()
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info("Your changes aren''t saved. If you leave this page, then your changes will be lost. Do you want to continue? >>> Yes 클릭 완료")

                        # 1) Billing 화면으로 이동
                        # driver.refresh()
                        # time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info("refresh")

                        # 2) AR 검색화면으로 이동 : 돋보기 클릭
                        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTsdiTransactionsQuickSearch::icon"]')))
                        driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTsdiTransactionsQuickSearch::icon"]').click()
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info("2")

                        # 3) Transaction Number 입력
                        driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTRaTj_id_1:1:qryId1:value00::content"]').clear()
                        driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTRaTj_id_1:1:qryId1:value00::content"]').send_keys(ar_info[0]['transaction_number'])
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info("3")

                        # 4) Transaction Number Search
                        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTRaTj_id_1:1:qryId1::search"]')))
                        driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTRaTj_id_1:1:qryId1::search"]').click()
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info("4")

                        # 5) 해당 AR 클릭
                        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/form/div[1]/div[1]/div/div/div/div[3]/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div[1]/div/div/div/div[1]/div[1]/div/div/div[1]/div/div[1]/table/tbody/tr/td[1]/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div/div/div/div/div/div/div/span/div[2]/div[2]/div/div[2]/table/tbody/tr/td[3]/span/a')))
                        driver.find_element(By.XPATH, '/html/body/div[1]/form/div[1]/div[1]/div/div/div/div[3]/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div[1]/div/div/div/div[1]/div[1]/div/div/div[1]/div/div[1]/table/tbody/tr/td[1]/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div/div/div/div/div/div/div/span/div[2]/div[2]/div/div[2]/table/tbody/tr/td[3]/span/a').click()
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info("5")

                        # 6) 삭제
                        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/form/div[1]/div[1]/div/div/div/div[3]/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div[1]/div/div/div/div[1]/div[1]/div/div/div[1]/div/div[1]/table/tbody/tr/td[1]/div/div/div/div/div[1]/table/tbody/tr/td[1]/div/div/div/div/div[1]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div/table/tbody/tr/td[2]/div/div/div[1]/div/div[1]/div[3]/div/div[1]/div[1]/table/tbody/tr/td/div/div/table/tbody/tr/td[8]/div/a')))
                        driver.find_element(By.XPATH, '/html/body/div[1]/form/div[1]/div[1]/div/div/div/div[3]/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div[1]/div/div/div/div[1]/div[1]/div/div/div[1]/div/div[1]/table/tbody/tr/td[1]/div/div/div/div/div[1]/table/tbody/tr/td[1]/div/div/div/div/div[1]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div/table/tbody/tr/td[2]/div/div/div[1]/div/div[1]/div[3]/div/div[1]/div[1]/table/tbody/tr/td/div/div/table/tbody/tr/td[8]/div/a').click()
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info("6")

                        # You're about to delete incomplete transaction. Do you want to continue?
                        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/form/div[2]/div[2]/div[1]/div[1]/table/tbody/tr/td/div/div/table/tbody/tr[3]/td[2]/table/tbody/tr/td[1]/button[1]')))
                        driver.find_element(By.XPATH, '/html/body/div[1]/form/div[2]/div[2]/div[1]/div[1]/table/tbody/tr/td/div/div/table/tbody/tr[3]/td[2]/table/tbody/tr/td[1]/button[1]').click()
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info("You're about to delete incomplete transaction. Do you want to continue? >>> Yes 클릭 완료")

                        # 7) Done
                        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/form/div[1]/div[1]/div/div/div/div[3]/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div[1]/div/div/div/div[1]/div[1]/div/div/div[1]/div/div[1]/table/tbody/tr/td[1]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div/table/tbody/tr/td[2]/div/div/div[1]/div/div[1]/div[3]/div/div[1]/div[1]/table/tbody/tr/td[1]/button')))
                        driver.find_element(By.XPATH, '/html/body/div[1]/form/div[1]/div[1]/div/div/div/div[3]/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div[1]/div/div/div/div[1]/div[1]/div/div/div[1]/div/div[1]/table/tbody/tr/td[1]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div/table/tbody/tr/td[2]/div/div/div[1]/div/div[1]/div[3]/div/div[1]/div[1]/table/tbody/tr/td[1]/button').click()
                        time.sleep(2)
                        # logger.LoggerFactory._LOGGER.info("7")


                except Exception as e:
                    print('else - else - 3rd except')
                    # logger.LoggerFactory._LOGGER.info('error msg : {}'.format(e))
                    # logger.LoggerFactory._LOGGER.info('3) ERP 로그인 및 Receivables > Billing 이동 <<< 실패')
                    # logger.LoggerFactory._LOGGER.info('사용자 정보를 다시 확인해주시기 바랍니다.')
                    re_count = re_count + 1
            print("--------------------")
        else:
            print("등록된 AR Job이 없습니다.")
        
    finally:
        if conn:
            conn.close()



# 4. 특정 시간마다 반복 (매 5초마다)
schedule.every(5).seconds.do(processing_ERP_AR_Transaction, name="Quick Check")

# 스케줄러 실행 루프
print("Scheduler started. Press Ctrl+C to exit.")
while True:
    schedule.run_pending() # 현재 시간이 되면 실행해야 할 작업을 실행
    time.sleep(1) # 1초마다 확인