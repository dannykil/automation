-- 3) 아래 칼럼명(한글인 경우 영어로 변환)을 사용해서 postgres db에 테이블 생성하는 쿼리 작성해줘. 
-- * 테이블명은 ar_job
-- * key칼럼은 job_id
-- * 모두 영어 소문자 사용
-- * 테이블 생성할 때 description을 넣을 수 있으면 칼럼들의 용도를 간략히 적어서 넣어줘
-- * job_id title user_name account created_at updated_at complete_yn

CREATE TABLE IF NOT EXISTS ar_job (
    job_id SERIAL PRIMARY KEY,
    title VARCHAR(255), -- 작업 제목
    user_name VARCHAR(255), -- 작업 요청 사용자 이름
    account VARCHAR(255), -- 관련 계정 정보
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 생성 일시
    updated_at TIMESTAMP WITH TIME ZONE, -- 수정 일시
    complete_yn VARCHAR(1) -- 완료 여부 (Y/N)
);

COMMENT ON COLUMN ar_job.job_id IS '작업 ID (기본 키)';
COMMENT ON COLUMN ar_job.title IS '작업 제목';
COMMENT ON COLUMN ar_job.user_name IS '작업 요청 사용자 이름';
COMMENT ON COLUMN ar_job.account IS '관련 계정 정보';
COMMENT ON COLUMN ar_job.created_at IS '레코드 생성 일시 (자동 생성)';
COMMENT ON COLUMN ar_job.updated_at IS '레코드 수정 일시';
COMMENT ON COLUMN ar_job.complete_yn IS '작업 완료 여부 (Y: 완료, N: 미완료)';