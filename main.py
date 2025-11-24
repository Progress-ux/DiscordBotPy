import asyncio
from bot.bot import Bot

def main():
   bot = Bot()
   asyncio.run(bot.run())


if __name__ == "__main__":
   main()