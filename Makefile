.PHONY: tests
tests:
	python -m pytest \
	--cov=nornsible \
	--cov-report html \
	--cov-report term \
	tests/.

.PHONY: docs
docs:
	python -m pdoc \
	--html \
	--output-dir docs \
	nornsible \
	--force
