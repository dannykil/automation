# 사용법

# 특이사항

# 개발 시 XPATH를 설정하는 방법 4가지

# 1)

# Exception 정리

- 가상환경 사용법

1. 가상환경 조회
   conda info --envs
   conda env list

2. 가상환경 생성
   conda create -n 8page python=3.12

3. 가상환경 활성화
   conda activate 8page

4. 가상환경 비활성화
   conda deactivate

5. 가상환경 삭제
   conda remove -n 8page --all

6. 가상환경 내 패키지 설치
   conda install <패키지명>
   pip install -r requirements.txt

7. 가상환경 내 설치된 패키지 추출
   pip freeze > requirements.txt

CREATE TABLE GeneralInformation (
id SERIAL PRIMARY KEY,
BusinessUnit VARCHAR(255),
TransactionSource VARCHAR(255),
TransactionType VARCHAR(255),
TransactionDate DATE,
AccountingDate DATE,
TransactionNumber VARCHAR(255),
BillToName VARCHAR(255),
PaymentTerms VARCHAR(255),
StructuredPaymentReference VARCHAR(255),
TaxProofType VARCHAR(255),
BusinessNumber VARCHAR(255),
ReverseIssue CHAR(1),
Email VARCHAR(255),
RegisterYN CHAR(1),
InvoiceDetails JSONB
);

CREATE TABLE InvoiceDetails (
id SERIAL PRIMARY KEY,
GeneralInformation_id INTEGER REFERENCES GeneralInformation(id), -- 외래 키 컬럼 추가
MemoLine VARCHAR(255),
Description VARCHAR(255),
Quantity INTEGER,
UnitPrice DECIMAL,
TaxClassification VARCHAR(255),
TBC VARCHAR(255),
CostCenter VARCHAR(255),
Account INTEGER,
Project VARCHAR(255)
);

CREATE TABLE UserInfo (
id SERIAL PRIMARY KEY,
user VARCHAR(255),
account VARCHAR(255) UNIQUE NOT NULL,
password VARCHAR(255) NOT NULL,
installed CHAR(1),
filepath VARCHAR(255),
filename VARCHAR(255),
reStartCount INTEGER,
displayYN CHAR(1)
);
