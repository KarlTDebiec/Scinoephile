ROOT        = $(shell pwd)
PYTHON      = $(shell which python)
DEPS        = $(wildcard *.py */*.py)
zysyzm      = /usr/local/anaconda3/envs/zysyzm/lib/python3.6/site-packages/zysyzm-0.1-py3.6.egg
EXTRACTION  = $(ROOT)/zysyzm/ExtractionManager.py
CLARGS      =

$(zysyzm): $(DEPS)
	cd $(ROOT) && \
	python setup.py install

clean:
	cd $(ROOT) && \
	rm -vr build dist zysyzm.egg-info

EXTRACTION:
	make $(zysyzm)
	cd $(HOME) && $(PYTHON) $(EXTRACTION) $(CLARGS)
