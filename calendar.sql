CREATE TABLE calendars (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_public boolean,
    created_at timestamp without time zone,
    owner_id integer NOT NULL
);

CREATE TABLE events (
    id integer NOT NULL,
    title character varying(50) NOT NULL,
    description text,
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone NOT NULL,
    location character varying(100),
    bg_color character varying(7),
    txt_color character varying(7),
    all_day boolean,
    created_at timestamp without time zone,
    calendar_id integer NOT NULL,
    creator_id integer NOT NULL
);

CREATE TABLE users (
    id integer NOT NULL,
    email character varying(50) NOT NULL,
    password character varying(100) NOT NULL,
    f_name character varying(40) NOT NULL,
    l_name character varying(40) NOT NULL,
    created_at timestamp without time zone
);
