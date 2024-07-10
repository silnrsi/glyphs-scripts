# MenuTitle: Build comps from SIL defs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Build or update glyphs from composite definitions in the SIL syntax. Under construction!
"""
__copyright__ = 'Copyright (c) 2015-2024, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'
# Based heavily on psfbuildcomp.py and comp.py from pysilfont (https://github.com/silnrsi/pysilfont/) 

# TO DO
# Remove old temp data and comments and debugging
# Test again with more data
# Support setting of Pendot override parameters
# Respect addGlyphs option
# Cell coloring
# Error checking
# Replace print with proper error log
# UI for control of input file and options

import re
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSGlyph, GSComponent

# defs and settings
thisFont = Glyphs.font  # frontmost font
thisFontMaster = thisFont.selectedFontMaster  # active master
thisMasterID = thisFontMaster.id
compDefsFilename = "compositestest.txt"  # relative to thisFont file - eventually to be replaced with user choice
addGlyphs = False    # should glyphs that don't exist in the font be added? Option not yet supported - glyph will be added

Glyphs.clearLog()  # clears log in Macro window

# temp stuff
oldtargetname = "iacute"
oldbasename = "idotless"
oldmarkname = "acutecomb"
oldanchorbase = "top"
oldanchormark = "_" + oldanchorbase

### PARSE COMP DEFS AND CREATE CompSpec OBJECT (taken from comp.py)
### REVISED TO NOT USE ElementTree

# REs to parse (from right to left) comment, SIL extension parameters, colorinfo, UID, metrics,
# and (from left) glyph name

# Extract comment from end of line (NB: Doesn't use re.VERBOSE because it contains #.)
# beginning of line, optional whitespace, remainder, optional whitespace, comment to end of line
noteinfo=re.compile(r"""^\s*(?P<remainder>.*?)(\s*#\s*(?P<noteinfo>.*))?$""")

# Parse SIL extension parameters in [...], but only after |
paraminfo=re.compile(r"""^\s*
    (?P<remainder>[^|]*
        ($|
        \|[^[]*$|
        \|[^[]*\[(?P<paraminfo>[^]]*)\]))
    \s*$""",re.VERBOSE)

# Parse colorinfo
colorinfo=re.compile(r"""^\s*
    (?P<remainder>[^!]*?)
    \s*
    (?:!\s*(?P<colorinfo>[.0-9]+(?:,[ .0-9]+){3}))?      # ! colorinfo
    (?P<remainder2>[^!]*?)
    \s*$""",re.VERBOSE)

# Parse uid
uidinfo=re.compile(r"""^\s*
    (?P<remainder>[^|]*?)
    \s*
    (?:\|\s*(?P<UID>[^^!]*)?)?                          # | followed by nothing, or 4- to 6-digit UID 
    (?P<remainder2>[^|]*?)
    \s*$""",re.VERBOSE)

# Parse metrics
metricsinfo=re.compile(r"""^\s*
    (?P<remainder>[^^]*?)
    \s*
    (?:\^\s*(?P<metrics>[-0-9]+\s*(?:,\s*[-0-9]+)?))?   # metrics (either ^x,y or ^a)
    (?P<remainder2>[^^]*?)
    \s*$""",re.VERBOSE)

# Parse glyph information (up to =)
glyphnameinfo=re.compile(r"""^\s*
    (?P<PSName>[._A-Za-z][._A-Za-z0-9-]*)               # glyphname
    \s*=\s*
    (?P<remainder>.*?)
    \s*$""",re.VERBOSE)

# break tokens off the right hand side from right to left and finally off left hand side (up to =)
initialtokens=[ (noteinfo,   'noteinfo', ""),  
                (paraminfo,   'paraminfo',   "Error parsing parameters in [...]"),
                (colorinfo,    'colorinfo',    "Error parsing information after !"),
                (uidinfo,     'UID',         "Error parsing information after |"),
                (metricsinfo, 'metrics',     "Error parsing information after ^"),
                (glyphnameinfo,    'PSName',      "Error parsing glyph name before =") ]

# Parse base and diacritic information
compdef=re.compile(r"""^\s*
    (?P<componentname>[._A-Za-z][._A-Za-z0-9-]*)             # name of base or diacritic in composite definition
        (?:@                                            # @ precedes position information
        (?:(?:\s*(?P<attachbase>[^: ]+)):)?             # optional base glyph to attach to followed by :
        \s*
        (?P<position>(?:[^ +&[])+)                      # position information (delimited by space + & [ or end of line)
        \s*)?                                           # end of @ clause
    \s*
    (?:\[(?P<params>[^]]*)\])?                          # parameters inside [..]
    \s*
    (?P<remainder>.*)$
    """,re.VERBOSE)

# Parse metrics
lsb_rsb=re.compile(r"""^\s*
    (?P<lsb>[-0-9]+)\s*(?:,\s*(?P<rsb>[-0-9]+))?        # optional metrics (either ^lsb,rsb or ^adv)
    \s*$""",re.VERBOSE)

# RE to break off one key=value parameter from text inside [key=value;key=value;key=value]
paramdef=re.compile(r"""^\s*
    (?P<paramname>[a-z0-9]+)                # paramname
    \s*=\s*                                 # = (with optional white space before/after)
    (?P<paramval>[^;]+?)                    # any text up to ; or end of string
    \s*                                     # optional whitespace
    (?:;\s*(?P<rest>.+)$|\s*$)              # either ; and (non-empty) rest of parameters, or end of line
    """,re.VERBOSE)

class CompSpec:

    def __init__(self):
        self.compdefline = None
        self.psname = ""
        self.note = None
        self.uid = None
        self.color = None
        self.paramsdic = None
        self.metricsdic = None
        self.glyphlist = []

    def _parseparams(self, rest):
        """Parse a parameter line such as:
        key1=value1;key2=value2
        and return a dictionary with key:value pairs.
        """
        params = {}
        while rest:
            matchparam=re.match(paramdef,rest)
            if matchparam == None:
                raise ValueError("Parameter error: " + rest)
            params[matchparam.group('paramname')] = matchparam.group('paramval')
            rest = matchparam.group('rest')
        return(params)

    def parsefromcompdefline(self):
        """Parse the composite glyph information (in self.compdefline) such as:
        LtnCapADiear = LtnCapA + CombDiaer@U |00C4 ! 1, 0, 0, 1 # comment
        and return a list of component specs.
        Position info after @ can include optional base glyph name followed by colon.
        """
        line = self.compdefline
        results = {}
        for parseinfo in initialtokens:
            if len(line) > 0:
                regex, groupname, errormsg = parseinfo
                matchresults = re.match(regex,line)
                if matchresults == None:
                    raise ValueError(errormsg)
                line = matchresults.group('remainder')
                resultsval = matchresults.group(groupname)
                if resultsval != None:
                    results[groupname] = resultsval.strip()
                    if groupname == 'paraminfo': # paraminfo match needs to be removed from remainder
                        line = line.rstrip('['+resultsval+']')
                if 'remainder2' in matchresults.groupdict().keys(): line += ' ' + matchresults.group('remainder2')
        # At this point results optionally may contain entries for any of 'noteinfo', 'paraminfo', 'colorinfo', 'UID', or 'metrics', 
        # but it must have 'PSName' if any of 'paraminfo', 'colorinfo', 'UID', or 'metrics' present

        #print("R=", results)

        self.psname = results['PSName']
        if 'PSName' not in results:
            if len(results) > 0:
                raise ValueError("Missing glyph name")
            else: # comment only, or blank line
                return None
            
        if 'noteinfo' in results:
            note = results.pop('noteinfo', None)
            notetext = note.rstrip()
            self.note = notetext

        if 'colorinfo' in results:
            color = results.pop('colorinfo', None)
            self.color = color

        if 'UID' in results:
            uid = results.pop('UID')
            self.uid = uid
            UIDpresent = True

        paramsdic = {}

        if 'paraminfo' in results:
            paramdata = results.pop('paraminfo')
            if UIDpresent:
                paramsdic = self._parseparams(paramdata)
                self.paramsdic = paramsdic
            else:
                line += " [" + paramdata + "]"

        metricsdic = {}

        if 'metrics' in results:
            m = results.pop('metrics')
            matchmetrics = re.match(lsb_rsb,m)
            if matchmetrics == None:
                raise ValueError("Error in parameters: " + m)
            elif matchmetrics.group('rsb'):
                metricsdic = {'lsb': matchmetrics.group('lsb'), 'rsb': matchmetrics.group('rsb')}
            else:
                metricsdic = {'advance': matchmetrics.group('lsb')}
            self.metricsdic = metricsdic
        else:
            metricsdic = None

        # Prepare to parse remainder of line
        prevbase = None
        prevdiac = None
        remainder = line
        expectingdiac = False
        glyphlist = []

        # top of loop to process remainder of line, breaking off base or diacritics from left to right
        while remainder != "":
            matchresults=re.match(compdef,remainder)
            if matchresults == None or matchresults.group('componentname') == "" :
                raise ValueError("Error parsing glyph name: " + remainder)
            
            componentname = matchresults.group('componentname')
            attachbase = matchresults.group('attachbase')
            position = matchresults.group('position')

            # Start gathering details of new component
            # Currently dumping any params inc. shifts into a propdic for now since we rarely use them (should be changed later)
            newcomponent = {'name': componentname}

            propdic = {}
            if matchresults.group('params'):
                propdic = self._parseparams(matchresults.group('params'))
                newcomponent['propdic'] = propdic
            
            if expectingdiac:
                # Determine parent element, based on previous base and diacritic glyphs and optional
                # matchresults.group('base'), indicating diacritic attaches to a different glyph
                if attachbase == None:
                    if prevdiac != None:
                        parent = prevdiac
                    else:
                        parent = prevbase
                elif attachbase != prevbase:
                    raise ValueError("Error in diacritic alternate base glyph: " + attachbase)
                else:
                    parent = prevbase
                    if prevdiac == None:
                        raise ValueError("Unnecessary diacritic alternate base glyph: " + attachbase)
                if position:
                    if 'with' in propdic:
                        withval = propdic.pop('with')
                    else:
                        withval = "_" + position
                    newcomponent['at'] = position
                    newcomponent['with'] = withval
                    newcomponent['prevglyph'] = parent
                prevdiac = componentname
            elif (attachbase or position):
                raise ValueError("Position information on base glyph not supported")
            else:
                prevbase = componentname
                prevdiac = None

            glyphlist.append( newcomponent )
            print( newcomponent )

            remainder = matchresults.group('remainder').lstrip()
            nextchar = remainder[:1]
            remainder = remainder[1:].lstrip()
            expectingdiac = nextchar == '+'
            if nextchar == '&' or nextchar == '+':
                if len(remainder) == 0:
                    raise ValueError("Expecting glyph name after & or +")
            elif len(nextchar) > 0:
                raise ValueError("Expecting & or + and found " + nextchar)
            
        self.glyphlist = glyphlist

### FUNCTIONS

def loadLocalFile( currFont, filename ): # read file in cuttent font's directory
    currFontPath = currFont.filepath
    currFontDir = os.path.dirname( currFontPath )
    localFilePath = os.path.join( currFontDir, filename )
    fin = open( localFilePath, "rt", encoding="utf-8" )
    contents = fin.read()
    fin.close()
    return contents

def updateGlyph(name, comps, anchors, width, uid): # create or update glyph from spec
    target = thisFont.glyphs[name]
    if not target:  # will always create a new glyph if not currently in font
        target = GSGlyph()
        target.name = name
        thisFont.glyphs.append(target)
    target.unicode = uid
    targetLayer = target.layers[thisMasterID]
    targetLayer.clear()
    for comp in comps:
        newComp = GSComponent(comp['name'], NSPoint(comp['offsetX'], comp['offsetY']))
        targetLayer.components.append(newComp)
    for anchor in anchors:
        targetLayer.anchors[anchor['ancname']] = GSAnchor()
        targetLayer.anchors[anchor['ancname']].position = NSPoint(anchor['posX'], anchor['posY'])
    targetLayer.width = width

### MAIN ROUTINE

# grab comp defs into a list
compDefs = loadLocalFile( thisFont, compDefsFilename )
print(">>>>> Full file content:")
print( compDefs, "\n" )
print(">>>>> Individual contents:")

# parse the list and process as composite specification objects
csobj = CompSpec()

for rawCDLine in compDefs.splitlines():
    CDLine = rawCDLine.strip()
    if len(CDLine) == 0 or CDLine[0] == "#": continue
    print( "-----" )
    csobj.compdefline = CDLine
    try:
        csobj.parsefromcompdefline()
    except ValueError as mess:
        print("Parsing error: " + str(mess))
        continue

    cdl = csobj.compdefline
    targetGlyphName = csobj.psname
    uid = csobj.uid
    glyphlist = csobj.glyphlist
    n = csobj.note          # will currently be ignored when building composite
    c = csobj.color         # will currently be ignored when building composite
    pd = csobj.paramsdic    # will currently be ignored when building composite
    md = csobj.metricsdic   # will currently be ignored when building composite
    print( "cdl > ", cdl )
    print( "ps u c n pd md> ", targetGlyphName, "/", uid, "/", c, "/", n, "/", pd, "/", md )
    print( "glyphlist >\n", glyphlist )

    # find each component glyph and compute x,y position (based on psfbuildcomp)
    xadvance = 0
    components = []
    targetAnchors = []
    targetAnchorSpecs = {}

    for g in glyphlist:
        currGlyphName = g['name']
        currGlyph = thisFont.glyphs[currGlyphName]
        if not currGlyph:
            print(currGlyph, "not found in font")
            continue
        currGlyphLayer = currGlyph.layers[thisMasterID]

        cgAnchors = currGlyphLayer.anchors

        if 'with' in g: diacAP = g['with']
        else: diacAP = None
        if 'at' in g: baseAP = g['at']
        else: baseAP = None
        if 'prevglyph' in g: prevG = g['prevglyph']
        else: prevG = None

        diacAPx = diacAPy = 0
        baseAPx = baseAPy = 0

        if prevG is None:   # this is new 'base'
            offsetX = xadvance
            offsetY = 0
            xadvance += currGlyphLayer.width
        else:                 	# this is 'attach'
            if diacAP is not None: # find diacritic Attachment Point in currglyph
                if not cgAnchors[diacAP]:
                    print("The AP '" + diacAP + "' does not exist on diacritic glyph " + currGlyphName)
                else:
                    diacAPx = cgAnchors[diacAP].position.x
                    diacAPy = cgAnchors[diacAP].position.y
            else:
                print("No AP specified for diacritic " + currGlyphName)
            if baseAP is not None: # find base character Attachment Point in targetglyph
                if baseAP in targetAnchorSpecs:
                    baseAPx = targetAnchorSpecs[baseAP]['posX']
                    baseAPy = targetAnchorSpecs[baseAP]['posY']
                    del targetAnchorSpecs[baseAP]
                else:
                    print("The AP '" + baseAP + "' does not exist on base glyph when building " + targetGlyphName)
            offsetX = baseAPx - diacAPx
            offsetY = baseAPy - diacAPy

        component = {'name': currGlyphName}
        #if offsetX != 0: component['offsetX'] = offsetX
        #if offsetY != 0: component['offsetY'] = offsetY
        component['offsetX'] = offsetX
        component['offsetY'] = offsetY
        components.append( component )

        # Move anchor information to targetAnchors
        for a in cgAnchors:
            thisAnchorName, thisAnchorX, thisAnchorY = a.name, a.position.x, a.position.y
            if diacAP is not None and thisAnchorName == diacAP:
                continue # skip this anchor
            targetAnchorSpecs[thisAnchorName] = {'ancname': thisAnchorName, 'posX': thisAnchorX + offsetX, 'posY': thisAnchorY + offsetY}

    for spec in targetAnchorSpecs:
        targetAnchors.append( targetAnchorSpecs[spec])

    print("targetGlyphName >", targetGlyphName)
    print('components >', components)
    print('targetAnchors >', targetAnchors)
    print('width >', xadvance)
    print('uid >', uid)

    updateGlyph(targetGlyphName, components, targetAnchors, xadvance, uid)

"""updateGlyph("IJ",
    [{'name': 'I', 'offsetX': 0, 'offsetY': 0}, {'name': 'J', 'offsetX': 1500, 'offsetY': 0}],
    [{'ancname': 'top', 'posX': 1365, 'posY': 1770}, {'ancname': 'bottom', 'posX': 1365, 'posY': -100}],
    2730, "0132")
updateGlyph("ij",
    [{'name': 'i', 'offsetX': 0, 'offsetY': 0}, {'name': 'j', 'offsetX': 620, 'offsetY': 0}],
    [{'ancname': 'top', 'posX': 620, 'posY': 1600}, {'ancname': 'bottom', 'posX': 620, 'posY': -100}],
    1240, "0133")
"""
# walk through list of targets
# process 'glyphlist' list of components
# check that they exist in the font and grab their anchor data
# calculate component offsets
# move anchor info to target def
# flatten components
# check if this new glyph exists in the font already; if so, decide whether to replace, or issue warning
# updateGlyph()



Glyphs.showMacroWindow()

"""
if thisFont.glyphs[basename] and thisFont.glyphs[markname]:
    base = thisFont.glyphs[basename]
    baseRegLayer = base.layers["Regular"]
    print( baseRegLayer )
    baseanchor = baseRegLayer.anchors[anchorbase]
    print( baseanchor )
    baseX = baseanchor.x
    print( baseX )
    baseY = baseanchor.y
    print( baseY )
    mark = thisFont.glyphs[markname]
    markRegLayer = mark.layers["Regular"]
    print( markRegLayer )
    markanchor = markRegLayer.anchors[anchormark]
    print( markanchor )
    markX = markanchor.x
    print( markX )
    markY = markanchor.y
    print( markY )
    offsetX = baseX - markX
    offsetY = baseY - markY
    target = thisFont.glyphs[targetname]
    if not target:
        target = GSGlyph()
        target.name = targetname
        thisFont.glyphs.append(target)
    for thisLayer in target.layers:
        thisLayer.clear()
        basecomp = GSComponent(basename)
        markcomp = GSComponent(markname, NSPoint(offsetX, offsetY))
        thisLayer.components.append(basecomp)
        thisLayer.components.append(markcomp)
else:
    print("Sources not found in font")
    """
