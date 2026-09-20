.PHONY: setup demo smoke test benchmark tamper-test

setup:
	@echo "Setting up Python backend..."
	cd backend && pip install -r requirements.txt
	@echo "Setting up Node frontend..."
	cd frontend && npm install
	@echo "Setting up Hardhat contracts..."
	cd contracts && npm install
	@echo "Setup complete!"

chain:
	@echo "Starting Hardhat local node... (Leave this terminal running)"
	cd contracts && npx hardhat node

deploy:
	@echo "Deploying contract to local node..."
	cd contracts && npx hardhat run scripts/deploy.ts --network localhost

demo:
	@echo "Building and running static Next.js demo..."
	cd frontend && npm run build && npm start

smoke:
	@echo "Running smoke test on precomputed data..."
	cd backend && python -m pytest tests/test_smoke.py -v -s

test:
	@echo "Running backend tests..."
	cd backend && python -m pytest tests/ -v
	@echo "Running contract tests..."
	cd contracts && npx hardhat test

benchmark:
	@echo "Running benchmarks..."
	cd backend && python ../scripts/benchmark.py

tamper-test:
	@echo "Running tamper detection test..."
	cd backend && python -m pytest tests/test_tamper.py -v -s
