-- DROP TABLE user_profile;

CREATE TABLE IF NOT EXISTS user (
        id INTEGER NOT NULL,
        username VARCHAR(80) NOT NULL,
        password_hash VARCHAR(128) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (username)
);

CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    full_name TEXT,
    age NUMERIC,
    city TEXT,
    state TEXT,
    picture text,
    bio TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);


