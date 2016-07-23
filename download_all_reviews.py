import sys
import urllib2
from itertools import count

from toolbox.log import setup_custom_logger, INFO
from toolbox.tor import setup_tor

logger = setup_custom_logger('scrape', level=INFO)

logger.info('setting up Tor...')
setup_tor()

for id in count(1):
    try:
        url = 'http://allrecipes.com/recipe/getreviews/?recipeid=' + str(id) + '&pagenumber=1&pagesize=-1&recipeType=Recipe&sortBy=MostHelpful'
        page = urllib2.urlopen(url)

        filename = str(id) + '.html'
        with open(filename, 'w') as fh:
            fh.write(page.read())
            logger.info("Saved %s" % filename)
    except:
        logger.error("Failed to scrape %d" % id)
        e = sys.exc_info()[0]
        print(str(e))
        continue
