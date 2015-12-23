'''

BEGIN CODE WRITTEN BY LIAM KINNEY FOR CRIME WAVES

'''



import math, random, collections, csv
from operator import itemgetter


# Function: Weighted Random Choice
# --------------------------------
# Given a dictionary of the form element -> weight, selects an element
# randomly based on distribution proportional to the weights. Weights can sum
# up to be more than 1. 
def weightedRandomChoice(weightDict):
    weights = []
    elems = []
    for elem in weightDict:
        weights.append(weightDict[elem])
        elems.append(elem)
    total = sum(weights)
    key = random.uniform(0, total)
    runningTotal = 0.0
    chosenIndex = None
    for i in range(len(weights)):
        weight = weights[i]
        runningTotal += weight
        if runningTotal > key:
            chosenIndex = i
            return elems[chosenIndex]
    raise Exception('Should not reach here')

# Function: distance
# --------------------------------
# The distance formula
def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)


# Functions: 
# --------------------------------
# Functions for querying things from the data lines
def getDate(datum):
    return datum[0].split(' ')[0]

def getDistrict(datum):
    return datum[4]

def getCategory(datum):
    return datum[1]

def getX(datum):
    return abs(datum[7])

def getY(datum):
    return abs(datum[8])

def getYear(datum):
    year, month, day = map(int, getDate(datum).split('-'))
    return year

def getMonth(datum):
    year, month, day = map(int, getDate(datum).split('-'))
    return month

def getDay(datum):
    year, month, day = map(int, getDate(datum).split('-'))
    return day

def isBefore(date1, date2):
    year1, month1, day1 = map(int, date1.split('-'))
    year2, month2, day2 = map(int, date2.split('-'))
    if year1 < year2: return True
    if year1 == year2 and month1 < month2: return True
    if year1 == year2 and month1 == month2 and day1 < day2: return True
    return False 

def isAfter(date1, date2):
    year1, month1, day1 = map(int, date1.split('-'))
    year2, month2, day2 = map(int, date2.split('-'))
    if year1 > year2: return True
    if year1 == year2 and month1 > month2: return True
    if year1 == year2 and month1 == month2 and day1 > day2: return True
    return False 


# Class: DataVisualizer
# ----------------------
# Maintain and update a belief distribution over the probability of a crime center
# being in a tile using a set of particles.
class DataBase(object):

    def __init__(self, filename, numHotspots = 3):

        # a lists of lists, where each lists is a single datapoint (a single crime) of
        # the form [date, category, desc, day, district, resolution, address, x, y]
        self.data = []

        # a dictionary of dates to the normalized probabilities of crimes happening
        # on that date
        self.distributions = collections.defaultdict(dict)

        # a list of the crime categories in the dataset
        self.categories = []

        # the number of unique dates in the dataset
        self.numDates = 4511

        # the number of days in a month
        self.numDaysInMonth = 30

        self.firstDate = ''

        self.lastDate = ''
        
        # boundaries of the grid/absolute values of long/lat
        self.maxY = 37.8199754923
        self.minY = 37.7078790224
        self.maxX = 122.513642064
        self.minX = 122.364937494

        # the number of rows and columns to be in belief
        self.numCols = 10
        self.numRows = 10

        # the average number of crimes per day, calculated over the entire dataset
        # (used for weighting)
        self.avgNumCrimesPerDay = {}

        # transProbDict is a Counter of (oldTile, newTile) tuples to the probability of that transition happening
        transProbDict = collections.Counter()

        # the k to use for kmeans (i.e. the number of crime hotspots for each category)
        self.k = numHotspots

        # the iterations of kmeans
        self.kmeansIters = 4

        # open the file and load into the list "data"
        with open(filename, 'r') as inputFile:
            next(inputFile)
            reader = csv.reader(inputFile, delimiter=',')
            for date, category, desc, day, district, resolution, address, x, y in reader:
                self.data.append([date, category, desc, day, district, resolution, address, float(x), float(y)])
                if category not in self.categories: self.categories.append(category)

        self.firstDate = getDate(self.data[-1])
        self.lastDate = getDate(self.data[0])

        # building average number of crimes per day dict
        for cat in self.categories:
            self.avgNumCrimesPerDay[cat] = sum(elem[1] == cat for elem in self.data)/float(self.numDates)

        # build the distributions dict
        runningDict = collections.Counter()

        for i, line in enumerate(self.data):

            runningDict[getCategory(line)] += 1

            # if we're at the end of the dataset or we're about to switch dates, normalize
            if i + 1 == len(self.data) or getDate(line) != getDate(self.data[i+1]):
                newDict = collections.Counter()
                # normalize
                for key in runningDict.keys():
                    newDict[key] = runningDict[key] / float(sum(runningDict.values()))
                
                self.distributions[getDate(line)] = newDict
                runningDict.clear()



    # Function: printCategoryDistributionOn
    # ------------------
    # prints the observed distributions of the crimes on a single date
    def printCategoryDistributionOn(self, year, month, day):

        #query the distributions dict
        if month < 10: month = "0"+str(month)
        if day < 10: day = "0"+str(day)
        date = str(year) + "-" + str(month) + "-" + str(day)
        #date = '2010-11-04'
        print "on ", date, " we saw..."
        if len(self.distributions[date].keys()) == 0: print "no data"

        # sort data from most occurring to least occuring
        sorted_dict = sorted(self.distributions[date].items(), key=itemgetter(1), reverse=True)
        for key, value in sorted_dict:
            print value, "percent chance of", key


    # Functions: northernBorder, southernBorder, easternBorder, westernBorder
    # ------------------
    # extract the x/y borders from the dataset. In the easternBorder and
    # northernBoarder functions, there are misreported data with long/lat pairs
    # outside of San Francisco, so we sort the data to find borders that
    # reflect the true boundaries of the city. After I used these to find
    # the boundaries, I hard-coded them as the max/min X/Y values to save
    # time.
    def easternBorder(self):
        # return max(elem[7] for elem in self.data)
        lister = sorted(self.data, key=itemgetter(7))
        for i, num in enumerate(lister):
            if i == 0: continue
            if float(num[7]) > float(-121):
                return lister[i-1][7]

    def westernBorder(self):
        return min(elem[7] for elem in self.data)

    def northernBorder(self):
        lister = sorted(self.data, key=itemgetter(8))
        for i, num in enumerate(lister):
            if i == 0: continue
            if float(num[8]) > 40:
                return lister[i-1][8]

    def southernBorder(self):
        return min(elem[8] for elem in self.data)


    # Function: avgDailyCrimes
    # ------------------
    # prints out the average number of crimes per day (averaged over the whole dataset)
    def avgDailyCrimes(self):
        print "on average, from", self.firstDate, "to", self.lastDate, "we see"
        sorted_dict = sorted(self.avgNumCrimesPerDay.items(), key=itemgetter(1), reverse=True)
        for key, value in sorted_dict:
            print key, ": ", value, " per day"



    # Function: Y to Row
    # -------------------------
    # Returns the row in the discretized grid, that the value y falls into.
    # This function does not check that y is in bounds.
    # Warning! Do not confuse rows and columns!
    def yToRow(self, belief, y):
        totalYDifference = self.maxY - self.minY             # calculate y difference over whole map
        currYDifference = y - self.minY                      # calculate current y offset from map's y-min
        tileYSize = totalYDifference / belief.getNumRows()   # calculate the size in y of a single tile
        return int((currYDifference / tileYSize))            # divide current y offset by the size of a single tile

    # Function: X to Col
    # -------------------------
    # Returns the col in the discretized grid, that the value x falls into.
    # This function does not check that x is in bounds.
    # Warning! Do not confuse rows and columns!
    def xToCol(self, belief, x):
        totalXDifference = self.maxX - self.minX             # calculate x difference over whole map
        currXDifference = x - self.minX                      # calculate current x offset from map's x-min
        tileXSize = totalXDifference / belief.getNumCols()   # calculate the size in x of a single tile
        return int((currXDifference / tileXSize))            # divide current x offset by the size of a single tile


    # Function: visualizeChangingBelief
    # ------------------
    # runs a command-line visualizer of the beliefs as they change
    # monthly from the startDate to the endDate for a given category
    def visualizeChangingBeliefMonthly(self, startDate, endDate, category):
        belief = Belief(self.numRows, self.numCols)

        # check that the input is valid
        if category not in self.categories:
            print category, "is not a valid category"
            return

        if isBefore(startDate, self.firstDate):
            print startDate, "is before the first date of", self.firstDate
            return

        if isAfter(endDate, self.lastDate):
            print endDate, "is after the end date of", self.lastDate
            return


        prunedDataset = [datum for datum in self.data if (isAfter(getDate(datum), startDate) and isBefore(getDate(datum), endDate) and getCategory(datum) == category)]
        # the data comes in sorted by date in decreasing chronological order, so
        # we reverse it
        prunedDataset.reverse()


        if prunedDataset == None:
            print "no ", category, "happened in the months between", startDate, "and", endDate
            return

        # print "this dataset should only have", category, "and the dates should be in ascending order:"
        # print prunedDataset[0]
        # print prunedDataset[1]
        # print prunedDataset[2]
        # print prunedDataset[3]
        # print prunedDataset[4]
        # print prunedDataset[5]
        # print prunedDataset[500]
        # print prunedDataset[1000]


        for i, datum in enumerate(prunedDataset):

            # update belief for this crime
            x = getX(datum)
            y = getY(datum)

            # check whether coordinates are valid
            if x < self.minX or x > self.maxX or y < self.minY or y > self.maxY:
                continue

            row = self.yToRow(belief, y)
            col = self.xToCol(belief, x)
            if col == self.numCols: col = col - 1
            if row == self.numRows: row = row - 1
            belief.addProb(row, col, 1)

            # if we're at the end of the dataset or we're about to switch months,
            # normalize, print, and reset belief
            if i + 1 == len(prunedDataset) or getMonth(datum) != getMonth(prunedDataset[i+1]):
                # print out this previous month
                print "for", getYear(datum), "/", getMonth(datum), "we saw:"
                #belief.normalize()
                for i in range(self.numRows):
                    row = ''
                    for j in range(self.numCols):
                        row += str(belief.getProb(i, j)) + ' '
                    print row

                belief = Belief(self.numRows, self.numCols)
                print ''


    # Function: findNearestCenter
    # ------------------
    # given a grid and a location inside the grid, iteratively check
    # a wider and wider range around the tile (i, j) until a tile is
    # found with weight greater than 0
    def findNearestCenter(self, centers, i, j):
        if centers[i][j] > 0:
            return (i, j)
        for x in range(0, self.numCols):
            for newi in range(i-x, i+x):
                for newj in range(j-x, j+x):
                    if newi >= self.numCols or newi < 0 or newj >= self.numRows or newj < 0: continue
                    if centers[newi][newj] > 0:
                        # we've found the nearest center. Return it
                        return (newi, newj)


    # Function: updateBelief
    # ------------------
    # adds the probability of the datum to the belief.
    def updateBelief(self, belief, datum):
        # update belief for this crime
        x = getX(datum)
        y = getY(datum)

        # check whether coordinates are valid; don't update belief if not
        if x < self.minX or x > self.maxX or y < self.minY or y > self.maxY: return

        row = self.yToRow(belief, y)
        col = self.xToCol(belief, x)
        if col == self.numCols: col = col - 1
        if row == self.numRows: row = row - 1
        belief.addProb(row, col, 1)



    # Function: normalizeCounter
    # ------------------
    # Given a counter where the values are probabilities, normalize it
    def normalizeCounter(self, counter):
        result = collections.Counter()
        for key in counter.keys():
            result[key] = counter[key] / float(sum(counter.values()))
        return result


    # Function: findLocalTransProbs
    # ------------------
    # Helper function to buildNewHotspots. Given a tile and a transProbs
    # dictionary, create a new normalized dict with only transition
    # probabilities from tile.
    def findLocalTransProbs(self, transProbs, tile):
        localTransProbs = collections.Counter()

        for key, value in transProbs.iteritems():
            if key[0] == tile:
                # oldTile is the local tile we're looking for
                localTransProbs[key] = value

        # normalize
        return self.normalizeCounter(localTransProbs)


    # Function: viewNewHotspots
    # ------------------
    # A visualizer for buildNewHotspots
    def viewNewHotspots(self, category, transProbs, month, year):
        newHotspots = self.buildNewHotspots(category, monthlyTransProbs, month, year)
        print "the", category, "hotspots for", year, "/", month, "given the previous month's data are"
        for i in range(numRowsCols):
            line = ''
            for j in range(numRowsCols):
                line += str(newHotspots[i][j]) + ' '
            print line



    # Function: getHotspots
    # ------------------
    # Given a category, month, and year, return a hotspot grid
    def getHotspots(self, category, month, year):

        belief = Belief(self.numRows, self.numCols)

        oldMonth = month - 1
        if oldMonth < 1:
            oldMonth = 12
            oldYear = year - 1
        else:
            oldYear = year

        # create a dataset with just the data from this month for this category
        prunedDataset = [datum for datum in self.data if (getCategory(datum) == category and getMonth(datum) == oldMonth and getYear(datum) == oldYear)]

        # build the belief
        for datum in prunedDataset:

            self.updateBelief(belief, datum)

        belief.normalize()

        return self.kmeans(self.k, belief)




    # Function: buildNewHotspots
    # ------------------
    # Given a category, it's transition probabilities, and a month, predict the hotspots
    # for the next month
    def buildNewHotspots(self, category, transProbs, month, year):

        # Step 1: get the hotspots for the previous month
        oldHotspots = self.getHotspots(category, month, year)

        # Step 2: from those hotspots, use transProbs and weightedRandomChoice to come up with new hotspots
        newHotspots = [[0 for _ in range(self.numCols)] for _ in range(self.numRows)]
        
        # iterate through oldHotspots and figure out where the newHotspots will be
        for i in range(self.numRows):
            for j in range(self.numCols):
                if oldHotspots[i][j] > 0:
                    # we're at a hotspot
                    localTransProbs = self.findLocalTransProbs(transProbs, (i, j))

                    # pick a weighted random transition to a new tile
                    if len(localTransProbs) == 0:
                        # if there's no transition information for this tile, keep the hotspot
                        # in the same place
                        newTile = (i, j)
                    else:
                        oldTile, newTile = weightedRandomChoice(localTransProbs)

                    # retain the weight from the previous month
                    newHotspots[newTile[0]][newTile[1]] = oldHotspots[i][j]


        return newHotspots




    # Function: buildMonthlyTransitionProbabilities
    # ------------------
    # Given a category, build a dictionary of (newTile, oldTile): monthly transition probability
    # using the data from the entire dataset
    def buildMonthlyTransitionProbabilities(self, category):
        print "building transition probabilities for", category, "..."

        # transProbDict
        transProbs = collections.Counter()

        lastMonthsCenters = None
        thisMonthsCenters = None

        belief = Belief(self.numRows, self.numCols)

        # since we're recording the transitions between months,
        # we can't do anything at the first month
        firstMonth = True
        
        prunedDataset = [datum for datum in self.data if (getCategory(datum) == category)]

        for i, datum in enumerate(prunedDataset):

            # update the belief with this data
            self.updateBelief(belief, datum)

            # if we're at the end of the dataset or we're about to switch months,
            # normalize, perform kmeans to find new centers, and record the transitions
            if i + 1 == len(prunedDataset) or getMonth(datum) != getMonth(prunedDataset[i+1]):

                belief.normalize()

                if firstMonth:
                    firstMonth = False
                    lastMonthsCenters = self.kmeans(self.k, belief)
                    continue

                thisMonthsCenters = self.kmeans(self.k, belief)

                for i in range(self.numRows):
                    for j in range(self.numCols):
                        if thisMonthsCenters[i][j] > 0:
                            # we're at a center; look for nearest center in last month's centers
                            newTile = (i, j)
                            oldTile = self.findNearestCenter(lastMonthsCenters, i, j)

                            # update transprobs
                            transProbs[(newTile, oldTile)] += 1.0


                lastMonthsCenters = thisMonthsCenters
                belief = Belief(self.numRows, self.numCols)

        # at the end, normalize over the entire dictionary of transition probabilities and return
        return self.normalizeCounter(transProbs)



    # Function: kmeans
    # ------------------
    # A helper function to buildMonthlyTransitionProbabilities, kmeans
    # uses the probabilities in the belief grid to locate k centers
    # and returns their locations on a grid
    def kmeans(self, k, belief):

        # centers is a grid where k of the tiles are centers. A center is represented
        # by a number corresponding to the sum of the tiles assigned to it
        centers = [[0 for _ in range(self.numCols)] for _ in range(self.numRows)]

        # assignments is a grid of tuples recording which center that tile belongs to
        assignments = [[None for _ in range(self.numCols)] for _ in range(self.numRows)]

        # a list of tuples where the first element is an (i, j) pair and the second
        # is the weight of that tile. This records the k heaviest tiles in belief
        # in order to initialize the centers to that position
        heaviestTiles = [None]*k

        for i in range(self.numRows):
            for j in range(self.numCols):
                if heaviestTiles[-1] == None:
                    # we haven't filled the heaviest tiles list yet
                    for i, elem in enumerate(heaviestTiles):
                        if elem == None:
                            heaviestTiles.insert(i, ((i, j), belief.getProb(i, j)))
                            del heaviestTiles[-1]
                elif belief.getProb(i, j) > heaviestTiles[-1][1]:
                    # this new probability belongs in the heaviestTiles list
                    for i in range(len(heaviestTiles)):
                        if heaviestTiles[i][1] < belief.getProb(i, j):
                            heaviestTiles.insert(i, ((i, j), belief.getProb(i, j)))
                            del heaviestTiles[-1]

        # initialize the centers to the heaviest tiles
        for tile, weight in heaviestTiles:
            centers[tile[0]][tile[1]] = weight


        for iteration in range(self.kmeansIters):

            # step 1: assign the tiles to centers
            for i in range(self.numRows):
                for j in range(self.numCols):
                    assignments[i][j] = self.findNearestCenter(centers, i, j)


            # step 2: rearrange the centers according to the tiles assigned to it
            newCenters = [[0 for _ in range(self.numCols)] for _ in range(self.numRows)]
            for _ in range(k):
                for i in range(self.numRows):
                    for j in range(self.numCols):
                        if centers[i][j] > 0:
                            # we're at a center; reassign it

                            # use the center of mass formula to find new center
                            totalWeight = 0
                            iBarNumerator = 0
                            jBarNumerator = 0

                            for x in range(self.numRows):
                                for y in range(self.numCols):
                                    if assignments[x][y] == (i, j):
                                        # we're at a point that's assigned to this center
                                        totalWeight += belief.getProb(x, y)
                                        iBarNumerator += belief.getProb(x, y)*x
                                        jBarNumerator += belief.getProb(x, y)*y

                            iBar = int(float(iBarNumerator) / totalWeight)
                            jBar = int(float(jBarNumerator) / totalWeight)

                            # update the new center to have a weight that is the sum of the
                            # weights of the tiles assigned to it
                            newCenters[iBar][jBar] = totalWeight

            centers = newCenters

        return centers



    # Function: checkAccuracy
    # ------------------
    # Given a predicted output myDistributions, measure it against
    # the actual distributions for that day and output a percent accuracy
    def checkAccuracy(self, myDistributions, month, year, x, y):

        # build the hotspots for place and month given the data in the database

        # run through categories and create a dictionary of categories : hotspot grids
        trueDistributions = collections.Counter()

        belief = Belief(self.numRows, self.numCols)
        row = self.yToRow(belief, y)
        col = self.xToCol(belief, x)


        for cat in self.categories:

            actualHotspots = self.getHotspots(cat, month, year)

            # find coordinates of nearest hotspot to our x and y
            i, j = self.findNearestCenter(actualHotspots, col, row)

            # get the weight of that hotspot
            hotspotWeight = actualHotspots[i][j]

            # apply weighting formula 
            trueDistributions[cat] = self.avgNumCrimesPerDay[cat]*hotspotWeight*(1/distance((i, j), (x, y)))

        normalizedTrueDistributions = self.normalizeCounter(trueDistributions)


        # compare true distributions and myDistributions to get % error
        totalPercentError = 0

        for cat, trueProb in normalizedTrueDistributions.iteritems():
            # percent error is difference divided by exact value
            percentError = abs(trueProb - myDistributions[cat]) / trueProb
            totalPercentError += percentError

        avgPercentError = totalPercentError / float(len(self.categories))

        percentAccuracy = 1 - avgPercentError

        lowerXBound, upperXBound = self.getLongBounds(x)
        lowerYBound, upperYBound = self.getLatBounds(y)

        print "Our distribution formed for", year, "-", month, "between longitudes", lowerXBound, "and", upperXBound, "and latitudes", lowerYBound, "and", upperYBound, "has"

        print "percent error:", avgPercentError
        print "percent accuracy:", percentAccuracy



    # Functions: getLongBounds, getLatBounds
    # ------------------
    # given longitudes and latitudes, return a tuple containing the bounds
    # of the tile around it
    def getLongBounds(self, x):
        totalXDifference = self.maxX - self.minX             # calculate x difference over whole map
        currXDifference = x - self.minX                      # calculate current x offset from map's x-min
        tileXSize = totalXDifference / self.numCols          # calculate the size in x of a single tile
        index = int((currXDifference / tileXSize))           # divide current y offset by the size of a single tile
        return (self.minX + tileXSize * index, self.minX + tileXSize * (index+1))


    def getLatBounds(self, y):
        totalYDifference = self.maxY - self.minY             # calculate x difference over whole map
        currYDifference = y - self.minY                      # calculate current x offset from map's x-min
        tileYSize = totalYDifference / self.numCols          # calculate the size in x of a single tile
        index = int((currYDifference / tileYSize))           # divide current y offset by the size of a single tile
        return (self.minY + tileYSize * index, self.minY + tileYSize * (index+1))


    # Function: showCrimeDistribution
    # ------------------
    # Visualizer for queryDatabase
    def showCrimeDistribution(self, month, year, x, y):

        distributions = database.queryDatabase(month, year, x, y)

        print ''

        lowerXBound, upperXBound = self.getLongBounds(x)
        lowerYBound, upperYBound = self.getLatBounds(y)

        print "on", year, "-", month, "between longitudes", lowerXBound, "and", upperXBound, "and latitudes", lowerYBound, "and", upperYBound, "a crime has a"

        for key, value in sorted(distributions.iteritems(), key=itemgetter(1), reverse=True):
            print value*100, "%% chance of being", key




    # Function: queryDatabase
    # ------------------
    # Given a month and a year, query the dataset for a list of distributions
    # showing the predicted probabilities of different categories of crime
    # happening in that location in that month.
    def queryDatabase(self, month, year, x, y):

        # run through categories and create a dictionary of categories : hotspot grids
        distributions = collections.Counter()

        belief = Belief(self.numRows, self.numCols)
        row = self.yToRow(belief, y)
        col = self.xToCol(belief, x)

        for count, cat in enumerate(self.categories):

            # create the dicctionary of transition probabilities for this category
            transProbs = self.buildMonthlyTransitionProbabilities(cat)

            # create the predicted hotspots grid for this month
            newHotspots = self.buildNewHotspots(cat, transProbs, month, year)

            # find coordinates of nearest hotspot to our x and y
            i, j = self.findNearestCenter(newHotspots, col, row)

            # get the weight of that hotspot
            hotspotWeight = newHotspots[i][j]

            # apply weighting formula 
            distributions[cat] = self.avgNumCrimesPerDay[cat]*hotspotWeight*(1/distance((i, j), (x, y)))

            print (float(count+1)/float(len(self.categories)))*100, "%% done"

        return self.normalizeCounter(distributions)



    # Function: predictCrimesForMonthAndLocation
    # ------------------
    # Given a set of distributions from a certain time and location, predict how
    # many crimes of each category are going to happen in that location.
    def predictCrimesForMonthAndLocation(self, distributions, month, year, x, y):
        lowerXBound, upperXBound = self.getLongBounds(x)
        lowerYBound, upperYBound = self.getLatBounds(y)

        print ''

        print "on", year, "-", month, "between longitudes", lowerXBound, "and", upperXBound, "and latitudes", lowerYBound, "and", upperYBound, "I predict:"

        for key, value in sorted(distributions.iteritems(), key=itemgetter(1), reverse=True):
            print str(value*self.numDaysInMonth*sum(self.avgNumCrimesPerDay.values()))+'s', str(key)+'s'

        print ''

        print "the actual data is:"

        prunedDataset = [datum for datum in self.data if (getMonth(datum) == month and getYear(datum) == year)]

        actualCrimeCount = collections.Counter()

        for datum in prunedDataset:
            actualCrimeCount[getCategory(datum)] += 1

        for key, value in sorted(actualCrimeCount.iteritems(), key=itemgetter(1), reverse=True):
            print str(value)+'s', str(key)+'s'


        print ''

        print "which gives us"

        # compare true distributions and myDistributions to get % error
        totalPercentError = 0

        for cat, trueCount in actualCrimeCount.iteritems():
            # percent error is difference divided by exact value
            percentError = abs(trueCount - distributions[cat]*self.numDaysInMonth*sum(self.avgNumCrimesPerDay.values())) / trueCount
            totalPercentError += percentError

        avgPercentError = totalPercentError / float(len(self.categories))

        percentAccuracy = 1 - avgPercentError

        print "percent error:", avgPercentError
        print "percent accuracy:", percentAccuracy


'''

END CODE WRITTEN BY LIAM KINNEY FOR CRIME WAVES

'''






'''

BELIEF CLASS TAKEN FROM THE STANFORD DRIVERLESS CAR PROJECT

'''

# Class: Belief
# ----------------
# This class represents the belief for a single inference state of a single 
# car. It has one belief value for every tile on the map. You *must* use
# this class to store your belief values. Not only will it break the 
# visualization and simulation control if you use your own, it will also
# break our autograder :).
class Belief(object):
    
    # Function: Init
    # --------------
    # Constructor for the Belief class. It creates a belief grid which is
    # numRows by numCols. As an optional third argument you can pass in the
    # initial belief value for every tile (ie Belief(3, 4, 0.0) would create
    # a belief grid with dimensions (3, 4) where each tile has belief = 0.0.
    def __init__(self, numRows, numCols, value = None):
        self.numRows = numRows
        self.numCols = numCols
        numElems = numRows * numCols
        if value == None:
            value = (1.0 / numElems)
        self.grid = [[value for _ in range(numCols)] for _ in range(numRows)]
        
    # Function: Set Prob
    # ------------------
    # Sets the probability of a given row, col to be p
    def setProb(self, row, col, p):
        self.grid[row][col] = p
        
    # Function: Add Prob
    # ------------------
    # Increase the probability of row, col by delta. Belief probabilities are
    # allowed to increase past 1.0, but you must later normalize.
    def addProb(self, row, col, delta):
        self.grid[row][col] += delta
        assert self.grid[row][col] >= 0.0
        
    # Function: Get Prob
    # ------------------
    # Returns the belief for tile row, col.
    def getProb(self, row, col):
        return self.grid[row][col]
    
    # Function: Normalize
    # ------------------
    # Makes the sum over all beliefs 1.0 by dividing each tile by the total.
    def normalize(self):
        total = self.getSum()
        for r in range(self.numRows):
            for c in range(self.numCols):
                self.grid[r][c] /= total
    
    # Function: Get Num Rows
    # ------------------
    # Returns the number of rows in the belief grid.
    def getNumRows(self):
        return self.numRows
    
    # Function: Get Num Cols
    # ------------------
    # Returns the number of cols in the belief grid.
    def getNumCols(self):
        return self.numCols
    
    # Function: Get Sum
    # ------------------
    # Return the sum of all the values in the belief grid. Used to make sure
    # that the matrix has been normalized.
    def getSum(self):
        total = 0.0
        for r in range(self.numRows):
            for c in range(self.numCols):
                total += self.getProb(r, c)
        return total


'''

BELIEF CLASS TAKEN FROM THE STANFORD DRIVERLESS CAR PROJECT

'''






'''

Tests for the individual components of the database module

'''

# filename = "train.csv"
# database = DataBase(filename)
# month = 12
# year = 2010
# x = 122.397744427103
# y = 37.7299346936044

# # test of printCategoryDistributionOn: print out the category distribution for a given day
# day = 4
# database.printCategoryDistributionOn(year, month, day)

# print ''

# # test of border-finding functions
# print "northern boarder: ", database.northernBorder()
# print "southern boarder: ", database.southernBorder()
# print "eastern Border: ", database.easternBorder()
# print "western Border: ", database.westernBorder()

# print ''

# # test of avgDailyCrimes: prints out the average number of crimes per day (averaged over the whole dataset)
# database.avgDailyCrimes()


# print ''

# # test of visualizeChangingBeliefMonthly: starts a visualizer of the normalized city grid containing the probability
# # distributions as they change month to month
# print "the list of categories: ", database.categories
# database.visualizeChangingBeliefMonthly("2010-01-01", "2012-01-01", "VANDALISM")

# print ''

# # test of buildMonthlyTransitionProbabilities
# monthlyTransProbs = database.buildMonthlyTransitionProbabilities("VANDALISM")
# for key, value in sorted(monthlyTransProbs.iteritems(), key=itemgetter(1), reverse=True):
#     print key, ":", value

# print ''

# # test of buildNewHotspots
# monthlyTransProbs = database.buildMonthlyTransitionProbabilities("VANDALISM")
# numRowsCols = 10
# month = 12
# year = 2010
# database.viewNewHotspots("VANDALISM", monthlyTransProbs, month, year)

# print ''

# # test of queryDatabase
# database.showCrimeDistribution(month, year, x, y)
# distributions = database.queryDatabase(month, year, x, y)

# print ''

# # test of checkAccuracy
# database.checkAccuracy(distributions, month, year, x, y)

# print ''

# # test of predictCrimesForMonthAndLocation
# database.predictCrimesForMonthAndLocation(distributions, month, year, x, y)


'''

Tests for the individual components of the database module

'''





