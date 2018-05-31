
import urllib.request
import xml.etree.ElementTree as ET
import time
import sys

#Need to change these to be interchangeable
#Insert the first argument as the taxon number to search
query = "txid" + str(sys.argv[1]) + "[organism]"
#The second arg is the output location
outputFileLocation = str(sys.argv[2])

print("Fetching the query: " + query)
#The base URL for eutils requests
urlBase = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

url = urlBase + "esearch.fcgi?db=protein&term=" + query + "&usehistory=y"
#print(url)

#Create a string for the XML output of the esearch
xmlOutput = ""

with urllib.request.urlopen(url) as response:
            #For each line in response, decode it from binary to UTF-8 text and
            #append to the xmlOutput string
            for line in response:
                line = line.decode("utf-8")
                xmlOutput += line

#Use the XML parset to find the root of the XML tree
root = ET.fromstring(xmlOutput)
#Fetch the "coount" property of the XML tree (the number of sequences)
count = int(root[0].text)
#Fetch the query key
queryKey = root[3].text
#Fetch the webEnv where the data are stored
webEnv = root[4].text


#We'll get gi no.s in batches of 500.  This is how many batches there are.
#If the number of sequences to fetch isn't exactly divisible by 500, set
#the number of batches to fetch as count / 500 rounded down, + 1
if (count % 500) > 0 :
    batches = int(count / 500) + 1
#If count is exactly divisible by 500, set the number of batches to count/500
else:
    batches = count / 500

#print("Count = ", count)
#print("Batches = ", batches)

#OPen the output file ready for data
with open(outputFileLocation, "a") as file:
    #For each batch
    for x in range (0, int(batches)):
        #Print an info string and then ask for the GI data
        print("Fetching records " + str(x * 500) + " to " + str((x*500) + 499)\
              + " of " + str(count) + " (" +\
              str(round((((x*500) + 499) / count)*100,2)) + " % complete)")
        
        request = urlBase + "efetch.fcgi?db=protein&WebEnv="  + webEnv +\
            "&query_key=" + queryKey + "&retstart=" + str(x * 500) + "&retmax="\
            + "500&rettype=gi&retmode=text"
        
        #Open the HTTP response as "response"
        with urllib.request.urlopen(request) as response:
            #For each line in response, decode it from binary to UTF-8 text
            #and append to the output file
            for line in response:
                line = line.decode("utf-8")
                file.write(line)
        #Limit this to 2 requests per second.  NCBI state they'll possibly
        #block any IP address making more than 3 per second.
        time.sleep(0.5)

        


