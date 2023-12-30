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


def parse_values(values: str):
    """
    Given a file handle and the raw values from a MySQL INSERT
    statement, write the equivalent CSV to the file
    """
    latest_row = []

    reader = csv.reader([values], delimiter=',',
                        doublequote=False,
                        escapechar='\\',
                        quotechar="'",
                        strict=True
    )

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
                    yield latest_row
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
            yield latest_row


def parse_sql_file(file, row_filter=None, columns: Optional[List[int]]=None):
    """
    Given a file handle of a MySQL dump file, generate rows

    Parameters
    ----------
    file : file handle
        File handle of MySQL dump file
    row_filter : function, optional
        Function which takes a row and returns True if it should be kept
    columns : list, optional
        Which columns to keep in the CSV. If not specified, all columns are kept
    """
    for line in file:
        if is_insert(line):
            values = get_values(line)
            if values_sanity_check(values):
                for row in parse_values(values):
                    if row_filter is None or row_filter(row):
                        if columns is not None:
                            row = [row[i] for i in columns]
                        yield row


def sqldump_to_csv(source_file, outfile, row_filter=None, columns: Optional[List[int]]=None):
    """
    Parameters
    ----------
    columns : list, optional
        Which columns to keep in the CSV. If not specified, all columns are kept
    """
    try:
        writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
        for row in parse_sql_file(source_file, row_filter, columns):
            writer.writerow(row)
    except KeyboardInterrupt:
        quit(0)


def sqldump_to_csv_path(source_path: str, outpath: str, row_filter=None, columns=None, source_encoding='iso-8859-1', out_encoding='utf-8'):
    with open(source_path, 'r', encoding=source_encoding) as infile:
        with open(outpath, 'w', encoding=out_encoding) as outfile:
            sqldump_to_csv(infile, outfile, row_filter, columns)


def peak_file(path: str, rows=5, start=0):
    assert rows > 0 and start >= 0, f"Invalid rows ({rows}) or start ({start})"
    with open(path, 'r') as f:
        for i, line in enumerate(f):
            if start < i < start + rows:
                print(line)
            elif i > start + rows:
                break


def peak_sql(path: str, rows=5, start=0, **kwargs):
    assert rows > 0 and start >= 0, f"Invalid rows ({rows}) or start ({start})"
    with open(path, 'r', encoding="iso-8859-1") as f:
        for i, line in enumerate(parse_sql_file(f, **kwargs)):
            if start < i < start + rows:
                print(line)
            elif i > start + rows:
                break


def main():
    """
    Parse arguments and start the program
    """
    sqldump_to_csv(fileinput.input(openhook=fileinput.hook_encoded("iso-8859-1")), sys.stdout, columns=[0, 1, 6])


if __name__ == "__main__":
    main()
    # peak_file('datasets/raw/enwiki-categories.tsv')
