--------------------------------------------------------

Crime Waves: Learning and Predicting Instances of Crime in San Francisco
A CS 221 Final Project

--------------------------------------------------------


--- divide_data.py ---

This module contains the single function divide_data


Function: Divide Data
------------------
Given a csv dataset with the categories "Dates", "Category","Descript",
"DayOfWeek","PdDistrict","Resolution","Address","X","Y", divide it into
fNum new dataset files.




'''
Begin K-means Learning + Hidden Markov Model section
'''

--- database.py ---

This module contains the database and belief classes, as well as some
helper functionsfor the database class. The database class implements
he K-means Learning + Hidden Markov Model portion of the project. The
user-facing functions are documented below. Other functions in the
class are internal helper methods for these functions. They can be
tested and  their outputs viewed by uncommenting the code at the
bottom of the file database.py.


Function: printCategoryDistributionOn
------------------
prints the observed distributions of the crimes on a single date


Functions: northernBorder, southernBorder, easternBorder, westernBorder
------------------
extract the x/y borders from the dataset. In the easternBorder and
northernBoarder functions, there are misreported data with long/lat pairs
outside of San Francisco, so we sort the data to find borders that
reflect the true boundaries of the city. After I used these to find
the boundaries, I hard-coded them as the max/min X/Y values to save
time.


Function: avgDailyCrimes
------------------
prints out the average number of crimes per day (averaged over the
whole dataset)


Function: visualizeChangingBelief
------------------
runs a command-line visualizer of the beliefs as they change
monthly from the startDate to the endDate for a given category


Function: buildMonthlyTransitionProbabilities
------------------
Given a category, build a dictionary of (newTile, oldTile): monthly transition probability
using the data from the entire dataset

Function: showCrimeDistribution
------------------
Visualizer for queryDatabase


Function: queryDatabase
------------------
Given a month and a year, query the dataset for a list of distributions
showing the predicted probabilities of different categories of crime
happening in that location in that month.


Function: checkAccuracy
------------------
Given a predicted output myDistributions, measure it against
the actual distributions for that day and output a percent accuracy


Function: predictCrimesForMonthAndLocation
------------------
Given a set of distributions from a certain time and location, predict how
many crimes of each category are going to happen in that location.


'''
End K-means Learning + Hidden Markov Model section
'''




'''
begin Linear Classification and Network Analysis section
'''



--- run_many.py ---

call this to run the Linear Classification and Network Analysis portion of the project.
It will control the simulations and their quantity.


--- Feature_Extractor.py ---

readData: Extracts features from the dataset.
Call the network simulation to calculate network features
Calculates basic spatial and temporal features from the original dataset.
Examples:
	Time of Day,
	Season
	timestampe UTC
	Street Address
	Intersection


--- divide_data.py ---

Given a desired number of entries, randomly selects a continuous set of train data and test data.
Writes output into a network file and a general file.


--- util.py ---

Basic util functions. All supplied by the CS221 coursestaff.


--- generateNetwork.py ---

Governs the network simulation.
Encapsulates a network and node object.
Nodes keep track of the spatial location of a crime, as well as their nearest neighbor
Networks keep track of their constituent nodes and a snap graph for calculating centrality measures.
Utilizes snap.py to calculate network features, but runs the simulation on a custom designed network
Has a "simulate" function to run the simulation itself, or an "addNode" function to be callable from other programs.


--- run_many.py ---

exectues multiple simulations sequentially
Might have some issues now because I changes the parameters for a few functions.


--- sdg.py ---

runs stochastic gradient descent. Basically the implementation of multiclass classifcation that was discussed in lecture and section. 


'''
end Linear Classification and Network Analysis section
'''



'''
Begin Random Forests (oracle) section
'''


--- Random_forests.py ---

This takes in half of the data from the file "train_data.csv" to train
and predicts the crime using the other half. Random Forests uses 10
trees to generate 10 votes on the outcome. 

The results from the prediction are compared to the actual crime
type, and the percent accurate is printed. 

Because the train and test data both include the description of the crime,
the algorithm performs extremely well, functioning as an oracle. In general,
the test data will not include the description of the crime. 

Run this file as "random_forests.py"
Must have numpy, pandas, and sklearn. 


'''
End Random Forests (oracle) section
'''






