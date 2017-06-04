import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from urlparse import urlparse
from slugify import slugify
import isodate
from dateutil import parser as dateutil_parser

from imdb.items import MovieItem


class IMDBSpider(CrawlSpider):
    name = 'imdb'
    allowed_domains = ["imdb.com"]
    start_urls = ["http://www.imdb.com/search/title?year=%d,%d" % (n, n) for n
                  in range(2017, datetime.now().year + 1)]
    domain = 'http://www.imdb.com'

    rules = (
        Rule(
            LinkExtractor(
                allow=(r'search\/title', )
            ),
            follow=True,
            process_links='filter_links'
        ),
        Rule(
            LinkExtractor(
                allow=(r'title\/', ),
                deny=(r'plotsummmary')
            ),
            follow=False,
            callback='parse_item',
            process_links='filter_links'
        ),
    )

    def filter_links(self, links):
        return_links = list()
        if links:
            for link in links:
                if not link.nofollow:
                    return_links.append(link)
        return return_links

    def __get_url(self, response):
        uri = urlparse(response.url)
        url = '%s://%s%s' % (uri.scheme, uri.netloc, uri.path)
        return url

    def __get_title(self, response):
        title = response.css('.title_wrapper > h1::text').extract_first()
        return title.strip() if title else ''

    def __get_content_type(self, response):
        item_type = response.css('div#pagecontent').xpath(
            '@itemtype').extract_first()
        if not item_type:
            return 'Other'
        uri = urlparse(item_type)
        return uri.path.strip('/')

    def __get_description(self, response):
        description = response.css(
            'div[itemprop=description] > p::text'
        ).extract_first()

        return description.strip() if description else ''

    def __get_duration(self, response):
        duration = 0
        _duration = response.css('time[itemprop=duration]').xpath(
            '@datetime').extract_first()
        if _duration:
            duration = isodate.parse_duration(_duration).seconds

        return duration

    def __get_date_published(self, response):
        date_published = datetime.min
        _date_published = response.css(
            'meta[itemprop=datePublished]'
        ).xpath('@content').extract_first()
        if _date_published:
            date_published = dateutil_parser.parse(_date_published)

        return date_published

    def __get_rating(self, response):
        rating = 0
        _rating = response.css(
            'span[itemprop=ratingValue]::text').extract_first()
        if _rating:
            rating = float(_rating)

        return rating

    def __get_vote_count(self, response):
        vote_count = 0
        _vote_count = response.css(
            'span[itemprop=ratingCount]::text').extract_first()
        if _vote_count:
            _vote_count = _vote_count.replace(',', '')
            vote_count = int(_vote_count)

        return vote_count

    def __get_directors(self, response):
        _directors_names = response.css(
            'span[itemprop=director] > a > span::text').extract()
        _directors_urls = response.css(
            'span[itemprop=director] > a').xpath('@href').extract()
        directors = []
        for i, name in enumerate(_directors_names):
            directors.append({
                'name': name,
                'url': '%s%s' % (self.domain, _directors_urls[i])
            })

        return directors

    def __get_writers(self, response):
        _writer_names = response.css(
            '.credit_summary_item span[itemprop=creator] > a > span::text').extract()
        _writer_urls = response.css(
            '.credit_summary_item span[itemprop=creator] > a').xpath('@href').extract()
        writers = []
        for i, name in enumerate(_writer_names):
            writers.append({
                'name': name,
                'url': '%s%s' % (self.domain, _writer_urls[i])
            })
        return writers

    def __get_cast(self, response):
        _cast_names = response.css(
            'td[itemprop=actor] > a > span::text').extract()
        _cast_urls = response.css(
            'td[itemprop=actor] > a').xpath('@href').extract()
        cast = []
        for i, name in enumerate(_cast_names):
            cast.append({
                'name': name,
                'url': '%s%s' % (self.domain, _cast_urls[i])
            })
        return cast

    def __get_color(self, response):
        color = response.css(
            r'a[href*=\/search\/title\?colors]::text'
        ).extract_first()
        return color

    def __get_genres(self, response):
        genres = [x.strip() for x in response.css(
            r'div[itemprop=genre] > a[href*=\/genre]::text'
        ).extract()]
        return genres

    def __get_country(self, response):
        country = response.css(
            r'a[href*=\/search\/title\?country_of_origin]::text'
        ).extract_first()
        return country

    def __get_language(self, response):
        lang = [x.strip() for x in response.css(
            r'a[href*=primary_language]::text'
        ).extract()]
        return lang

    def __get_keywords(self, response):
        keywords = response.css(
            r'div#keywords_content a[href*=\/keyword\/]::text'
        ).extract()
        return [x.strip() for x in keywords]

    def __get_filming_locations(self, response):
        locations = response.css(
            r'div#filming_locations_content a[href*=locations]::text'
        ).extract()
        return [x.strip() for x in locations]

    def parse_filming_locations(self, response):
        item = response.meta['item']
        item['locations'] = self.__get_filming_locations(response)
        next_request = response.meta.get('next_request')
        if next_request:
            request = scrapy.Request(
                next_request['url'],
                callback=next_request['callback']
            )
            request.meta['item'] = item
            yield request
        else:
            yield item

    def parse_keywords(self, response):
        item = response.meta['item']
        item['keywords'] = self.__get_keywords(response)
        yield item

    def parse_item(self, response):
        url = self.__get_url(response)
        title = self.__get_title(response)
        date_published = self.__get_date_published(response)
        year = date_published.year

        if title:
            self.logger.info('Url: %s, Title: %s, Year: %s' %
                             (url, title, year))
            item = MovieItem()
            item['_id'] = slugify('%s - %s' % (title, year))
            item['modified_date'] = datetime.utcnow()
            item['content_type'] = self.__get_content_type(response)
            item['title'] = title
            item['url'] = url
            item['description'] = self.__get_description(response)
            item['duration'] = self.__get_duration(response)
            item['date_published'] = date_published
            item['rating'] = self.__get_rating(response)
            item['vote_count'] = self.__get_vote_count(response)
            item['directors'] = self.__get_directors(response)
            item['writers'] = self.__get_writers(response)
            item['cast'] = self.__get_cast(response)
            item['color'] = self.__get_color(response)
            item['genres'] = self.__get_genres(response)
            item['country'] = self.__get_country(response)
            item['language'] = self.__get_language(response)

            filming_locations_url = response.css(
                r'a[href*=locations]'
            ).xpath('@href').extract_first()

            keywords_url = response.css(
                r'a[href*=keywords]'
            ).xpath('@href').extract_first()

            if filming_locations_url:
                request = scrapy.Request(
                    '%s%s' % (self.domain, filming_locations_url),
                    callback=self.parse_filming_locations
                )
                request.meta['item'] = item
                if keywords_url:
                    request.meta['next_request'] = {
                        'url': '%s%s' % (self.domain, keywords_url),
                        'callback': self.parse_keywords
                    }
                    keywords_url = None
                yield request

            if keywords_url:
                request = scrapy.Request(
                    '%s%s' % (self.domain, keywords_url),
                    callback=self.parse_keywords
                )
                request.meta['item'] = item
                yield request
