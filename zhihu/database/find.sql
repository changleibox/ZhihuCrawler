# DROP DATABASE IF EXISTS zhihu;

CREATE DATABASE IF NOT EXISTS zhihu
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;

USE zhihu;

SET NAMES utf8mb4;

DROP TABLE IF EXISTS Find;

CREATE TABLE Find (
  id        VARCHAR(100) NOT NULL,
  content   LONGTEXT     NOT NULL,
  timestamp LONG         NOT NULL
  COMMENT '爬虫更新时间',
  PRIMARY KEY (id)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;