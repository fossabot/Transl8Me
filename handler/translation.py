"""this is a module docstring"""
from datadog import initialize, statsd
from textblob import TextBlob
from googletrans import Translator
import discord


class TranslateMe:
    """Class supplying translation related methods"""

    lang_counts = {"de": 0, "fr": 0, "en": 0, "ru": 0, "other": 0}

    def __init__(self, config):
        self.src_lang = ""
        self.config = config

        # metrics
        if self.config["global_settings"]["datadog_metrics"]:
            options = {"statsd_host": "127.0.0.1", "statsd_port": 8125}
            initialize(**options)

    def get_language(self, text):
        """method to extract the language of a given text"""
        lang = TextBlob(text)
        self.src_lang = lang.detect_language()

        return self.src_lang

    def translate_text(self, text, valid_languages: list) -> dict:
        """method to translate a given text based on the supplied language code"""
        t = Translator()
        translations = {}
        lang_count = 1

        if self.src_lang in valid_languages:
            for lang_id in self.lang_counts:
                if lang_id == self.src_lang:
                    self.lang_counts[lang_id] += 1
            valid_languages.remove(self.src_lang)

            for lang in valid_languages:
                result = t.translate(text, lang)
                translations[lang_count] = result
                lang_count += 1
        else:
            self.lang_counts["other"] += 1

        return translations

    def generate_embed(self, message):
        """Method to manage the translation"""
        valid_languages = ["de", "en", "fr", "ru"]
        trans_messages = self.translate_text(message.content, valid_languages)

        if trans_messages != {}:
            statsd.increment("translated_msg", tags=["environment:develop"])
            translate_embed = discord.Embed(
                colour=discord.Colour(0x4A90E2),
                description=f"{trans_messages[1].text} \n\n "
                f"{trans_messages[2].text} \n\n"
                f"{trans_messages[3].text}",
            )

            result = {
                "embed": translate_embed,
            }
        else:
            result = {
                "embed": None,
            }

        return result

    def get_language_counts(self):
        """Method to acquire language counts and other language usage related params"""
        return self.lang_counts
