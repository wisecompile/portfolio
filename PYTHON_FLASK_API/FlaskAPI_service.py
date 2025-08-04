import win32serviceutil
import win32service
import win32event
import servicemanager
import os
import sys
import subprocess

class FlaskAPI_service(win32serviceutil.ServiceFramework):
    _svc_name_ = "FlaskAPI"
    _svc_display_name_ = "Flask API Service"
    _svc_description_ = "Запускает Flask API-приложение (bulk) через Waitress для обработки API-запросов"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.process:
            self.process.terminate()
            self.process.wait()
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        python_exe = r"C:\Program Files\Python313\python.exe"
        script_path = os.path.join(r"C:\FlaskInventory", "wsgi_api.py")

        self.process = subprocess.Popen(
            [python_exe, script_path],
            cwd= r"C:\FlaskInventory"
        )
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(FlaskAPI_service)
