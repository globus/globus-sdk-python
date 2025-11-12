SDK_VERSION=$(shell grep '^version' pyproject.toml | head -n 1 | cut -d '"' -f2)

# these are just tox invocations wrapped nicely for convenience
.PHONY: lint test docs all-checks
lint:
	tox -e lint,mypy,mypy-test,pylint
test:
	tox
docs:
	tox -e docs
all-checks:
	tox -e lint,pylint,mypy,mypy-test,test-lazy-imports,py37,py310,poetry-check,twine-check,docs

.PHONY: showvars tag-release prepare-release
showvars:
	@echo "SDK_VERSION=$(SDK_VERSION)"
prepare-release:
	tox -e prepare-release
tag-release:
	git tag -s "$(SDK_VERSION)" -m "v$(SDK_VERSION)"
	-git push $(shell git rev-parse --abbrev-ref @{push} | cut -d '/' -f1) refs/tags/$(SDK_VERSION)

.PHONY: install
install:
	python -m venv .venv --upgrade-deps
	.venv/bin/pip install -e . --group test

.PHONY: clean
clean:
	rm -rf dist build *.egg-info .tox .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
