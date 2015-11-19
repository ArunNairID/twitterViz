print "Started."
import datetime
now = datetime.datetime.now()
print 'Time is now: ', now


import pandas  ##Data analysis
import nltk ##word tokenizing
import json ##json loading and saving
import csv  ##importing from csv
from mpl_toolkits.basemap import Basemap ##map functionality for matplotlib
import matplotlib.pyplot as plt ##plotting
import numpy as np  ##minimally used for plotting
import matplotlib.animation as animation ##animating the resulting plot
from collections import Counter ##counting frequencies
from progressbar import ProgressBar, ETA, Bar ##aprising user of progress
import urllib2 ##web i/o
print "Imported all modules successfully."

##load a list of countries to check against
def loadCountriesList():
    data = urllib2.urlopen("http://restcountries.eu/rest/v1/all")
    d = json.load(data)
    countries = ["STATES"] ##catch united states since we can't catch two word countries
    for i in d:
        countries.append(i['name'].upper())
    return countries
countries = loadCountriesList()
print "Loaded country list."

##Load all of the tweets from the disk
print "Loading tweets..."
outData = []
timestamps = []
countries_in_tweets = []
data = pandas.read_csv("/Volumes/Sherwin/tweetsOut1.csv", skiprows=6) ##make sure we get rid of the header
cursor = 0
data.columns = ["Time", "ID", "User", "Screen", "Lang", "Text"]
tweets = data['Text']
dates = data['Time']

progress = ProgressBar(maxval=len(tweets)).start() ##keep me posted on what is going on
##search through all tweets
while cursor < len(tweets):
    try:
        timestamp = dates[cursor]
        text = tweets[cursor].decode("utf-8", "ignore") ##important to decode because many tweets have unicode in them
        words = nltk.word_tokenize(text) ##break into words
        tweetCountries = []
        for word in words:
            word = word.upper()
            ##check if word is in the list of countries we got previously
            if word in countries:
                tweetCountries.append(word)
        countries_in_tweets.append(tweetCountries)
        timestamps.append(timestamp)
        cursor += 1
        progress.update(cursor)
    except:
        cursor += 1
        progress.update(cursor)

progress.finish()
print "Completed Search Cursor."
print "Loading dataframe"
##turn two lists into one dataframe
outData.append(timestamps)
outData.append(countries_in_tweets)
out = pandas.DataFrame(outData)
out = out.transpose() ##flip it so we have rows and columns instead of columns and rows
print "Writing to csv."
out.to_csv("/Volumes/Sherwin/country_mentions2.csv") ##save the result so we could skip this part in the future


##now count the frequency of each country per timestamp
out.columns = ["Index1",  "Time", "Countries"]
dates = out['Time']
allCountries = out['Countries']
##do it for hours, minutes and seconds
allSeconds = []
allMinutes = []
allHours = []

##hold the last timestamp to compare against
lastSecond = -1
secondsCountries = []
secondsData = []
lastMinute = -1
minutesCountries = []
minutesData = []
lastHour = -1
hoursData = []
hoursCountries = []
cursor = 0
progress = ProgressBar(widgets=[Bar(), ETA()], maxval=len(allCountries)).start() ##graphical progress bar

##Downsamples to hours, minutes, and seconds
while cursor < len(allCountries):
    timestamp = pandas.to_datetime(dates[cursor])
    second = timestamp.second
    minute = timestamp.minute
    hour = timestamp.hour
    if timestamp != lastSecond:
        if secondsCountries != []:
            secondsData.append(secondsCountries)
            allSeconds.append(timestamp)
        secondsCountries = []
        lastSecond = timestamp
    if minute != lastMinute:
        if minutesCountries != []:
            minutesData.append(minutesCountries)
            allMinutes.append(timestamp)
        minutesCountries = []
        lastMinute = minute
    if hour != lastHour:
        if hoursCountries != []:
            hoursData.append(hoursCountries)
            allHours.append(timestamp)
        hoursCountries = []
        lastHour = hour
    ##parses the list back into python format from a string
    countries = allCountries[cursor]
    countries = countries.replace("[", "")
    countries = countries.replace("]", "")
    countries = countries.split(",")
    ##add the country to memory
    for country in countries:
        country = country.strip()
        if country != "":
            secondsCountries.append(country)
            minutesCountries.append(country)
            hoursCountries.append(country)
    progress.update(cursor)
    cursor += 1
progress.finish()

##now count up all of the occurrences per second, per minute, and per hour
print "Working on resampling to seconds..."
outSeconds = []
outSeconds.append(allSeconds)
outSeconds.append(secondsData)
outSeconds = pandas.DataFrame(outSeconds)
outSeconds = outSeconds.transpose()
outSeconds.columns = ["Timestamp", "Mentions"]
cursor = 0
counters = {}
progress = ProgressBar(widgets=[Bar(), ETA()], maxval=len(outSeconds['Mentions'])).start()
while cursor < len(outSeconds['Mentions']):
    row = outSeconds['Mentions'][cursor]
    rowCount = dict(Counter(row))
    timestamp = str(outSeconds['Timestamp'][cursor])
    counters[timestamp] = str(rowCount)
    progress.update(cursor)
    cursor += 1
progress.finish()
print "Dumping to json file."
##Then save to a json file
f = open("/Volumes/Sherwin/seconds.json", 'w')
out = json.dumps(counters)
f.write(out)
f.close()


print "Working on resampling to minutes..."
outMinutes = []
if len(allMinutes) != 0:
    outMinutes.append(allMinutes)
    outMinutes.append(minutesData)
    outMinutes = pandas.DataFrame(outMinutes)
    outMinutes = outMinutes.transpose()
    outMinutes.columns = ["Timestamp", "Mentions"]
    cursor = 0
    counters = {}
    progress = ProgressBar(widgets=[Bar(), ETA()], maxval=len(outMinutes['Mentions'])).start()
    while cursor < len(outMinutes['Mentions']):
        row = outMinutes['Mentions'][cursor]
        rowCount = dict(Counter(row))
        timestamp = str(outMinutes['Timestamp'][cursor])
        counters[timestamp] = str(rowCount)
        progress.update(cursor)
        cursor += 1
    progress.finish()
    print "Dumping to json file."
    f = open("/Volumes/Sherwin/minutes.json", 'w')
    out = json.dumps(counters)
    f.write(out)
    f.close()

print "Working on resampling to Hours..."
outHours = []
if len(allHours) != 0:
    outHours.append(allHours)
    outHours.append(hoursData)
    outHours = pandas.DataFrame(outHours)
    outHours = outHours.transpose()
    outHours.columns = ["Timestamp", "Mentions"]
    cursor = 0
    counters = {}
    progress = ProgressBar(widgets=[Bar(), ETA()], maxval=len(outHours['Mentions'])).start()
    while cursor < len(outHours['Mentions']):
        row = outHours['Mentions'][cursor]
        rowCount = dict(Counter(row))
        timestamp = str(outHours['Timestamp'][cursor])
        counters[timestamp] = str(rowCount)
        progress.update(cursor)
        cursor += 1
    progress.finish()
    print "Dumping to json file."
    f = open("/Volumes/Sherwin/hours.json", 'w')
    out = json.dumps(counters)
    f.write(out)
    f.close()
    print "Job Complete."


##now lets animate that shit

fig = plt.figure()

ax1 = fig.add_subplot(211)


print "Setting up basemap..."
# ##set up the base map on which to draw
map = Basemap(projection='robin', resolution = 'l', area_thresh = 1000.0,
          lat_0=0, lon_0=0)
map.drawcoastlines()
map.drawcountries()
map.fillcontinents(color = 'white')
map.drawmapboundary()
map.drawmeridians(np.arange(0, 360, 30))
map.drawparallels(np.arange(-90, 90, 30))

print "Getting country centroids..."
##get the centroids to use as proportional symbol base
f = open("/Volumes/Sherwin/centroids.csv", 'rU')
reader = csv.DictReader(f)
lats = []
lngs = []
points = []
names = []
for i in reader:
    lat = float(i['LAT'])
    lng = float(i['LONG'])
    x, y = map(lng, lat)
    point = map.plot(x, y, 'ro', markersize=0)[0]
    points.append(point)
    names.append(i['SHORT_NAME'].upper())

print "Loaded country centroids..."
print "Getting frequency data..."

###Load the json file with the frequencies

maximumValue = -1

data = json.load(open("/Volumes/Sherwin/minutes.json"))
for timestamp in data:
    data[timestamp] = json.loads(data[timestamp])
    tsVal = 0
    for i in data[timestamp]:
        old = i
        i = i.replace("u'", "")
        i = i.replace("'", "")
        data[timestamp][i] = data[timestamp].pop(old)
        tsVal += data[timestamp][i]
    if tsVal > maximumValue:
        maximumValue = tsVal

print "Loaded frequency data...."


timestamps = sorted(data.keys())


def lookupValue(country, timestamp):
    country = country.upper()
    timestampValues = data[timestamp]
    countries_in_timestamp = timestampValues.keys()
    if country in countries_in_timestamp:
        return timestampValues[country]
    else:
        return False


def classifyValue(i):
    """Created classified symbol sizes"""
    return i * 0.1


print "Now animating..."
##add a timestamp to the plot
timeLabel=ax1.set_title("Initialized", bbox=dict(facecolor='red', alpha=0.5), fontsize=16)


ax2 = fig.add_subplot(212)
ax2.set_xlim([0, len(timestamps)])
ax2.set_ylim([0, maximumValue * 1.1])


ax2.set_title("Initialized", fontsize=12)
line, = ax2.plot([], [], lw=2)

allX = []
allY = []


##The animation function --> called each frame
def animate(i):
    thisTimestamp = timestamps[i]
    totalValue = 0
    j = 0
    while j < len(points):
        point = points[j]
        name = names[j]
        value = lookupValue(name, thisTimestamp)
        totalValue += value
        if totalValue < 10:
            pass
        else:
            point.set_markersize(classifyValue(value))
            timestampLabel = str(thisTimestamp)[:-3]
            ax1.set_title(timestampLabel)
        j += 1
    if totalValue > 100:
        ax2.set_title(str("Mentions per Hour: " + str(totalValue)))
        allX.append(i)
        allY.append(totalValue)
        # allX.pop(0)
        # allY.pop(0)
        line.set_data(allX, allY)  # update the data
    return line,

##do the animation
anim = animation.FuncAnimation(plt.gcf(), animate,
                               frames=len(timestamps), interval=5, blit=False)

##Save the animation
anim.save('/Volumes/Sherwin/minutes1.mp4', fps=30, extra_args=['-vcodec', 'libx264'])
print "Wrote to disk."
##plt.show() ##Show the animation


