black:
	find src -name '*.py' | xargs black --safe $(ARGS)

isort:
	isort -rc src

lint: isort black
