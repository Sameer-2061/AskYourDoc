@echo off
title AI Chatbot Server

echo =========================================
echo     Starting AI Chatbot Backend...
echo =========================================
:: Start the FastAPI server in a new command window
start cmd /k ".\ai_env\Scripts\activate && uvicorn main:app --reload"

echo.
echo  Waiting for the server to initialize (3 seconds)...
timeout /t 3 /nobreak > nul

echo.
echo  Opening the Chatbot Interface...
:: Open the HTML file in your default browser
start index.html

exit