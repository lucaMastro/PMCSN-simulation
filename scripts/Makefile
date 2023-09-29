
PYTHON = python3
SCRIPT1 = compute_theoretical_values.py
SCRIPT2 = check_interval.py
SCRIPT3 = graph_generator.py
SCRIPT4 = costs_analysis.py
CONFIG_FILE=Config.py

# put without extention
THEOR_OUT=theoreticals

CHECK_OUT=interval.txt
SHOW_GRAPH=

all: theor check graph costs

theor:
	rm -f $(THEOR_OUT).csv
	$(PYTHON) $(SCRIPT1) -cf ../configurations/$(CONFIG_FILE) -sf $(THEOR_OUT)

check:
ifeq ($(CHECK_OUT),)
	$(PYTHON) $(SCRIPT2) -tf $(THEOR_OUT).csv 
else
	$(PYTHON) $(SCRIPT2) -tf $(THEOR_OUT).csv > $(CHECK_OUT)
endif

graph:
ifeq ($(SHOW_GRAPH),)
	$(PYTHON) $(SCRIPT3) -a 
else
	$(PYTHON) $(SCRIPT3) -a -sg
endif

costs:
	$(PYTHON) $(SCRIPT4)
