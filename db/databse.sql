ALTER SCHEMA public OWNER TO switches_user;
GRANT ALL ON SCHEMA public TO switches_user;

CREATE TABLE prueba (id serial primary key);
DROP TABLE prueba;