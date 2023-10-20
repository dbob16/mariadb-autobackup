import mariadb as mdb # pip install mariadb
import csv
import os
import datetime as dt
from configparser import ConfigParser
from getpass import getpass

# Creates the config object
config = ConfigParser()

def main():
    # Runs the startup sequence
    # Which triggers setup or reads the config from settings.ini
    startup()
    # Initializes the default library into dictionaries
    connconf = config["default"]
    connparam = {
        "host": connconf["host"],
        "port": int(connconf["port"]),
        "user": connconf["user"],
        "password": connconf["password"],
        "database": connconf["database"]
    }
    # Creates the connection and cursor objects
    global conn
    conn = mdb.connect(**connparam)
    cur = conn.cursor()
    # creates object and variable for the current date and time
    timenow = dt.datetime.now()
    timenow_f = timenow.strftime("%Y-%m-%d-%H%M%S")
    # Makes and sets current folder as current date and time
    os.mkdir(timenow_f)
    os.chdir(timenow_f)
    # Lists all tables user has access to.
    cur.execute("SHOW TABLES")
    # List comprehension for grabbing just the table names
    tablelist = [table[0] for table in cur.fetchall()]
    # Iteration into the tablelist
    for table in tablelist:
        # Creates a new csv file
        with open(f"{table}.csv", "w", newline='') as csvfile:
            # Shows all columns
            cur.execute(f"SHOW COLUMNS FROM {table}")
            # List comprehension for grabbing just the column names
            column_list = [column[0] for column in cur.fetchall()]
            # Creates the writer object to write to the csv file
            writer = csv.writer(csvfile)
            # Writes the header row
            writer.writerow(column_list)
            # Collects all rows
            cur.execute(f"SELECT * FROM {table}")
            # Creates object with results
            results = cur.fetchall()
            # Writes the results to csv rows
            writer.writerows(results)

def startup():
    # Checks for settings.ini file
    if os.path.isfile("settings.ini"):
        # Reads from settings.ini file if check is passed
        config.read("settings.ini")
    # Otherwise, setup sequence starts
    else:
        #Asks for information and applies defaults for blanks
        hostname = input("Insert hostname here: [default = localhost] ")
        if hostname == "":
            hostname = "localhost"
        port = input("Insert port here: [default = 3306]")
        if port == "":
            port = "3306"
        try:
            port = int(port)
        except:
            err_str = "Port needs to be a whole number."
            print(err_str)
            write2log(err_str)
            exit()
        user = input("Insert username here: ")
        password = getpass("Insert password here: ")
        database = input("Insert database here: ")
        # Creates dictionary of settings
        condict = {
            "host": hostname,
            "port": port,
            "user": user,
            "password": password,
            "database": database
        }
        # Adds dictionary to config object
        config["default"] = condict
        # Tries the credentials provided
        try:
            mdb.connect(**condict)
        except:
            err_str = "Connection not successful. Please check all credentials and try again."
            print(err_str)
            write2log(err_str)
            exit()
        # If the above check is passed, writes the config file
        with open("settings.ini", "w") as file:
            config.write(file)

def write2log(statement):
    with open("error.log", "a") as file:
        timenow = dt.datetime.now()
        file.write(f"{timenow.strftime('%Y-%m-%d %H:%M:%S')}: {statement}")

if __name__ == "__main__":
    main()