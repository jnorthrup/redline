# Makefile for Redline project

.PHONY: all clean lint dce

all: clean

clean:
	rm -rf build dist *.egg-info

lint:
	flake8 redline/*.py

dce:
	vulture redline/ tests/ status_line.py supervisor.py
	ts-unused-exports redline/**/*.ts src/**/*.ts
