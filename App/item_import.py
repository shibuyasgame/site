import csv

pin_files = ['']
thread_files = ['']
food_files = ['']

def import_food():
    for files in food_files:
        with open(file) as csvfile:
            r = csv.reader(csvfile, delimiter=',')
            for row in r:
                print(row)
