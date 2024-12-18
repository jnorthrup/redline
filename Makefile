.PHONY: clean build install test dev-install

clean:
	pip install hatch
	hatch clean

build:
	pip install hatch
	hatch build

install:
	pip install hatch
	pip install .

test:
	pip install hatch
	pip install '.[test]'
	hatch run test:test llm_connector/tests llm_connector/gnarl/tests

dev-install:
	pip install hatch
	pip install -e '.[test]'
