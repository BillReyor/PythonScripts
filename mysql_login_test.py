#usage: python mysql_login_test.py -host_file hosts.txt -user_file users.txt -password_file passwords.txt

import argparse
import sys
import pymysql

def test_mysql_login(host, user, password, database='your_database_name'):
    """
    Test MySQL login credentials and save successful credentials to a file.

    :param host: MySQL database host IP address
    :param user: MySQL database username
    :param password: MySQL database password
    :param database: MySQL database name (optional)
    """
    try:
        connection = pymysql.connect(host=host, user=user, password=password, database=database)
        print(f'Successfully logged in as {user}.')

        with open('cred.txt', 'a') as f:
            f.write(f'Host: {host}\nUser: {user}\nPassword: {password}\n\n')

        connection.close()

    except pymysql.Error as e:
        print(f'Error: {e}')

def read_file(file_path):
    """
    Read a file and return its content as a list of lines.

    :param file_path: Path to the file
    :return: List of lines in the file
    """
    with open(file_path, 'r') as file:
        content = file.read().splitlines()
    return content

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test MySQL login credentials.')
    parser.add_argument('-host_file', help='File with MySQL database host IP addresses', type=str)
    parser.add_argument('-user_file', help='File with MySQL database usernames', type=str)
    parser.add_argument('-password_file', help='File with MySQL database passwords', type=str)

    args = parser.parse_args()

    if args.host_file:
        hosts = read_file(args.host_file)
    else:
        print('Please provide a file with a list of hosts.')
        sys.exit(1)

    if args.user_file:
        users = read_file(args.user_file)
    else:
        print('Please provide a file with a list of usernames.')
        sys.exit(1)

    if args.password_file:
        passwords = read_file(args.password_file)
    else:
        print('Please provide a file with a list of passwords.')
        sys.exit(1)

    for host in hosts:
        for user in users:
            for password in passwords:
                test_mysql_login(host.strip(), user.strip(), password.strip())
