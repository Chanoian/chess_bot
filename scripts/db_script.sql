gcloud sql connect sql-instance
use chess_games; (This is the database name)
show tables;
describe chess_games.game (game is the table name)


create table demo_tbl(
   id INT NOT NULL AUTO_INCREMENT,
   session_url VARCHAR(200) NOT NULL,
   board VARBINARY(500) NOT NULL,
   player_color VARCHAR(20) NOT NULL,
   engine_level INT NOT NULL,
   PRIMARY KEY ( id )
);