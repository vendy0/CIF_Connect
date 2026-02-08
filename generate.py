import random

def generate_pseudos(words, limit=10000):
	results = set()
	while len(results) < limit:
		m1 = random.choice(words["mots1"])
		m2 = random.choice(words["mots2"])
		num = random.choice(words["nombres"])
		results.add(f"{m1}{m2}{num}")
	return list(results)

# Exemple
words = {
	"mots1": ["Lion","Aigle","Neg","Kreyol","Ayiti","Urban","Leader","Force"],
	"mots2": ["Fort","Libre","Fier","Actif","Calme","Puissant","Royal"],
	"nombres": [1,5,7,9,10,23,33,44,509]
}

pseudos = generate_pseudos(words, 10000)
print(pseudos)