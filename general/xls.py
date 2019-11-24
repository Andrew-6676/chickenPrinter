import win32com
import win32com.client
EXCEL = win32com.client.Dispatch("Excel.Application")
EXCEL.Visible = False
