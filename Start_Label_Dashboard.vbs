' DoD Label Generator - Web Dashboard Launcher
' Double-click this file to start the Streamlit web dashboard
' The browser will open automatically to http://localhost:8501

Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Run "cmd /c streamlit run dod_label_app.py", 1, False
WScript.Sleep 3000
WshShell.Run "http://localhost:8501"
