def is_pangram(s):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for letter in alphabet:
        if s.count(letter) == 0:
            return False
    return True

print(is_pangram("Cwm fjord bank glyphs vext quiz"))