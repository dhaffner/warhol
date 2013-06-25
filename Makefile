.PHONY: extension server clean

all: extension server

extension:
	./make-extension

server:
	cd server && python setup.py install;

clean:
	\rm chrome.crx
