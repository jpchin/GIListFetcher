# GIListFetcher
Get all proteins of a GI from NCBI using a taxon number


A script to take an input taxon number and fetch all proteins for that
organism from the NCBI protein database.  NCBI state that this sort of
operation is most efficient when you request the data to be posted to their
History server first, and then download that data in batches.  This script
is intended to be run from the command line, with the taxon number as the first
argument, and the output file location as the second
(e.g. pthon3 GIListFetcher.py 2157 C:\Users\user\Desktop\allArchaea.gi)



TODO:
* Clean up comments to be more clear
* Make it parse the command line arguments properly so that they can be
entered in any order, and fail gracefully if an invalid value is given
* Add the possibility of API numbers being added, and if so allow a faster
rate of data requests (See the NCBI eUtilities manual for details)
