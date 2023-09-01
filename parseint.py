numbers = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
modifiers = {"hundred": 100, "thousand": 1000, "million": 1000000}

def parse_int(string):
    str_split = string.split()
    return operation(str_split)

def operation(str_split):
    final = 0
    for i, split in enumerate(str_split):
        if split == "and":
            continue
            
        if (mod := modifiers.get(split, -1)) != -1:
            final *= mod
            final += operation(str_split[i + 1:])
            break
            
        if "-" in split:
            final += numbers[split.split("-")[0]] + numbers[split.split("-")[1]]
            continue
        
        final += numbers[split]
    return final

print(parse_int('six hundred sixty-six thousand six hundred sixty-six'))