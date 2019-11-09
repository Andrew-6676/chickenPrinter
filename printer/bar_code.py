import time
from io import BytesIO
import barcode
from PIL import Image as PILImage
import openpyxl
import treepoem
from barcode.writer import ImageWriter

# ----------------------------------------------------------------------------------------------- #
def generateBarCode_simple(type, data):
	fp = BytesIO()
	writer_options = {
        'module_width': 0.08,
        'module_height': 1.4,
        'quiet_zone': 0.1,
        'font_size': 5,
        'text_distance': 0.7,
	}

	barcode.generate(type, data,
	                 writer=ImageWriter(),
	                 output=fp,
	                 writer_options=writer_options)
	return PILImage.open(fp)
# ----------------------------------------------------------------------------------------------- #
def generateBarCode_tree(type, data):
	options = {
		'ean13': {
			'includetext': True,
			'textfont': 'Arial-Black',
			'textsize': 10,
			# 'textgaps': 5,
			'height': 0.4,
		},
		'code128': {
			'includetext':True,
			'textfont': 'Arial-Black',
			'textsize': 10,
			'textgaps': 2,
			'height': 0.3,
			'includecheck': True
		}
	}
	image = treepoem.generate_barcode(
		barcode_type=type,
		data=str(data),
		options = options[type]
	)
	size = image.width/2, image.width/2
	image.thumbnail(size, PILImage.NEAREST)
	# image.convert('1').save('barcode.png')
	return image
# ----------------------------------------------------------------------------------------------- #
def insertBarCode(sheet, anchor, code_type, code_data):
	im = generateBarCode_tree(code_type, code_data)
	img = openpyxl.drawing.image.Image(im)
	img.anchor = anchor
	sheet.add_image(img)
