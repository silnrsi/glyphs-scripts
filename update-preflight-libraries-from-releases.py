#MenuTitle: Update preflight libraries
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__ = """
Update preflight libraries (pysilfont/glyphsLib from master/main)
"""
__copyright__ = 'Copyright (c) 2021, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Nicolas Spalinger'

# using brew and sudo we expect launchers to be put into /usr/local/bin/ and the libs in /usr/local/lib
# but if you install manually with --user you will need to add ~/Library/Python/3.*/bin to your PATH in ~/.bash_profile

from subprocess import Popen, PIPE
import GlyphsApp

def runAppleScript(scpt, args=[]):
        p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf8')
        stdout, stderr = p.communicate(scpt)
        if stderr:
                print("AppleScript Error:")
                print(stderr.decode('utf-8'))
        return stdout


preflightupdate = """

tell application "Finder"

	tell application "Terminal"

		activate

		tell window 1

	        	do script "which python3; python3 --version; python3 -m pip --version; sudo -H python3 -m pip uninstall --yes pysilfont glyphsLib fontTools mutatorMath defcon fontMath; sudo -H python3 -m pip install --upgrade --no-cache-dir git+https://github.com/silnrsi/pysilfont.git@master#egg=pysilfont git+https://github.com/googlefonts/GlyphsLib.git@main#egg=glyphsLib fontTools fs mutatorMath defcon fontMath ; echo 'Please check to make sure these dependencies have been installed correctly: defcon, fontMath, fontTools, glyphsLib, MutatorMath and pysilfont. Only these dependencies are needed for preflight, other libraries can be reported as missing without problems. '; psfversion"

		end tell

	end tell

end tell

tell application "Finder"
	display notification "Updating, enter your password." with title "Preflight libraries: updating" sound name "default"
end tell

tell application "Finder"
	display notification "Libraries versions: see output" with title "Preflight librairies: versions"
end tell

tell application "Finder"
	display notification "Watch for issues, when done close the window" with title "Preflight librairies: done"
end tell


"""

save = runAppleScript(preflightupdate)
