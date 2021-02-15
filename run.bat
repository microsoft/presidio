echo >/dev/null # >nul & GOTO WINDOWS & rem ^

E2E_TESTS_DIR=e2e-tests
docker-compose up --build -d
python -m venv ${E2E_TESTS_DIR}/presidio-e2e
source ${E2E_TESTS_DIR}/presidio-e2e/bin/activate
pip install -r ${E2E_TESTS_DIR}/requirements.txt
pytest -v ${E2E_TESTS_DIR}
deactivate
exit 0

:WINDOWS

@echo off
set E2E_TESTS_DIR=e2e-tests
docker-compose up --build -d || exit /b
if not exist "%E2E_TESTS_DIR%\presidio-e2e" py -m venv %E2E_TESTS_DIR%\presidio-e2e
call %E2E_TESTS_DIR%\presidio-e2e\Scripts\activate || exit /b
pip install -r %E2E_TESTS_DIR%\requirements.txt || exit /b
pytest -v %E2E_TESTS_DIR%
deactivate

