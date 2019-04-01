import csv
from app.models import Ticker
from app import db

with open('Constituents_csv.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	i = 0
	for row in csv_reader:
		t = Ticker(id=i, symbol=row[0], name=row[1], sector=row[2])
		db.session.add(t)
		db.session.commit()
		print("Commited to the database:")
		print(t.symbol, t.name, t.sector)
		print("\n")
		i = i + 1




