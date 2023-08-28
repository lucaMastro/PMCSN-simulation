
PYTHON = python3
SCRIPT = simulation.py 
SEED = 123

infinite:
	$(PYTHON) $(SCRIPT) -ih -s $(SEED)

finite:
	$(PYTHON) $(SCRIPT) -fh -s $(SEED)

infinite-no-gauss:
	$(PYTHON) $(SCRIPT) -ih -s $(SEED) -ngf

finite-no-gauss:
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -ngf

clean:
	rm -f ./output/*.csv
	rm -f ./output/finite/*.csv
	rm -f ./output/infinite/*.csv
