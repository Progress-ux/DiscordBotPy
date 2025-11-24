class NoWarningLogger:
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

YDL_OPTIONS = {
    "logger": NoWarningLogger(),
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'ignoreerrors': True, 
    'cachedir': False,
    # "extractor_args": {
    #     "youtube": {
    #         "player_client": ["default"]
    #     }
    # },
}