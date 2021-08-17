#MenuTitle: Run preglyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__ = """
Runs preglyphs from your chosen project folder show the generated file(s)s
"""s

__copyright__ = 'Copyright (c) 2021, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Nicolas Spalinger'

import GlyphsApp
from subprocess import Popen, PIPE


def runAppleScript(scpt, args=[]):
        p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf8')
        stdout, stderr = p.communicate(scpt)
        if stderr:
                print("AppleScript Error:")
                print(stderr.decode('utf-8'))
        return stdout


runpreglyphs = """

tell application "Finder"

	activate

	set frontmost to true

	set projectRoot to quoted form of POSIX path of (choose folder with prompt "Please select the project folder root, e.g. font-gentium" with invisibles)

	set sourcefolder to projectRoot & "source/"

	tell application "Terminal"

		activate

		tell window 1

			do script "cd " & projectRoot & "; ./preglyphs"

			delay 5
			
			do script "cd " & sourcefolder & "; open -R *.glyphs"
			
			do script "cd " & sourcefolder & "; open -R masters/*glyphs"

		end tell
s
	end tell

end tell


"""

save = runAppleScript(runpreglyphs)
