from playwright.sync_api import sync_playwright
import time 
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.edge import service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from dateutil.relativedelta import *
# pip3 install python-dateutil
import logger
import json
from openpyxl import load_workbook
import calendar
from db import dbConnection, db_commit

# with open('./conf/data_mapping_test.json', 'rt', encoding='UTF8') as f:
# with open('./conf/data_mapping.json', 'rt', encoding='UTF8') as f:
#     customer_config = json.load(f)

with open('./conf/query_billStatement.json') as f:
    query_config = json.load(f)


def processing_ERP_AR_Transaction(count, issue_cnt, not_issue_cnt, re_count):

    if count == 0:
        logger.LoggerFactory.create_logger()

    logger.LoggerFactory._LOGGER.info('--------------------------------------------------')
    logger.LoggerFactory._LOGGER.info('ERP AR_Transaction 발행 시작')

    # DB 연결
    con = dbConnection()
    cursor = con.cursor()


    # 결산시점(전월) 설정
    today = datetime.today()
    year = str(today.strftime('%Y'))
    month = str(today.strftime('%m'))

    # this_year = str(today.strftime('%Y'))
    this_month = str(today.strftime('%m'))
    
    if this_month == '01':
        this_year = datetime(today.year, today.month, 1) + relativedelta(years=-1)
        this_month = datetime(today.year, today.month, 1) + relativedelta(months=-1)
    else :
        this_year = datetime(today.year, today.month, 1) + relativedelta(years=0)
        this_month = datetime(today.year, today.month, 1) + relativedelta(months=-1)
    
    # first_day = calendar.monthrange(this_year.year, this_month.month)[0]
    last_day = calendar.monthrange(this_year.year, this_month.month)[1]

    this_year = this_year.strftime('%Y')
    this_month = this_month.strftime('%m')

    bill_date = str(this_year) + '-' + str(this_month)
    logger.LoggerFactory._LOGGER.info('결산시점 : {}'.format(bill_date))


    # ERP 페이지 이동(Chrome)
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 20)

    # dev
    # url = 'https://efuw-test.fa.ap1.oraclecloud.com/'
    # live
    url = 'https://efuw.login.ap1.oraclecloud.com/'

    driver.get(url)
    time.sleep(2)
    logger.LoggerFactory._LOGGER.info('ERP 페이지 이동 완료')


    # ERP 전표 발행 대상 엑셀 불러오기
    destination = rf"D:\ajmkil\aMBP\메시지 정산 - 자동화\{year}{month}\{year}.{this_month}월 ERP 전표 발행 대상.xlsx"

    # 변수선언
    jobId        = 0
    writer       = ''
    writerId     = ''
    password     = ''
    writer_email = ''

    wb = load_workbook(destination)

    ws1 = wb['담당자']
    writer_row = 2
    while writer_row <= 11 :
        # if ws1['B{}'.format(writer_row)].value == 'V170016':
        # if ws1['A{}'.format(writer_row)].value == '1':
        if str(ws1['A{}'.format(writer_row)].value) == '1':
            jobId        = ws1['A{}'.format(writer_row)].value
            writer       = ws1['C{}'.format(writer_row)].value
            writerId     = ws1['D{}'.format(writer_row)].value
            password     = ws1['E{}'.format(writer_row)].value
            writer_email = ws1['F{}'.format(writer_row)].value
            logger.LoggerFactory._LOGGER.info('{}번쨰 행 : {} {} {} {}'.format(writer_row, writer, writerId, password, writer_email))

        writer_row = writer_row + 1

    try:
        # 로그인
        # input_username = driver.find_element(By.NAME, "userid")
        # input_password = driver.find_element(By.NAME, "password")
        # submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")

        # input_username.send_keys(writerId)
        # input_password.send_keys(password)
        # time.sleep(2)

        # submit_button.click()
        # time.sleep(2)
        # logger.LoggerFactory._LOGGER.info('로그인 완료')

        # 로그인2
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnActive"]')))
        displayOK = driver.find_element(By.XPATH, '//*[@id="btnActive"]').is_displayed()
        logger.LoggerFactory._LOGGER.info('displayOK : {}'.format(displayOK))
        # displayOK = driver.find_element(By.XPATH, '//*[@id="btnActive"]').isDisplayed()
        # logger.LoggerFactory._LOGGER.info('displayOK : {}'.format(displayOK))
        driver.find_element(By.XPATH, '//*[@id="userid"]').send_keys(writerId)
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(password)
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="btnActive"]').click() 
        time.sleep(2)
        logger.LoggerFactory._LOGGER.info('로그인 완료')
        logger.LoggerFactory._LOGGER.info('{} : {}'.format(writerId, password))

        # AR Transaction 이동
        # 햄버거 버튼 클릭
        time.sleep(10)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pt1:_UISmmLink::icon"]'))) # dev
        # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="groupNode_my_information"]'))) # live - 화면이 모두 로딩되고 나서
        driver.find_element(By.XPATH, '//*[@id="pt1:_UISmmLink::icon"]').click() 
        time.sleep(2)
        logger.LoggerFactory._LOGGER.info('햄버거 버튼 클릭 완료')

        # Receivables 메뉴 클릭
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pt1:_UISnvr:0:nvgpgl2_groupNode_receivables"]')))
        driver.find_element(By.XPATH, '//*[@id="pt1:_UISnvr:0:nvgpgl2_groupNode_receivables"]').click() 
        time.sleep(2)
        logger.LoggerFactory._LOGGER.info('Receivables 메뉴 클릭 완료')

        # Billing 클릭
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pt1:_UISnvr:0:nv_itemNode_receivables_billing"]')))
        driver.find_element(By.XPATH, '//*[@id="pt1:_UISnvr:0:nv_itemNode_receivables_billing"]').click() 
        time.sleep(2)
        logger.LoggerFactory._LOGGER.info('Billing 클릭 완료')

    except Exception as ex:
        # logger.LoggerFactory._LOGGER.info('전표 발행 대상 리스트 작성 실패 : {}'.format(company_name))
        logger.LoggerFactory._LOGGER.info('error msg : {}'.format(ex))
        # break
    

    ws2 = wb['프로젝트']
    project_row = 2
    while project_row <= 11 :
        if ws2['B{}'.format(project_row)].value == 'V170016':
            logger.LoggerFactory._LOGGER.info('프로젝트 코드 : {}'.format(ws2['B{}'.format(project_row)].value))

            project                      = ws2['B{}'.format(project_row)].value # V170016
            cost_center                  = ws2['D{}'.format(project_row)].value # cost_center
            transaction_source           = ws2['E{}'.format(project_row)].value # transaction_source
            transaction_type             = ws2['F{}'.format(project_row)].value # transaction_type
            # transaction_number           = 'ART{}{}{}'.format(str(datetime.now().strftime('%y%m%d')), writer, str(datetime.now().strftime('%H%M'))) # ARTyymmdd이름hhmm(하단에서 값 생성)
            transaction_date             = ws2['G{}'.format(project_row)].value 
            date_in_transaction_number   = ws2['G{}'.format(project_row)].value # transaction_date >>> transaction_number에 같은 일자가 사용되어야 함
            accounting_date              = ws2['H{}'.format(project_row)].value # accounting_date
            transaction_date             = str(datetime.now().strftime('%Y-%m-{}').format(transaction_date)) 
            accounting_date              = str(datetime.now().strftime('%Y-%m-{}').format(accounting_date))
            payment_terms                = ws2['I{}'.format(project_row)].value # payment_terms
            structured_payment_reference = ws2['J{}'.format(project_row)].value # structured_payment_reference
            structured_payment_reference = structured_payment_reference.format(this_month)
            tax_proof_type               = ws2['K{}'.format(project_row)].value # tax_proof_type
            memo_line                    = ws2['L{}'.format(project_row)].value # memo_line
            description                  = ws2['M{}'.format(project_row)].value # description
            description                  = description.format(this_month)
            quantity                     = ws2['N{}'.format(project_row)].value # quantity
            tax_classification           = ws2['O{}'.format(project_row)].value # tax_classification
            revenu                       = ws2['P{}'.format(project_row)].value # revenu            

            # logger.LoggerFactory._LOGGER.info('{}번쨰 행 : {} {} {} {}'.format(writer_row, writer, userid, password, email))

        project_row = project_row + 1
    # transaction_source           = ws2['D{}'.format(rowNo)].value # HX_MANUAL
    # transaction_type             = ws2['E{}'.format(rowNo)].value # 영업매출
    # writer                       = ws2['F{}'.format(rowNo)].value # 작성자
    # transaction_number           = 'ART{}{}{}'.format(str(datetime.now().strftime('%y%m%d')), writer, str(datetime.now().strftime('%H%M'))) # ARTyymmdd이름hhmm
    # # transaction_date             = ws2['G{}'.format(rowNo)].value # %Y-%m-10
    # # accounting_date              = ws2['H{}'.format(rowNo)].value # %Y-%m-10
    # transaction_date             = str(datetime.now().strftime('%Y-%m-10'))
    # accounting_date              = str(datetime.now().strftime('%Y-%m-10'))
    # bill_to_name                 = ws2['I{}'.format(rowNo)].value # 젬텍(알림톡)
    # payment_terms                = ws2['K{}'.format(rowNo)].value # 당월말 입금
    # structured_payment_reference = '{}월 메시징 서비스 사용료'.format(str(billing_month.strftime('%m')))
    # tax_proof_type               = ws2['M{}'.format(rowNo)].value # 10(세금계산서[전자])
    # writer_email                 = ws2['N{}'.format(rowNo)].value # jm.kil@hist.co.kr
    # memo_line                    = ws2['O{}'.format(rowNo)].value # 메시징 수익
    # # description                  = ws2['P{}'.format(rowNo)].value # {}월 메시징 서비스 사용료
    # description                  = '{}월 메시징 서비스 사용료'.format(str(billing_month.strftime('%m')))
    # quantity                     = ws2['Q{}'.format(rowNo)].value # 1
    # unit_price                   = ws2['R{}'.format(rowNo)].value # 9642100
    # tax_classification           = ws2['S{}'.format(rowNo)].value # HX_매출과세
    # revenu                       = ws2['T{}'.format(rowNo)].value # HX-999-99999--413131-0000--000000-00000
    # cost_center                  = ws2['U{}'.format(rowNo)].value # 전문솔루션그룹
    # project                      = ws2['V{}'.format(rowNo)].value # V170016


    ws3 = wb['AR_정산내역서']
    billStatement_row = 3
    while billStatement_row <= 52 :
        company_name = ws3['C{}'.format(billStatement_row)].value

        if company_name != '' and company_name != None :
            if ws3['G{}'.format(billStatement_row)].value == 'E' :
                logger.LoggerFactory._LOGGER.info('{}번쨰 : {} 기발행 실패(에러 or 사용자 없음)'.format(billStatement_row-2, company_name))
            elif ws3['G{}'.format(billStatement_row)].value == 'X' :
                logger.LoggerFactory._LOGGER.info('{}번쨰 : {} 발행 안함(선입금 or 선불)'.format(billStatement_row-2, company_name))
            elif ws3['G{}'.format(billStatement_row)].value == 'N' :
                logger.LoggerFactory._LOGGER.info('#################### {}번째 : {} ####################'.format(billStatement_row-2, company_name))
                
                unit_price         = ws3['D{}'.format(billStatement_row)].value
                # transaction_number = 'ART{}{}{}'.format(str(datetime.now().strftime('%y%m%d')), writer, str(datetime.now().strftime('%H%M'))) # ARTyymmdd이름hhmm
                transaction_number = 'ART{}{}{}{}{}'.format(str(datetime.now().strftime('%y')), str(datetime.now().strftime('%m')), date_in_transaction_number, writer, str(datetime.now().strftime('%H%M'))) # ARTyymmdd이름hhmm
                
                # ws4 = wb['업체']
                ws4 = wb['업체(청구단위)']
                customer_row = 2
                while customer_row <= 51 :
                    # logger.LoggerFactory._LOGGER.info('{}'.format(company_name == str(ws4['B{}'.format(customer_row)].value)))
                    # if company_name == ws4['B{}'.format(customer_row)].value :
                    #     bill_to_name = ws4['C{}'.format(customer_row)].value
                    if company_name == ws4['C{}'.format(customer_row)].value :
                        bill_to_name = ws4['D{}'.format(customer_row)].value
                        cust_sn = ws4['B{}'.format(customer_row)].value

                    customer_row = customer_row + 1

                try: 
                    # Tasks 이미지 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTsdi__TransactionsWorkArea_itemNode__FndTasksList::icon"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTsdi__TransactionsWorkArea_itemNode__FndTasksList::icon"]').click() 
                    # time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Tasks 이미지 클릭 완료')

                    # Create Transaction 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTRaT:0:RAtl1"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:_FOTRaT:0:RAtl1"]').click()
                    logger.LoggerFactory._LOGGER.info('Create Transaction 클릭 완료')


                    # 데이터 입력
                    # Transaction Source
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:batchSourceId::content"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:batchSourceId::content"]').send_keys(transaction_source)
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:batchSourceId::content"]').send_keys(Keys.ENTER)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Transaction Source 입력 완료')

                    # Transaction Type : 매출유형
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:transactionTypeId::content"]').send_keys(transaction_type)
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:transactionTypeId::content"]').send_keys(Keys.ENTER)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Transaction Type : 매출유형 입력 완료')

                    # Transaction Number : 전표번호(ARTyymmdd이름hhmm)
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:inputText2::content"]').send_keys(transaction_number)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Transaction Number : 전표번호 입력 완료')
                    
                    # Transaction Date : 계산서 발행일자(yyyy-mm-10) - 사용익월 10일
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:tdt::content"]').clear()
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:tdt::content"]').send_keys(transaction_date)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Transaction Date : AR 작성일자 입력 완료')

                    # Accounting Date : 계산서 발행일자(yyyy-mm-10) - 사용익월 10일
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:inputDate9::content"]').clear()
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:inputDate9::content"]').send_keys(accounting_date)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Accounting Date : 계산서 발행일자 입력 완료')

                    # Bill-to Name	
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:billToNameId::content"]').send_keys(bill_to_name)
                    # driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:billToNameId::content"]').send_keys(Keys.ENTER)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Bill-to Name	입력 완료')

                    # Payment Terms	: 수금조건
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:paymentTermId::content"]').send_keys(payment_terms)
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:paymentTermId::content"]').send_keys(Keys.ENTER)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Payment Terms : 수금조건 입력 완료')

                    # Show More 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:showMore"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:showMore"]').click()
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Show More 클릭 완료')

                    # Miscellaneous 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:showDetailItem5::disAcr"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:showDetailItem5::disAcr"]').click()
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Miscellaneous 클릭 완료')

                    # Structured Payment Reference : 적요 입력 필수
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:it20::content"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:it20::content"]').send_keys(structured_payment_reference)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Structured Payment Reference : 적요 입력 완료')

                    # 세무 증빙 유형 
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:df1_TransactionHeaderDFF2IteratorslipTypeHXSlipType::content"]').send_keys(tax_proof_type)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('세무 증빙 유형 입력 완료')

                    # 작성자 E-Mail	
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:df1_TransactionHeaderDFF2IteratoruserEmailHXSlipType::content"]').send_keys(writer_email)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('작성자 E-Mail 입력 완료')

                    # Invoice Lines
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:0:memoLineNameId::content"]').send_keys(memo_line)
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:0:memoLineNameId::content"]').send_keys(Keys.ENTER)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Memo Line 입력 완료')

                    # Description
                    # Memo Line보다 먼저 입력하면 나중에 Memo Line 내용으로 바뀜
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:0:descriptionId::content"]').clear()
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:0:descriptionId::content"]').send_keys(description)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Description 입력 완료')

                    # Quantity 
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:0:quantity::content"]').send_keys(quantity)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Quantity 완료')

                    # Unit Price
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:0:sellingPrice::content"]').send_keys(unit_price)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Unit Price 완료')

                    # Tax Classification : 과세유형
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:0:taxClassificationCodeId::content"]').send_keys(tax_classification)
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:AT1:_ATp:table1:0:taxClassificationCodeId::content"]').send_keys(Keys.ENTER)
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Tax Classification 완료')

                    # save
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:saveMenu"]/table/tbody/tr/td[1]/a/span')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:saveMenu"]/table/tbody/tr/td[1]/a/span').click()
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Save 완료')

                    # Action → Edit Distribution
                    time.sleep(10)
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:m1"]/div/table/tbody/tr/td[2]/a')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:m1"]/div/table/tbody/tr/td[2]/a').click()
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Action 버튼 클릭 완료')

                    # driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:Trans1:0:ap110:cmi7"]/td[2]').click()
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:cmi7"]/td[2]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:cmi7"]/td[2]').click()    
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Edit Distribution 클릭 완료')

                    # driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:Trans1:0:ap110:cb7"]').click()
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:cb7"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:cb7"]').click()
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Alert창 Yes 클릭 완료')

                    # Edit Distributions - Distributions - Revenue
                    # driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1CS::content"]').clear()
                    # driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1CS::content"]').send_keys('HX-999-99999-SELHLDM-413131-0000-V170016-000000-00000')
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1CS::content"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1CS::content"]').clear()
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1CS::content"]').send_keys(revenu)
                    # time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Edit Distributions > Revenue 입력 완료')

                    # Edit Distributions - Distributions - 우측 돋보기 버튼 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1KBIMG::icon"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1KBIMG::icon"]').click()
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Edit Distributions > 돋보기 버튼 클릭 완료')

                    # //*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value20::content"]
                    # Edit Distributions - Distributions - RESP Center
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value20::content"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value20::content"]').clear()
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value20::content"]').send_keys('99999')
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Distributions > RESP Center 입력 완료')

                    # Edit Distributions - Distributions - RESP Center 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value20::_fndSuggestPopup_sugg_ListOfValues_0"]/div/div[2]/div/span[2]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value20::_fndSuggestPopup_sugg_ListOfValues_0"]/div/div[2]/div/span[2]').click()
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Distributions > RESP Center 클릭 완료')

                    # Edit Distributions - Distributions - Cost Center
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value30::content"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value30::content"]').clear()
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value30::content"]').send_keys(cost_center) # 전문솔루션그룹
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Distributions > Cost Center 입력 완료')

                    # Edit Distributions - Distributions - Cost Center 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value30::_fndSuggestPopup_sugg_ListOfValues_0"]/div/div[2]/div/span[2]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value30::_fndSuggestPopup_sugg_ListOfValues_0"]/div/div[2]/div/span[2]').click()
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Distributions > Cost Center 클릭 완료')

                    # Edit Distributions - Distributions - Project
                    # /html/body/div[1]/form/div[2]/div[2]/div[3]/div[1]/table/tbody/tr/td/div/div/table/tbody/tr[2]/td[2]/div/div[1]/table/tbody/tr[2]/td[2]/div/div/div[2]/div/table/tbody/tr/td/table/tbody/tr[8]/td[2]/table/tbody/tr/td[1]/span/span/input
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value60::content"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value60::content"]').clear()
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value60::content"]').send_keys(project) # 대외
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Distributions > Project 입력 완료')

                    # //*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value60::_fndSuggestPopup_sugg_ListOfValues_0"]/div/div[2]/div/span[2]
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value60::_fndSuggestPopup_sugg_ListOfValues_0"]/div/div[2]/div/span[2]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SPOP_query:value60::_fndSuggestPopup_sugg_ListOfValues_0"]/div/div[2]/div/span[2]').click()
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Distributions > Project 클릭 완료')

                    # Edit Distributions - Distributions - OK 버튼 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SEl"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:DistTF1:1:AT2:_ATp:table2:1:kf1SEl"]').click()
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('Distributions > OK 버튼 클릭 완료')

                    # Save and Close
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:cb5"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:cb5"]').click()
                    # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:Trans1:0:ap110:cb5"]')))
                    # driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:Trans1:0:ap110:cb5"]').click()
                    time.sleep(3) # 없애면 오류발생

                    # Save 우측 화살표버튼 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:saveMenu::popEl"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:saveMenu::popEl"]').click()
                    # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:Trans1:0:ap110:saveMenu::popEl"]')))
                    # driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:Trans1:0:ap110:saveMenu::popEl"]').click()
                    time.sleep(3) # 없애면 오류발생
                    logger.LoggerFactory._LOGGER.info('Save 우측 화살표버튼 클릭 완료')

                    # Save and Close
                    # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:Trans1:0:ap110:cmi10"]/td[2]')))
                    # driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:Trans1:0:ap110:cmi10"]/td[2]').click()
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:cmi10"]/td[2]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:pt1:Trans1:0:ap110:cmi10"]/td[2]').click()
                    time.sleep(3) # 없애면 오류발생
                    logger.LoggerFactory._LOGGER.info('Save and Close 클릭 완료')

                    # Billing 화면에서 Alert창 내 OK버튼 클릭
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOd1::msgDlg::cancel"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOd1::msgDlg::cancel"]').click()
                    time.sleep(3) # 없애면 오류발생
                    logger.LoggerFactory._LOGGER.info('Billing 화면에서 Alert창 내 OK버튼 클릭 완료')

                    ws3['G{}'.format(billStatement_row)] = 'Y'
                    logger.LoggerFactory._LOGGER.info('AR 발행완료 : {}'.format(company_name))
                    wb.save(destination)

                    # MBP_Admin 고객사 > 청구내역 관리 내 업데이트 프로세스
                    logger.LoggerFactory._LOGGER.info('세금계산서 발행 상태 업데이트 : [{}]'.format(company_name))
                    update_status_after_writeAR = query_config['update_status_after_writeAR']
                    cursor.execute(update_status_after_writeAR.format(cust_sn, this_year, this_month))
                    db_commit(con)
                    logger.LoggerFactory._LOGGER.info('세금계산서 발행 상태 업데이트 완료')

                except Exception as ex:
                    logger.LoggerFactory._LOGGER.info('error msg : {}'.format(ex))
                    logger.LoggerFactory._LOGGER.info('AR 발행 중 오류 발생 : {}'.format(company_name))
                    ws3['G{}'.format(billStatement_row)] = 'E'
                    wb.save(destination)
                    time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('true false : {}'.format(EC.find_elements((By.XPATH, '//*[@id="_FOd1::msgDlg::cancel"]'))))

                    driver.refresh()

                    # if driver.find_element(By.XPATH, '//*[@id="_FOpt1:_UISmmLink::icon"]').is_displayed() : 
                    #     logger.LoggerFactory._LOGGER.info('햄버거 버튼 displayed : {}'.format(driver.find_element(By.XPATH, '//*[@id="_FOpt1:_UISmmLink::icon"]').is_displayed()))
                    # else :
                    #     logger.LoggerFactory._LOGGER.info('햄버거 버튼 displayed : {}'.format(driver.find_element(By.XPATH, '//*[@id="_FOpt1:_UISmmLink::icon"]').is_displayed()))
                    #     driver.refresh()
                    #     logger.LoggerFactory._LOGGER.info('화면 refresh')

                    # AR Transaction 이동
                    # 햄버거 버튼 클릭
                    # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pt1:_UISmmLink::icon"]')))
                    # driver.find_element(By.XPATH, '//*[@id="pt1:_UISmmLink::icon"]').click() 
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_UISmmLink::icon"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_UISmmLink::icon"]').click() 
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('햄버거 버튼 클릭 완료')

                    # Receivables 메뉴 클릭
                    # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pt1:_UISnvr:0:nvgpgl2_groupNode_receivables"]')))
                    # driver.find_element(By.XPATH, '//*[@id="pt1:_UISnvr:0:nvgpgl2_groupNode_receivables"]').click() 
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_UISnvr:0:nv_itemNode_receivables_billing"]/span')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_UISnvr:0:nv_itemNode_receivables_billing"]/span').click() 
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('billing 메뉴 클릭 완료')

                    # If you leave this page, then your changes will be lost. Do you want to continue?
                    # Yes : //*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAyes"]
                    # No  : //*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAno"]
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAyes"]')))
                    driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAyes"]').click() 
                    time.sleep(2)
                    logger.LoggerFactory._LOGGER.info('changes will be lost. Do you want to continue? >>> Yes 클릭 완료')

                    continue
                        

                    # Billing 클릭
                    # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pt1:_UISnvr:0:nv_itemNode_receivables_billing"]')))
                    # driver.find_element(By.XPATH, '//*[@id="pt1:_UISnvr:0:nv_itemNode_receivables_billing"]').click() 
                    # wait.until(EC.element_to_be_clickable((By.XPATH, '')))
                    # driver.find_element(By.XPATH, '').click() 
                    # # time.sleep(2)
                    # logger.LoggerFactory._LOGGER.info('Billing 클릭 완료')


                    # if EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOd1::msgDlg::cancel"]')) : 
                    #     # Error창 OK 클릭
                    #     wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOd1::msgDlg::cancel"]')))
                    #     time.sleep(2)
                    #     driver.find_element(By.XPATH, '//*[@id="_FOd1::msgDlg::cancel"]').click() 
                    #     logger.LoggerFactory._LOGGER.info('Error창 OK 클릭 완료')

                    #     # Cancel 클릭
                    #     wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:commandToolbarButton2"]/a')))
                    #     time.sleep(2)
                    #     driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:commandToolbarButton2"]/a').click() 
                    #     logger.LoggerFactory._LOGGER.info('Cancel 클릭 완료')

                    #     # Warning창 Yes 클릭
                    #     wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:dialogCancel::yes"]')))
                    #     time.sleep(2)
                    #     driver.find_element(By.XPATH, '//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:1:pt1:TCF:0:ap1:dialogCancel::yes"]').click() 
                    #     logger.LoggerFactory._LOGGER.info('Warning창 Yes 클릭 완료')
                    
                    # else :
                    #     driver.refresh()

                    #     # AR Transaction 이동
                    #     # 햄버거 버튼 클릭
                    #     wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pt1:_UISmmLink::icon"]')))
                    #     driver.find_element(By.XPATH, '//*[@id="pt1:_UISmmLink::icon"]').click() 
                    #     # time.sleep(2)
                    #     logger.LoggerFactory._LOGGER.info('햄버거 버튼 클릭 완료')

                    #     # Receivables 메뉴 클릭
                    #     wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pt1:_UISnvr:0:nvgpgl2_groupNode_receivables"]')))
                    #     driver.find_element(By.XPATH, '//*[@id="pt1:_UISnvr:0:nvgpgl2_groupNode_receivables"]').click() 
                    #     # time.sleep(2)
                    #     logger.LoggerFactory._LOGGER.info('Receivables 메뉴 클릭 완료')

                    #     # Billing 클릭
                    #     wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pt1:_UISnvr:0:nv_itemNode_receivables_billing"]')))
                    #     driver.find_element(By.XPATH, '//*[@id="pt1:_UISnvr:0:nv_itemNode_receivables_billing"]').click() 
                    #     # time.sleep(2)
                    #     logger.LoggerFactory._LOGGER.info('Billing 클릭 완료')


                    # MBP_Admin 고객사 > 청구내역 관리 내 업데이트 프로세스
                    # logger.LoggerFactory._LOGGER.info('세금계산서 발행 상태 업데이트 : [{}]'.format(mbp_account[0]))
                    # update_status_after_sendmail = query_config['update_status_after_writeAR']
                    # cursor.execute(update_status_after_sendmail.format(mbp_account[0], billing_year, billing_month))
                    # db_commit(con)
                    # logger.LoggerFactory._LOGGER.info('청구내역서 발송 및 청구상태 업데이트 완료')

                    # break
                    
            else :
                logger.LoggerFactory._LOGGER.info('{}번쨰 : {} 기발행 완료'.format(billStatement_row-2, company_name))


        billStatement_row = billStatement_row + 1


    # ws4 = wb['업체']

    wb.save(destination)
    logger.LoggerFactory._LOGGER.info('ERP AR_Transaction 발행 종료')


# processing_ERP_AR_Transaction(0, 0, 0, 0)