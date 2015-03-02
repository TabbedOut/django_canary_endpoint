DJANGO_SETTINGS_MODULE ?= tests.projects.example
PACKAGES ?= tests
XUNIT_TMP ?= "coverage/xunit.xml"

clean:
	find . -name "*.pyc" -delete

test: clean
	mkdir -p coverage
	DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) \
		python -Wignore -m nose $(PACKAGES) \
		--nologcapture \
		--with-xunit --xunit-file=$(XUNIT_TMP) \
		--with-cov --cov-report=xml --cov-report=html

@PHONY: clean test
