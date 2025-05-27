-- prompt:
-- 현재 postgre DB를 사용하고 있는데 아래 칼럼을 가진 테이블을 생성하는 쿼리 만들어줘.
-- 1) table name : boards
-- 2) table columnes : 
-- id : auto increment
-- title : varchar(255)
-- created_at : timestamp
-- updated_at : timestamp
-- use_yn : char(1)

-- prompt:
-- 현재 postgre DB를 사용하고 있는데 아래 칼럼을 가진 테이블을 생성하는 쿼리 만들어줘.
-- id : auto increment
-- board_id : int
-- filename : varchar(255)
-- filetype : varchar(255)
-- filepath : varchar(255)
-- filesize : int

-- prompt:
-- 아래 테이블은 업로드된 파일들의 정보를 저장하기 위한 테이블이야. 여기에 이전에 너가 개발해준 파이썬 백엔드 소스코드에서 DB Insert까지 할 수 있도록 수정해줄 수 있어?
CREATE TABLE boards (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255)
);

-- prompt:
-- postgres db 테이블에서 analysis_yn라는 이름으로 char(1) 칼럼을 추가해줘. default는 'N'으로 해줘.
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    board_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    filetype VARCHAR(255),
    filepath VARCHAR(255) NOT NULL,
    filesize INTEGER NOT NULL
);

-- prompt:
-- 전체 구조를 바꿔야 할 것 같은데 수정해야할 파일 3개를 너한테 순서대로 전달할테니 이해했는지 대답해줄 수 있어?

-- prompt:
-- 1) css 파일 전달
-- 이해됐으면 됐다고 대답해줘. 안그러면 내가 너한테 수정을 부탁 할 수 없어.

-- prompt:
-- 2) 리액트 코드 전달
-- 이해됐으면 됐다고 대답해줘. 안그러면 내가 너한테 수정을 부탁 할 수 없어.

-- prompt:
-- 3) 백엔드 코드 전달
-- 이해됐으면 됐다고 대답해줘. 안그러면 내가 너한테 수정을 부탁 할 수 없어.

-- prompt:
-- 좋아, 너가 이해하기 편하도록 순서대로 Instruction을 구성해봤어. 아래의 내용을 보고 순서대로 작업해줘.

-- 목표 : 현재는 파일 업로드 버튼을 클릭하면 GCS에 업로드되는데 '저장' 버튼을 클릭하면 업로드되도록 수정
-- 순서 : 
-- 1. 프론트엔드
-- 1) 제목이 입력되어야 저장 가능(현재 유지)
-- 2) 파일은 지금처럼 한개씩 업로드하고 '업로드' 버튼은 제거(저정 버튼 클릭 시 업로드)
-- 3) 드래그 앤 드랍으로 파일을 올리면 아래 업로드할 파일 목록 보여주기(현재 유지 - 디자인을 업로드하는 컴포넌트와 통일할 수 있으면 더 좋음)

-- 2. 백엔드
-- 1) upload_file() 수정
-- boards 테이블에 제목과 파일 정보, 그리고 현재시간을 insert하는 쿼리 추가(update_at은 현재시간으로)
-- boards 테이블에 insert가 성공하면 files 테이블에 파일 정보 insert
-- files 테이블에 insert가 성공하면 파일명들을 alert을 통해 보여주고(3초간) 새로 만들(아래) 컴포넌트로 redirect

-- 3. 업로드된 파일 목록을 보여주는 컴포넌트 추가(css파일)
-- 이건 현재 css파일에 있는 디자인과 가능한 유사하게 만들어줘.