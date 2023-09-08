
PYTHON = python3
SCRIPT1 = compute_theoretical_values.py
SCRIPT2 = check_interval.py
SCRIPT3 = graph_generator.py
SCRIPT4 = costs_analysis.py
CONFIG_FILE=Config.py
THEOR_OUT=theoreticals.csv
CHECK_OUT=interval.txt
SHOW_GRAPH=

all: theor check graph costs

theor:
	$(PYTHON) $(SCRIPT1) -cf ../configurations/$(CONFIG_FILE) -sf $(THEOR_OUT)

check:
ifeq ($(CHECK_OUT),)
	$(PYTHON) $(SCRIPT2) > $(CHECK_OUT)
else
	$(PYTHON) $(SCRIPT2)
endif

graph:
ifeq ($(SHOW_GRAPH),)
	$(PYTHON) $(SCRIPT3) -a -sg
else
	$(PYTHON) $(SCRIPT3) -a
endif

costs:
	$(PYTHON) $(SCRIPT4)
