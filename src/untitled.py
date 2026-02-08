from generate_pseudo import generer


def get_initials():
	pseudo = generer()
	initials = ""
	for i in pseudo:
		if i.isupper():
			initials += i
			if len(initials) == 2:
				break
	print(f"Pseudo : {pseudo}")
	print(f"Initials : {initials}")
	return initials


if __name__ == "__main__":
	get_initials()
