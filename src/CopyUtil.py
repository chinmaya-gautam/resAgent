'''
First version of copy tool, which ignores copy errors
caused by file permissions or files in use
'''

import os
import shutil


def copyTree(sourceDir, destDir):
    print "sourceDir:", sourceDir
    print "destDir:", destDir
    print

    errors = list()

    if not os.path.exists(sourceDir):
        return (False, "Source Directory does not exists")

    if not os.path.exists(destDir):
        try:
            os.makedirs(destDir)
        except:
            return (False, "Could not create %s" % destDir)

    cwd = destDir
    for dirName, subDirList, fileList in os.walk(sourceDir):
        cwd = os.path.join(destDir, dirName[len(sourceDir):].strip(os.sep))

        for subDir in subDirList:
            newDirPath = os.path.join(cwd, subDir)
            if not os.path.exists(newDirPath):
                try:
                    os.makedirs(newDirPath)
                except:
                    errors.append("Could not create %s" % str(newDirPath))

        for _file in fileList:
            try:
                shutil.copy(os.path.join(dirName, _file), cwd)
            except:
                errors.append("Could not create %s" % str(os.path.join(dirName, _file)))

    if len(errors) > 0:
        return (False, '\n'.join(errors))
    else:
        return (True, '')