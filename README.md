# scrapy_imdb
IMDB Movie/Series Parser with Scrapy

"pip install -r requirements.txt"  
"cd imdb"  
"scrapy crawl imdb"

MongoDB Connection String is in imdb/settings.py  
You can change pipelines with the same settings file

To parse single url "scrapy parse http://www.imdb.com/title/tt3920596/ -c parse_item --pipelines --depth=10"
