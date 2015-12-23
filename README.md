--------------------------------------------------------

Crime Waves: Learning and Predicting Instances of Crime in San Francisco
A CS 221 Final Project

--------------------------------------------------------


Module: divide_data.py
------------------
This module contains the single function divide_data


-- Function: Divide Data --
Given a csv dataset with the categories "Dates", "Category","Descript",
"DayOfWeek","PdDistrict","Resolution","Address","X","Y", divide it into
fNum new dataset files.



Module: database.py
------------------
This module contains the database and belief classes, as well as some
helper functions for the database class. The database class implements
he K-means Learning + Hidden Markov Model portion of the project. The
user-facing functions are documented below. Other functions in the
class are internal helper methods for these functions. They can be
tested and  their outputs viewed by uncommenting the code at the
bottom of the file database.py.


-- Function: printCategoryDistributionOn --
prints the observed distributions of the crimes on a single date


-- Functions: northernBorder, southernBorder, easternBorder, westernBorder --
extract the x/y borders from the dataset. In the easternBorder and
northernBoarder functions, there are misreported data with long/lat pairs
outside of San Francisco, so we sort the data to find borders that
reflect the true boundaries of the city. After I used these to find
the boundaries, I hard-coded them as the max/min X/Y values to save
time.


-- Function: avgDailyCrimes --
prints out the average number of crimes per day (averaged over the
whole dataset)


-- Function: visualizeChangingBelief --
runs a command-line visualizer of the beliefs as they change
monthly from the startDate to the endDate for a given category


-- Function: buildMonthlyTransitionProbabilities -- 
Given a category, build a dictionary of (newTile, oldTile): monthly transition probability
using the data from the entire dataset


-- Function: showCrimeDistribution --
Visualizer for queryDatabase


-- Function: queryDatabase --
Given a month and a year, query the dataset for a list of distributions
showing the predicted probabilities of different categories of crime
happening in that location in that month.


-- Function: checkAccuracy --
Given a predicted output myDistributions, measure it against
the actual distributions for that day and output a percent accuracy


-- Function: predictCrimesForMonthAndLocation --
Given a set of distributions from a certain time and location, predict how
many crimes of each category are going to happen in that location.




