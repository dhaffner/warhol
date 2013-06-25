.PHONY: extension server

all: extension server

extension:
	./load-extension

server:
	python ./server/setup.py install
