import mysql.connector
import copy
# INFO for MYSQL
mysqlhost = ''
mysqluser = ''
mysqlpassword = ''
mysqldatabase = ''


def findname(result,res):
	"""find a record according to name"""
	targetname = input("Please input a name:")
	nameresult = []
	for i in range(len(result)):
		if res[i][0] == targetname:
			nameresult.append(result[i])
	if len(nameresult) == 0:
		print("No record found!")
	else:
		print("Found {} matching records".format(len(nameresult)))
		for i in nameresult:
			print(i)

def findkeywords(res,result):
	"""find a record according to keyword"""
	targetname = input("Please input a keyword:")
	keyresult = []
	for i in range(len(result)):
		if res[i][3] == targetname:
			keyresult.append(result[i])
	if len(keyresult) == 0:
		print("No record found!")
	else:
		print("Found {} matching records".format(len(keyresult)))
		for i in keyresult:
			print(i)

def most_common(lst):
	"""find most frequent item in a list"""
	return max(set(lst), key=lst.count)


def info_report(result,res):
	"""report basic information"""
	users = []
	oss = []
	topic = []
	number = []
	for i in range(len(result)):
		users.append(result[i][0])
		oss.append(result[i][2])
		topic.append(result[i][3])
		number.append(int(result[i][4]))
	pass
	print("The most frequent user is {}".format(most_common(users)))
	print("The most frequent user os is {}".format(most_common(oss)))
	print("The most frequent Topic {}".format(most_common(topic)))
	print("The average of picture per feed is {}".format(sum(number)/len(result)))

def addon(res):
	"""add title to records"""
	for i in range(len(res)):
		res[i] = list(res[i])
	for i in range(len(res)):
		res[i][0] = "usename: " + str(res[i][0])
		res[i][1] = "record time: " + str(res[i][1])
		res[i][2] = "operating system: " + str(res[i][2])
		res[i][3] = "Search keyword: " + str(res[i][3])
		res[i][4] = "Number of pictures: " + str(res[i][4])
		if len(str(res[i][5]))>100:
			res[i][5] = "Image URL" + str(res[i][5][:100] + '...')
		else:
			res[i][5] = "Image URL" + str(res[i][5])
		if len(str(res[i][6]))>100:
			res[i][6] = "Image URL" + str(res[i][6][:100] + '...')
		else:
			res[i][6] = "Image URL" + str(res[i][6])
	return res


def main():
	"""main function"""
	try:
		db = mysql.connector.connect(
			host = mysqlhost,
			user = mysqluser,
			password = mysqlpassword,
			database = mysqldatabase
		)
		print('mysql login success')
	except:
		exit(1)
	cursor = db.cursor()
	# cursor.execute("USE sql9267564")
	sql = "SELECT * FROM project1_log ORDER BY time"
	cursor.execute(sql)
	result = list(cursor.fetchall())
	res = result[:]
	res = addon(res)
	print("{} records found!".format(len(result)))
	info_report(result,res)
	order = input("Enter u for username search, enter k for keyword search, others to exit:")
	if order == "u":
		findname(result,res)
	elif order == "k":
		findkeywords(result,res)
	else:
		exit(0)

if __name__ == '__main__':
	main()