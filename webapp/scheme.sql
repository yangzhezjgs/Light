drop database if exists my_user;

create database my_user;

use my_user;

create table users (
    `id` varchar(50) not null,
    `passwd` varchar(50) not null,
    `name` varchar(50) not null,
    primary key (`id`)
) engine=innodb default charset=utf8;
