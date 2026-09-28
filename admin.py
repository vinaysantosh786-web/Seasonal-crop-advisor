import mysql.connector
from werkzeug.security import generate_password_hash
from getpass import getpass


# ============================================
# MYSQL CONNECTION
# ============================================

connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="Vinay@53",
    database="seasonal_crop_advisor"
)


cursor = connection.cursor()


# ============================================
# ADMIN DETAILS
# ============================================

username = input("Enter admin username: ")

password = getpass("Enter admin password: ")

confirm_password = getpass("Confirm admin password: ")


if password != confirm_password:

    print("Passwords do not match.")

    cursor.close()
    connection.close()

    exit()


# ============================================
# HASH PASSWORD
# ============================================

password_hash = generate_password_hash(password)


# ============================================
# INSERT ADMIN
# ============================================

sql = """
INSERT INTO admins
(username, password_hash)
VALUES
(%s, %s)
"""


cursor.execute(
    sql,
    (username, password_hash)
)


connection.commit()


print()
print("================================")
print("Admin account created successfully!")
print("Username:", username)
print("================================")


cursor.close()
connection.close()