import csv
from pathlib import Path

home = str(Path.home())
print(home)

with open(home + '/Desktop/punedb.csv') as csv_file:
    rows = csv.reader(csv_file, delimiter=',')
    for row in rows:
        print(row[-1])
        
