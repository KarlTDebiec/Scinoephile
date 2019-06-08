PYTHON      = $(shell which python)
SPHINXBUILD = $(shell which sphinx-build)
SPHINXPROJ  = scinoephile

.PHONY: html
html:
	$(PYTHON) $(SPHINXBUILD) -M html "." "." $(O)

.PHONY: full
full:
	cd .. && make
	make html

.PHONY: clean
clean:
	rm -frv html/*
