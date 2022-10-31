from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler


import os



def main(config_file, restart):
    #DANE ADDITION, NUKES OLD SAVES dane-crawler4py/frontier.shelve.dir
    if restart == True and os.path.exists("/home/ics-home/dane-crawler4py/frontier.shelve.bak"):
        print("NUKING old stuff")
        os.remove("/home/ics-home/dane-crawler4py/frontier.shelve.bak")
        os.remove("/home/ics-home/dane-crawler4py/frontier.shelve.dat")
        os.remove("/home/ics-home/dane-crawler4py/frontier.shelve.dir")

        #reset the urls and words txt files
        f = open("urls.txt", "w")
        f.write("")
        f.close()
        f = open("word_freqs.txt", "w")
        f.write("")
        f.close()

    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)
    crawler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
