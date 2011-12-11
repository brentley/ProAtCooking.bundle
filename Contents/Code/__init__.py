import re

####################################################################################################

PROATCOOKING_PREFIX  = "/video/proatcooking"
PROATCOOKING_URL     = "http://www.proatcooking.com/"
PROATCOOKING_RSS_URL = "http://proatcooking.blip.tv/rss"
MEDIA_NAMESPACE      = {'media':'http://search.yahoo.com/mrss/'}
BLIP_NAMESPACE       = {'blip':'http://blip.tv/dtd/blip/1.0'}
DEBUG_XML_RESPONSE   = False

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PROATCOOKING_PREFIX, MainMenu, L("proatcooking"), "icon-default.png", "art-default.png")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  MediaContainer.content = 'Items'
  MediaContainer.title1 = 'Pro At Cooking'
  MediaContainer.art = R("art-default.png")


def MainMenu():

  # Top level menu
  # Show available episodes

  dir = MediaContainer()

  page = XML.ElementFromURL(PROATCOOKING_RSS_URL, cacheTime=CACHE_1HOUR)

  episodes = page.xpath("//channel/item")

  # We store the episodes into a dictionary so we can reorder it

  episodeDict = dict()

  for episode in episodes:

    episodeFullTitle = episode.xpath("./title/text()")[0]
    # Strip 'Pro at Cooking' from the title
    episodeTitle = re.search(r'(Pro at Cooking )?(.*)', episodeFullTitle).group(2)
    # Find the episode number from the title
    episodeNumber = re.search(r'Episode\s*(\d+)$', episodeFullTitle).group(1)

    # Get the description
    episodeFullDescription = TidyString(episode.xpath("./blip:puredescription/text()", namespaces=BLIP_NAMESPACE)[0])
    # Strip out just the first part
    episodeDescription = re.search(r'^([^\.]+)\.', episodeFullDescription).group(1)
    episodeTitle = episodeTitle + " : " +  episodeDescription

    episodeImage = episode.xpath("./media:thumbnail", namespaces=MEDIA_NAMESPACE)[0].get('url')

    episodeFlv = episode.xpath("./enclosure")[0].get('url')

    episodeLengthSeconds = episode.xpath("./blip:runtime/text()", namespaces=BLIP_NAMESPACE)[0]
    episodeLength = str(int(episodeLengthSeconds) * 1000)

    video = VideoItem(episodeFlv, title=episodeTitle, duration=episodeLength, thumb=episodeImage)

    episodeDict[episodeNumber] = video

  # Now append the videos in a sorted order
  for key in sorted(episodeDict.keys(), reverse=True):
    dir.Append(episodeDict[key])


  if DEBUG_XML_RESPONSE:
    PMS.Log(dir.Content())
  return dir


def TidyString(stringToTidy):
  # Function to tidy up strings works ok with unicode, 'strip' seems to have issues in some cases so we use a regex
  if stringToTidy:
    # Strip new lines
    stringToTidy = re.sub(r'\n', r' ', stringToTidy)
    # Strip leading / trailing spaces
    stringSearch = re.search(r'^\s*(\S.*?\S?)\s*$', stringToTidy)
    if stringSearch == None: 
      return ''
    else:
      return stringSearch.group(1)
  else:
    return ''
