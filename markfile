.PHONY: install uninstall test clean

install:
	sudo ./install.sh

uninstall:
	sudo ./uninstall.sh

test:
	./test.sh

docker-build:
	docker build -t wifi-demon .

docker-run:
	docker run --rm -it --privileged --network host wifi-demon

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -f handshake_* scan_results* *.cap *.csv *.netxml

lint:
	flake8 wifi_demon.py
	pylint wifi_demon.py

package:
	zip -r wifi-demon.zip . -x "*.git*" "*.pyc" "__pycache__/*"
