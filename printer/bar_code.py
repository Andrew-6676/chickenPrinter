import os
from io import BytesIO

import barcode
from PIL import Image as PILImage
import openpyxl
import treepoem
from barcode.writer import ImageWriter

# ----------------------------------------------------------------------------------------------- #
def generateBarCode_simple(type, data, rotate=0):
	fp = BytesIO()
	writer_options = {
        'module_width': 0.08,
        'module_height': 1.4,
        'quiet_zone': 0.1,
        'font_size': 5,
        'text_distance': 0.7,
	}

	barcode.generate(type,
	                 str(data),
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
			# 'includecheck': True,
			'includecheckintext': True
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
def generateBarCode_node(type, data, rotate=0, resize=1):
	# rotate = '--rotate=' + {0: 'N', 90: 'R', 270: 'L', 180: 'I'}[rotate]
	if type=='ean13':
		command = f'bwip-js --bcid={type} --text={data} --includetext=true  --scaleY=1 --scale=2 --height=10 --width=25 --textyoffset=-5 code1.png'
		os.system(command)
		image = PILImage.open('code1.png')
		im2 = image.rotate(-rotate, expand=True)
		im2.save('code1.png')
		# image = PILImage.open('code1.png')
		return PILImage.open('code1.png')
	if type == 'code128':
		command = f'bwip-js --bcid={type} --text={data} --includetext=true --textgaps=1 --includetext=true  --scaleY=1 --scale=2 --height=10 --width=25 code2.png'
		os.system(command)
		image = PILImage.open('code2.png')
		im2 = image.rotate(-rotate, expand=True)
		im2.save('code2.png')
		# im3 = PILImage.open('code2.png')
		return PILImage.open('code2.png')

# ----------------------------------------------------------------------------------------------- #
def insertBarCode(sheet, anchor, code_type, code_data, rotate=0, resize=1):
	im = generateBarCode_node(code_type, code_data, rotate, resize)
	img = openpyxl.drawing.image.Image(im)
	img.width *= resize
	img.height *= resize
	img.anchor = anchor
	sheet.add_image(img)

