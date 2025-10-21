"""Deliberately vulnerable SQL injection example for CodeQL testing.

DO NOT USE THIS CODE IN PRODUCTION - IT IS INTENTIONALLY INSECURE.
"""

import sqlite3


def vulnerable_query(user_input):
    """
    Vulnerable function that demonstrates SQL injection vulnerability.

    This function is intentionally insecure and should trigger CodeQL alerts.
    It constructs SQL queries using string formatting with user input,
    making it vulnerable to SQL injection attacks.

    Args:
        user_input: Unsanitized user input that will be directly interpolated into SQL

    Returns
        Query results from the database
    """
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    # VULNERABILITY: SQL injection via string formatting
    # This will be detected by CodeQL as CWE-89: SQL Injection
    cursor.execute(f"SELECT * FROM users WHERE name = '{user_input}'")

    results = cursor.fetchall()
    conn.close()
    return results


def another_vulnerable_query(table_name, user_id):
    """
    Another vulnerable function with SQL injection via concatenation.

    Args:
        table_name: User-provided table name
        user_id: User-provided ID value

    Returns
        Query results
    """
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    # VULNERABILITY: SQL injection via string concatenation
    query = "SELECT * FROM " + table_name + " WHERE id = " + str(user_id)
    cursor.execute(query)

    results = cursor.fetchall()
    conn.close()
    return results


def vulnerable_update(user_id, new_email):
    """
    Vulnerable UPDATE query demonstrating SQL injection in modification operations.

    Args:
        user_id: User ID from untrusted source
        new_email: New email address from untrusted source

    Returns
        Number of rows affected
    """
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    # VULNERABILITY: SQL injection in UPDATE statement
    cursor.execute(f"UPDATE users SET email = '{new_email}' WHERE id = {user_id}")

    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    print("This file contains deliberately vulnerable code for testing purposes.")
    print("It should trigger CodeQL security alerts for SQL injection (CWE-89).")
