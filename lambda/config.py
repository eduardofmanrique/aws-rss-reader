rss_readers_kwargs = [
    {
        'feeder_name': 'Google News',
        'url': 'https://news.google.com/rss/search?q=GTA+6+(release+OR+launch+OR+date)&ceid=US:en&hl=en-US&gl=US',
        'entries_parameters' : {
            'title': 'Título',
            'link': 'Link'
        },
        'top_entries': 5
    },
    {
        'feeder_name': 'G1 Economia',
        'url': 'https://g1.globo.com/rss/g1/economia/',
        'entries_parameters': {
            'title': 'Título',
            'link': 'Link',
            'media_content.0.url': 'image'
        },
        'top_entries': 5
    }
]