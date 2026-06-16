# 快速启动脚本 - Windows批处理

@echo off
chcp 65001 >nul
title 档案管理分析系统 - 安装向导

echo =====================================================
echo     档案管理分析系统 - 自动安装脚本
echo =====================================================
echo.

REM 检查Docker安装
echo [*] 检查Docker安装...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker未安装，请先安装Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)
echo [✓] Docker已安装

REM 检查Docker Daemon
echo [*] 检查Docker服务...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker服务未运行，请启动Docker Desktop
    echo.
    pause
    exit /b 1
)
echo [✓] Docker服务运行正常

REM 获取当前目录
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo [*] 开始初始化系统...
echo.

REM 创建必要的目录
echo [*] 创建目录结构...
if not exist "data" mkdir data
if not exist "data\mysql" mkdir data\mysql
if not exist "data\orangehrm" mkdir data\orangehrm
if not exist "data\uploads" mkdir data\uploads
if not exist "data\ollama" mkdir data\ollama
if not exist "logs" mkdir logs

echo [✓] 目录创建完成

REM 构建Docker镜像
echo.
echo [*] 拉取基础镜像（首次运行需要几分钟）...
docker pull mysql:5.7
docker pull php:7.4-apache
docker pull python:3.9-slim
docker pull ollama/ollama:latest

echo [✓] 基础镜像拉取完成

REM 启动Docker Compose
echo.
echo [*] 启动所有服务...
docker-compose build --no-cache
if %errorlevel% neq 0 (
    echo [✗] 镜像构建失败
    pause
    exit /b 1
)

echo [✓] 镜像构建完成

echo.
echo [*] 启动Docker容器...
docker-compose up -d

if %errorlevel% neq 0 (
    echo [✗] 容器启动失败
    echo 错误信息已显示在上方，请检查
    pause
    exit /b 1
)

echo [✓] 容器启动完成

REM 等待服务就绪
echo.
echo [*] 等待服务启动（约30秒）...

setlocal enabledelayedexpansion
for /L %%i in (1,1,30) do (
    timeout /t 1 /nobreak >nul
    cls
    echo [*] 等待服务启动... %%i/30
)

echo [✓] 服务启动完成

REM 显示访问信息
echo.
echo =====================================================
echo     系统安装完成！
echo =====================================================
echo.
echo [✓] 所有服务已启动
echo.
echo 📍 访问地址: http://localhost:8080
echo 👤 默认用户: admin
echo 🔑 默认密码: admin
echo.
echo 📞 其他服务:
echo   - OCR服务: http://localhost:8001
echo   - 分析服务: http://localhost:8002
echo   - 大模型服务: http://localhost:11434
echo   - 数据库: localhost:3306
echo.
echo =====================================================
echo.

REM 尝试打开浏览器
echo [*] 打开系统...
timeout /t 2 /nobreak >nul

start http://localhost:8080

echo.
echo [✓] 安装完成！请在浏览器中访问 http://localhost:8080
echo.
pause
