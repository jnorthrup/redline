# Makefile for Redline project

.PHONY: all clean lint

all: clean

clean:
	rm -rf build dist *.egg-info

lint:
	flake8 redline/*.py
