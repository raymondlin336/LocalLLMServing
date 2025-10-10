import re

class Log:

    @staticmethod
    def print_title(text):
        print("=" * 30, text)

    @staticmethod
    def print_subtitle(text):
        print("-" * 10, text)

    @staticmethod
    def print_model_output(text):
        print(text.replace("<think>\n\n", "").replace("</think>\n\n", ""), end="\n")

    @staticmethod
    def return_model_output(text):
        return text.replace("<think>\n\n", "").replace("</think>\n\n", "")

    @staticmethod
    def print_message(text):
        print(text)
