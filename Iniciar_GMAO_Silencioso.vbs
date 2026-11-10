' Script VBScript para iniciar GMAO Industrial Pro silenciosamente en segundo plano
Set WshShell = CreateObject("WScript.Shell")
strPath = WshShell.CurrentDirectory

' Ejecutar el servidor sin ventana visible (0)
WshShell.Run "cmd /c """ & strPath & "\scripts\run_server.bat""", 0, False

' Esperar 2 segundos y abrir la aplicación en el navegador
WScript.Sleep 2000
WshShell.Run "http://localhost:8000"
