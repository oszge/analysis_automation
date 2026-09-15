# Node-RED automation

- Editor: http://127.0.0.1:1880
- Dashboard: http://127.0.0.1:8501
- Schedule: every day at **10:00 Europe/Budapest**, including daylight-saving changes.
- Manual run: click the button to the left of **Run report now**.
- Results: Debug sidebar, **Report result + log path**. `success` and exit code `0` mean the report was generated.

The flow runs `run_pipeline.py` with the project's virtual environment. The wrapper
launches `analysis_automation.data_processing` from the correct parent directory,
prevents overlapping runs, imposes a 10-minute timeout and saves a JSON log to
`run_logs`. Validation failures return a nonzero exit code. It never imports sales
or sends emails. Report output remains `business_intelligence_report.md`.

The existing `REFRESH_AI_RESPONSE` flag in `data_processing.py` controls AI use:
`False` reads the saved AI response; `True` requests a new response on each run.
It is currently `False`. Changed source data can therefore make validation fail
until an appropriate new AI analysis is generated.

`start-services.ps1` starts Node-RED and Streamlit hidden, bound to loopback only.
A **Sales Intelligence Automation** shortcut in the Windows Startup folder runs
it at user sign-in. The machine must be on, awake and signed in, with Node-RED
running, at 10:00. Missed runs are not replayed automatically. There is no Windows
service or wake-from-sleep task. To start manually:

```powershell
powershell -NoProfile -File .\node_red\start-services.ps1
```

Node.js is installed under `%LOCALAPPDATA%\Programs\NodeJS`; Node-RED is installed
under `%APPDATA%\npm`. Runtime files and service logs are under
`%LOCALAPPDATA%\NodeRED\analysis-automation`. `settings.js` loads this folder's
`flows.json`. The process timezone is set to `Europe/Budapest` by the launcher.

The dashboard reads source data with its existing five-minute cache. After a
scheduled run, reopening or interacting with the dashboard refreshes expired
data; **Refresh data** reloads immediately. The flow does not generate new app code
or force an idle browser page to refresh.

To change the schedule, edit **Daily 10:00 · Budapest** in Node-RED and Deploy.
To disable login startup, remove the named shortcut from the Windows Startup folder.

Official installation guide: https://nodered.org/docs/getting-started/windows
