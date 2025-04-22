-- 2) 아래 칼럼명(한글인 경우 영어로 변환)을 사용해서 postgres db에 테이블 생성하는 쿼리 작성해줘. 
-- * 테이블명은 ar_info_detail
-- * key칼럼은 ar_info_detail_id
-- * 모두 영어 소문자 사용
-- ar_info_detail_id ar_info_id Memo_Line	Description	Quantity	 Unit)Price	 부가세 	 총청구금액	Tax_Classification	Cost_Center	Account	Project	AR발행여부

CREATE TABLE IF NOT EXISTS ar_info_detail (
    -- ar_info_detail_id INTEGER PRIMARY KEY,
    ar_info_detail_id SERIAL PRIMARY KEY,
    ar_info_id INTEGER,
    memo_line VARCHAR(255),
    description TEXT,
    quantity NUMERIC,
    unit_price NUMERIC,
    vat NUMERIC,
    total_amount NUMERIC,
    tax_classification VARCHAR(255),
    cost_center VARCHAR(255),
    account VARCHAR(255),
    project VARCHAR(255),
    ar_issued_yn VARCHAR(10)
);