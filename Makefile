.PHONY: install test fitness demo clean

install:
	pip3 install pytest pytest-cov

test:
	python3 -m pytest examples/pricing-discount-capsule/tests/ -v

fitness:
	python3 fitness-functions/slop_score.py examples/pricing-discount-capsule

demo:
	@echo "=== Regenerable Architecture Demo ==="
	@echo ""
	@echo "--- Running tests ---"
	$(MAKE) test
	@echo ""
	@echo "--- Running fitness functions ---"
	$(MAKE) fitness
	@echo ""
	@echo "=== Demo complete ==="

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
