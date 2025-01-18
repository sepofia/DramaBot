CREATE TABLE tv_series
(
    id                  INTEGER PRIMARY KEY,
    name_movie          VARCHAR(100),
    kp_rating           NUMERIC,
    imdb_rating         NUMERIC,
    production_year     INTEGER,
    link                VARCHAR(100),
    description         TEXT,
    all_countries       VARCHAR(200),
    all_genres          VARCHAR(200)
);

-- DROP TABLE tv_series;

CREATE TABLE countries
(
    id              INTEGER PRIMARY KEY,
    FOREIGN KEY (id) REFERENCES tv_series(id),
    south_korea     BOOLEAN,
    china           BOOLEAN,
    japan           BOOLEAN
);

-- DROP TABLE countries;

CREATE TABLE genres
(
    id              INTEGER PRIMARY KEY,
    FOREIGN KEY (id) REFERENCES tv_series(id),
    biography       BOOLEAN,
    action_movie    BOOLEAN,
    military        BOOLEAN,
    detective       BOOLEAN,
    drama           BOOLEAN,
    history         BOOLEAN,
    comedy          BOOLEAN,
    criminal        BOOLEAN,
    melodrama       BOOLEAN,
    music           BOOLEAN,
    adventures      BOOLEAN,
    thriller        BOOLEAN,
    horrors         BOOLEAN,
    fantastic       BOOLEAN,
    fantasy         BOOLEAN
);

-- DROP TABLE genres;
