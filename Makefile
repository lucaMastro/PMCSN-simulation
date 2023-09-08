PYTHON = python3
SCRIPT = simulation.py
SEED = 123
WEEK_OUTPUT = week
WEEKEND_OUTPUT = weekend

all: clean infinite-week infinite-weekend finite-week finite-week-no-gauss finite-weekend finite-weekend-no-gauss

infinite-week:
ifeq ($(CONFIG_FILE),)
	$(PYTHON) $(SCRIPT) -ih -s $(SEED) -of $(WEEK_OUTPUT)
else
	$(PYTHON) $(SCRIPT) -ih -s $(SEED) -of $(WEEK_OUTPUT) -cf $(CONFIG_FILE)
endif

infinite-weekend:
ifeq ($(CONFIG_FILE),)
	$(PYTHON) $(SCRIPT) -ih -s $(SEED) -wed -of $(WEEKEND_OUTPUT)
else
	$(PYTHON) $(SCRIPT) -ih -s $(SEED) -wed -of $(WEEKEND_OUTPUT) -cf $(CONFIG_FILE)
endif

finite-week:
ifeq ($(CONFIG_FILE),)
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -of $(WEEK_OUTPUT)_gauss
else
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -of $(WEEK_OUTPUT)_gauss -cf $(CONFIG_FILE)
endif

finite-week-no-gauss:
ifeq ($(CONFIG_FILE),)
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -of $(WEEK_OUTPUT) -ngf
else
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -of $(WEEK_OUTPUT) -ngf -cf $(CONFIG_FILE)
endif

finite-weekend:
ifeq ($(CONFIG_FILE),)
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -of $(WEEKEND_OUTPUT)_gauss -wed
else
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -of $(WEEKEND_OUTPUT)_gauss -wed -cf $(CONFIG_FILE)
endif

finite-weekend-no-gauss:
ifeq ($(CONFIG_FILE),)
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -of $(WEEKEND_OUTPUT) -wed -ngf
else
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -of $(WEEKEND_OUTPUT) -wed -ngf -cf $(CONFIG_FILE)
endif


clean:
	rm -f ./output/*.csv
	rm -f ./output/finite/*.csv
	rm -f ./output/infinite/*.csv
