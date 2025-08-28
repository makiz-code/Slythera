.PHONY: env start stop

# Build Environment
env:
ifeq ($(OS),Windows_NT)
	python -m venv .venv
	.venv\Scripts\python.exe -m pip install --upgrade pip
	.venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt
else
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install --no-cache-dir -r requirements.txt
endif

# Run Game Service
start:
ifeq ($(OS),Windows_NT)
	cmd.exe /C start "" powershell -NoExit -Command "$$host.UI.RawUI.WindowTitle = 'PROGRAM'; .venv\Scripts\python.exe src/agent.py"
else
	gnome-terminal -- bash -c ".venv/bin/python src/agent.py; exec bash" || \
	osascript -e 'tell app "Terminal" to do script \".venv/bin/python src/agent.py\"'
endif

# Stop Game Service
stop:
ifeq ($(OS),Windows_NT)
	-@taskkill /F /IM python.exe >nul 2>&1
	-@taskkill /FI "WINDOWTITLE eq PROGRAM*"
else
	-pkill -f "python src/agent.py"
endif
