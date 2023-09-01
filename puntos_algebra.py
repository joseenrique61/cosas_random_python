puntos = [[1,3,4,2], [2,1,3,6]]
lineas = [[1,1,1,2,3], [2,3,4,3,4]]

def polygon(pts, lns):
    for i, j in zip(lns[0], lns[1]):
        print(f"Segmento(({pts[0][i - 1], pts[1][i - 1]}),({pts[0][j - 1], pts[1][j - 1]}))")

def escala(c, eje):
    if not isinstance(c, int):
        if eje == "x":
            return [[f"c{i}" for i in puntos[0]], puntos[1]]
        else:
            return [puntos[0], [f"c{i}" for i in puntos[1]]]
    else:
        if eje == "x":
            return [[i * c for i in puntos[0]], puntos[1]]
        else:
            return [puntos[0], [i * c for i in puntos[1]]]

def reflexion():
    return [puntos[1], puntos[0]]

def cortes(c, eje):
    if not isinstance(c, int):
        if eje == "x":
            return [[f"{i} + c{j}" for i, j in zip(puntos[0], puntos[1])], puntos[1]]
        else:
            return [puntos[0], [f"{i} + c{j}" for i, j in zip(puntos[1], puntos[0])]]
    else:
        if eje == "x":
            return [[i + j * c for i, j in zip(puntos[0], puntos[1])], puntos[1]]
        else:
            return [puntos[0], [i + (j * c) for i, j in zip(puntos[1], puntos[0])]]

def imprimir(letra, pts_original, pts):
    string = letra
    string += "\left(\\begin{matrix}"
    string += f"{pts_original[0]}\\\\{pts_original[1]}"
    string += "\\\\\\end{matrix}\\right)=\\left(\\begin{matrix}"
    string += f"{pts[0]}\\\\{pts[1]}"
    string += "\\\\\\end{matrix}\\right)"
    print(string)

esc = "c"
ej = "y"
ltr = "Ty"

def imprimir_varios(letra, pts: list):
    for i in range(0, len(pts[0])):
        imprimir(letra, [puntos[0][i], puntos[1][i]], [pts[0][i], pts[1][i]])

imprimir_varios(ltr, cortes(esc, ej))