python --version
pip --version
python -c "import fastapi; print('fastapi ok')" 2>$null || echo "fastapi not installed"
python -c "import sqlalchemy; print('sqlalchemy ok')" 2>$null || echo "sqlalchemy not installed"
python -c "import uvicorn; print('uvicorn ok')" 2>$null || echo "uvicorn not installed"
