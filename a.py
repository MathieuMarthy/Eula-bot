nombre = 15

for i in range(0, nombre, 10):
    i = i if i < nombre else nombre
    print(i, i+10)
