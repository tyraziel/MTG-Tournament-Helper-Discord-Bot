import requests
import urllib.parse
import json
import time

class Tournament:
    tournament_data = {}

    def __init__(self):
        something = 0

    def writeToFile(self):
        the_json = json.dumps(the_object)
        with open("tournament.json") as outfile:
            outfile.write(the_json)

    @static
    def loadFromFile(filename : str):
        with open(filename, 'r') as the_file:
            the_object = json.load(the_file)
        return Tournament()

    def createMoxfieldConstructsForParticipantDeckLists(self):
        return

    def __str__(self):
        return f"""Bot Cache Statistics: (hits / misses / items)
        uniqueListCache       {self.uniqueListCacheStats['cacheHit']} / {self.uniqueListCacheStats['cacheMiss']} / {len(self.uniqueListCache)}
        scryFallJSONCardCache {self.scryFallJSONCardCacheStats['cacheHit']} / {self.scryFallJSONCardCacheStats['cacheMiss']} / {len(self.scryFallJSONCardCache)}
        imageCache            {self.imageCacheStats['cacheHit']} / {self.imageCacheStats['cacheMiss']} / {len(self.imageCache)}

Bot Fetch Statistics: (fetches (failures)/ total time)
        uniqueListFetch       {self.uniqueListFetchStats['fetchCount']} ({self.uniqueListFetchStats['fetchFailures']}) / {self.uniqueListFetchStats['timeFetching']}
        scryFallJSONCardFetch {self.scryFallJSONCardFetchStats['fetchCount']} ({self.scryFallJSONCardFetchStats['fetchFailures']}) / {self.scryFallJSONCardFetchStats['timeFetching']}
        imageFetch            {self.imageFetchStats['fetchCount']} ({self.imageFetchStats['fetchFailures']}) / {self.imageFetchStats['timeFetching']}
        """