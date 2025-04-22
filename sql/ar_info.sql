-- 1) 아래 칼럼명(한글인 경우 영어로 변환)을 사용해서 postgres db에 테이블 생성하는 쿼리 작성해줘. 
-- * 테이블명은 ar_info
-- * key칼럼은 ar_info_id
-- * 모두 영어 소문자 사용
-- job_id ar_info_id Transaction_Date	Bill_to_Name	Account_Number	Transaction_Number	Payment_Terms	Structured_Payment_Reference	세무증빙유형	역발행여부

CREATE TABLE IF NOT EXISTS ar_info (
    job_id INTEGER,
    ar_info_id SERIAL PRIMARY KEY,
    transaction_date DATE,
    bill_to_name VARCHAR(255),
    account_number VARCHAR(255),
    transaction_number VARCHAR(255),
    payment_terms VARCHAR(255),
    structured_payment_reference VARCHAR(255),
    tax_proof_type VARCHAR(255),
    reverse_issue_yn VARCHAR(10)
);