# divideData
# given a csv formatted in the way our data is, this splits it up into fNum files
import csv
def divideData(filename="train.csv", fNum=2):
	
	# initialize list of lists data, with headers
	data = []
	for i in range(fNum):
		data.append([])
		data[i].append(["Dates", "Category","Descript","DayOfWeek","PdDistrict","Resolution","Address","X","Y"])

	with open(filename, 'r') as inputFile:
		next(inputFile)
		reader = csv.reader(inputFile, delimiter=',')
		index = 0
		for date, category, desc, day, district, resolution, address, x, y in reader:
			data[index%fNum].append([date, category, desc, day, district, resolution, address, x, y])
			index += 1
	for i in range(len(data)):
		print "creating file #",i+1
		fileData = data[i]
		with open("train_data_"+str(i+1)+".csv", "w") as outputFile:
			spamwriter = csv.writer(outputFile, delimiter=',')
			for line in fileData:
				spamwriter.writerow(line)
divideData()
