
import urllib.request
import xml.etree.ElementTree as ET
import time
import sys

def fetchGIs(arguments):
    print(arguments)
    numArgs = len(arguments)
    taxID = ""
    outputFileLocation = ""
    apiKeyLocation = ""
    apiKey = ""

    while (numArgs > 0):
        if arguments[0] == "-taxid":
            taxID = str(arguments[1])
            del arguments[0:2]
            numArgs -= 2
        elif arguments[0] == "-out":
            outputFileLocation = arguments[1]
            del arguments[0:2]
            numArgs -= 2
        elif (arguments[0] == "GIListFetcher.py"):
            del arguments[0]
            numArgs -= 1
        elif (arguments[0] == "-api"):
            apiKeyLocation = arguments[1]
            del arguments[0:2]
            numArgs -= 2
        else:
            print("Error, argument " + arguments[0] + " is not valid.")
            time.sleep(1)

    if (apiKeyLocation != ""):
        with open(apiKeyLocation, "r") as apiKeyFile:
            apiKey = apiKeyFile.read()
            print("Using API key " + apiKey)


    #Insert the first argument as the taxon number to search
    query = "txid" + taxID + "[organism]"

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

    if (apiKey != ""):
        delay = 0.11
    else:
        delay = 0.35

    #Open the output file ready for data
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

            if (apiKey != ""):
                request += "&api_key=" + apiKey
        
            #Open the HTTP response as "response"
            with urllib.request.urlopen(request) as response:
                #For each line in response, decode it from binary to UTF-8 text
                #and append to the output file
                for line in response:
                    line = line.decode("utf-8")
                    file.write(line)
            #Limit this to 2 requests per second.  NCBI state they'll possibly
            #block any IP address making more than 3 per second.
            time.sleep(delay)

if __name__ == "__main__":
    taxid = input("Please type a taxID to search: ")
    outputFileLocation = input("Please type an output file location: ")
    apiKeyLocation = input("If you have an eUtils API key please type the location of the file here\
, otherwise hit enter to skip: ")
    arguments = ["-taxid", taxid, "-out", outputFileLocation, "-api", apiKeyLocation]
    fetchGIs(arguments)
