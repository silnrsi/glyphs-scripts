#MenuTitle: Load UFO family
# -*- coding: utf-8 -*-
__doc__="""
Loads a family of UFOs. Choose the Regular face and all others in the same folder will loaded. Requires that files be named according to http://silnrsi.github.io/FDBP/en-US/Font_Naming.html
"""
"""
To Do:
- Work around autosave problem
- Add support for custom master sets
"""
__copyright__ = 'Copyright (c) 2017, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

import os

familymembers = ['Bold', 'Italic', 'BoldItalic']

# Open Dialog:
fontfile = GetOpenFile()

if fontfile[-11:] == 'Regular.ufo':
	mainfont = GSFont(fontfile)
	familypath = fontfile[:-11]
	for s in familymembers:
		addfontpath = familypath + s + '.ufo'
		if os.path.exists(addfontpath):
			addfont = GSFont(addfontpath)
			mainfont.addFontAsNewMaster_(addfont.masters[0])
			mainfont.instances.append(addfont.instances[0].copy())
	Glyphs.fonts.append(mainfont)
else:
	Message('Try again','Please select a file with a name ending in Regular.ufo',OKButton='OK')
