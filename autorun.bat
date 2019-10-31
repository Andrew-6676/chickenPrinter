echo Timeuot before running scales server. Please wait 30 seconds
ping localhost -n 30 
echo Start scales server... 

python serve.py
set /p input="Press Enter for exit "