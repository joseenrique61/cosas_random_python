def same_structure_as(original,other):
    try:
        if len(original) != len(other):
            return False
        
        for element1, element2 in zip(original, other):
            if type(element1) != type(list()) and type(element2) != type(list()):
                continue
            elif (type(element1) == type(list()) and type(element2) != type(list())) or (type(element1) != type(list()) and type(element2) == type(list())):
                return False
            
            if not same_structure_as(element1, element2):
                return False
                
        return True
    except:
        return False

print(same_structure_as([],{}))