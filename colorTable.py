#!/usr/bin/env python3
#creates an array of bash colors
colors = []
for clfg in list(range(31,37)):
	#Formatting
	for attr in list(range(2)):

		colors.append("\033["+str(attr)+";49;"+str(clfg)+"m")

for clfg in list(range(90,97)):
	for attr in list(range(2)):
		colors.append("\033["+str(attr)+";49;"+str(clfg)+"m")

clfg=39
for attr in list(range(2)):
	colors.append("\033["+str(attr)+";49;"+str(clfg)+"m")

