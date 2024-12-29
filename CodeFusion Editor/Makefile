name = builder
pwd = $(shell pwd)
user = $(shell whoami)

build:
	mkdir -p dist
	sudo docker build --target final -t $(name) .
	sudo docker run --rm -v "$(pwd)/dist:/dist" $(name)
	sudo chown -R $(user):$(user) "$(pwd)/dist"

clean:
	sudo rm dist/*
