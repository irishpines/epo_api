companies = []
with open("companies.txt", "r") as f:
    for line in f.readlines():
        print(line, type(line))
        companies.append(line.strip())
print(companies)
