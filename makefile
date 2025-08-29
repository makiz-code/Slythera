.PHONY: env start stop

# Build Environment
env:
ifeq ($(OS),Windows_NT)
	python -m venv app\.venv
	app\.venv\Scripts\python.exe -m pip install --upgrade pip
	app\.venv\Scripts\python.exe -m pip install --no-cache-dir -r app\requirements.txt
else
	python3 -m venv app/.venv
	app/.venv/bin/python -m pip install --upgrade pip
	app/.venv/bin/python -m pip install --no-cache-dir -r app/requirements.txt
endif

# Run Game Service
start:
ifeq ($(OS),Windows_NT)
	cmd.exe /C start "" powershell -NoExit -Command "$$host.UI.RawUI.WindowTitle = 'APP'; app\.venv\Scripts\python.exe app\src\agent.py"
else
	gnome-terminal -- bash -c "app/.venv/bin/python app/src/agent.py; exec bash" || \
	osascript -e 'tell app "Terminal" to do script \"app/.venv/bin/python app/src/agent.py\"'
endif

# Stop Game Service
stop:
ifeq ($(OS),Windows_NT)
	-@taskkill /F /IM python.exe >nul 2>&1
	-@taskkill /FI "WINDOWTITLE eq APP*"
else
	-pkill -f "python app/src/agent.py"
endif
