sp = [1, 2, 3, 4, 5, 6, 7, 8, 9]
sp = [sp[i:i+2] for i in range(0, len(sp), 2)]
print(sp[:-1])