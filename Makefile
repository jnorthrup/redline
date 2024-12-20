# Makefile for Redline project

.PHONY: all clean lint dce

all: clean

clean:
	rm -rf build dist *.egg-info

lint:
	flake8 redline/*.py

dce:
	@echo "Checking for dead code and unused functions..."
	
	# Python dead code detection with vulture
	vulture redline/ tests/ \
		--min-confidence 80 \
		--exclude "*/__pycache__/*,*/tests/*" \
		--sort-by-size

	# Find unused imports with pyflakes  
	@echo "\nChecking for unused imports..."
	python -m pyflakes redline/
	python -m pyflakes tests/

	# Find unused functions with coverage
	@echo "\nChecking for unused functions..."
	coverage run -m pytest tests/
	coverage report --fail-under=80

	# Static call graph analysis
	@echo "\nGenerating call graph..."
	pycg redline/ --max-iter 1000 > call_graph.txt
	
	# Custom dead call detection
	@echo "\nAnalyzing for dead calls..."
	python -c 'import sys; from pycg.pycg import CallGraphGenerator; g = CallGraphGenerator(["redline/"]); dead = g.get_unused_functions(); print("Dead calls found:", len(dead)); sys.exit(len(dead))'
