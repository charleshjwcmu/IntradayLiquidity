echo "AUTORUN"

set hr=%time:~0,2%
if "%hr:~0,1%" equ " " set hr=0%hr:~1,1%

C:\Users\e620927\AppData\Local\Continuum\anaconda3\python Z:\Charles\IntradayLiquidity\SourceCodes-Production\main.py >> Z:\Charles\IntradayLiquidity\LOG\Log_main_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%h_%time:~3,2%m_%time:~6,2%s.txt
::C:\Users\E620927\AppData\Local\Anaconda\Anaconda3\python Z:\Charles\IntradayLiquidity\SourceCodes-Production\main.py >> Z:\Charles\IntradayLiquidity\LOG\Log_main_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%h_%time:~3,2%m_%time:~6,2%s.txt

pause

