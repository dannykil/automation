-- 4) 아래 칼럼명(한글인 경우 영어로 변환)을 사용해서 postgres db에 테이블 생성하는 쿼리 작성해줘. 
-- * 테이블명은 ar_event
-- * key칼럼은 xpath_id
-- * 모두 영어 소문자 사용
-- * 테이블 생성할 때 description을 넣을 수 있으면 칼럼들의 용도를 간략히 적어서 넣어줘
-- * xpath_id, process, mapped_xpath_id, description, xpath, created_at, updated_at

CREATE TABLE ar_event (
    event_id SERIAL PRIMARY KEY,
    process VARCHAR(255),
    mapped_xpath_id VARCHAR(255),
    xpath TEXT, -- The XPath string
    description VARCHAR(255), -- Description of the XPath
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the record was created
    updated_at TIMESTAMP WITH TIME ZONE -- Timestamp when the record was last updated
);

COMMENT ON COLUMN ar_event.event_id IS 'event의 고유 식별자';
COMMENT ON COLUMN ar_event.process IS 'event를 사용하는 프로세스의 이름(ex. ar)';
COMMENT ON COLUMN ar_event.mapped_xpath_id IS 'event의 XPath 조회 시 사용되는 식별자(직접 생성하여 매핑). 아니면 프로세스 중간에 추가되면 순서를 모두 변경해야함';
COMMENT ON COLUMN ar_event.description IS 'event의 XPath에 대한 간략한 설명';
COMMENT ON COLUMN ar_event.xpath IS '실제 XPath 문자열';
COMMENT ON COLUMN ar_event.created_at IS '레코드가 생성된 시간';
COMMENT ON COLUMN ar_event.updated_at IS '레코드가 마지막으로 업데이트된 시간';