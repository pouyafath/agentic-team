# The kit's own checks. Projects replace these targets with their real toolchain,
# keeping the same names: CI and every agent rely on them.
.PHONY: lint test acceptance ci

lint:
	python3 -m py_compile .claude/hooks/guard.py scripts/metrics.py
	python3 -c "import json; json.load(open('.claude/settings.json')); json.load(open('.claude/hooks/policy.json'))"
	bash -n scripts/install.sh scripts/setup-github.sh

test:
	python3 -m unittest discover -s scripts/tests

acceptance:
	@echo "The kit has no acceptance suite; projects define one under tests/acceptance or e2e/."

ci: lint test acceptance
