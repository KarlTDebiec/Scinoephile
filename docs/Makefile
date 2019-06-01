PYTHON      = $(shell which python)
SPHINXBUILD = $(shell which sphinx-build)
SPHINXPROJ  = scinoephile
SOURCEDIR   = .
BUILDDIR    = build

.PHONY: html
html:
	$(PYTHON) $(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(O)

.PHONY: full
full:
	cd .. && make
	$(PYTHON) $(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(O)

.PHONY: clean
clean:
	rm -rvf $(BUILDDIR)/*
