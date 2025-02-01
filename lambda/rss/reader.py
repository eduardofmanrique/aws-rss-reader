import feedparser
import hashlib
import time
from datetime import datetime
from typing import Any


class RssReader:
    def __init__(self,
                 feeder_name: str,
                 url: str,
                 entries_parameters: dict,
                 top_entries: int = 10):
        self.feeder_name = feeder_name
        self.url = url
        self.entries_parameters = entries_parameters
        self.top_entries = top_entries

    def parse(self) -> feedparser.FeedParserDict:
        return feedparser.parse(self.url)

    def get_nested_value(self, obj: Any, key: str) -> Any:
        keys = key.split('.')
        for k in keys:
            if isinstance(obj, list):
                try:
                    obj = obj[int(k)]
                except (ValueError, IndexError):
                    return None
            else:
                obj = obj.get(k, None)
            if obj is None:
                return None
        return obj

    def select_entries(self, entries: feedparser.FeedParserDict) -> list[dict]:
        return_entries = []
        current_time = datetime.utcnow()

        for entry in entries.entries:
            return_entries_dict = {'id': hashlib.md5(entry.link.encode('utf-8')).hexdigest()}

            published_parsed = getattr(entry, 'published_parsed', None)
            entry_time = datetime.fromtimestamp(time.mktime(published_parsed)) if published_parsed else current_time

            if entry_time.date() != current_time.date():
                continue

            return_entries_dict['info'] = {
                'Data': entry_time,
            }

            for entry_old_name, entry_new_name in self.entries_parameters.items():
                value = self.get_nested_value(entry, entry_old_name)
                return_entries_dict['info'][entry_new_name] = value

            return_entries.append(return_entries_dict)

        return sorted(return_entries, key=lambda x: x['info']['Data'], reverse=True)[:self.top_entries]

    def full_parse(self):
        entries = self.parse()
        return self.select_entries(entries=entries)


if __name__ == '__main__':
    url = "https://news.google.com/rss/search?q=GTA+6+(release+OR+launch+OR+date)&ceid=US:en&hl=en-US&gl=US"
    entries_parameters = {
        'title': 'Título',
        'link': 'Link',
        'media_content.0.url': 'image'
    }

    rss_reader = RssReader(
        feeder_name="Investing News",
        url=url,
        entries_parameters=entries_parameters,
        top_entries=10
    )

    parsed_entries = rss_reader.full_parse()

    for entry in parsed_entries:
        print(entry)
