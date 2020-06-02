CREATE TABLE books (
  id              serial primary key,
  title           varchar(100) not null,
  author          varchar(100) null,
  isbn            varchar (20) null,
  year            integer null

);


CREATE TABLE users (
  id              serial primary key,
  name            varchar(100) not null,
  surname         varchar(100) null,
  username        varchar(50) not null,
  password        varchar(32) not null,
  email           varchar(50) null,
  entryDateTime   timestamp null,
  country         varchar(50)  null,
  photo           bytea null,
  description     text null,
  birthdate       date null

);


CREATE TABLE reviews (
  id              serial primary key,
  comment  text not null,
  review_count    integer,
  average_score   numeric,
  user_id         integer references users(id),
  book_id         integer references books(id)
);
