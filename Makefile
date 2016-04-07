DJANGO_SETTINGS_MODULE ?= tests.projects.example
PACKAGES ?= tests
ATTRIBUTES ?= # Set `-a "!rq"` to skip RQ tests
XUNIT_TMP ?= "coverage/xunit.xml"
XUNIT ?= --with-xunit --xunit-file=$(XUNIT_TMP)
COVERAGE ?= --with-cov --cov-report=xml --cov-report=html

clean: clean/pyc
	rm -rf .tox
	rm -rf *.egg-info
	coverage erase

clean/pyc:
	find . -name "*.pyc" -delete

test: clean/pyc
	mkdir -p coverage
	DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) \
		python -Wignore -m nose $(ATTRIBUTES) $(PACKAGES) \
		--nologcapture $(XUNIT) $(COVERAGE)
