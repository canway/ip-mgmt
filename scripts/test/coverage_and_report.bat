@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set BATCH_PATH=%~dp0
call %BATCH_PATH%..\develop\envs.bat

:: 清理历史数据
if exist .cover (rd /S /Q .cover)

set INCLUDE_PATH=home_application/*
set OMIT_PATH=*/migrations/*,*/tests/*
set exclude_tag=
set module=

:: 脚本参数解析
::if "%~5" neq "" goto :usage
::if "%~4" == "" goto :usage
::call :getopts %1 %2 %3 %4
if "%~1" neq "" (
  if "%~1" == "-m" (
    if "%~2" == "" goto :usage
    set module=%~2
  ) else (
    if "%~1" == "-e" (
    if "%~2" == "" goto :usage
    set exclude_tag=%~2) else goto :usage
  )
)
if "%~3" neq "" (
  if "%~3" == "-e" (
    if "%~4" == "" goto :usage
    set exclude_tag=%~4

  ) else (
    if "%~3" == "-m" (
    if "%~4" == "" goto :usage
    set module=%~4) else goto :usage
  )
)

:: 单元测试数据库配置
set DB_NAME=test_%random%
call :backup

:: 单元测试覆盖率报告
coverage erase
coverage run --include=%INCLUDE_PATH% --omit=%OMIT_PATH% ./manage.py test %module% --exclude-tag=%exclude_tag% || call:revert
coverage html -d .cover
coverage report --include=%INCLUDE_PATH% --omit=%OMIT_PATH% || call:revert

call :revert
goto :eof

:: 校验脚本参数
:getopts
if "%~1" == "-m" (
  set module=%~2
) else (
  if "%~1" == "-e" (set exclude_tag=%~2) else goto :usage
)
if "%~3" == "-e" (
  set exclude_tag=%~4

) else (
  if "%~3" == "-m" (set module=%~4) else goto :usage
)
goto :eof

:: 修改dev.py单元测试DB
:backup
ren config\dev.py dev.py.bak
for /f "skip=2 delims=" %%a in ('find "" /v /n config\dev.py.bak') do (
  set line=%%a
  set flag=0
  echo !line! | findstr ]] >nul&& set flag=1
  if !flag! == 1 (
    echo ]>>config\dev.py
  ) else (
      for /f "delims=] tokens=1*" %%i in ("!line!") do (
        set line=%%j
        if "!line!" == "" (
          echo.>>config\dev.py
        ) else (
          set line=!line:test_db=%DB_NAME%!
          echo !line!>>config\dev.py
        )
     )
  )
)
del config\dev.py.bak
goto :eof

:: 还原dev.py单元测试DB
:revert
ren config\dev.py dev.py.bak
for /f "skip=2 delims=" %%a in ('find "" /v /n config\dev.py.bak') do (
  set line=%%a
  set flag=0
  echo !line! | findstr ]] >nul&& set flag=1
  if !flag! == 1 (
    echo ]>>config\dev.py
  ) else (
      for /f "delims=] tokens=1*" %%i in ("!line!") do (
        set line=%%j
        if "!line!" == "" (
          echo.>>config\dev.py
        ) else (
          set line=!line:%DB_NAME%=test_db!
          echo !line!>>config\dev.py
        )
     )
  )
)
del config\dev.py.bak
goto :eof

:: 脚本使用说明
:usage
echo Usage: [-m test module] [-e exclude tag]
goto :eof
