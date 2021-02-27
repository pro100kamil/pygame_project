with open('пояcнения к карте.txt', encoding='utf-8') as file:
    for line in file:
        s = line.strip().split(' - ')
        if len(s) == 2:
            a, b = s
            print(f"'{a}': {b},")
