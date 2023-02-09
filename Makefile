
build:
	docker build -t birdbuddy .

run: build
	docker run -it --rm --name birdbuddy birdbuddy