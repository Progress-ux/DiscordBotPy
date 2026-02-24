class NoWarningLogger:
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

# Setting up for searching by video link
YDL_OPTIONS = {
    "logger": NoWarningLogger(),
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'nocheckcertificate': True,
    'verbose': True,
    'ignoreerrors': True, 
    'cachedir': False,
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us,en;q=0.5",
        "Sec-Fetch-Mode": "navigate"
    },
    "extractor_args": {
        "youtube": {
            "player_client": ["default", 'android','web']
        }
    },
}

# Setting up to search by video title
YDL_OPTIONS_FROM_TITLE = { 
    "logger": NoWarningLogger(),
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'nocheckcertificate': True,
    'verbose': True,
    'ignoreerrors': True, 
    'cachedir': False,
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us,en;q=0.5",
        "Sec-Fetch-Mode": "navigate"
    },
    "extractor_args": {
        "youtube": {
            "player_client": ["default", 'android','web']
        }
    },
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}