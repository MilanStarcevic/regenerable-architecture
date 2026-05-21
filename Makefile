.PHONY: install test fitness demo clean

install:
	pip3 install pytest pytest-cov

test:
	python3 -m pytest examples/ -v

fitness:
	@echo "--- pricing-discount-capsule ---"
	python3 examples/pricing-discount-capsule/fitness/decay_dashboard.py
	@echo ""
	@echo "--- order-capsule ---"
	python3 examples/order-capsule/fitness/decay_dashboard.py

demo:
	@echo "=== Regenerable Architecture Demo ==="
	@echo ""
	@echo "--- Running tests (all capsules) ---"
	$(MAKE) test
	@echo ""
	@echo "--- Running fitness functions (all capsules) ---"
	$(MAKE) fitness
	@echo ""
	@echo "=== Demo complete ==="

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
