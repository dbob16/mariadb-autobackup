import os
import mariadb as mdb
import datetime as dt
from configparser import ConfigParser
from getpass import getpass

config = ConfigParser()

def main():
    startup()
    configdict = {
        "host": config["default"]["host"],
        "port": int(config["default"]["port"]),
        "user": config["default"]["user"],
        "password": config["default"]["password"],
        "database": config["default"]["database"]
    }
    date = dt.date.today()
    time = dt.datetime.now()
    time = time.strftime("%H%M%S")
    foldername = f"{date}_{time}"
    os.mkdir(f"{foldername}")
    os.chdir(f"{foldername}")
    global conn
    conn = mdb.connect(**configdict)
    global cur
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = [table[0] for table in cur.fetchall()]
    for table in tables:
        print(table)
        cur.execute(f"SHOW COLUMNS FROM {config["default"]["database"]}.{table}")
        licolumn = [column[0] for column in cur.fetchall()]
        columnstr = ""
        for column in licolumn:
            columnstr += f"{column}, "
        columnstr = columnstr[:-2]
        with open(f"{table}.csv", "w") as file:
            file.write(f"{columnstr}\n")
        cur.execute(f"SELECT * FROM {table}")
        rows = [row for row in cur.fetchall()]
        for row in rows:
            rowstr = ""
            for field in row:
                if field == "None":
                    field = ""
                rowstr += f"{field}, "
            rowstr = rowstr[:-2]
            with open(f"{table}.csv", "a") as file:
                file.write(f"{rowstr}\n")

def startup():
    if os.path.isfile('config.ini'):
        config.read('config.ini')
    else:
        hostname = input("Enter hostname here: [default = localhost] ")
        if hostname == "":
            hostname = "localhost"
        port = input("Enter port here: [default = 3306] ")
        if port == "":
            port = "3306"
        try:
            port = int(port)
        except:
            string = "Only whole numbers accepted for port."
            print(string)
            write2log(string)
        username = input("Enter username here: ")
        if username == "":
            string = "Username cannot be blank."
            print(string)
            write2log(string)
            exit()
        password = getpass("Enter password here: ")
        database = input("Enter database name here: ")
        try:
            mdb.connect(
                host=hostname,
                port=port,
                user=username,
                password=password,
                database=database
            )
        except Exception as e:
            print(e)
            write2log(e)
            exit()
        config["default"] = {
            "host": hostname,
            "port": port,
            "user": username,
            "password": password,
            "database": database
        }
        with open("config.ini", "w") as file:
            config.write(file)

def write2log(statement):
    date = dt.date.today()
    time = dt.datetime.now()
    time = time.strftime("%H:%M:%S")
    with open("errors.log", "a") as file:
        file.write(f"{date} {time} - {statement}\n")

if __name__ == "__main__":
    main()