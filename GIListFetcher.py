import urllib.request
import xml.etree.ElementTree as ET
import time
import sys



def fetchGIs(arguments):
    numArgs = len(arguments)
    taxID = ""
    outputFileLocation = ""
    apiKeyLocation = ""
    apiKey = ""

    #################################################################
    # Get and process the inputs which define which GIs to look for #
    #################################################################

    #If this is being run standalone, interactively get the search details
    if __name__ == "__main__":
        #Stuff for file selection dialogue boxes:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()

        #Get a taxID to search
        taxID = input("\nPlease type a taxID to search: ")

        #Get a file location to save the output data
        gettingLocation = True
        while (gettingLocation == True):
            print("\nPlease choose an output file location and file name: ")
            outputFileLocation = filedialog.asksaveasfilename()
            try:
                file = open(outputFileLocation,"w")
                gettingLocation = False
            except IOError:
                print("Sorry, I'm unable to open that file location.")

        #Ask for an api key
        gettingKey = True
        while (gettingKey == True):
            apiInput = input("\nDo you have an NCBI eTools API key?  This is not\
 required but speeds up the rate at which requests can be made.  If you have one\
 type 'y', otherwise type 'n' to skip.")
            if (apiInput == "n"):
                gettingKey = False
            elif (apiInput == "y"):
                print("\nPlease select a file containing your API key: it should be\
 a plain text document with any name containing ONLY your key.")
                apiKeyLocation = filedialog.askopenfilename()
                try:
                    if (apiKeyLocation != ""):
                        file = open(outputFileLocation,"r")
                        apiKey = file.read()
                        gettingKey = False
                    else:
                        print("Sorry, I'm unable to open that file.")
                except IOError:
                    print("Sorry, I'm unable to open that file.")
                    pass
            else:
                print("\nSorry, I didn't recognise that.  Please type 'y' if you\
have an API key or 'n' if you don't.")
    
        #Use the gathered information to create a list of arguments
        arguments = ["-taxid", taxID, "-out", outputFileLocation]
        #If an api key was provided, add that too
        if (apiKeyLocation != ""):
            print("Using API key " + apiKey)
            arguments += ["-api", apiKey]
    
    #If not being run standalone (i.e. has been imported into another script) get the details via an arguments list
    else:      
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


    ###########################################################################
    # Ask NCBI to move the list of GIs for that taxon into the History server #
    ###########################################################################

    #Create an empty string for XML formmated output of the web requests
    xmlOutput = ""

    #Get the human-readable name of the taxon being searched for and print it
    urlNameBase =  "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id="
    url = urlNameBase + taxID
    with urllib.request.urlopen(url) as response:
            #For each line in response, decode it from binary to UTF-8 text and
            #append to the xmlOutput string
            for line in response:
                line = line.decode("utf-8")
                xmlOutput += line
    #Use the XML parser to find the root of the XML tree
    root = ET.fromstring(xmlOutput)
    #Fetch the "ScientificName" property of the XML tree
    taxon = root[0][1].text
    print("Fetching proteins from organisms  with the taxonomic ID of " + taxID + " (" + taxon + ")")
    #Clear xmlOutput for later use
    xmlOutput = ""

    #Insert the first argument as the taxon number to search
    query = "txid" + taxID + "[organism]"

    #The base URL for eutils requests
    urlBase = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    url = urlBase + "esearch.fcgi?db=protein&term=" + query + "&usehistory=y"


    with urllib.request.urlopen(url) as response:
            #For each line in response, decode it from binary to UTF-8 text and
            #append to the xmlOutput string
            for line in response:
                line = line.decode("utf-8")
                xmlOutput += line

    #Use the XML parser to find the root of the XML tree
    root = ET.fromstring(xmlOutput)
    #Fetch the "count" property of the XML tree (the number of sequences in the requested GI list)
    count = int(root[0].text)
    #Fetch the query key
    queryKey = root[3].text
    #Fetch the webEnv where the data are stored
    webEnv = root[4].text
    
    #We'll get GI numbers in batches of 500.  This is how many batches there are.
    #If the number of sequences to fetch isn't exactly divisible by 500, set
    #the number of batches to fetch as count / 500 rounded down, + 1
    if (count == 0):
        print("\nERROR! This taxon has no proteins associated with it.  Please check the NCBI taxonomy database.")
        return 1
    elif (count % 500) > 0 :
        batches = int(count / 500) + 1
    #If there are fewer than 500 sequences to get, set batches to "1"
    elif (count < 500) :
        batches = 1
    #Otherwise the count is exactly divisible by 500, so set the number of batches to count/500
    else:
        batches = count / 500
 
    #Set the delay (in seconds) between requests.  API keys enable a greater rate of requests.
    if (apiKey != ""):
        delay = 0.11
    else:
        delay = 0.35

    ###############################################################################
    # Fetch the requested data in batches of 500, append these to the output file #
    ###############################################################################

    #Open the output file ready for data
    with open(outputFileLocation, "a") as file:
        #For each batch
        for x in range (0, batches):
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
            #Wait for the proscribed amount of time before making another request (see the section above)
            time.sleep(delay)
    print("Done!")
    return 0

if __name__ == "__main__":
    fetchGIs([])
