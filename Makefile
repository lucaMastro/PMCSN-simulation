PYTHON = python3
SCRIPT = simulation.py
SEED = 123
WEEK_OUTPUT = week
WEEKEND_OUTPUT = weekend

all: clean infinite-week infinite-weekend finite-week finite-week-no-gauss finite-weekend finite-weekend-no-gauss

infinite-week:
	$(PYTHON) $(SCRIPT) -ih -s $(SEED) -of $(WEEK_OUTPUT)

infinite-weekend:
	$(PYTHON) $(SCRIPT) -ih -s $(SEED) -wed -of $(WEEKEND_OUTPUT)

finite-week:
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -of $(WEEK_OUTPUT)_gauss

finite-week-no-gauss:
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -of $(WEEK_OUTPUT) -ngf

finite-weekend:
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -of $(WEEKEND_OUTPUT)_gauss -wed

finite-weekend-no-gauss:
	$(PYTHON) $(SCRIPT) -fh -s $(SEED) -of $(WEEKEND_OUTPUT) -wed -ngf

clean:
	rm -f ./output/*.csv
	rm -f ./output/finite/*.csv
	rm -f ./output/infinite/*.csv
