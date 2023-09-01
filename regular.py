import re

print(re.match(r"\s?((CAP[IÍ]TULO)|(CHAPTER):?\s?[\dIVXLCDM]+\b)|(\b[\dIVXLCDM]+\b)",
               " Chapter 1: Prologue - Three Ways to Survive in a Ruined  World".upper()))