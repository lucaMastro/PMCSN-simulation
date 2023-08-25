
PYTHON = python3
SCRIPT = simulation.py 
SEED = 123

infinite:
	$(PYTHON) $(SCRIPT) -ih -s $(SEED) -cc BATCH_K 256
