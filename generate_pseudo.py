import random
import json


def is_prime(num):
	for x in range(2, num):
		if (num % x) == 0:
			return False
	return True


list_pseudos = []
with open("pseudos.json", "r", encoding="utf-8") as f:
	list_pseudos = json.load(f)
nums = range(1, 1000)


groupe1 = random.choice(list_pseudos)
groupe2 = random.choice(list_pseudos)
primes = list(filter(is_prime, nums))

while groupe1 == groupe2:
	groupe2 = random.choice(list_pseudos)

mot1 = random.choice(groupe1)
mot2 = random.choice(groupe2)
num = random.choice(primes)

print(f"Pseudo : {mot1}{mot2}{num}")
