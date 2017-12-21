drop table if exists BookCatalogue;
create table BookCatalogue (
    id integer primary key autoincrement,
    user_id integer not null,
    title text not null,
    author text not null,
    pgcnt integer not null,
    avgrating real not null,
    thumbnail integer not null
);

drop table if exists Users;
create table Users (
    id integer primary key autoincrement,
    username text not null,
    password text not null
);

insert into Users (username, password) values ('admin', 'password');
insert into Users (username, password) values ('user', 'password');
insert into Users (username, password) values ('book', 'password');
