distancias = """764.13 m
855.47 m
340.39 m
479.73 m
672.21 m
373.51 m
393.81 m
531.69 m
638.57 m
432.93 m
451.24 m
400.36 m
339.91 m
349.48 m
536.25 m
357.87 m
672.74 m
595.44"""

lst = distancias.split(" m\n")
suma = 0
for i in lst:
    suma += float(i)
print(suma)