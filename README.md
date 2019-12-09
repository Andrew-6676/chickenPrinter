# chickenPrinter
Обращаем внимание на разрядность системы!
- [FireBird 2.5](https://firebirdsql.org/en/firebird-2-5/) (может быть установлен на любом компе в сети, там же должна лежать и БД)
- [python 3.7](https://www.python.org/downloads/release/python-380/) (`pip install -r requirements.txt`) (добавить в path)
- [Ghostscript](https://www.ghostscript.com/download/gsdnld.html) (добавить в path)
- [nodejs](https://nodejs.org/en/download/) (+ [bwip-js](https://www.npmjs.com/package/bwip-js/v/1.7.3) `npm install -g bwip-js`)
- Microsoft Office (Excel)

Монитор COM-порта - [Advanced.Serial.Port.Monitor](https://github.com/Andrew-6676/chickenPrinter/files/3938108/Advanced.Serial.Port.Monitor.3.5.41.Withkey.zip)

-------
##  Содержимое `config.ini` (в папке с програмой)
```ini
[report]
	database=localhost:C:\DATABASE.FDB
	limit=7
[scales]
	port=COM1
	minWeight=0.01
[printer]
	name=default
	gs=gswin32c
[websocket]
	port=8888
[programmer]
	phone=336959382
	mail=andrew-6676@ya.ru
	name=Андрей
```
-------
База данных - [DATABASE.ZIP](https://github.com/Andrew-6676/chickenPrinter/files/3938129/DATABASE.ZIP)

Шаблоны - [templates.zip](https://github.com/Andrew-6676/chickenPrinter/files/3938130/templates.zip)

-------

Самый компактный из найденных шрифтов - [compact](http://allfont.ru/download/compact/)

------
`{{code_128=code128}}` - `code_128`, `ean_13` - тип кода, `code128` - имя переменной с кодом

`{{code_128=code128,90}}` - чтобы повернуть штрихкод на нужный угол по часовой стрелке
