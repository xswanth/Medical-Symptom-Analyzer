CREATE DATABASE medical_symptom_analyzer;
USE medical_symptom_analyzer;

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) DEFAULT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin TINYINT(1) DEFAULT 0,
    PRIMARY KEY (id)
);

CREATE TABLE disease_descriptions (
    dname VARCHAR(100) PRIMARY KEY,
    description TEXT,
    FOREIGN KEY (dname) REFERENCES diseases(dname)
);

create table diseases (
	dname varchar(100) primary key,
	prec1 varchar(200),
	prec2 varchar(200),
	prec3 varchar(200),
    prec4 varchar(200)
);
