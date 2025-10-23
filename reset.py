import sqlite3

def reset():
    con = sqlite3.connect("db/trpo.db")
    cur = con.cursor()

    query1 = """PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM works;

DROP TABLE works;

CREATE TABLE works (
    work_id          INTEGER PRIMARY KEY AUTOINCREMENT
                             NOT NULL,
    work_title       TEXT    NOT NULL,
    work_type        TEXT,
    student_id       NUMERIC NOT NULL
                             REFERENCES students (student_id),
    discipline_id    NUMERIC REFERENCES disciplines (discipline_id) 
                             NOT NULL,
    publication_date TEXT    DEFAULT (2023),
    storage_location TEXT    NOT NULL,
    file        text
);

INSERT INTO works (
                      work_id,
                      work_title,
                      work_type,
                      student_id,
                      discipline_id,
                      publication_date,
                      storage_location,
                      file
                  )
                  SELECT work_id,
                         work_title,
                         work_type,
                         student_id,
                         discipline_id,
                         publication_date,
                         storage_location,
                         file
                    FROM sqlitestudio_temp_table;
DROP TABLE sqlitestudio_temp_table;
PRAGMA foreign_keys = 1;"""
    query2 = """PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM students;

DROP TABLE students;

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT
                       NOT NULL,
    first_name TEXT,
    last_name  TEXT,
    [group]    TEXT    DEFAULT [М3О-310Б-21]
                       NOT NULL
);

INSERT INTO students (
                         student_id,
                         first_name,
                         last_name,
                         [group]
                     )
                     SELECT student_id,
                            first_name,
                            last_name,
                            "group"
                       FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

PRAGMA foreign_keys = 1;
"""
    query3 = """PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM disciplines;

DROP TABLE disciplines;

CREATE TABLE disciplines (
    discipline_id   INTEGER PRIMARY KEY AUTOINCREMENT
                            NOT NULL,
    discipline_name TEXT    NOT NULL
);

INSERT INTO disciplines (
                            discipline_id,
                            discipline_name
                        )
                        SELECT discipline_id,
                               discipline_name
                          FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

PRAGMA foreign_keys = 1;
"""
    cur.executescript(query1)
    con.commit()
    cur.executescript(query2)
    con.commit()
    cur.executescript(query3)
    con.commit()
    con.close()

def fill():
    con = sqlite3.connect("db/trpo.db")
    cur = con.cursor()

    query1 = """INSERT INTO disciplines (discipline_name)
            VALUES 
            ('Дисциплина 1'),
            ('Дисциплина 2'),
            ('Дисциплина 3'),
            ('Дисциплина 4'),
            ('Дисциплина 5'),
            ('Дисциплина 6'),
            ('Дисциплина 7'),
            ('Дисциплина 8'),
            ('Дисциплина 9'),
            ('Дисциплина 10');"""

    query2 = """INSERT INTO students (first_name, last_name, [group])
                VALUES 
                ('Иван', 'Иванов', 'М3О-310Б-21'),
                ('Петр', 'Петров', 'М3О-311Б-21'),
                ('Мария', 'Сидорова', 'М3О-309Б-21'),
                ('Анна', 'Козлова', 'М3О-310Б-21'),
                ('Денис', 'Смирнов', 'М3О-309Б-21'),
                ('Елена', 'Попова', 'М3О-319Б-21'),
                ('Сергей', 'Морозов', 'М3О-310Б-21'),
                ('Александра', 'Волкова', 'М3О-319Б-21'),
                ('Владимир', 'Кузнецов', 'М3О-309Б-21'),
                ('Ольга', 'Борисова', 'М3О-311Б-21');
                            """

    query3 = """INSERT INTO works (work_title, work_type, student_id, discipline_id, publication_date, storage_location, file)
                VALUES 
                ('Работа 1', 'Тип работы 1', 1, 1, '2022', 'Кафедра 1', 'works/work.txt'),
                ('Работа 2', 'Тип работы 2', 2, 2, '2023', 'Кафедра 2', 'works/work.txt'),
                ('Работа 3', 'Тип работы 3', 3, 3, '2021', 'Кафедра 3', 'works/work.txt'),
                ('Работа 4', 'Тип работы 4', 4, 4, '2020', 'Кафедра 4', 'works/work.txt'),
                ('Работа 5', 'Тип работы 5', 5, 5, '2023', 'Кафедра 5', 'works/work.txt'),
                ('Работа 6', 'Тип работы 6', 6, 6, '2022', 'Кафедра 6', 'works/work.txt'),
                ('Работа 7', 'Тип работы 7', 7, 7, '2019', 'Кафедра 7', 'works/work.txt'),
                ('Работа 8', 'Тип работы 8', 8, 8, '2023', 'Кафедра 8', 'works/work.txt'),
                ('Работа 9', 'Тип работы 9', 9, 9, '2021', 'Кафедра 9', 'works/work.txt'),
                ('Работа 10', 'Тип работы 10', 10, 10, '2020', 'Кафедра 10', 'works/work.txt');"""

    cur.executescript(query1)
    con.commit()
    cur.executescript(query2)
    con.commit()
    cur.executescript(query3)
    con.commit()

    con.close()

def delete():
    con = sqlite3.connect("db/trpo.db")
    cur = con.cursor()

    query1 = """delete from works;
                delete from students;
                delete from disciplines;"""
    cur.executescript(query1)
    con.commit()
    con.close()

delete()
reset()
fill()