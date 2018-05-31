# GIListFetcher
Get all proteins of a GI from NCBI using a taxon number


A script to take an input taxon number and fetch all proteins for that
taxon from the NCBI protein database.  Has an option for providing an NCBI E Utilities API key for faster data download, or falls back to slower downloads if one isn't present.

This script was written in Python3 and **requires** an internet connection, but does not use any modules from outside the Python standard library.

CURRENT STATE:

It works, but I can think of several errors it won't handle gracefully, and there are probably a lot of bugs to be irons out.

TODO:
* Resilience and bugfixing
