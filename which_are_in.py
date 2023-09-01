def in_array(array1, array2):
    lst = set()
    for a2 in array2:
        for a1 in array1:
            if a1 in a2:
                lst.add(a1)
    
    return sorted(list(lst))

print(in_array(["cod", "code", "wars", "ewar", "pillow", "bed", "phht"], ["lively", "alive", "harp", "sharp", "armstrong", "codewars", "cod", "code"]))