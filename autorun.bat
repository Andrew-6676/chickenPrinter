echo Timeuot before running scales server. Please wait 5 seconds
ping localhost -n 5 
echo Start scales server... 

python serve.py
set /p input="Press Enter for exit "