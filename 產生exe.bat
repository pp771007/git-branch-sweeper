@echo off
setlocal enabledelayedexpansion

rem 找到第一個.py或.pyw檔案
for %%f in (*.py *.pyw) do (
    set "py_file=%%f"
	echo 有找到pyhton檔案: "!py_file!"
    goto :py_found
)

:py_found

rem 檢查是否存在.ico檔案
for %%i in (*.ico) do (
    set "custom_icon=%%i"
    goto :icon_found
)

:icon_found

rem 使用pyinstaller生成可執行檔，指定自訂圖示
if defined custom_icon (
	echo 有找到圖示檔: "!custom_icon!"
    pyinstaller --onefile --icon=!custom_icon! "!py_file!"
) else (
    rem 使用pyinstaller生成可執行檔，不指定圖示
    pyinstaller --onefile --noconsole "!py_file!"
)

rem 尋找生成的可執行檔
for %%i in (dist\*.exe) do (
    move "%%i" .
)

rem 刪除build資料夾、dist資料夾和.spec檔案
rd /s /q build
rd /s /q dist
del *.spec

endlocal
