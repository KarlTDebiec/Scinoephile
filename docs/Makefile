PYTHON      = $(shell which python)
SPHINXBUILD = $(shell which sphinx-build)
SPHINXPROJ  = scinoephile

.PHONY: html
html:
	$(PYTHON) $(SPHINXBUILD) -M html "." "."

.PHONY: coverage
coverage:
	$(PYTHON) $(SPHINXBUILD) -M html "." "." -b coverage

.PHONY: full
full:
	cd .. && make
	make html

.PHONY: clean
clean:
	rm -frv html/*
