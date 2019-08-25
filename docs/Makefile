PYTHON      = $(shell which python)
SPHINXBUILD = $(shell which sphinx-build)
SPHINXPROJ  = scinoephile

.PHONY: clean
clean:
	rm -frv html/*

.PHONY: html
docs:
	$(PYTHON) $(SPHINXBUILD) -M html "." "."

.PHONY: coverage
coverage:
	$(PYTHON) $(SPHINXBUILD) -M html "." "." -b coverage

.PHONY: docs_badges
badges:

	cd $(ROOT)/scinoephile/utils/scripts/ && \
		$(PYTHON) update_badges.py

.PHONY: docs_helptext
helptext:
	cd $(ROOT)/scinoephile/utils/scripts/ && \
		$(PYTHON) update_helptext.py
