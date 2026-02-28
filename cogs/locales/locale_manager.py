import json
import os
from typing import Dict
from discord.ext import commands

class LocaleManager:
   def __init__(self, bot):
      self.bot = bot,
      self.locales: Dict[str, Dict] = {}
      self.guild_locales: Dict[int, str] = {}
      self.locales_path = os.path.dirname(__file__)
      self._load_locales()
      self._load_guild_settings()

   def _load_locales(self):
      for filename in os.listdir(self.locales_path):
         if not filename.endswith('.json'):
            continue
         if filename in ['guild_settings.json']:
            continue

         file_path = os.path.join(self.locales_path, filename)
         if os.path.isdir(file_path):
            continue

         lang_code = filename.replace('.json', '')

         try:
            with open(file_path, 'r', encoding='utf-8') as f:
               self.locales[lang_code] = json.load(f)
            print(f"Loaded locale: {lang_code}")
         except json.JSONDecodeError as e:
            print(f"Failed to parse JSON for locale {lang_code}: {e}")
         except Exception as e:
            print(f"Failed to load locale: {lang_code}: {e}")

   def _load_guild_settings(self):
      setting_file = os.path.join(self.locales_path, 'guild_settings.json')
      if os.path.exists(setting_file):
         try:
            with open(setting_file, 'r', encoding='utf-8') as f:
               self.guild_locales = { int(k): v for k, v in json.load(f).items() }
            print(f"Loaded guild language settings for {len(self.guild_locales)} servers")
         except Exception as e:
            print(f"Failed to load guild settings: {e}")

   def _save_guild_settings(self):
      settings_file = os.path.join(self.locales_path, 'guild_settings.json')
      try:
         with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.guild_locales, f, ensure_ascii=False, indent=2)
      except Exception as e:
         print(f"Failed to save guild settings: {e}")
   
   def get_guild_locale(self, guild_id: int) -> str:
      return self.guild_locales.get(guild_id, 'eng')
   
   def set_guild_locale(self, guild_id: int, language: str):
      if language in self.locales:
         self.guild_locales[guild_id] = language
         self._save_guild_settings()
         return True
      return False
   
   def get_text(self, guild_id: int, key: str, **kwargs) -> str:
      lang = self.get_guild_locale(guild_id)
      locale_data = self.locales.get(lang, self.locales['eng'])

      parts = key.split('.')
      value = locale_data

      for part in parts:
         if isinstance(value, dict):
            value = value.get(part)
         else:
            value = None
            break

      if value is None:
         value = self.locales['eng']
         for part in parts:
            if isinstance(value, dict):
               value = value.get(part)
            else: 
               return key
            
      if kwargs and isinstance(value, str):
         try:
            return value.format(**kwargs)
         except KeyError:
            return value
         
      return value if isinstance(value, str) else key
   
   def get_available_languages(self) -> Dict[str, str]:
      return {
         'eng': 'English',
         'rus': 'Русский'
      }