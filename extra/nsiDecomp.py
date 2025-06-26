##                                                      encoding: utf-8 
##   NullsoftDecompiler 1.2 alpha
##
##
##   Decompiles 'script.bin' -> 'script.bin.nsi'
##   (Note: that thingy is anything else than finished yet)
##
##   To run that file you'll need to install Python:
##   
##   http://www.python.org/ftp/python/2.7.6/python-2.7.6.msi
##   http://www.python.org/download/
##
##   Tested with python 2.7.3
##		
##   Updates:
##	Please see if there are any news:
##	http://deioncube.in/files/?dir=cw2k/Nullsoft%20Installer%20Decompiler
##
##   Pimpup options: (if 'idle' is not good enough)
##
##      http://www.activestate.com/activepython/downloads
##  OR
##      http://www.wingware.com/downloads/wingide
##          -> http://sourceforge.net/projects/easypythondecompiler/
##          -> c:\Program Files\Wing IDE 5.0\bin\2.7\src.zip\process\abstract.py
##          ->    def LicenseOK(self):
##                   return 1  # <- add type line
##           Note: delete abstract.pyo and just put EDITED abstract.py there
##
##                                                          cw2k ätt gmx.de
###############################################################################
##
##  History:
##
##   1.2 feb 2014 first release
## 
VERSION = "1.2"

import struct
import os,sys

###############  C o n f i g ' s  ##################

DoDecompile = 1 #False
DumpStrings = 1 #False
supressCodeOutsideSections = 0
supressRawTokens = 0
CommentOutWriteUninstaller = 1 

####################################################

NSIS_COMMENT = '#'

isVerNS3 = 0

fDecomp_Dir = '!Decompiled'

CurrFileName = ""
CurrFileOffset = 0

FileRaw_Num = [0]
fo = 0
fo2 = 0
fo3 = 0
fDecomp = 0
a={}

HeaderAddlines = 'AddBrandingImage left 100'

UserVarNames = {}

# for extracting ...
class FileExtract:
    CurDir = ''
    Files  = []
    isUninstall = False


File_Num = 0

err_Region__Num = 0
err_Region_Start = 0

TOKENBASE = 1
isInsideSection = False

class switch(object):
    value = None
    def __new__(class_, value):
        class_.value = value
        return True

def case(*args):
    return any((arg == switch.value for arg in args))


def extend(a,b):
    """Create a new dictionary with a's properties extended by b,
    without overwriting.

    >>> extend({'a':1,'b':2},{'b':3,'c':4})
    {'a': 1, 'c': 4, 'b': 2}
    """
    return dict(a,**b)

def uI32ToI32(value):
    return(Long(~value) & 0x80000000L )

class myFile(file):

    def byte( self ):
        return file.read( self,  1);

    def i8( self ):
        tmp = self.byte( )
        return struct.unpack( "<b", tmp )[0];

    def uInt8( self ):
        tmp = self.byte( )
        return struct.unpack( "<B", tmp )[0];

    def i8_write( self, data  ):
        tmp = struct.pack( "<b", data );
        file.write( self, tmp)

    def uInt16( self ):
        tmp = file.read( self,  2)
        return struct.unpack( "<H", tmp )[0];

    def uInt32( self ):
        tmp = file.read( self,  4)
        return struct.unpack( "<I", tmp )[0];

    def uInt32_rgb( self ):
        tmp = file.read( self,  4)
        return struct.unpack( ">I", tmp )[0] >>8;

    def uInt24( self ):
        tmp = '\0' + file.read( self,  3)

        return struct.unpack( "<I", tmp )[0];

    def Int32( self ):
        tmp = file.read( self,  4)
        return struct.unpack( "<i", tmp )[0];

    def read_sz(self):
        """
        Reads a null-terminated string from the file. This is not implemented
        in an efficient manner for long strings!
        """
        output_string = ''
        char = self.read(1)
        while char != '\x00':
            output_string += char
            char = self.read(1)
            if len(char) == 0:
                break
        return output_string



    
from StringIO import StringIO

class myString(StringIO):

    def byte( self ):
        return 	StringIO.read( self,  1);

    def i8( self ):
        tmp = self.byte( )
        return struct.unpack( "<b", tmp )[0];

    def uInt8( self ):
        tmp = self.byte( )
        return struct.unpack( "<B", tmp )[0];

    def i8_write( self, data  ):
        tmp = struct.pack( "<b", data );
        StringIO.write( self, tmp)

    def uInt16( self ):
        tmp = StringIO.read( self,  2)
        return struct.unpack( "<H", tmp )[0];

    def uInt32( self ):
        tmp = StringIO.read( self,  4)
        return struct.unpack( "<I", tmp )[0];

    def uInt32_rgb( self ):
        tmp = StringIO.read( self,  4)
        return struct.unpack( ">I", tmp )[0] >>8;

    def uInt24( self ):
        tmp = '\0' + StringIO.read( self,  3)

        return struct.unpack( "<I", tmp )[0];

    def Int32( self ):
        tmp = StringIO.read( self,  4)
        return struct.unpack( "<i", tmp )[0];

    def read_sz(self):
        """
        Reads a null-terminated string from the StringIO. This is not implemented
        in an efficient manner for long strings!
        """
        output_string = ''
        char = self.read(1)
        while char != '\x00':
            output_string += char
            char = self.read(1)
            if len(char) == 0:
                break
        return output_string



    
    
class cls_Decomp:
    Sections_start = {}
    Sections_idx_To_Offset = {}
    Sections_idx = {}
    SectionsIN = {}
    Sections_end = {}
    isInsideSection = False


    Labels = {}
    Functions = {}
    isInsideFunction = False

    Tokens = {}
    Decomps = {}
    Comments = {}

    SectionTxt = {}
    DoSupress = {}

    SetOverwrite = 0  #'on'



class EW_Tokens:
    EW_INVALID_OPCODE,    \
        \
        EW_RET,               \
        EW_NOP,               \
        EW_ABORT,             \
        EW_QUIT,              \
        EW_CALL,              \
        EW_UPDATETEXT,        \
        EW_SLEEP,             \
        EW_BRINGTOFRONT,      \
        EW_CHDETAILSVIEW,     \
        EW_SETFILEATTRIBUTES, \
        EW_CREATEDIR,         \
        EW_IFFILEEXISTS,      \
        EW_SETFLAG,           \
        EW_IFFLAG,            \
        EW_GETFLAG,           \
        \
        EW_RENAME,            \
        \
        \
        EW_GETFULLPATHNAME,   \
        EW_SEARCHPATH,        \
        EW_GETTEMPFILENAME,   \
        \
        \
        EW_EXTRACTFILE,       \
        \
        \
        \
        EW_DELETEFILE,        \
        \
        \
        EW_MESSAGEBOX,        \
        \
        \
        EW_RMDIR,             \
        \
        \
        EW_STRLEN,            \
        EW_ASSIGNVAR,         \
        EW_STRCMP,            \
        \
        \
        EW_READENVSTR,        \
        \
        \
        EW_INTCMP,            \
        EW_INTOP,             \
        EW_INTFMT,            \
        \
        \
        EW_PUSHPOP,           \
        \
        \
        EW_FINDWINDOW,        \
        EW_SENDMESSAGE,       \
        EW_ISWINDOW,          \
        \
        \
        EW_GETDLGITEM,        \
        EW_SETCTLCOLORS,      \
        EW_SETBRANDINGIMAGE,  \
        EW_CREATEFONT,        \
        EW_SHOWWINDOW,        \
        \
        \
        EW_SHELLEXEC,         \
        \
        \
        EW_EXECUTE,           \
        \
        \
        EW_GETFILETIME,       \
        \
        \
        EW_GETDLLVERSION,     \
        \
        \
        EW_REGISTERDLL,       \
        \
        \
        EW_CREATESHORTCUT,    \
        \
        \
        EW_COPYFILES,         \
        \
        \
        EW_REBOOT,            \
        \
        \
        EW_WRITEINI,          \
        EW_READINISTR,        \
        \
        \
        EW_DELREG,            \
        EW_WRITEREG,          \
        \
        EW_READREGSTR,        \
        EW_REGENUM,           \
        \
        \
        EW_FCLOSE,            \
        EW_FOPEN,             \
        EW_FPUTS,             \
        EW_FGETS,             \
        EW_FSEEK,             \
        \
        \
        EW_FINDCLOSE,         \
        EW_FINDNEXT,          \
        EW_FINDFIRST,         \
        \
        \
        EW_WRITEUNINSTALLER,  \
        \
        \
        \
        \
        EW_SECTIONSET,        \
        \
        \
        \
        EW_INSTTYPESET,       \
        \
        \
        \
        EW_GETLABELADDR,      \
        EW_GETFUNCTIONADDR, \
        \
        EW_LOCKWINDOW, \
        \
        EW_FPUTWS, \
        EW_FGETWS, \
        = range(0x46)

    def __init__(self):
        ''' Creates EW_* Names List
        '''
        # That get's all varNames in the class
        d = EW_Tokens.__dict__

        # Creates a dictory that will look like this: {..., 2: EW_NOP,  3: EW_ABORT, ... }
        EW_Tokens.__Names = dict((value, key) \
                                 for (key, value) in d.iteritems() \
                                 if key.startswith('EW_'))
        print EW_Tokens.__Names


    def Names ( self,op ):
        return EW_Tokens.__Names[op]

NB_STRINGS_Max = 0
NB_STRINGS = 0
NB_LANGTABLES = 0

Tokenindex = 1

DecompComment = ''

strOffset=0

#setup\nsis-2.09-src\Source\build.cpp
#  m_UserVarNames\.add\("([^"]*)",[^/]*// (..).*
# $2 \t: '$1', \
m_UserVarNames = {
# init with 1
    0 	: '0', \
    1 	: '1', \
    2 	: '2', \
    3 	: '3', \
    4 	: '4', \
    5 	: '5', \
    6 	: '6', \
    7 	: '7', \
    8 	: '8', \
    9 	: '9', \
    10 	: 'R0', \
    11 	: 'R1', \
    12 	: 'R2', \
    13 	: 'R3', \
    14 	: 'R4', \
    15 	: 'R5', \
    16 	: 'R6', \
    17 	: 'R7', \
    18 	: 'R8', \
    19 	: 'R9', \
    20 	: 'CMDLINE', \
    21 	: 'INSTDIR', \
    22 	: 'OUTDIR', \
    23 	: 'EXEDIR', \
    24 	: 'LANGUAGE', \
# init with -1
    25 	: 'TEMP', \
    26 	: 'PLUGINSDIR', \
    27 	: 'EXEPATH', \
    28 	: 'EXEFILE', \
    29 	: 'HWNDPARENT', \
    30 	: '_CLICK', \
# init with 1
    31 	: '_OUTDIR', \

}

import csidl

CSIDLs = { \
    csidl.CSIDL_WINDOWS: 'WINDIR', \
    csidl.CSIDL_SYSTEM: 'SYSDIR', \
    csidl.CSIDL_PROGRAM_FILES: 'PROGRAMFILES', \
    csidl.CSIDL_PROGRAMS: 'SMPROGRAMS', \
    csidl.CSIDL_STARTUP: 'SMSTARTUP', \
    csidl.CSIDL_DESKTOPDIRECTORY: 'DESKTOP', \
    csidl.CSIDL_STARTMENU: 'STARTMENU', \
    csidl.CSIDL_APPDATA: 'QUICKLAUNCH', \
    csidl.CSIDL_PROGRAM_FILES_COMMON: 'COMMONFILES', \
    csidl.CSIDL_PERSONAL: 'DOCUMENTS', \
    csidl.CSIDL_SENDTO: 'SENDTO', \
    csidl.CSIDL_RECENT: 'RECENT', \
    csidl.CSIDL_FAVORITES: 'FAVORITES', \
    csidl.CSIDL_MYMUSIC: 'MUSIC', \
    csidl.CSIDL_MYPICTURES: 'PICTURES', \
    csidl.CSIDL_MYVIDEO: 'VIDEOS', \
    csidl.CSIDL_NETHOOD: 'NETHOOD', \
    csidl.CSIDL_FONTS: 'FONTS', \
    csidl.CSIDL_TEMPLATES: 'TEMPLATES', \
    csidl.CSIDL_APPDATA: 'APPDATA', \
    csidl.CSIDL_LOCAL_APPDATA: 'LOCALAPPDATA', \
    csidl.CSIDL_PRINTHOOD: 'PRINTHOOD', \
    csidl.CSIDL_ALTSTARTUP: 'ALTSTARTUP', \
    csidl.CSIDL_INTERNET_CACHE: 'INTERNET_CACHE', \
    csidl.CSIDL_COOKIES: 'COOKIES', \
    csidl.CSIDL_HISTORY: 'HISTORY', \
    csidl.CSIDL_PROFILE: 'PROFILE', \
    csidl.CSIDL_ADMINTOOLS: 'ADMINTOOLS', \
    csidl.CSIDL_RESOURCES: 'RESOURCES', \
    csidl.CSIDL_RESOURCES_LOCALIZED: 'RESOURCES_LOCALIZED', \
    csidl.CSIDL_CDBURN_AREA: 'CDBURN_AREA', \
}


exec_flags_autoclose      = 0
exec_flags_all_user_var   = 1
exec_flags_exec_error     = 2
exec_flags_abort          = 3
exec_flags_exec_reboot    = 4
exec_flags_reboot_called  = 5
exec_flags_XXX_cur_insttype = 6
exec_flags_XXX_insttype_changed  = 7 # Renamed to 'exec_flags_plugin_api_version'  in ver3
exec_flags_silent         = 8
exec_flags_instdir_error  = 9
exec_flags_rtl            = 10
exec_flags_errlvl         = 11

#new in Ver3
exec_flags_alter_reg_view         = 12  
exec_flags_status_update          = 13

REG_HKEYS = "HKCR HKCU HKLM HKU HKPD HKCC HKDD SHCTX" 

def BitOptions (Flag, Names, Sep = ' '):

    if type(Names)==str:
        Names = Names.split(Sep)

    StrAttributes = ''

    MaskBitselect = 1
    for bits in range( Flag.bit_length() ):
        bit =  Flag & MaskBitselect

        if bit:

            StrAttributes += ( '' if (StrAttributes == '') else Sep)

            try:
                if type(Names) == dict:
                    StrAttributes += Names [bit]

                else:
                    StrAttributes += Names [bits]

            except:
                StrAttributes += Sep + '0x%X' % (Flag >> bits)

        MaskBitselect <<= 1

    return StrAttributes


def E( data, Enum = '', PreFix_NotFound = ''):
    return getnumtokens( data, Enum, PreFix_NotFound )

def getnumtokens( data, Enum = '', PreFix_NotFound = '' ):
    global DecompComment

    try:
        index = int( S(data) )
    except Exception:
        DecompComment += ' Whoops using data directly as enum idx.'
        index = data

    try:
        EnumList = Enum.split(' ')
        return EnumList [index]
    except IndexError:
        DecompComment += "Select EnumMember '%i' fail - plz do it manually from this list: %s" % (index, Enum)

        return PreFix_NotFound + '%i' % index


def SECTION_FIELD( data):

    data = GetNSISString(data)
    SectidxName = "Section_%s" % data

    Offset = cls_Decomp.Sections_idx_To_Offset[ int(data) ]
    cls_Decomp.Sections_idx[ Offset] = SectidxName

    return '${' + SectidxName + '}'

def F( data):
    return ns_func( data, 'func')

def ns_func( data, Prefix = '', Offset = 0, AppendOffset = True):
    # create Label Text    
    if type(data) == str:
        if (Offset < 0): # TODO .. or Entries[Offset] == EW_RET
            return '""'
        FuncText =  '%s%s' % (Prefix, data) 
        if AppendOffset:
            FuncText +=  '_%X' % Offset
        
        data = Offset
    else:
        if (data < 0):
            FuncText = GetUserVarName(~data)
        else:
            FuncText = '%s_0x%X' % (Prefix, data)

    # Store in
    cls_Decomp.Functions[data + TOKENBASE] = 'Function ' + FuncText + '\n'
    #cls_Decomp.isInsideFunction = True

    return FuncText

def LL( yes, no):
    if no:
        return '%s %s' % ( ns_label( yes, 0) , ns_label( no) )
    else:
        return ns_label( yes )

def L( data):
    return ns_label( data )

def ns_label( data, Empty='', Prefix = 'Label'):
    if data: 
        # create Label Text    
        LabelText =  '%s_0x%X' % (Prefix, data)

        # Store in Labels
        cls_Decomp.Labels[data] = LabelText + ':'
    else:
        LabelText = Empty

    return LabelText


def I( data, Prefix = '', SkipIfNull = False  ):
    return gettoken_int( data, Prefix, SkipIfNull )

def gettoken_int( data, Prefix = '', SkipIfNull = False ):
    if data or (SkipIfNull == False):
        return Prefix + '%i' % data
    else:
        return ''

def V( data):
    return GetUserVarIndex( data)

def GetUserVarIndex ( data):
    return GetUserVarName(data)

    #if data in range(0,99):
        #return '$%i' % data
    #else:
        #return GetNSISString( data)


def B( data ):
    if isVerNS3:
        return repr( GetNSISString( data ) )
    else:
        return hex(data)
    
#Quote Empty stringd
def Sq( data, Prefix = ''  ):
    tmp = add_string( data, Prefix )
    if tmp == "":
        return '""'
    else:
        return tmp 

def S_Int( data, Prefix = '', Postfix = ''  ):
    return add_intstring( data, Prefix, Postfix )

def add_intstring( data, Prefix = '', Postfix = ''  ):
    try:
        return int(S( data, Prefix, Postfix ))
    except ValueError:
        if data==0:
            return 0
        else:
            raise(ValueError)

def S( data, Prefix = '', Postfix = ''  ):
    return add_string( data, Prefix, Postfix )

def add_string( data, Prefix = '', Postfix = ''  ):
    return quoteStringIfNeeded (Prefix + GetNSISString( data ) + Postfix)

def JJ( yes, no ):
    return LL( yes, no )

def J( data ):
#    return L( data )
    return process_jump( data )

def process_jump( data ):
    if data <= 0: return ''
    
    global Tokenindex
    TokenRelatively =  data - Tokenindex 

    global DecompComment
    DecompComment += " Or 0x%x " % data


    return '%+i' % TokenRelatively

    #return GetNSISString( data )


def MaskNewLine( data ):
    return  data \
              .replace( '$' , '$$'  ) \
              .replace('\n' , '$\\n') \
              .replace('\r' , '$\\r') \
              .replace('\t' , '$\\t') \


def quoteString( data ):
    hasSingleQ   = "'" in data
    hasSingleBwQ = "`" in data
    hasDoubleQ   = '"' in data
    if   hasSingleBwQ and hasSingleQ and hasDoubleQ:
        #if '$' in data:
        #    data = data.replace('$','$$')
        
        return  '"%s"' % data.replace('"','$\\"')
    
    elif hasSingleQ and hasDoubleQ:
        return  '`%s`' % data
        
    elif hasSingleQ:
        return  '"%s"' % data
    else:
        return  "'%s'" % data
    
def quoteStringIfNeeded( data ):
    hasSpace = " " in data
    hasDash  = "#" in data
    isKeyword = "section" in data.lower()
    if hasSpace or hasDash or isKeyword:
        return  quoteString( data )
    else:
        return data


# stupid buggy macro from fileform.h   
def DECODE_SHORT (fo, TypeForDebug = '' ):
    A = fo.uInt8()
    B = fo.uInt8()
    nData = ( (B & ~0x80) << 7) | \
        (A & ~0x80)
#   print TypeForDebug + " 0x%X | 0x%X<<7 => %x" % (A, B, nData)


    return nData

def GetNSISString( strOffset, fo2NoSeekback = False):

    global NB_STRINGS, NB_STRINGS_Max;
    global NB_LANGTABLES
    global isVerNS3

#nsis-2.09-src
    NS_SKIP_CODE  = 252  #0xfc    // to consider next character as a normal character
    NS_VAR_CODE   = 253  #0xfd    // for a variable
    NS_SHELL_CODE = 254  #0xfe    // for a shell folder path
    NS_LANG_CODE  = 255  #0xff    // for a langstring

#nsis-3.0a2-src
        #NS_LANG_CODE  _T('\x01')
        #NS_SHELL_CODE _T('\x02')
        #NS_VAR_CODE   _T('\x03')
        #NS_SKIP_CODE  _T('\x04')

    if isVerNS3:
        NS_SKIP_CODE    = -NS_SKIP_CODE     & 0xff
        NS_VAR_CODE     = -NS_VAR_CODE      & 0xff
        NS_SHELL_CODE   = -NS_SHELL_CODE    & 0xff
        NS_LANG_CODE    = -NS_LANG_CODE     & 0xff

    NS_CODES_START = NS_SKIP_CODE

    if strOffset < 0:
        NB_offset = NB_LANGTABLES +2 +4  + -strOffset * 4
        #print "NB_LANGTABLES_off: @0x%X" % ( NB_offset )
        fo3.seek( NB_offset )
        strOffset = fo3.Int32()
        print "NB_LANGTABLES: @0x%X : %X" % (NB_offset, strOffset)


    if strOffset in range(0, NB_STRINGS_Max ):

        fo2_oldPos = fo2.tell()

        fo2.seek( NB_STRINGS + strOffset -1)

        # Previous chat must be an string terminator
        if fo2.i8():
            global DecompComment
            DecompComment += 'GetNSISString(): inside string warning:'


#     strData = fo2.read_sz()
        strData = ''
        char = fo2.read(1)
        while char != '\x00':
            if (ord(char) >= NS_CODES_START) if isVerNS3 else \
               (ord(char) <  NS_CODES_START):
                strData += MaskNewLine( char )

            else:
                ns = ord(char)
                #print "NS_CODE: 0x%X" % ns

                if ns == NS_SHELL_CODE:
##               if isVerNS3:
##                   nsCur = DECODE_SHORT(fo2, 'NS_SHELL_CODE' )
##                   nsAll = nsCur
##               else:
                    nsCur = fo2.uInt8()
                    nsAll = fo2.uInt8()

                    #msg = "NS_SHELL_CODE(%x): cur:0x%X  all:0x%X" % (ns, nsCur, nsAll)
                    #print msg
                    #DecompComment += msg

                    if (nsCur & 0x80):# and isVerNS3:

                        isX64     = nsCur & 0x40
                        is32onX64 = nsCur & 0xC0  # <= 0x80|0x40 !
                        # that is wrong or crap since it'll be always true

                        # so there's just 00..3F space left for indexing
                        retval = GetNSISString(nsCur & 0x3F)

                        #print "retval => %s" % retval
                        if   "ProgramFilesDir" == retval:
                            expanded = CSIDLs [csidl.CSIDL_PROGRAM_FILES]

                        elif "CommonFilesDir" == retval:
                            expanded = CSIDLs [csidl.CSIDL_PROGRAM_FILES_COMMON]

                        else:
                            expanded = retval +'!!<- HKLM\Software\\Microsoft\\Windows\\CurrentVersion\[This]!!'

                        if isX64:
                            expanded += '32' if is32onX64 else '64'


                    else:


                        try:
                            expanded = CSIDLs [nsAll]
                        except KeyError:
                            try:
                                expanded = CSIDLs [nsCur]
                            except KeyError:
                                expanded = 'Unknown_CSIDL_%X_or_%X' % (nsAll, nsCur)

                    #print '%s' % expanded
                    strData += '$' + expanded


                elif ns == NS_VAR_CODE:
                    nData =  DECODE_SHORT(fo2, 'NS_VAR_CODE' )
                    strData += GetUserVarName(nData)


                elif ns == NS_LANG_CODE:
                    #nData = DECODE_SHORT(fo2, 'NS_LANG_CODE' )
                    A = fo2.uInt8()
                    B = fo2.uInt8()
                    nData = ( (B & ~0x80) << 7) | \
                        (A & ~0x80) 
                    if B & 0x80:
                        retval = GetNSISString(-nData-1)
                        #print "retval => %s" % retval
                        strData += retval
                    else:
                        fo2.seek(-2, os.SEEK_CUR) 
                        #strData += chr(A) + chr(B) 
                    #stop

                elif ns == NS_SKIP_CODE:
                    # 0xfc that's the german 'ü' 
                    #print "NS_SKIP_CODE"
                    char = fo2.read(1)
                    strData += MaskNewLine( char )



            char = fo2.read(1)
            if len(char) == 0:
                break

        #print '         %.128s' % strData
        if fo2NoSeekback==False:
            fo2.seek(fo2_oldPos)

        return strData 


def MakeUserVarName(num):
    UserVarName = "UserVar%i" % num
    
    #Track if declared
    if UserVarNames.has_key(num):
        pass
    else:
        fDecompOut("var /GLOBAL %s\n" % UserVarName)
        UserVarNames[num] = UserVarName
        
    return('$' + UserVarName)

def GetUserVarName(nData):
    
    if nData < 0:
        return GetNSISString(nData)
    
    staticUserVars = len(m_UserVarNames)
    #expanded = ''
    # -1 because first item in dict is 1: (and not 0:)
    if nData in range( 0, staticUserVars-1):
        return '$' + m_UserVarNames[ nData ]
    else:
        return MakeUserVarName(nData - staticUserVars)

    #print '%s' % expanded   
    #return expanded

#try:
        #with myFile( CSV_NameFile, 'rb') as fdata:


##########################################################################
##########################################################################
##########################################################################
def LoadCommonheader():
    global NB_STRINGS, NB_LANGTABLES, NB_STRINGS_Max
    global Tokenindex

    global fDecomp

    global DecompComment


    #common header
    ch_flag = fo.uInt32()
    CH_FLAGS_DETAILS_SHOWDETAILS  	=   0x1
    CH_FLAGS_DETAILS_NEVERSHOW  	=   0x2
    CH_FLAGS_PROGRESS_COLORED  	        =   0x4
    CH_FLAGS_SILENT  	                =   0x8
    CH_FLAGS_SILENT_LOG  	        =  0x10
    CH_FLAGS_AUTO_CLOSE  	        =  0x20
    CH_FLAGS_DIR_NO_SHOW  	        =  0x40
    CH_FLAGS_NO_ROOT_DIR  	        =  0x80
    CH_FLAGS_COMP_ONLY_ON_CUSTOM  	= 0x100
    CH_FLAGS_NO_CUSTOM  	        = 0x200

    ch_flag_text = BitOptions ( ch_flag, \
                                'CH_FLAGS_DETAILS_SHOWDETAILS\n' + \
                                'CH_FLAGS_DETAILS_NEVERSHOW\n' + \
                                'CH_FLAGS_PROGRESS_COLORED\n' + \
                                'CH_FLAGS_SILENT\n' + \
                                'CH_FLAGS_SILENT_LOG\n' + \
                                'CH_FLAGS_AUTO_CLOSE\n' + \
                                'CH_FLAGS_DIR_NO_SHOW\n' + \
                                'CH_FLAGS_NO_ROOT_DIR\n' + \
                                'CH_FLAGS_COMP_ONLY_ON_CUSTOM\n' + \
                                'CH_FLAGS_NO_CUSTOM\n' ,\
                                '\n'
                                )


    print 'CH_Flags:      0x%.4X\n%s' %  (ch_flag, ch_flag_text)

    NB_PAGES      = fo.uInt32(); NB_PAGES_Num       = fo.uInt32();
    NB_SECTIONS   = fo.uInt32(); Sections_Num    = fo.uInt32();
    NB_ENTRIES    = fo.uInt32(); NB_ENTRIES_Num     = fo.uInt32();
    NB_STRINGS    = fo.uInt32(); NB_STRINGS_Num     = fo.uInt32();
    NB_LANGTABLES = fo.uInt32(); NB_LANGTABLES_Num  = fo.uInt32();
    NB_CTLCOLORS  = fo.uInt32(); NB_CTLCOLORS_Num   = fo.uInt32();
    NB_BGFONT     = fo.uInt32(); NB_BGFONT_Num      = fo.uInt32();
    NB_DATA       = fo.uInt32(); NB_DATA_Num        = fo.uInt32();

    print '#%i NB_PAGES      %.8X: %.8X' %  (1, NB_PAGES, NB_PAGES_Num)
    print '#%i NB_SECTIONS   %.8X: %.8X' %  (2, NB_SECTIONS, Sections_Num)
    print '#%i NB_ENTRIES    %.8X: %.8X' %  (3, NB_ENTRIES, NB_ENTRIES_Num)
    print '#%i NB_STRINGS    %.8X: %.8X' %  (4, NB_STRINGS, NB_STRINGS_Num)
    print '#%i NB_LANGTABLES %.8X: %.8X' %  (5, NB_LANGTABLES, NB_LANGTABLES_Num)
    print '#%i NB_CTLCOLORS  %.8X: %.8X' %  (6, NB_CTLCOLORS, NB_CTLCOLORS_Num)
    print '#%i NB_BGFONT     %.8X: %.8X' %  (7, NB_BGFONT, NB_BGFONT_Num)
    print '#%i NB_DATA       %.8X: %.8X' %  (8, NB_DATA, NB_DATA_Num)

    NB_STRINGS_Max = NB_LANGTABLES - NB_STRINGS

    # CEXEBuild::init_shellconstantvalues() of Ver3 
    # will make look stringtable like this:
    #0x0000:  
    #0x0001:  ProgramFilesDir
    #0x0011:  CommonFilesDir
    #0x0020:  C:\Program Files ...
    #0x0031:  02  81 20 00
    #         ^^ - NS_SHELL_CODE !!  - that'll be an other way to detect
    # 1 for "ProgramFilesDir" if it uses that 0x80-quickmasking crap for NS_SHELL_CODE
    global isVerNS3
    isVerNS3 =  bool( S( 0x0011 ) == "CommonFilesDir")
    print 'isVerNS3: %s' % isVerNS3

    install_reg_rootkey   = fo.uInt32()
    install_reg_key_ptr   = fo.uInt32()
    install_reg_value_ptr = fo.uInt32()


    bg_color1     = fo.uInt32_rgb() 
    bg_color2     = fo.uInt32_rgb() 
    bg_textcolor  = fo.uInt32_rgb()

    lb_bg     = fo.uInt32_rgb()
    lb_fg     = fo.uInt32_rgb()


    ch = dict( \
        A9_langtable_size = fo.uInt32() , \
        A_license_bg      = fo.uInt32() \
    )
    # note python 2.8 supports OrderedDict()
    for k, v in sorted(ch.iteritems()):
        print '%s: %.6X' % (k, v)


    onXFunc = dict( \
        B_code_onInit     = fo.Int32() , \
        C_code_onInstSuccess     = fo.Int32() , \
        D_code_onInstFailed     = fo.Int32() , \
        E_code_onUserAbort     = fo.Int32() , \
        \
        F_code_onGUIInit     = fo.Int32() , \
        G_code_onGUIEnd     = fo.Int32() , \
        H_code_onMouseOverSection     = fo.Int32() , \

        I_code_onVerifyInstDir     = fo.Int32() , \
        J_code_onSelChange     = fo.Int32() , \
        K_code_onRebootFailed     = fo.Int32() \
    )

    for k, v in sorted( onXFunc.iteritems() ):
        k = k.partition('code_')[2]
        #print '%s:\t0x%.4X' % (k, v)

        # add on event function to list
        if v > 0:
            ns_func(k, '.', v + TOKENBASE, False)



    InstTypes = DumpInstTypes(CH_FLAGS_NO_CUSTOM, ch_flag, CH_FLAGS_COMP_ONLY_ON_CUSTOM)

    install_directory_ptr             = fo.uInt32()
    install_directory_auto_append     = fo.uInt32()


    ch = dict( \
        M_install_directory_ptr     = install_directory_ptr , \
        N_install_directory_auto_append     = install_directory_auto_append , \
        \
        O_str_uninstchild     = fo.Int32() , \
        P_str_uninstcmd     = fo.Int32() , \
        Q_str_wininit     = fo.Int32() , \
        Z_OffSetEnd     = fo.tell() \
    )
    for k, v in sorted(ch.iteritems()):
        str = ''
        try:
            str = S(v)
        except: pass
        print '%s:\t0x%.4X - %.60s' % (k, v, str)


#"none\0user\0highest\0admin\0"

    if S(install_directory_auto_append):
        DecompLine = 'Name %s' % S(install_directory_auto_append) 
        print DecompLine
        fDecompOut( DecompLine + '\n')

        DecompLine = 'OutFile %s ; NsiDecompiler: generated value!' % S(install_directory_auto_append, '', '.exe') 
        print DecompLine
        fDecompOut( DecompLine + '\n')
    
    EMPTYCOLOR = 0xFFFFFF
    if not(bg_color1 == bg_color2 == bg_textcolor == EMPTYCOLOR):
        BGGradient =  'BGGradient %.6X %.6X %.6X\n' % (bg_color1, bg_color2, bg_textcolor)
        print BGGradient
        fDecompOut( BGGradient)

    if not(lb_fg == lb_bg == EMPTYCOLOR):    
        InstallColors =  'InstallColors %.6X %.6X\n' % (lb_fg, lb_bg)
        print InstallColors
        fDecompOut( InstallColors)

    if install_directory_ptr:
        DecompLine = 'InstallDir %s' % S(install_directory_ptr) 
        print DecompLine
        fDecompOut( DecompLine + '\n')
        
    if S(install_reg_key_ptr):
        DecompLine = 'InstallDirRegKey %s %s %s' % ( \
            E(install_reg_rootkey & 0xf, REG_HKEYS),
            S(install_reg_key_ptr), \
            S(install_reg_value_ptr)  \
        )
        print DecompLine
        fDecompOut( DecompLine + '\n')


    # Just some static lines to Quickfix certain compiling issues like AddBrandingImage
    fDecompOut( HeaderAddlines + '\n' )
               
    dumpPages( NB_PAGES, NB_PAGES_Num, NB_SECTIONS)

    # dump Install Types
    for item in InstTypes:

        line = 'InstType %s' % item
        print line
        line +='\n'
        fDecompOut (line)




    dumpSections( NB_SECTIONS, Sections_Num, NB_ENTRIES)


    global DoDecompile    
    if DoDecompile:
        ProcessEntries( NB_ENTRIES, NB_ENTRIES_Num)

    global DumpStrings    
    if DumpStrings:
        dumpLangTables( NB_LANGTABLES, NB_LANGTABLES_Num, NB_CTLCOLORS)
        dumpStrings( NB_STRINGS, NB_LANGTABLES)


def DumpInstTypes(CH_FLAGS_NO_CUSTOM, ch_flag, CH_FLAGS_COMP_ONLY_ON_CUSTOM):
    NSIS_MAX_INST_TYPES = 0x20
    InstType = []
    # InstType from 1..31
    for i in range(NSIS_MAX_INST_TYPES):
        item = fo.Int32()
        if item != 0:
            str = ''
            try:
                str = S(item)
                InstType.append (str)

                print '#%i:   InstType %s %X' % (i, str, item )

            except: pass

    # Custom (32) 
    item = fo.Int32()
    try:
        str = S(item)
    except: pass 

    if str != 'Custom':
        InstType.append ('/CUSTOMSTRING=%s' % str)

    if ch_flag & CH_FLAGS_NO_CUSTOM:
        InstType.append ('/NOCUSTOM')

    if ch_flag & CH_FLAGS_COMP_ONLY_ON_CUSTOM:
        InstType.append ('/COMPONENTSONLYONCUSTOM')

    return InstType    

    #if NB_BGFONT:   
    #    dumpBGFONT( NB_BGFONT )

def dumpPages( NB_PAGES, NB_PAGES_Num, MaxOffset):

    print "\n\n\n == Dumping  P a g e s  ==\n\n\n"    
    NSIS_MAX_STRLEN = 0x400 

    fo.seek(NB_PAGES)
    #TextFile = open ("NB_PAGES.txt" , "wt")
    for page in range(NB_PAGES_Num):

        print "== Page %i ==" % page


        dlg_id     = fo.uInt32()

        print 'dlg_id: 0x%.4X' % (dlg_id)


        wndproc_id = fo.uInt32()
        p_id = "%i" % wndproc_id
        
        if wndproc_id > 4:
            PageName = "custom"
        else:
            PageName = E(wndproc_id + 1, "custom license components directory instfiles uninstConfirm")
            
        print 'wndproc_id: 0x%.4X -> %s' % ( wndproc_id, PageName)
        
        prefunc   = fo.Int32();  prefuncText = ns_func( ("pre_page"+ p_id) if dlg_id else "create_page"+ p_id,'' , prefunc)
        print 'prefunc: 0x%.4X %s' % ( prefunc, prefuncText)
        
        showfunc  = fo.Int32();  
        showfuncText = ns_func( "show_page"+ p_id,'' , showfunc)
            
        print 'showfunc: 0x%.4X %s' % ( showfunc, showfuncText)
        
        leavefunc = fo.Int32();  leavefuncText = ns_func( "leave_page"+ p_id,'' , leavefunc)
        print 'leavefunc: 0x%.4X %s' % ( leavefunc, leavefuncText)

        print 'flags: 0x%.4X' % ( fo.uInt32())

        caption = fo.Int32()
        captiontext = S(caption)
        print 'caption: 0x%.4X - %s' % ( caption, captiontext)
        print 'back: 0x%.4X - %s' % ( fo.Int32(), '')
        print 'next: 0x%.4X - %s' % ( fo.Int32(), '')
        print 'clicknext: 0x%.4X - %s' % ( fo.Int32(), '')
        print 'cancel: 0x%.4X - %s' % ( fo.Int32(), '')
        print 'parms0: 0x%.4X - %s' % ( fo.Int32(), '')
        print 'parms1: 0x%.4X - %s' % ( fo.Int32(), '')
        print 'parms2: 0x%.4X - %s' % ( fo.Int32(), '')
        print 'parms3: 0x%.4X - %s' % ( fo.Int32(), '')
        print 'parms4: 0x%.4X - %s\n' % ( fo.Int32(), '')

        isHidden = dlg_id < 0
        
        isNotLastPage = True # (page < NB_PAGES_Num-1)
        if isNotLastPage and not isHidden:
            fDecompOut("Page %s %s %s %s\n" % (PageName, \
                                               prefuncText, \
                                               \
                              '' if PageName == "custom" else \
                                               showfuncText, \
                                               \
                                               leavefuncText, \
                                               ))
                                               #\
                                               #'' if captiontext in ('" "', "' '") else \
                                               #captiontext,\
 
    #TextFile.close()

def dumpSections( NB_SECTIONS, Sections_Num, MaxOffset):

    print "\n\n\n == Dumping  S e c t i o n s ==\n\n\n"

    NSIS_MAX_STRLEN = 0x400 # 0x418 section size
#    TextFile = open ("NB_SECTIONS.txt" , "wt")

    fo.seek(NB_SECTIONS)

    for i in range(Sections_Num):
        name_ptr      = fo.uInt32() # initial name pointer
        install_types = fo.uInt32()  # bits set for each of the different install_types, if any.

        flags          = fo.uInt32()
        flags_text = BitOptions(flags, \
                                'SF_SELECTED' \
                                'SF_SECGRP' \
                                'SF_SECGRPEND' \
                                'SF_BOLD' \
                                'SF_RO' \
                                'SF_EXPAND' \
                                'SF_PSELECTED' \
                                'SF_TOGGLED' \
                                'SF_NAMECHG' \
                                ,'\n')

        SF_SELECTED =     1 # v
        SF_SECGRP   =     2 # v
        SF_SECGRPEND=     4 # v
        SF_BOLD     =     8 # v
        SF_RO       =  0x10 # v
        SF_EXPAND   =  0x20 # v
        SF_PSELECTED=  0x40 #
        SF_TOGGLED  =  0x80 #
        SF_NAMECHG  = 0x100 #
        # for labels, it looks like it's only used to track how often it is used.

        code         = fo.uInt32()  # The "address" of the start of the code in count of struct entries.
        code_size    = fo.uInt32()  # The size of the code in num of entries?

        codeEnd = code + code_size

        size_kb      = fo.uInt32()
        invisible_sections         = fo.read(NSIS_MAX_STRLEN)

        name          = S(name_ptr, '!' if flags & SF_BOLD else '')
        print '#%i' % i 
        print '  name_ptr: 0x%.4X - %s' % (name_ptr, name)
        print '  install_types: 0x%.4X' % install_types
        print '  flags: 0x%.4X\n%s' % (flags, flags_text)
        print '  code: 0x%.4X size: 0x%.4X => end: 0x%.4X' % (code, code_size, codeEnd)
        print '  size_kb: %i' % size_kb
        #print 'invisible_sections: %s' % invisible_sections
        print '---------------------------\n'

        SF_Group = 'Group' if (flags & (SF_SECGRP | SF_SECGRPEND)) else ''

        SF_Options = ''
        if (flags & SF_EXPAND) :
            SF_Options += '/e '

        if not(flags & SF_SELECTED) :
            SF_Options += '/o '

        Section = 'Section' + SF_Group + ' ' + SF_Options + name

        SectionIn = '\nSectionIn ' + BitOptions( install_types, [ '%i' % num  for num in range(1,32) ] ) + \
            (' RO' if flags & SF_RO else '')

        if not(flags & SF_SECGRPEND):
            cls_Decomp.Sections_start [ code  ]    =  Section
            if install_types and (name != ''):
                cls_Decomp.SectionsIN [ code  ]   = SectionIn
        # +1 is stupid fix for 'return' outside section
            cls_Decomp.Sections_end [ codeEnd +1  ]   = 'Section' + SF_Group + 'End' # name
        #print cls_Decomp.Sections_start

        # That is just to find the Section by idx
        cls_Decomp.Sections_idx_To_Offset[i] = code


    #        for LangTableEntryIdx in range(fo.tell(), MaxOffset, 4):

def dumpStrings( NB_STRINGS, MaxOffset):

    print "\n\n\n == Dumping  S t r i n g s ==\n\n\n"


    TextFile = open ("NB_STRINGS.txt" , "wt")
    fo2.seek(NB_STRINGS)
    while fo2.tell() < MaxOffset:

        EntryOffset = int(fo2.tell())-NB_STRINGS

        data = GetNSISString( EntryOffset, True )
        print '#0x%.4X:  %s' % (EntryOffset, data)

        TextFile.write (data + '\n')

    TextFile.close()

def dumpLangTables( NB_LANGTABLES, NB_LANGTABLES_Num, MaxOffset):

    print "\n\n\n == Dumping  NB_LANGTABLES ==\n\n\n"    
    TextFile = open ("NB_LANGTABLES.txt" , "wt")

    fo.seek(NB_LANGTABLES)

    for LangTable in range(NB_LANGTABLES_Num):
        langID = fo.uInt16()
        print 'Language ID: 0x%.4X' % langID
        FontName = fo.uInt16()
        Fontsize = fo.uInt16()
        Codepage = fo.uInt16()
        RTL = fo.uInt16()

        print 'FontName: 0x%.4X' % FontName
        print 'Fontsize: 0x%.4X' % Fontsize
        print 'Codepage: 0x%.4X' % Codepage
        print 'RTL: 0x%.4X' % RTL

        for LangTableEntryIdx in range(fo.tell(), MaxOffset, 4):

            LangTableEntry = fo.uInt32()

            data = S(LangTableEntry)
            print '#0x%.4X:  0x%.4X - %s' % (LangTableEntryIdx, LangTableEntry, data)

            TextFile.write (data + '\n')

        TextFile.close()
def dumpBGFONT( NB_BGFONT):

    print "\n\n\n == Dumping  BGFONT ==\n\n\n"    

    fo.seek(NB_BGFONT)
    LF_FACESIZE = 32
    #EntrySize = fo.uInt32()
    lfHeight = fo.uInt32()
    lfWidth = fo.uInt32()
    lfEscapement = fo.uInt32()
    lfOrientation = fo.uInt32()
    lfWeight = fo.uInt32()

    #/ITALIC /UNDERLINE /STRIKE
    (lfItalic,       lfUnderline,     lfStrikeOut, lfCharSet, \
     lfOutPrecision, lfClipPrecision, lfQuality,   lfPitchAndFamily) = \
        ( fo.uInt8(), fo.uInt8(), fo.uInt8(), fo.uInt8(),\
          fo.uInt8(), fo.uInt8(), fo.uInt8(), fo.uInt8())
    lfFaceName = fo.readline(LF_FACESIZE)

    #print 'EntrySize: 0x%.4X' % EntrySize    
    print 'lfHeight: %i' % lfHeight
    print 'lfWidth: 0x%.4X' % lfWidth
    print 'lfEscapement: 0x%.4X' % lfEscapement
    print 'lfOrientation: 0x%.4X' % lfOrientation
    print 'lfWeight: %i -> %s' % (lfWeight, \
                                  'FW_NORMAL' if lfWeight == 400 else \
                                  'FW_BOLD' if lfWeight == 700 else '')
    print 'lfItalic: %i, lfUnderline, lfStrikeOut, lfCharSet, ' + \
          'lfOutPrecision, lfClipPrecision, lfQuality, lfPitchAndFamily ... AS BYTES'

    print 'lfFaceName: %s' % lfFaceName

    print 'FilePointer: 0x%X -  %s' % ( fo.tell(), fo.name )


def fDecompOut(Text):
    if DoDecompile:
        fDecomp.write(Text)
        #os.sys.stderr.write(Text)

def ProcessEntries( NB_ENTRIES, NB_ENTRIES_Num):
    global NSIS_COMMENT
    instident = '       '
    print "\n\n\n == Dumping  E n t r i e s ==\n\n\n"   

    global TOKENBASE
    fo.seek(NB_ENTRIES)

    e = EW_Tokens()


    global isInsideSection



    for i in range(TOKENBASE, NB_ENTRIES_Num + TOKENBASE):

        global Tokenindex
        Tokenindex = i

        Decomp = ''
        DecompComment = ''
        skipCommand = False       

        which = fo.uInt32()
        parm0 = fo.Int32()
        parm1 = fo.Int32()
        parm2 = fo.Int32()
        parm3 = fo.Int32()
        parm4 = fo.Int32()
        parm5 = fo.Int32()

        which_Name = e.Names(which)

        #case 

#        E_Type in range(1,0x41)
        def R( Num ):
            return '%4X' % Num if Num else \
                   '%4s' % '-' 
        
        lineRawInfo  = '#%4.3X %.2X_%16s' % (i, which,which_Name)
        if parm0|parm1|parm2:
            lineRawInfo += '  : p0: %s %s %s' % ( R(parm0), R(parm1), R(parm2) )

        if parm3|parm4|parm5:
            lineRawInfo +=   '  p3: %s %s %s' % ( R(parm3), R(parm4), R(parm5) )

        print '       ' + lineRawInfo

        while switch(which):
            if case(e.EW_WRITEINI):
                if parm4 == 1:
                    Decomp = 'WriteINIStr %s %s %s %s' % ( \
                        S( parm3 ), \
                        S( parm0 ), \
                        S( parm1 ), \
                        Sq( parm2 ))
                elif (parm2 == 0) and (parm1 != 0):
                    Decomp = 'DeleteINIStr  %s %s %s' % ( \
                        S( parm3 ), \
                        S( parm0 ), \
                        S( parm1 ) )
                elif (parm1 == 0) and (parm0 != 0):
                    Decomp = 'DeleteINISec  %s %s' % ( \
                        S( parm3 ), \
                        S( parm0 ))
                else: 
                    Decomp = 'FlushINI %s ' % S( parm3 )

                break

            if case(e.EW_ASSIGNVAR):

                isGetCurrentAddress = False
                try:
                    isGetCurrentAddress =  S_Int(parm1) == Tokenindex 
                except: pass
                
                if isGetCurrentAddress:
                    Decomp = 'GetCurrentAddress %s' %  V( parm0 )

                else:    
                    Decomp = 'StrCpy %s %s %s %s' % ( \
                        V( parm0 ), \
                        Sq(parm1 ), \
                        S( parm2 ), \
                        S( parm3 ))
                    if V( parm0 ) == '$PLUGINSDIR':
                        DecompComment += '<-that\'ll give a compile error! Anyway delete whole function and replace calls with a simple "InitPluginsDir" '

                break

            if case(e.EW_READREGSTR):

                if   parm4 == 0:     CmdName = 'Str'
                elif parm4 == 1:     CmdName = 'DWORD'
                else: CmdName = 'ERRoR!!!'

            #"HKCR HKLM HKCU HKU HKCC HKDD HKPD SHCTX" <- original order
            #"HKCR HKCU HKLM HKU HKPD HKCC HKDD SHCTX" <- Reordered so it's 0x80000000..6
                Decomp = 'ReadReg%s %s %s %s %s' % ( \
                    CmdName, \
                    V( parm0 ), \
                    E( parm1 & 0xf ,"HKCR HKCU HKLM HKU HKPD HKCC HKDD SHCTX"), \
                    S( parm2 ), \
                    S( parm3 ))
                break

            if case(e.EW_WRITEREG):
                REG_SZ          = 1
                REG_EXPAND_SZ   = 2
                REG_BINARY      = 3
                REG_DWORD       = 4

                data = S( parm3 )
                if   parm5 == REG_SZ:        CmdName = 'Str'
                elif parm5 == REG_EXPAND_SZ: CmdName = 'ExpandStr'
                elif parm5 == REG_BINARY:    CmdName = 'Bin';data = B( parm3 )
                elif parm5 == REG_DWORD:     CmdName = 'DWORD'

            #"HKCR HKLM HKCU HKU HKCC HKDD HKPD SHCTX" <- original order
            #"HKCR HKCU HKLM HKU HKPD HKCC HKDD SHCTX" <- Reordered so it's 0x80000000..6
                Decomp = 'WriteReg%s %s %s %s %s' % ( \
                    CmdName,
                    E( parm0 & 0xf ,REG_HKEYS), \
                    Sq( parm1 ), \
                    Sq( parm2 ), \
                    data )
                break

            if case(e.EW_DELREG):
                
                if   parm3 == 0:        CmdName = 'Key' #and param4 in (1,3)
                else:                   CmdName = 'Value'
            # REG_HKEYS   
            #"HKCR HKLM HKCU HKU HKCC HKDD HKPD SHCTX" <- original order
            #"HKCR HKCU HKLM HKU HKPD HKCC HKDD SHCTX" <- Reordered so it's 0x80000000..6
                Decomp = 'DeleteReg%s %s %s %s %s' % ( \
                    CmdName,
                    E( parm1 & 0xf ,REG_HKEYS), \
                    Sq( parm2 ), \
                    S( parm3 ), \
                    "/ifempty" if parm4==3 else "" )
                break

            if case(e.EW_READINISTR):
                Decomp = 'ReadINIStr %s %s %s %s' % ( \
                    V( parm0 ) , \
                    S( parm3 ), \
                    S( parm1 ), \
                    S( parm2 ))
                break

            if case(e.EW_FOPEN):
                #parm1
                #define GENERIC_READ  0x8000 0000
                #define GENERIC_WRITE 0x4000 0000
                #parm1>>29
                
                #parm2
                #  CREATE_NEW    1
                #  CREATE_ALWAYS 2 w
                #  OPEN_EXISTING 3 r
                #  OPEN_ALWAYS   4 a
                openmode = E( parm2 -2, 'r w a')
                
                Decomp = 'FileOpen %s %s %s' % ( \
                    V( parm0 ) , \
                    S( parm3 ), \
                    openmode, \
                    )
                break
            if case(e.EW_FCLOSE):
                
                Decomp = 'FileClose %s' % V( parm0 )
                break
            
            if case(e.EW_FGETS):
                if param3 == 1:
                    cmdext = "Byte"
                    FR_size = ''
                else:
                    cmdext = ''
                    FR_size = S( parm2 )
                    
                Decomp = 'FileRead%s %s %s %s' % ( cmdext, \
                    V( parm0 ) , \
                    V( parm1 ), \
                    FR_size)
                break  
            
            if case(e.EW_FPUTS):
                cmdext = "Byte" if param2 == 1 else ''
                Decomp = 'FileWrite%s %s %s %s' % ( cmdext, \
                    V( parm0 ) , \
                    S( parm1 ))
                break

            if case(e.EW_FGETWS):
                if param3 == 1:
                    cmdext = "Word"
                    FR_size = ''
                else:
                    cmdext = 'UTF16LE'
                    FR_size = S( parm2 )
                    
                Decomp = 'FileRead%s %s %s %s' % ( cmdext, \
                    V( parm0 ) , \
                    V( parm1 ), \
                    FR_size)
                break  
            
            if case(e.EW_FPUTWS):
                cmdext = "Word" if param2 == 1 else 'UTF16LE'
                Decomp = 'FileWrite%s %s %s' % ( cmdext, \
                    V( parm0 ) , \
                    S( parm1 ))
                break

            
            if case(e.EW_FSEEK):
                    
                Decomp = 'FileSeek %s %s %s %s' % (\
                    V( parm0 ), \
                    S( parm2 ), \
                    E( parm3 ,' CUR END'), \
                    V( parm1 ), \
                    )
                #Note SET is default
                break  
            
            
            if case(e.EW_FINDFIRST):
                Decomp = 'FindFirst %s %s %s' % ( \
                    V( parm1 ) , \
                    V( parm0 ), \
                    S( parm2 ))
                break
            
            if case(e.EW_FINDNEXT):
                Decomp = 'FindNext %s %s' % ( \
                    V( parm1 ) , \
                    V( parm0 ))
                break  
            
            if case(e.EW_FINDCLOSE):
                Decomp = 'FindClose %s' % ( \
                    V( parm0 ))
                break            
            
            if case(e.EW_WRITEUNINSTALLER):
                global CommentOutWriteUninstaller
                
                Decomp = (NSIS_COMMENT if CommentOutWriteUninstaller else '') + \
                            'WriteUninstaller %s' % S( parm0 )

                DecompComment = 'Offset: %x  Iconstyle: %x  More: %s' % ( \
                    parm1 , \
                    parm2, \
                    S( parm3 ))
                break

            if case(e.EW_CREATESHORTCUT):

                # parm4 bitlayout
                #    0  IconIndex
                #    8  ShowState
                #   16  HotKey
                #   24  FKey
                import ctypes 
                c_uint8 = ctypes.c_uint8

                class EW_CREATESHORTCUT_Flags_bits( ctypes.LittleEndianStructure ):
                    _fields_ = [
                        ("IconIndex", c_uint8, 8 ),  # 0
                        ("ShowState", c_uint8, 3 ),  # 8
                        ("Filler1", c_uint8, 5 ),  
                        ("HotKey_key", c_uint8, 8 ),  # 16
                        ("HotKey_mod", c_uint8, 8 ),  # 24
                    ]

                class EW_CREATESHORTCUT_Flags( ctypes.Union ):
                    _fields_ = [
                        ("b",      EW_CREATESHORTCUT_Flags_bits ),
                        ("asByte", c_uint8    ),
                        ("asInt32", ctypes.c_uint32   )
                    ]
                    _anonymous_ = ("b")


                HOTKEYF_SHIFT      = 1
                HOTKEYF_CONTROL    = 2
                HOTKEYF_ALT        = 4
                HOTKEYF_EXT        = 8
                VK_F1          = 0x70


                parm4_opt           =   EW_CREATESHORTCUT_Flags()
                parm4_opt.asInt32   =   parm4

                hotkeys_int = parm4_opt.HotKey_mod #parm4 >> 24
                hotkeys =  ''
                if (hotkeys_int & HOTKEYF_ALT):      hotkeys += 'ALT|'
                if (hotkeys_int & HOTKEYF_CONTROL):  hotkeys += 'CONTROL|'
                if (hotkeys_int & HOTKEYF_SHIFT):    hotkeys += 'SHIFT|'
                if (hotkeys_int & HOTKEYF_EXT):      hotkeys += 'EXT|'

                FKey = parm4_opt.HotKey_key #(parm4 >> 16 ) & 0xff
                if FKey >= VK_F1:
                    FKey -= VK_F1 - 1

                    FKey = 'F' + str(FKey)
                else:
                    if FKey in range(0x20, 0x7f): 
                        FKey = chr(FKey)
                        
                if FKey==0: FKey=''

                    #icon_index_number = parm4 & 0xff  
                CommandlineParameters = Sq( parm2 )
                icon_file = Sq( parm3 )
                description = S( parm5 )
                Decomp = 'CreateShortCut %s %s %s %s %s %s %s%s %s' % ( \
                    Sq( parm0 ), \
                    Sq( parm1 ), \
                    CommandlineParameters , \
                    icon_file , \
                    I( parm4_opt.IconIndex ), \
                    E(parm4_opt.ShowState , ' SW_SHOWNORMAL  SW_SHOWMAXIMIZED    SW_SHOWMINIMIZED' ), \
                    hotkeys ,  \
                    FKey , \
                    description)
                    # ent.offsets[4]=1; // write
                break

            if case(e.EW_CREATEDIR):
                op = S( parm0 )
                if parm1==1:

                    #if op=="$INSTDIR":
                    #   op='"-"'

                    Decomp = 'SetOutPath %s ' % op
                    
                    FileExtract.CurDir = op
                else:
                    Decomp = 'CreateDirectory %s ' % op

                break
            
            if case(e.EW_INVALID_OPCODE):
                 DecompComment = 'INVALID_OPCODE:%x @ 0x%X' % (e.EW_INVALID_OPCODE, Tokenindex)
 
                 break
             
            if case(e.EW_UPDATETEXT):
                Decomp = 'DetailPrint %s ' % Sq( parm0 )

                break

            if case(e.EW_CREATEDIR):
                Decomp = 'CreateDirectory %s' % S( parm0 )
                break 

            if case(e.EW_STRLEN):
                Decomp = 'StrLen %s %s ' % ( \
                    V( parm0 ), \
                    S( parm1 ))
                break

            if case(e.EW_INTOP):
                op1 = S( parm1 )               
                op2 = S( parm2 )
                op  = E( parm3, '+ - * / | & ^ ! || && % << >> ~ ' )

                if  (op =='^') and (op2 == '0xFFFFFFFF'):
                    op  = '~'
                    op2 = ''

                Decomp = 'IntOp %s %s %s %s' % ( \
                    V( parm0 ), \
                    op1, \
                    op, \
                    op2 )
                break

            if case(e.EW_INTCMP):
                #"a" "b" is less more
                # catch undocumented Label use parm2 <, parm3 = , parm4 >
                #assert parm3==0
                
                Decomp = 'IntCmp' + \
                    ('U' if parm5 else '') + \
                    ' %s %s %s %s' % ( \
                        Sq( parm0 ), \
                        Sq( parm1 ), \
                        J ( parm2 ), \
                        JJ( parm3, parm4 ) )
                break

            if case(e.EW_STRCMP):
                
                # catch undocumented Label use parm2 <, parm3 = , parm4 >
                #assert parm4==0
                
                Decomp = 'StrCmp%s %s %s %s %s' % ( \
                    'S' if parm5==1 else '' , \
                    Sq( parm0 ), \
                    Sq( parm1 ), \
                    JJ ( parm2, parm3), \
                    J  ( parm4 ) )
                break

            if case(e.EW_RET):

                DecompComment = "Return"

                if supressCodeOutsideSections:
                    skipCommand = True

                #if cls_Decomp.isInsideFunction:
                    #cls_Decomp.Functions[i] = ";FunctionEnd\n"
                    #cls_Decomp.isInsideFunction = False
                break

            if case(e.EW_SLEEP):
                Decomp = "Sleep %s" % S(parm0)
                break

            if case(e.EW_LOCKWINDOW):
                Decomp = "LockWindow %s" % E(parm0, "on off")
                break

            if case(e.EW_BRINGTOFRONT):
                Decomp = "BringToFront"
                break

            if case(e.EW_QUIT):
                Decomp = "Quit"
                break

            if case(e.EW_ABORT):
                Decomp = 'Abort %s' % S( parm0 )
                break

            if case(e.EW_REBOOT):
                Decomp = "Reboot"
                if parm0 != 0xbadf00d:
                    DecompComment = "Installation corrupted"
                break

            if case(e.EW_SEARCHPATH):
                Decomp = 'SearchPath %s %s' % ( V( parm0 ), S( parm1 ) )
                break

            if case(e.EW_NOP):
                if parm0 == 0:
                    Decomp = "Nop"
                else:
                    Decomp = "Goto %s" % L ( parm0 )

                break


            if case(e.EW_PUSHPOP):
                if parm1==0:

                    if parm2==0:
                        Decomp = "Push %s" % S( parm0 )
                    else:
                        Decomp = "Exch %s" % I( parm2 )
                        DecompComment = "TODO: Check Push/POP around this. Maybe remove them!"
                else:
                    Decomp = "Pop %s"    % V( parm0 )
                break

            if case(e.EW_SETCTLCOLORS):
                Decomp = 'SetCtlColors %s %s %s' % ( \
                    S( parm0 ), \
                    Sq( parm1 ), \
                    S( parm2 ) )
                DecompComment = "Warning: SetCtlColors is not completely implemented"

                break

            if case(e.EW_SETBRANDINGIMAGE):
                #IDD_INST                        105
                #CONTROL "", 1046, "STATIC", SS_BITMAP, 0, 0, 100, 35
                #IDC_BRANDIMAGE
                #NeedsAddBrandingImage = True
                Decomp = 'SetBrandingImage /IMGID=%i %s %s' % ( parm1, \
                                                                "/RESIZETOFIT" if parm2 else "", \
                                                                GetNSISString( parm0) )
                DecompComment = 'you may need to "AddBrandingImage left 100" or sth at the beginning - exact data for the is in .rsrc\DLG_105:1033[SS_BITMAP]; brandingCtl.sHeight = wh brandingCtl.sX = padding; (left|right|top|bottom)'
                break

            if case(e.EW_GETFUNCTIONADDR):
                Decomp = "GetFunctionAddress %s %s" % \
                    (V( parm0 ),  F( parm1 ))
                break

            if case(e.EW_CALL):
                if parm1 == 1:
                    #isLabel
                    Decomp = "Call :%s" % L(parm0)

                else:
                    Decomp = "Call %s" % F(parm0)

                break

            if case(e.EW_GETTEMPFILENAME):
                base_dir = S( parm1 )

                Decomp = "GetTempFileName %s %s" % ( \
                    V( parm0 ), \
                    base_dir if (base_dir.upper() != '$TEMP') else ''\
                )
                break

            if case(e.EW_GETDLLVERSION):
                Decomp = "GetDLLVersion %s %s %s" % ( \
                    S( parm2 ), \
                    V( parm0 ), \
                    V( parm1 ))
                break

            if case(e.EW_GETDLGITEM):
                Decomp = "GetDlgItem %s %s %s" % ( \
                    V( parm0 ), \
                    S( parm1 ), \
                    S( parm2 ))
                break

            if case(e.EW_IFFILEEXISTS):
                Decomp = "IfFileExists  %s %s" % ( \
                    S( parm0 ), \
                    JJ( parm1, parm2 ))
                break

            if case(e.EW_IFFLAG):

                if parm2 == exec_flags_exec_error:
                    Decomp = "IfErrors"
                    #if param3 == 0:

                elif parm2 == exec_flags_abort:
                    Decomp = "IfAbort"
                    #if param3 != 0:

                elif parm2 == exec_flags_exec_reboot:
                    Decomp = "IfRebootFlag"
                    #if param3 != 0:

                elif parm2 == exec_flags_silent:
                    Decomp = "IfSilent"
                    #if param3 != 0:

                Decomp = Decomp + " %s" % LL(parm0, parm1)

                break

            if case(e.EW_SETFLAG):
                
                parm1 = S_Int( parm1)
                
                if parm0 == exec_flags_exec_error:
                    if (parm1 == 0):
                        Decomp = "ClearErrors"
                    else:
                        Decomp = "SetErrors"
                        DecompComment += str(parm1)

                elif parm0 == exec_flags_errlvl:
                    Decomp = "SetErrorLevel %i" %  parm1 

                elif parm0 == exec_flags_exec_reboot:
                    Decomp = "SetRebootFlag %s"      % E( parm1, 'false true ' )

                elif parm0 == exec_flags_silent:
                    Decomp = "SetSilent %s"          % E( parm1, 'normal silent ' )

                elif parm0 == exec_flags_all_user_var:
                    Decomp = "SetShellVarContext %s" % E( parm1, 'current all ' )

                elif parm0 == exec_flags_autoclose:
                    Decomp = "SetAutoClose %s"       % E( parm1, 'false true ' )


                elif parm0 == exec_flags_alter_reg_view:
                    #TODO: Test this!
                    KEY_WOW64_64KEY = 0x100
                    if parm2 == 1:
                        detaillevel = "lastused"
                        
                    elif parm1 == KEY_WOW64_64KEY:
                        detaillevel = "64"
                    else :
                        detaillevel = str( parm1 )
                        
                    Decomp = "SetRegView %s" % detaillevel
                
                elif parm0 == exec_flags_status_update:
                    if parm2==1:
                        detaillevel = "lastused"
                        #if lastcmd == e.EW_CALL and param1==0
                        DecompComment +='maybe call func_x above is >InitPluginsDir<'
                    else:
                        detaillevel = E( parm1>>1, "both textonly listonly none")
                    Decomp = "SetDetailsPrint %s" % detaillevel
                    
                    
                else:
                    Decomp = "SetAutoClose,RebootFlag..."

                break

            if case(e.EW_IFFLAG):

                if parm2 == exec_flags_exec_error:
                    Decomp = "IfErrors"
                    #if param3 == 0:

                elif parm2 == exec_flags_abort:
                    Decomp = "IfAbort"
                    #if param3 != 0:

                elif parm2 == exec_flags_exec_reboot:
                    Decomp = "IfRebootFlag"
                    #if param3 != 0:

                elif parm2 == exec_flags_silent:
                    Decomp = "IfSilent"
                    #if param3 != 0:

                Decomp = Decomp + " %s %s" %  LL (parm0, parm1) 

                break



            if case(e.EW_CREATEFONT):
                
                Decomp = 'CreateFont %s %s %s %s %s' % ( \
                    V(parm0), \
                    Sq( parm1 ), \
                    S( parm2) , S( parm3) , \
                    BitOptions(parm4,' /ITALIC /UNDERLINE /STRIKE') \
                )
                break

            if case(e.EW_SENDMESSAGE):
                
                #TODO: Pack WM_MSGs inside some init
                WM_MSGs={}
                import win32con
                for (k,v) in win32con.__dict__.items():
                    if k.startswith("WM_"):
                        WM_MSGs[v] = k
                
                HWND   = S( parm1)
                msg    = S( parm2)
                msgAsText    = WM_MSGs.get( eval(msg) )

                paramflag = parm5 & 3
                if paramflag == 1:
                    wparam = S( parm3 , 'STR:')
                else:
                    wparam = S( parm3)

                if paramflag == 2:
                    lparam = S( parm4 , 'STR:')
                else:
                    lparam = S( parm4)

                TimeOut= I( parm5 >> 2, "/TIMEOUT=", True) 

                user_var = '' if parm0 <0 else \
                           V( parm0 )

                Decomp = 'SendMessage %s %s/*$(%s)*/ %s %s %s %s' % ( \
                    HWND, \
                    msg, msgAsText, \
                    wparam , \
                    lparam , \
                    user_var , \
                    TimeOut)
                
                break

            if case(e.EW_MESSAGEBOX):
                
                MB_IDs = ' IDOK IDCANCEL IDABORT IDRETRY IDIGNORE IDYES IDNO'
                #MB_IDsBitWidth = 3 # from 0..7 that be b000 to b111 -> 3bit's
                MB_IDsBitMask = 7
                
                BitsPerHexDigit = 4
                installerIsSilentBitPos = (5 * BitsPerHexDigit) + 1
                installerIsSilent = parm0 >> installerIsSilentBitPos
                SD_option = "/SD %s" % E (installerIsSilent , MB_IDs) \
                            if installerIsSilent else ""
                parm0 &= ~(MB_IDsBitMask << installerIsSilentBitPos)
                
                MB = MB_Style(parm0)
                


                MB_Text = Sq( parm1 )
                Decomp = 'MessageBox  %s %s %s %s %s %s %s' % ( \
                    MB, \
                    MB_Text, \
                    SD_option, \
                    E (parm2 , MB_IDs), J( parm3), \
                    E (parm4 , MB_IDs), J( parm5), \
                    )
                
                if MB_Text == "Error! Can't initialize plug-ins directory. Please try again later.":
                    DecompComment += 'Name of this function is "Initialize_____Plugins" - Plz delete it and replace all Calls (+SetDetailsPrint lastused) with "InitPluginsDir"'

                
                #uninstall_mode?
                #   Initialize_____Plugins
                #un.Initialize_____Plugins

                break


            if case(e.EW_FINDWINDOW):
                Decomp = 'FindWindow %s %s %s %s %s' % ( \
                    V(parm0), \
                    Sq( parm1 ), \
                    Sq( parm2) , \
                    Sq( parm3) , S( parm4 ))
                break

            if case(e.EW_REGISTERDLL):

                # \nsis-2.09-src\Source\lang.h
                #NLF_REGISTERING = -62
                #NLF_UNREGISTERING = -61 ?

                dllfile = S( parm0 )
                function_name = S( parm1 )
                nlf = I (parm2)

                NOUNLOAD = '/NOUNLOAD' \
                    if parm3==1 else ''                 

                if    function_name == 'DllUnregisterServer':
                    #nlf == NLF_UNREGISTERING
                    Decomp = "UnRegDLL  %s" % dllfile

                elif function_name =='DllRegisterServer':
                    #nlf == NLF_REGISTERING
                    Decomp = "RegDLL  %s"   % dllfile

                else:
                    #nlf == 0
                    Decomp = "CallInstDLL  %s %s %s" % ( dllfile, \
                                                         NOUNLOAD, \
                                                         function_name )

                DecompComment = 'maybe that from TOK__PLUGINCOMMAND sequence: EW_REGISTERDLL <- EW_PUSHPOP <- EW_UPDATETEXT <- EW_EXTRACTFILE <-EW_CALL \n' 
                DecompComment += '# or sth like >InstallOptions::initDialog "$INI"< CallInstDLL InstallOptions.dll  Push $INI SetDetailsPrint lastused File Call $PLUGINSDIR \n' \
                    if parm4 else ''

                #function_name: %s |     function_name , 
                DecompComment += "#nfl: %s | DoNot_FreeLibrary: %s | Do_GetModuleHandle: %s" % (nlf, I (parm3), I (parm4))

                break

            if case(e.EW_COPYFILES):
                FOF_SILENT          =     4
                FOF_NOCONFIRMATION  =  0x10
                FOF_FILESONLY       =  0x80
                FOF_SIMPLEPROGRESS  = 0x100
                FOF_NOCONFIRMMKDIR  = 0x200

                flags =  ''
                #parm4 = int( S(parm4) )
                if (parm4 and FOF_FILESONLY): # and not(parm2 and FOF_SIMPLEPROGRESS)
                    flags += ' /FILESONLY'
                if (parm4 and FOF_SILENT):
                    flags += ' /SILENT'

                DecompComment = '%s %s' % (S(parm2), S(parm3))

                Decomp = 'CopyFiles %s %s %s' % ( \
                    flags,
                    S( parm0 ), \
                    S( parm1 ) \
                )
                break

            if case(e.EW_SETFILEATTRIBUTES):
                FILE_ATTRIBUTE_READONLY	= 0x0001
                FILE_ATTRIBUTE_HIDDEN		= 0x0002
                FILE_ATTRIBUTE_SYSTEM		= 0x0004
                FILE_ATTRIBUTE_ARCHIVE		= 0x0020
                FILE_ATTRIBUTE_NORMAL		= 0x0080
                FILE_ATTRIBUTE_TEMPORARY	= 0x0100
                FILE_ATTRIBUTE_OFFLINE		= 0x1000

                FILE_ATTRIBUTES = { \
                    FILE_ATTRIBUTE_NORMAL:	'NORMAL', \
                    FILE_ATTRIBUTE_ARCHIVE:	'ARCHIVE', \
                    FILE_ATTRIBUTE_HIDDEN:	'HIDDEN', \
                    FILE_ATTRIBUTE_OFFLINE:	'OFFLINE', \
                    FILE_ATTRIBUTE_READONLY:	'READONLY', \
                    FILE_ATTRIBUTE_SYSTEM:	'SYSTEM', \
                    FILE_ATTRIBUTE_TEMPORARY:	'TEMPORARY', \
                    FILE_ATTRIBUTE_NORMAL:	'0' \
                }
                RawAttributes = parm1
                StrAttributes = BitOptions( RawAttributes, FILE_ATTRIBUTES, '|' )

                Decomp = 'SetFileAttributes %s %s' % ( \
                    S( parm0 ), \
                    StrAttributes )
                break

            if case(e.EW_RENAME):
                Decomp = 'Rename %s %s %s' % ( \
                    "/REBOOTOK" if parm2 else "", \
                    S( parm0 ), \
                    S( parm1 ), \
                )
                break

            if case(e.EW_RMDIR):
                #define DEL_DIR 1
                #define DEL_RECURSE 2
                #define DEL_REBOOT 4
                #define DEL_SIMPLE 8
                Decomp = 'RMDir %s %s' % ( \
                    S( parm0 ), \
                    BitOptions(parm1, " /r /REBOOTOK") \
                    )
                break

            if case(e.EW_DELETEFILE):

                Decomp = 'Delete %s %s' % ( \
                    "/REBOOTOK" if parm1 else "", \
                    S( parm0 ), \
                )
                break

            if case(e.EW_EXECUTE):
                if parm2:
                    Decomp = 'ExecWait %s %s' % ( S( parm0 ), V( parm1 ) )
                else:
                    Decomp = 'Exec %s'        %   S( parm0 )

                break

            if case(e.EW_SHELLEXEC):
                Decomp = 'ExecShell %s %s %s %s' % ( \
                    S( parm0 ), \
                    S( parm1 ), \
                    S( parm2 ), \
                    E( parm3, "SW_SHOWDEFAULT  SW_SHOWMAXIMIZED SW_SHOWMINIMIZED SW_HIDE SW_SHOW SW_SHOWNA SW_SHOWMINNOACTIVE" ) \
                    ) # no SW_SHOWNORMAL
                DecompComment = S( parm5 )
                break

            if case(e.EW_EXTRACTFILE):

                SetOverwrite = parm0 & 7

                MB_Const = parm0 >> 3

                IDCANCEL = 2
                isIDCANCEL = MB_Const & (IDCANCEL << 21)
                MB_Const  &= ~(IDCANCEL << 21)
                if isIDCANCEL:
                    MB_Const  |= IDCANCEL

                SetOverwriteAsText = E(SetOverwrite, "on off try ifnewer ifdiff lastused")   
                if cls_Decomp.SetOverwrite != SetOverwrite:
                    Decomp = 'SetOverwrite ' + SetOverwriteAsText + '\n' + instident
                
 
                try:
                    dt = ''
                    #Int32x32To64
                    ft_dec = struct.unpack('>Q', struct.pack('>ll', parm4, parm3))[0]
                    
                    from datetime import datetime
                    
                    # UnixTimeToFileTime http://support.microsoft.com/kb/167296                    
                    EPOCH_AS_FILETIME = 116444736000000000;  HUNDREDS_OF_NANOSECONDS = 10000000
                    
                    # Don't use Timezone Information - timpstamp was get (during compiling) via GetFileTime()
                    dt = datetime.fromtimestamp((ft_dec - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOSECONDS)
                except: pass
                
 
                ##ifdef _WIN32
                        #FILETIME ft;
                        #if (GetFileTime(hFile,NULL,NULL,&ft))
                        #{
                        #PULONGLONG fti = (PULONGLONG) &ft;
                        #*fti -= *fti % 20000000; // FAT write time has a resolution of 2 seconds
                        #ent.offsets[3]=ft.dwLowDateTime, ent.offsets[4]=ft.dwHighDateTime;
                        #}
                ##else
                        
                        #ll = Int32x32To64(t, 10000000) + 116444736000000000;
                        # 		       
                        #struct stat st;
                        #if (!fstat(fd, &st))
                        #{
                        #unsigned long long ll = (st.st_mtime * 10000000LL) + 116444736000000000LL;
                        #ll -= ll % 20000000; // FAT write time has a resolution of 2 seconds
                        #ent.offsets[3] = (int) ll, ent.offsets[4] = (int) (ll >> 32);
                        #}
                ##endif


                FileName     = Sq( parm1 )
                FileOffset   = parm2
                
                Decomp += "File  %s\n"  \
                           "%s   data_handle/Offset: %s  SetOverwrite %s  MB_Const:%x - %s  Time:%s (%X %X) msg:%s\n" % ( \
                    FileName, NSIS_COMMENT, \
                    B(FileOffset) , SetOverwriteAsText, \
                    MB_Const, MB_Style(MB_Const), \
                    dt, parm3, parm4, \
                    S(parm5) )
                cls_Decomp.SetOverwrite = SetOverwrite
                
                FileExtract.Files.append( (FileName, FileExtract.CurDir, FileOffset, ft_dec) )
                
                DecompComment = "Optimisation hint: >> File FOO.DIR\\%s<<  => IF prev cmd is 'SetOutPath' followed by a single(!) 'File' command(...followed by SetOutPath somewhere later)" % FileName
                
                break   

            if case(e.EW_SHOWWINDOW):
                if parm3==1:
                    Decomp = "EnableWindow %s %s " % ( \
                        S( parm0 ), \
                        S( parm1 ))
                elif parm2==1:
                    Decomp = "HideWindow"
                    DecompComment = "TOK_HIDEWINDOW %s %s" % ( \
                        S( parm0 ), \
                        S( parm1 ))
                else:
                    handle    = S( parm0 )
                    showState = S( parm1 )
                    Decomp = "ShowWindow %s %s " % ( \
                        S( parm0 ), \
                        S( parm1 ))

                    if (showState == '5'):#and (handle=='$HWNDPARENT'):
                        #skip next 
                        #i+=1
                        n_which = fo.uInt32()
                        #n_parm0 = fo.Int32()
                        #n_parm1 = fo.Int32()
                        #n_parm2 = fo.Int32()
                        #n_parm3 = fo.Int32()
                        #n_parm4 = fo.Int32()
                        #n_parm5 = fo.Int32()

                        fo.seek (-4,os.SEEK_CUR)
                        if e.EW_BRINGTOFRONT != n_which:
                            print "ERROR !!! Expected next command to be EW_BRINGTOFRONT"
                            #i-=1
                            #fo.seek (-4*7,os.SEEK_CUR)
                        else:
                            skipCommand = True


                        #Decomp = "BringToFront"


                break
            if case(e.EW_SECTIONSET):
                #SECTION_FIELD_GET_name_ptr = 0
                #SECTION_FIELD_SET_name_ptr = -1

                what = ''
                Arg2 = '""'
                default = parm3

                if parm2 in (0,~0): what = 'Text';      Arg2 = Sq( parm4 )
                if parm2 in (1,~1): what = 'InstTypes'; Arg2 = Sq( parm1 )
                if parm2 in (2,~2): what = 'Flags';     Arg2 = Sq( parm1 )#; assert(default == 1)
                if parm2 in (5,~5): what = 'Size';      Arg2 = Sq( parm1 )

                if parm2 >= 0:
                    Decomp = 'SectionGet%s %s %s' % ( what, SECTION_FIELD( parm0 ), V( parm1 ))
                else:
                    Decomp = 'SectionSet%s %s %s' % ( what, SECTION_FIELD( parm0 ), Arg2)

                break
            if case(e.EW_INSTTYPESET):

                if   parm3 == 0:
                    if   parm2 == 0:
                        Decomp = 'InstTypeGetText %s %s' % ( S( parm0 ), V( parm1 ))
                    elif parm2 == 1:
                        Decomp = 'InstTypeSetText %s %s' % ( S( parm0 ), Sq( parm1 ))

                elif parm3 == 1:
                    if   parm2 == 1:
                        Decomp = 'SetCurInstType %s'     % ( S( parm0 )            )
                    elif parm2 == 0:
                        Decomp = 'GetCurInstType %s'     % (             V( parm1 ))
                break

            try:     
                print "   parm0: %s \n" % S( parm0 )
                print "   parm1: %s \n" % S( parm1 )
                print "   parm2: %s \n" % S( parm2 )
                print "   parm3: %s \n" % S( parm3 )
                print "   parm4: %s \n" % S( parm4 )
                print "   parm5: %s \n" % S( parm5 )
                Decomp = "Decompiling that command it not implemented yet!" 
            except:  pass
#           stop()
            break

    # insert Sections labels
        SectionTxt = MakeSectionTxt(Tokenindex)
        #, isInsideSection


        DecompComment = ("\t\t; " if DecompComment else "") + \
            DecompComment

        global supressCodeOutsideSections
        DoSupress =(isInsideSection == False) and supressCodeOutsideSections
        if DoSupress:
            Decomp = "SUPRESSED!!!  " + Decomp

        if skipCommand:
            Decomp = "SKiPPED!!!  " + Decomp

        if cls_Decomp.Functions.has_key(i):
            print cls_Decomp.Functions[i]

        if cls_Decomp.Labels.has_key(i):
            print cls_Decomp.Labels[i]

        lineDecomp    = instident + "%s" % (Decomp)
        lineDecompcmt = instident + "// %s" % (DecompComment)

        print SectionTxt
        print lineDecomp
        #print lineDecompcmt

#        if SectionTxt:
#            cls_Decomp.SectionTxt[i] = SectionTxt

        if not(skipCommand):
            cls_Decomp.Tokens   [i] = lineRawInfo
            cls_Decomp.Decomps  [i] = Decomp
            cls_Decomp.Comments [i] = DecompComment
        cls_Decomp.DoSupress[i] = DoSupress or skipCommand

    off = fo.tell()
    print 'End Of Entries: %.8X' % off 


    SaveDecompiledToNsiFile(NB_ENTRIES_Num, instident)


def SaveDecompiledToNsiFile(NB_ENTRIES_Num, instident):
    # write nsi files (second pass)
    # Now also post defined labels are written.
    for i in range(TOKENBASE, NB_ENTRIES_Num + TOKENBASE):

        Tokenindex = i


        # Write SectionTxt 'Section[Group]...', 'SectionIn...', 'Section[Group] End'
        SectionTxt = MakeSectionTxt(Tokenindex)
        if SectionTxt:
            fDecompOut( SectionTxt)

        # Write Function   
        if cls_Decomp.Functions.has_key(i):
            if cls_Decomp.isInsideFunction:
                fDecompOut( "FunctionEnd\n\n" )
                #cls_Decomp.isInsideFunction = False
            else:
                cls_Decomp.isInsideFunction = True
                
            fDecompOut( "%s" % cls_Decomp.Functions[i] )
            

        # Write Labels
        if cls_Decomp.Labels.has_key(i):
            fDecompOut( \
                "  %s\n" % cls_Decomp.Labels[i] ) 

        if cls_Decomp.DoSupress.get(i,False)==False:

            global supressRawTokens
            if supressRawTokens == False:
                # Write Token info
                fDecompOut( \
                    "   %s\n" % \
                    cls_Decomp.Tokens.get(i) \
                )
            # Write Decompiled Lines
            fDecompOut( \
                instident + "%s%s\n\n" % \
                ( cls_Decomp.Decomps.get(i), \
                  cls_Decomp.Comments.get(i) \
                  ))
            
    if cls_Decomp.isInsideFunction:
        fDecompOut( "FunctionEnd\n\n" )


def MakeSectionTxt(Tokenindex):
    global isInsideSection
    SectionTxt = ''
    pos = Tokenindex - TOKENBASE

    if cls_Decomp.Sections_end.has_key(pos):
        SectionTxt += cls_Decomp.Sections_end[pos] + '\n\n'
        isInsideSection = False

    if cls_Decomp.Sections_start.has_key(pos):
        if cls_Decomp.isInsideFunction:
            fDecompOut( "FunctionEnd\n\n" )
            cls_Decomp.isInsideFunction = False 
            
        SectionTxt += cls_Decomp.Sections_start[pos] + \
            ' ' + cls_Decomp.Sections_idx.get(pos, '') + '\n' + \
            cls_Decomp.SectionsIN.get(pos, '') + '\n'
        isInsideSection = True


    if cls_Decomp.Functions.has_key(pos):
        isInsideSection |= not( 'FunctionEnd' in cls_Decomp.Functions[pos] )

    return SectionTxt#, isInsideSection

def MB_Style(parm0):
    # 0..5
    MB = []
    MB.append(getnumtokens( parm0 & 7 ,\
                            "MB_OK MB_OKCANCEL MB_ABORTRETRYIGNORE MB_YESNOCANCEL MB_YESNO MB_RETRYCANCEL" ) )

    #16 32 48 64		
    bits = (parm0 >> 4) & 7
    if bits:
        MB.append( getnumtokens( bits , \
                                 " MB_ICONSTOP MB_ICONQUESTION MB_ICONEXCLAMATION MB_ICONINFORMATION" ) )

    MB_USERICON = 0x80
    if parm0 & MB_USERICON:    
        MB.append( 'MB_USERICON' )

        #  define MB_SETFOREGROUND   0x10000
        #  define MB_TOPMOST         0x40000
        #  define MB_RIGHT           0x80000
        #  define MB_RTLREADING     0x100000
    bits = (parm0 >> 16) & 7
    if bits:
        MB.append( BitOptions( bits & 7 , \
                               "MB_SETFOREGROUND MB_TOPMOST MB_RIGHT MB_RTLREADING" ) )

    Rest = (parm0 & ~( 7<<16 | 017<<4 | 7))
    if Rest:
        MB.append(  hex( Rest ) )

    return '|'.join( MB )




def main(argv):

    global CurrFileOffset,CurrFileName
    global fo, fo2, fo3
    global fDecomp
    global DoDecompile
    
    global fDecomp_Dir
    Outpath = os.path.join( \
                  os.path.dirname(argv), \
                  fDecomp_Dir)
    
    NewFileName = os.path.join( \
                                Outpath, \
                                os.path.basename(argv) + '.nsi' \
                            )
    CurrFileName = argv
    global File_Num
    File_Num = os.path.getsize(CurrFileName)
    print 'File_Num: %d \n' % File_Num

    
    def makedirs_p(path, mode = 0777, exist_ok = True):
        import os, errno
        
        # Note: For Python ≥ 3.2
        #       os.makedirs has an optional third argument exist_ok
        #       so in that case you may remove that try..except block
        try:
            os.makedirs(path, mode)
        except OSError as e: # Python >2.5
            if  e.errno == errno.EEXIST and \
                os.path.isdir(path) and \
                exist_ok:
                pass
            else: 
                raise
    
    fo = myFile( CurrFileName, 'rb')
    fo2 = myFile( CurrFileName, 'rb')
    fo3 = myFile( CurrFileName, 'rb')

    if DoDecompile:
        
        makedirs_p( Outpath )
        fDecomp = myFile( NewFileName  , 'wt')


    LoadCommonheader()

#     while (CurrFileOffset < File_Num):
#          GetRawData( )     
#          fRaw = open("mywav.raw","wb")
#          fRaw.write(WaveFileRaw[0])      
#          fRaw.close()

            #print 'RawData_Num: %d' % WaveFileRaw_Num[0]
            #print '\n'


            #CurrFileOffset += 8

#          if (not CONFIG_ExtractOnly ):
#               fo.seek(CurrFileOffset)
#               fo.write(WaveFileRaw[0])

#          CurrFileOffset += FileRaw_Num[0]

    if DoDecompile:
        fDecomp.close()

    fo3.close()
    fo2.close()
    fo.close()


def _dodecomp( size_comp, size_decomp):
    import zlib
    global fo
    
    if not(isVerNS3):
        size = fo.Int32()
        iscompressed = size < 0
        if iscompressed:
            size = -size
            print hex(size)
    
    compressed = buffer( fo.read(size_comp) )
    print "EndOfCompressedData: %X - EOF: %s" % ( fo.tell(), \
                                                 ''==fo.read(1) ) 
    
    decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)    
    
    data = myString( decompressobj.decompress(compressed ) )
   
    NewFileName = 'script.bin'#"File_all.bin" 
    fDecomp = open(NewFileName, "wb")
    fDecomp.write( data.read() )
    fDecomp.close() 

    
    main('script.bin')    
    
    FileExtract_NoDup = {}
    for i in FileExtract.Files:
        (FileName, FileExtract.CurDir, FileOffset, ft_dec) = i
        #print "{2:8} {1} {0}".format(*i) #(FileName, FileExtract.CurDir, FileOffset, ft_dec)
        
        FileExtract_NoDup[FileOffset]=(FileName, FileExtract.CurDir, ft_dec)
    
    print '_________________________________________________________'
    
    for i in sorted ( FileExtract_NoDup.items() ):
        (FileOffset, ( FileName, Dir, ft_dec)) = i
        print (FileOffset, Dir, FileName, ft_dec)    

    i = 0
    while decompressobj.unused_data:
            
        data = decompressobj.decompress( decompressobj.unused_data )
        NewFileName = "File_%i.bin" % i 
        fDecomp = open(NewFileName, "wb")
        #print "%i - %x" % (i,script_bin_size)
        fDecomp.write( data )
        fDecomp.close()
        
        i += 1

    return
    data.seek(0)  
    
    i = 0
    
    try:
        for i in range(9999):
            script_bin_size = data.uInt32()
            if script_bin_size <= 0: break
            
            NewFileName = "File_%i.bin" % i 
            fDecomp = open(NewFileName, "wb")
            print "%i - %x" % (i,script_bin_size)
            fDecomp.write( data.read(script_bin_size) )
            fDecomp.close()
            
            FileExtract.Files.append( NewFileName )
    except: pass
    
    def ren(old,new):
        try:
            os.remove(new)
        except: pass
        
        os.rename(old, new)
                
   
    #lastFile is uninstaller
    if i > 1:
        ren( FileExtract.Files[0], 'script.bin')
        
        OpenNSIS_SetupExe( FileExtract.Files[-1])
        
    else:
        ren( FileExtract.Files[0], 'script_uninst.bin')
    
    
    #print "%100s" % data
    return

    

def OpenNSIS_SetupExe(CurrFileName):
    global fo
    fo = myFile( CurrFileName, 'rb')
    FH_SIG = '\xEF\xBE\xAD\xDENullsoftInst'
    #from mmap import *
    #s = mmap(fo.fileno(), 0, access=ACCESS_READ)
    
    
    def EndOfExe( CurrFileName):
        try:
            import pefile
            pe = pefile.PE(CurrFileName, fast_load = True)
            LastSect = pe.sections[-1]
            return LastSect.PointerToRawData + LastSect.SizeOfRawData
        
        except Exception:
            print "%s" % Exception
            return 0
            
            
    EOExe = EndOfExe(CurrFileName)
    fo.seek(EOExe)
    
    Searchbuff = fo.read(0x2000)
    
    NSIS_Start = Searchbuff.find(FH_SIG)
    if NSIS_Start >= 0:
        NSIS_Start += EOExe
       
        fo.seek(NSIS_Start - 4)
        flags = fo.uInt32()
        print hex(flags)
        #define FH_FLAGS_MASK 15
        FH_FLAGS_UNINSTALL = 1
        #ifdef NSIS_CONFIG_SILENT_SUPPORT
        #  define FH_FLAGS_SILENT 2
        #endif
        #ifdef NSIS_CONFIG_CRC_SUPPORT
        #  define FH_FLAGS_NO_CRC 4
        #  define FH_FLAGS_FORCE_CRC 8
        #endif        

        # if there are any flags are set like NSIS_CONFIG_SILENT_SUPPORT or NSIS_CONFIG_CRC_SUPPORT 
        #I'll means that setup was create with a
        # special build with #define crap that'll probably mess the one or other
        # datastructure
        assert (flags & ~FH_FLAGS_UNINSTALL) == 0
        
        FileExtract.isUninstall = flags & FH_FLAGS_UNINSTALL 
        
        NSIS_Start += len(FH_SIG)        

        fo.seek(NSIS_Start)
        #print hex(fo.tell())
        
        #uncompressed
        length_of_header = fo.uInt32()
        
        #compressed
        length_of_all_following_data = fo.uInt32()
        
        print 'length_of_header: ' + str( length_of_header )
        print 'length_of_all_following_data: ' + str( length_of_all_following_data )  
        _dodecomp(length_of_all_following_data, length_of_header)
    fo.close

if __name__ == "__main__":
    #OpenNSIS_SetupExe('setup.exe')
    #OpenNSIS_SetupExe('FileFunc.exe')
    #OpenNSIS_SetupExe('AudioLog 4.exe')
    main('script.bin')
    main('script_uninst.bin')
    #main(sys.argv[1])
    
    #for i in FileExtract.Files:
        #(FileName, FileExtract.CurDir, FileOffset, ft_dec) = i
    #    print "{2:8} {1} {0}".format(*i) #(FileName, FileExtract.CurDir, FileOffset, ft_dec)