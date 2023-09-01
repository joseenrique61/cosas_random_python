def narcissistic( value ):
    lst = list(str(value))
    total = 0
    for num in lst:
        total += int(num)**len(lst)
    return total == value

print(narcissistic(35452590104031691935943))