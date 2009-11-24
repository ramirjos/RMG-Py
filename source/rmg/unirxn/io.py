#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
#
#	RMG - Reaction Mechanism Generator
#
#	Copyright (c) 2002-2009 Prof. William H. Green (whgreen@mit.edu) and the
#	RMG Team (rmg_dev@mit.edu)
#
#	Permission is hereby granted, free of charge, to any person obtaining a
#	copy of this software and associated documentation files (the 'Software'),
#	to deal in the Software without restriction, including without limitation
#	the rights to use, copy, modify, merge, publish, distribute, sublicense,
#	and/or sell copies of the Software, and to permit persons to whom the
#	Software is furnished to do so, subject to the following conditions:
#
#	The above copyright notice and this permission notice shall be included in
#	all copies or substantial portions of the Software.
#
#	THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#	FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#	DEALINGS IN THE SOFTWARE.
#
################################################################################

"""
This module handles the reading and writing of input and output files involving
standalone called to the rmg.unirxn module.
"""

from rmg.io import *
from rmg.species import Species
from rmg.reaction import Reaction

from network import Network

def readInputFile(fstr):
	"""
	Parse an input file found at `fstr`. If successful, this function returns
	a :class:`Network` object containing the unimolecular reaction network and
	a tuple of options.
	"""

	try:

		# Parse the RMG input XML file into a DOM tree
		document = XML(path=fstr)

		# Make sure root element is a <rmginput> element
		rootElement = document.getRootElement()
		if rootElement.tagName != 'rmginput':
			raise InvalidInputFileException('Incorrect root element; should be <rmginput>.')

		# Load databases
		databases = readDatabaseList(document, rootElement)
		for database in databases:
			if database[1] == 'general':
				logging.debug('General database: ' + database[2])
				# Load only frequency database
				loadFrequencyDatabase(database[2] + os.sep)
		logging.debug('')

		# Create Network object
		network = Network()

		# Process species
		speciesDict = {}
		speciesListElement = document.getChildElement(rootElement, 'speciesList')
		speciesElements = document.getChildElements(speciesListElement, 'species')
		logging.info('Found ' + str(len(speciesElements)) + ' species')
		for element in speciesElements:
			# Load species ID
			sid = str(document.getAttribute(element, 'id', required=True))
			# Load the species data from the file
			species = Species()
			species.fromXML(document, element)
			# Add to local species dictionary (for matching with other parts of file)
			speciesDict[sid] = species
		logging.debug('')

		# Process reactions
		reactionListElement = document.getChildElement(rootElement, 'reactionList')
		reactionElements = document.getChildElements(reactionListElement, 'reaction')
		logging.info('Found %i reactions' % (len(reactionElements)))
		for reactionElement in reactionElements:
			reaction = Reaction()
			reaction.fromXML(document, reactionElement)
			network.pathReactions.append(reaction)
		logging.debug('')




		# Cleanup the DOM tree when finished
		document.cleanup()

	#except InvalidInputFileException, e:
	#	logging.exception(str(e))
	#	raise e
	#except InvalidXMLError, e:
	#	logging.exception(str(e))
	#	raise InvalidInputFileException(e.msg)
	#except IOError, e:
	#	logging.exception('Input file "' + e.filename + '" not found.')
	#	raise e
	except xml.parsers.expat.ExpatError, e:
		logging.exception('Invalid XML file: '+e.message+'\n')
		raise InvalidInputFileException('Invalid XML file: '+e.message)

################################################################################
