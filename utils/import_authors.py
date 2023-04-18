import sqlite3
import argparse
import os
import sys
import pandas as pd


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".

    FROM: https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def import_authors(*, excel_path: str, db_path: str) -> int:
    connection = sqlite3.connect(db_path)
    c = connection.cursor()

    c.execute("""DROP TABLE IF EXISTS authors""")

    df = pd.read_excel(excel_path)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df.to_sql(name="authors", con=connection)

    result = c.execute("""SELECT COUNT(*) FROM authors""")
    authors = result.fetchone()[0]

    c.close()
    connection.commit()
    connection.close()
    return authors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="AuthorToDB",
        description="Import an Excel file with authors into a sqlite database",
    )
    parser.add_argument(
        "-db",
        "--database",
        help="Absolute path to the sqlite database file",
        required=True,
    )
    parser.add_argument(
        "-f", "--file", help="Absolute path to the excel file", required=True
    )

    args = parser.parse_args()

    database_path = args.database
    excel_path = args.file

    if not os.path.exists(excel_path):
        print("Excel file does not exists")
        exit(-1)
    if not os.path.exists(database_path):
        print("Databse file does not exists")
        exit(-1)
    if not query_yes_no(
        question="This will delete all existing data. Continue?", default="no"
    ):
        exit(0)
    number_of_authors = import_authors(excel_path=excel_path, db_path=database_path)
    print(f"Inserted {number_of_authors} authors")
