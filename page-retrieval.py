from xml.etree.cElementTree import Element, iterparse

# TODO: Get new dataset with article text
file_path = 'datasets/raw/enwikibooks-20230401-pages-meta-current.xml'
root = iterparse(file_path, events=('start', 'end'))

path = []
element: Element
for event, element in root:
	if event == 'start':
		path.append(element.tag)
	elif event == 'end':
		# if 'page' in element.tag:
		# 	title = element.find('{http://www.mediawiki.org/xml/export-0.10/}title')
		# 	element_id = element.find('{http://www.mediawiki.org/xml/export-0.10/}id')
		# 	print(title.text)
		# 	for child in element:
		# 		print(child.tag)
		# if 'title' in element.tag:
		# 	print(element.text)
		print('\n', element.tag)
		for child in element:
			print('C:', child.tag)
			for c2 in child:
				print('\t', c2.tag)
		path.pop()
