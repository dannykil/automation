CREATE TABLE IF NOT EXISTS user_info (
    id SERIAL PRIMARY KEY, -- 자동 증가하는 고유 ID (추가)
    user_name VARCHAR(255),
    account VARCHAR(255) UNIQUE, -- account를 고유 키로 설정 (유지)
    password VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 생성 일자 (추가)
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 업데이트 일자 (추가)
    -- installed CHAR(1),
    filepath TEXT,
    filename VARCHAR(255),
    restart_count INTEGER,
    display_yn CHAR(1)
);