#!/usr/bin/env python

# * ADAPTED FROM https://github.com/jamesmishra/mysqldump-to-csv
# * RUN AS `python sqldump_to_csv.py dump.sql > dump.csv`

import fileinput
import csv
import sys
from tqdm import tqdm
from typing import List, Optional


__all__ = ['sqldump_to_csv']


def is_insert(line: str):
    """
    Returns true if the line begins a SQL insert statement.
    """
    return line.startswith('INSERT INTO') or False


def get_values(line: str):
    """
    Returns the portion of an INSERT statement containing values
    """
    return line.partition('` VALUES ')[2]


def values_sanity_check(values):
    """
    Ensures that values from the INSERT statement meet basic checks.
    """
    assert values
    assert values[0] == '('
    # Assertions have not been raised
    return True


def parse_values(values: str, outfile, columns: Optional[List[int]]=None):
    """
    Given a file handle and the raw values from a MySQL INSERT
    statement, write the equivalent CSV to the file

    Parameters
    ----------
    values : str
        Raw values from a MySQL INSERT statement. May contain multiple CSV lines
    outfile : file handle
        A file handle to write the CSV to
    columns : list, optional
        Which columns to keep in the CSV. If not specified, all columns are kept
    row_filter : callable, optional
        A function with signature f(row[columns]) -> bool that returns whether to keep a row
    """
    latest_row = []

    reader = csv.reader([values], delimiter=',',
                        doublequote=False,
                        escapechar='\\',
                        quotechar="'",
                        strict=True
    )

    writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
    for reader_row in reader:
        for column in reader_row:
            # If our current string is empty...
            if len(column) == 0 or column == 'NULL':
                latest_row.append(chr(0))
                continue
            # If our string starts with an open paren
            if column[0] == "(":
                # Assume that this column does not begin
                # a new row.
                new_row = False
                # If we've been filling out a row
                if len(latest_row) > 0:
                    # Check if the previous entry ended in
                    # a close paren. If so, the row we've
                    # been filling out has been COMPLETED
                    # as:
                    #    1) the previous entry ended in a )
                    #    2) the current entry starts with a (
                    if latest_row[-1][-1] == ")":
                        # Remove the close paren.
                        latest_row[-1] = latest_row[-1][:-1]
                        new_row = True
                # If we've found a new row, write it out
                # and begin our new one
                if new_row:
                    if columns is not None:
                        latest_row = [latest_row[i] for i in columns]
                    writer.writerow(latest_row)
                    latest_row = []
                # If we're beginning a new row, eliminate the
                # opening parentheses.
                if len(latest_row) == 0:
                    column = column[1:]
            # Add our column to the row we're working on.
            latest_row.append(column)
        # At the end of an INSERT statement, we'll
        # have the semicolon.
        # Make sure to remove the semicolon and
        # the close paren.
        if latest_row[-1][-2:] == ");":
            latest_row[-1] = latest_row[-1][:-2]
            if columns is not None:
                latest_row = [latest_row[i] for i in columns]
            writer.writerow(latest_row)


def sqldump_to_csv(source_file, outfile, columns: Optional[List[int]]=None):
    try:
        for line in tqdm(source_file):
            # Look for an INSERT statement and parse it.
            if is_insert(line):
                values = get_values(line)
                if values_sanity_check(values):
                    parse_values(values, outfile, columns)
    except KeyboardInterrupt:
        sys.exit(0)


def main():
    """
    Parse arguments and start the program
    """
    sqldump_to_csv(fileinput.input(openhook=fileinput.hook_encoded("iso-8859-1")), sys.stdout, columns=[0, 1, 6])


if __name__ == "__main__":
    main()

    # with open('datasets/raw/enwiki-latest-categorylinks.sql', 'r', encoding='iso-8859-1') as f: 
    #     with open('datasets\raw\enwiki-latest-categorylinks.csv', 'w', encoding='utf-8') as outfile:
    #         sqldump_to_csv(f, outfile, columns=[0, 1, 6])
