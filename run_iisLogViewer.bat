@ECHO off
SETLOCAL

REM set log_file="C:\IIS_LogFile_Viewer\app_logs\bat_app_launcher_logs.log"
set log_file="D:\workspace\python\iisLogParser\iislp\app_logs\bat_app_launcher_logs.log"
REM set iislp_log_file="C:\IIS_LogFile_Viewer\app_logs\run_time.log"
set iislp_log_file="D:\workspace\python\iisLogParser\iislp\app_logs\run_time.log"
REM set ilfv_dir=C:\IIS_LogFile_Viewer\IIS_LogFile_Viewer
set ilfv_dir=D:\workspace\python\iisLogParser\iislp\IIS_LogFile_Viewer
set debian_server_ip=192.168.56.101
set ts=%date:~-4,4%-%date:~4,2%-%date:~7,2% %time%
set ftp_resp=FTP_CONNECTED
set check_conn_msg=CHECK CONNECTION
set conn_success_msg=CONNECT SUCCESS
set conn_err_msg=CONNECT ERROR

REM
REM Check that the Q: drive is connected so we can get the 
REM logs_done directory which holds all the logs.
REM
ECHO [ %ts% ]  This batch file output sent to %log_file%...
REM ECHO %log_file% will launch in Notepad after this batch file is finished...
ECHO [ %ts% ]  START: IIS LogFile Viewer launcher...>>%log_file%
ECHO [ %ts% ]  %check_conn_msg%: Q:\soft\Leads\web\log_done...>>%log_file%
C:
IF NOT EXIST Q:\soft\Leads\web\log_done GOTO NOQDIR
ECHO [ %ts% ]  %conn_success_msg%	: Q:\soft\Leads\web\log_done...>>%log_file%
GOTO YESQDIR

:NOQDIR
ECHO [ %ts% ]  %conn_err_msg%	: Q:\soft\Leads\web\log_done does not exist!>>%log_file%

:YESQDIR
ECHO [ %ts% ]  %check_conn_msg%: DebianDev VM - %debian_server_ip%...>>%log_file%
REM
REM Check to see that we have a connection to the Virtual
REM Server, "Debian 7", which should be running in VirtualBox.
REM
%SystemRoot%\System32\ping.exe -n 1 %debian_server_ip% >>%log_file%
if errorlevel 1 goto NoServer

ECHO [ %ts% ]  %conn_success_msg%	: DebianDev VM - %debian_server_ip%...>>%log_file%
REM
REM Check the connectivity to the FTP server.
REM
ECHO [ %ts% ]  %check_conn_msg%: FTP server...>>%log_file%
ECHO [ %ts% ]  Attempting FTP download, filename 'test.txt'...>>%log_file%
curl -u bcftp:32davis*bc ftp://192.168.56.101/test.txt > tmpFile 2>>%log_file%
set /p resvar= < tmpFile
del tmpFile
REM
REM Test to see if the text 'FTP_CONNECTED' is in the var 'resvar'.
REM
ECHO.%resvar%| FIND /I "FTP_CONNECTED">nul && (
	GOTO YESFTPCONN
) || (
	GOTO NOFTPCONN
)

:NOFTPCONN
ECHO [ %ts% ]  %conn_err_msg%	: FTP server is not available...>>%log_file% 
	
:YESFTPCONN
ECHO [ %ts% ]  %conn_success_msg%	: FTP server...>>%log_file%

ECHO [ %ts% ]  Launching iislp.py (IIS Log Parser): output sent to %iislp_log_file%...
py %ilfv_dir%\iislp.py

REM Leave batch file...
GOTO :EOF

:NoServer
ECHO [ %ts% ]  %conn_err_msg%	: %debianServer% is not available.>>%log_file%


