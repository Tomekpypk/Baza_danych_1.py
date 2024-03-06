import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def update(conn, table, id, **kwargs):
    """Update status, begin_date, and end_date of a task
    :param conn: Connection object
    :param table: table name
    :param id: row id
    :return:
    """
    parameters = [f"{k} = ?" for k in kwargs]
    parameters = ", ".join(parameters)
    values = tuple(v for v in kwargs.values())
    values += (id, )

    sql = f''' UPDATE {table}
             SET {parameters}
             WHERE id = ?'''
    try:
        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
        print("OK")
    except sqlite3.OperationalError as e:
        print(e)

def execute_sql(conn, sql):
    """Execute SQL script
    :param conn: Connection object
    :param sql: SQL script
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)

def add_project(conn, project):
    """Add a new project to the 'projects' table
    :param conn: Connection object
    :param project: Project data
    :return: Project ID
    """
    sql = '''INSERT INTO projects(id, nazwa, start_date, end_date)
             VALUES(?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid

def create_projects_table(conn):
    """Create the 'projects' table in the database if it doesn't exist
    :param conn: Connection object
    :return:
    """
    create_projects_sql = """
    -- Table 'projects'
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        nazwa TEXT NOT NULL,
        start_date TEXT,
        end_date TEXT
    );
    """
    execute_sql(conn, create_projects_sql)

def add_task(conn, task):
    """Add a new task to the 'tasks' table
    :param conn: Connection object
    :param task: Task data
    :return: Task ID
    """
    sql = '''INSERT INTO tasks(projekt_id, nazwa, opis, status, start_date, end_date)
             VALUES(?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()
    return cur.lastrowid

def create_tasks_table(conn):
    """Create the 'tasks' table in the database if it doesn't exist
    :param conn: Connection object
    :return:
    """
    create_tasks_sql = """
    -- Table 'tasks'
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        projekt_id INTEGER NOT NULL,
        nazwa VARCHAR(250) NOT NULL,
        opis TEXT,
        status VARCHAR(15) NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        FOREIGN KEY (projekt_id) REFERENCES projects (id)
    );
    """
    execute_sql(conn, create_tasks_sql)

def display_data(conn):
    """Display data from the 'projects' and 'tasks' tables in the database
    :param conn: Connection object
    """
    try:
        c = conn.cursor()

        # Display data from the 'projects' table
        c.execute("SELECT * FROM projects")
        print("Table 'projects':")
        print(c.fetchall())

        # Display data from the 'tasks' table
        c.execute("SELECT * FROM tasks")
        print("\nTable 'tasks':")
        print(c.fetchall())

    except Error as e:
        print(e)

def select_task_by_status(conn, status):
    """Query tasks by status
    :param conn: Connection object
    :param status: Task status
    :return: Rows matching the query
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE status=?", (status,))
    rows = cur.fetchall()
    return rows

def select_all(conn, table):
    """Query all rows in the table
    :param conn: Connection object
    :param table: Table name
    :return: All rows from the table
    """
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    return rows

def select_where(conn, table, **query):
    """Query tasks from the table with data from the query dict
    :param conn: Connection object
    :param table: Table name
    :param query: Dict of attributes and values
    :return: Rows matching the query
    """
    cur = conn.cursor()
    qs = []
    values = ()
    for k, v in query.items():
        qs.append(f"{k}=?")
        values += (v,)
    q = " AND ".join(qs)
    cur.execute(f"SELECT * FROM {table} WHERE {q}", values)
    rows = cur.fetchall()
    return rows

def delete_where(conn, table, **kwargs):
    """Delete rows from the table where attributes match the provided values
    :param conn: Connection to the SQLite database
    :param table: Table name
    :param kwargs: Dict of attributes and values
    :return:
    """
    qs = []
    values = tuple()
    for k, v in kwargs.items():
        qs.append(f"{k}=?")
        values += (v,)
    q = " AND ".join(qs)

    sql = f'DELETE FROM {table} WHERE {q}'
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    print("Deleted")

def delete_all(conn, table):
    """Delete all rows from the table
    :param conn: Connection to the SQLite database
    :param table: Table name
    :return:
    """
    sql = f'DELETE FROM {table}'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print("Deleted")

if __name__ == "__main__":
    conn = create_connection("database.db")

    # Delete rows from the 'projects' table where 'nazwa' is 'Powtórka z angielskiego'
    delete_where(conn, "projects", nazwa="Powtórka z angielskiego")

    # Create 'projects' and 'tasks' tables if they don't exist
    create_projects_table(conn)
    create_tasks_table(conn)

    # Add fitness exercises
    exercises_data = [
        (1, "Klatka piersiowa", "06.03.2024 10:00", "06.03.2024 13:00"),
        (2, "Plecy", "06.03.2024 10:00", "06.03.2024 13:00"),
        (3, "Nogi", "06.03.2024 10:00", "06.03.2024 13:00"),
        (4, "Barki", "06.03.2024 10:00", "06.03.2024 13:00"),
        (5, "Biceps", "06.03.2024 10:00", "06.03.2024 13:00"),
        (6, "Triceps", "06.03.2024 10:00", "06.03.2024 13:00"),
    ]

    for exercise_data in exercises_data:
        add_project(conn, exercise_data)

    # Display data from the database
    display_data(conn)

    # Close the connection to the database
    conn.close()
