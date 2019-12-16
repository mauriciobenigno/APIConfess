import pymysql

# Open database connection
db = pymysql.connect("us-cdbr-iron-east-05.cleardb.net","bc3024c3520660","41d897e1","heroku_5b193e052a7ad86" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

# execute SQL query using execute() method.
cursor.execute("SELECT VERSION()")

# Fetch a single row using fetchone() method.
data = cursor.fetchone()
print ("Database version : %s " % data)

# disconnect from server
db.close()
