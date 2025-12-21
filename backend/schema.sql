-- PortfoLab Database Schema
-- MariaDB / MySQL

-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS portfolab DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE portfolab;

-- 역할 테이블
CREATE TABLE role (
    role_no INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL
);

-- 사용자 테이블
CREATE TABLE user (
    user_no INT AUTO_INCREMENT PRIMARY KEY,
    role_no INT NOT NULL DEFAULT 1,
    email VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(30) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    CONSTRAINT fk_user_role FOREIGN KEY (role_no) REFERENCES role(role_no)
);

-- 섹터 테이블
CREATE TABLE sector (
    sector_no INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- 종목 테이블 (ETF/주식)
CREATE TABLE stock (
    stock_no INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    market VARCHAR(20) NOT NULL DEFAULT 'KOSPI',
    sector_no INT,
    current_price INT,
    price_updated_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_stock_sector FOREIGN KEY (sector_no) REFERENCES sector(sector_no)
);

-- 가격 히스토리 테이블 (분석용)
CREATE TABLE price_history (
    history_no INT AUTO_INCREMENT PRIMARY KEY,
    stock_no INT NOT NULL,
    date DATE NOT NULL,
    close_price INT NOT NULL,
    open_price INT,
    high_price INT,
    low_price INT,
    volume BIGINT,
    CONSTRAINT fk_history_stock FOREIGN KEY (stock_no) REFERENCES stock(stock_no),
    UNIQUE KEY unique_stock_date (stock_no, date)
);

-- 포트폴리오 테이블
CREATE TABLE portfolio (
    portfolio_no INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT NOT NULL,
    name VARCHAR(40) NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_portfolio_user FOREIGN KEY (user_no) REFERENCES user(user_no)
);

-- 포트폴리오-종목 연결 테이블
CREATE TABLE portfolio_stock (
    portfolio_no INT NOT NULL,
    stock_no INT NOT NULL,
    quantity INT NOT NULL,
    avg_price INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (portfolio_no, stock_no),
    CONSTRAINT fk_ps_portfolio FOREIGN KEY (portfolio_no) REFERENCES portfolio(portfolio_no) ON DELETE CASCADE,
    CONSTRAINT fk_ps_stock FOREIGN KEY (stock_no) REFERENCES stock(stock_no)
);

-- 공지사항 테이블
CREATE TABLE notice (
    notice_no INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT NOT NULL,
    title VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_notice_user FOREIGN KEY (user_no) REFERENCES user(user_no)
);

-- 초기 데이터: 역할
INSERT INTO role (name) VALUES ('USER'), ('ADMIN');

-- 초기 데이터: 섹터
INSERT INTO sector (name) VALUES 
    ('IT/기술'),
    ('금융'),
    ('헬스케어'),
    ('소비재'),
    ('산업재'),
    ('에너지'),
    ('부동산'),
    ('채권'),
    ('원자재'),
    ('유틸리티'),
    ('커뮤니케이션');

-- 샘플 종목 데이터 (테스트용)
INSERT INTO stock (symbol, name, market, sector_no, current_price) VALUES
    ('005930', '삼성전자', 'KOSPI', 1, 71000),
    ('000660', 'SK하이닉스', 'KOSPI', 1, 178000),
    ('035420', 'NAVER', 'KOSPI', 1, 215000),
    ('035720', '카카오', 'KOSPI', 1, 42000),
    ('005380', '현대차', 'KOSPI', 5, 235000),
    ('069500', 'KODEX 200', 'ETF', NULL, 35000),
    ('102110', 'TIGER 200', 'ETF', NULL, 35500),
    ('379800', 'KODEX 미국S&P500TR', 'ETF', NULL, 15000),
    ('360750', 'TIGER 미국S&P500', 'ETF', NULL, 18000),
    ('069660', 'KOSEF 국고채10년', 'ETF', 8, 102000);

-- 인덱스 추가
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_stock_symbol ON stock(symbol);
CREATE INDEX idx_portfolio_user ON portfolio(user_no);
CREATE INDEX idx_price_history_date ON price_history(stock_no, date);
