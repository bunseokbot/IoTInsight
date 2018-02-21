@echo off

powershell.exe -NoProfile -ExecutionPolicy Bypass "& {& '%~dp0scripts\installDependency.ps1'}"