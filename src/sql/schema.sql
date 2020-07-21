drop table if exists articles;
create table articles (
    id integer primary key autoincrement,
    titre text not null,
    contenu text not null
)