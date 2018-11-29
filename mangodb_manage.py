from pymongo import MongoClient
MONGODB_URI = ""


def findname(result):
	"""find record according to name"""
	targetname = input("Please input a name:")
	nameresult = []
	for i in range(len(result)):
		if result[i]['username'] == targetname:
			nameresult.append(result[i])
	if len(nameresult) == 0:
		print("No record found!")
	else:
		print("Found {} matching records".format(len(nameresult)))
		for i in nameresult:
			print(i)

def findkeywords(result):
	"""find record according to keyword"""
	targetname = input("Please input a keyword:")
	keyresult = []
	for i in range(len(result)):
		if result[i]['topic'] == targetname:
			keyresult.append(result[i])
	if len(keyresult) == 0:
		print("No record found!")
	else:
		print("Found {} matching records".format(len(keyresult)))
		for i in keyresult:
			print(i)


def most_common(lst):
	"""find the most frequent item in a list"""
	return max(set(lst), key=lst.count)


def info_report(result):
	"""report basic information"""
	users = []
	oss = []
	topic = []
	number = []
	for i in range(len(result)):
		users.append(result[i]['username'])
		oss.append(result[i]['os'])
		topic.append(result[i]['topic'])
		number.append(int(result[i]['numberofpic']))
	pass
	print("The most frequent user is {}".format(most_common(users)))
	print("The most frequent user os is {}".format(most_common(oss)))
	print("The most frequent Topic {}".format(most_common(topic)))
	print("The average of picture per feed is {}".format(sum(number)/len(result)))


def main():
	"""main function"""
	client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
	db = client.get_database("project1_log")
	user_records = db.project1_log
	records = user_records.find({})
	result = []
	for i in records:
		result.append(i)
	print("{} records found!".format(len(result)))
	info_report(result)
	order = input("Enter u for username search, enter k for keyword search, others to exit:")
	if order == "u":
		findname(result)
	elif order == "k":
		findkeywords(result)
	else:
		exit(0)


if __name__ == '__main__':
	main()

