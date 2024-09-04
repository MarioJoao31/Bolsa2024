from gurobipy import *

maquinas = (1,2,3,4)
productos = (1,2,3)
# Secuencia: {Producto: [Maquina i, Maquina j...] }
secuencia={1:[1,3,4],2:[1,2,4],3: [2,3]}
# Tiempo (producto, maquina)
tiempo ={(1, 1): 30,
(1, 3): 40,
(1, 4): 20,
(2, 1): 25,
(2, 2): 25,
(2, 4): 10,
(3, 2): 10,
(3, 3): 30,
(3, 4): 10}
arcos = [(i,j) for i in productos for j in secuencia[i]]
print(arcos)