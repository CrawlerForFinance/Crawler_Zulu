from distutils.core import setup  
import py2exe  
import sys
includes = ["encodings", "encodings.*"]    
sys.argv.append("py2exe")  
options = {"py2exe":   { "bundle_files": 1 }  }
setup(console=['winrun.py','Crawler_zulu.py', 'tools_zulu.py'],data_files=[r"config"])