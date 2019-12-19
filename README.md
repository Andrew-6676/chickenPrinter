# chickenPrinter
**Обращаем внимание на разрядность системы!**

**В настройках принтера необходимо добавить нужные размеры этикетки**

**Режим передачи веса желательно установить в "передача после успокоения" (в крайнем случае "непрерывный режим")**

-------
# Необходимо установить:
- [FireBird 2.5](https://firebirdsql.org/en/firebird-2-5/) (может быть установлен на любом компе в сети, там же должна лежать и БД)
- [python 3.7](https://www.python.org/downloads/release/python-380/) (`pip install -r requirements.txt`) (добавить в path) (для запуска программы)
- [Ghostscript](https://www.ghostscript.com/download/gsdnld.html) (добавить в path) (для вывода на принтер)
- [nodejs](https://nodejs.org/en/download/) (+ [bwip-js](https://www.npmjs.com/package/bwip-js/v/1.7.3) `npm install -g bwip-js`) (для формирования штрихкода)
- Microsoft Office (Excel) (для конвертации xlsx в pdf)

может пригодиться монитор COM-порта - [Advanced.Serial.Port.Monitor](https://github.com/Andrew-6676/chickenPrinter/files/3938108/Advanced.Serial.Port.Monitor.3.5.41.Withkey.zip)

-------
##  Содержимое `config.ini` (в папке с програмой)
```ini
[report]
	database=localhost:C:\DATABASE.FDB
	limit=7
[scales]
	port=COM1
	minTareWeight=0.01
	minProdWeight=0.10
	precision=3
[printer]
	name=default
	gs=gswin32c
[websocket]
	port=8888
[webserver]
	port=8080
	name=Комп намба уан
	color=#f00
	factory_code=6666
	code128_prefix=22
[programmer]
	phone=336959382
	mail=andrew-6676@ya.ru
	name=Андрей
```
-------
База данных - [DATABASE.ZIP](https://github.com/Andrew-6676/chickenPrinter/files/3938129/DATABASE.ZIP)

Шаблоны - [templates.zip](https://github.com/Andrew-6676/chickenPrinter/files/3938130/templates.zip)

Инструкция к весам - [CI-5010A](https://github.com/Andrew-6676/chickenPrinter/files/3982060/CI-5010A.pdf)

-------

Самый компактный из найденных шрифтов - [compact](http://allfont.ru/download/compact/)

------
`{{code_128=code128}}` - `code_128`, `ean_13` - тип кода, `code128` - имя переменной с кодом

`{{code_128=code128,90}}` - чтобы повернуть штрихкод на нужный угол по часовой стрелке

------
# Звуки
`winsound.Beep(200, 900)`: 200 - это частота, 900 - длительность в миллисекундах
- Ошибки:
    - глухой и долгий `(200, 900)` - при ошибке взвешивания
    - два глухих коротких `(500, 150),(500, 150)` - не выбран продукт
 - Подтверждающие звуки:
    - два звонких коротких `(4500, 70),(3500, 170)`- считан вес тары 
    - три звонких коротких `(4500, 70),(4500, 70),(3500, 200) `- получен вес продукта и начата подготовка этикетки
    - один звонкий длинный `(2500, 700)` - этикетка отправлена на принтер, можно взвешивать дальше
