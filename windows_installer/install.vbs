MsgBox "Initial configuration of cloud api", 64, "SSO configuration"
connectionName = InputBox("Please enter a name for the Cloud API connection", "SSO configuration", "cloud_api_connection")
appServerAddress = InputBox("Enter (IP) address of the application server" , "SSO configuration", "127.0.0.1")
appServerPort = InputBox("Enter port of the Application server", "SSO configuration", "80")
xmlRpcUrl = InputBox("Enter URL path of the XML-RPC transport of the application server", "SSO configuration", "/appserver/xml-rpc")
customerLogin = InputBox("Enter customer login (optional)", "SSO configuration")

set WshShell = CreateObject("WScript.Shell")
set WshEnv = WshShell.Environment("Process")
WinPath = WshEnv("SystemRoot")
Set fs = CreateObject("Scripting.FileSystemObject")


blaFile = Wscript.ScriptFullName
blaFile = fs.GetAbsolutePathName(blaFile)
fileName = fs.getFile(blaFile).Name
destDir = Replace(blaFile, fileName, "")
destFile = fs.BuildPath(destDir, "cfg\qconfig\cloudapiconnection.cfg")

' MsgBox("Wrote " & destFile)

strFileName = fs.GetAbsolutePathName(strFileName)
Set ts = fs.OpenTextFile(destFile, 2, True)
ts.writeLine "[" & connectionName & "]"
ts.WriteLine "passwd ="
ts.WriteLine "server = " & appServerAddress
ts.writeLine "path = " & xmlRpcUrl
ts.writeLine "login = " & customerLogin
ts.writeLine "port = " & appServerPort
ts.Close

' MsgBox "Configuration of agent finished", 64, "SSO Agent configuration"

qshellCmd = fs.BuildPath(destDir, "qshell.bat ")


qshellCmd = qshellCmd & " -c q.manage.applicationserver.restart()"
logFile = fs.BuildPath(destDir, "var\log\applicationserver.log")
' LINE 40
' MsgBox "Restarting application server " & qshellCmd

WshShell.run qshellCmd

appPath = fs.BuildPath(destDir, "bin\twistd ")
scCmd = "sc create twisted displayname= ""twisted"" binpath= """ & appPath
scCmd = scCmd & " -l " & logFile & " --config=applicationserver"""

' MsgBox RUnning & scCmd

WshShell.run scCmd
