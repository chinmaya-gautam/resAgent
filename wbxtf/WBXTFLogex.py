__author__ = 'huajin2, Ares Ou (weou@cisco.com)'

import logging
import logging.handlers
import sys
import threading
import os

###   logging levels
WBXTF_NOTSET = logging.NOTSET
WBXTF_DEBUG = logging.DEBUG
WBXTF_INFO = logging.INFO
WBXTF_WARNING = logging.WARNING
WBXTF_ERROR = logging.ERROR
###   logger destination
WBXTF_LOG_CONSOLE = 0x1
WBXTF_LOG_FILE = 0x10
WBXTF_LOG_HTTP = 0x100

WBXTF_LOG_SEPARATOR = "##############################################################"
_WBXTF_LOGGER_FORMAT = "[%(levelname)s][%(asctime)s][PID:%(process)d][TID:%(thread)d] %(message)s"


class lowerThanWarnFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.WARNING


class HandlerFactory(object):
    handlers = {}

    @classmethod
    def getLowerThanWarnHandler(cls):
        if 'LowerThanWarnHandler' not in cls.handlers:
            lowerThanWarnHandler = logging.StreamHandler(sys.stdout)
            lowerThanWarnHandler.setFormatter(logging.Formatter(_WBXTF_LOGGER_FORMAT))
            lowerThanWarnHandler.addFilter(lowerThanWarnFilter())
            cls.handlers['LowerThanWarnHandler'] = lowerThanWarnHandler

        return cls.handlers['LowerThanWarnHandler']

    @classmethod
    def getWarningErrorHandler(cls):
        if 'warningErrorHandler' not in cls.handlers:
            warningErrorHandler = logging.StreamHandler(sys.stderr)
            warningErrorHandler.setFormatter(logging.Formatter(_WBXTF_LOGGER_FORMAT))
            warningErrorHandler.setLevel(logging.WARNING)
            cls.handlers['warningErrorHandler'] = warningErrorHandler

        return cls.handlers['warningErrorHandler']

    @classmethod
    def getRotatingFileHandler(cls, logPath, maxBytes, backupCount):
        if 'rotatingFileHandler' not in cls.handlers:
            cls.handlers['rotatingFileHandler'] = {}

        if logPath not in cls.handlers['rotatingFileHandler']:
            rotatingFileHandler = logging.handlers.RotatingFileHandler(
                logPath, 'a', maxBytes, backupCount)
            rotatingFileHandler.setFormatter(logging.Formatter(_WBXTF_LOGGER_FORMAT))
            cls.handlers['rotatingFileHandler'][logPath] = rotatingFileHandler

        return cls.handlers['rotatingFileHandler'][logPath]

# # set root logger
# logging.getLogger().setLevel(WBXTF_NOTSET)
# logging.getLogger().addHandler(HandlerFactory.getLowerThanWarnHandler())
# logging.getLogger().addHandler(HandlerFactory.getWarningErrorHandler())
# # logger for this module
# logger = logging.getLogger(__name__)
# logger.level = logging.DEBUG


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class WBXTFLogex(object):
    def __init__(self, threadLog=False):
        # default logger setting
        #logger.info("WBXTFLogex init")
        print "WBXTFLogex init"
        self.__loggers = {}
        self.__logLevel = WBXTF_DEBUG
        self.__mainThreadID = str(self.getCurrentThreadID())
        self.setLogLevel(WBXTF_DEBUG)
        self.__logDestination = WBXTF_LOG_CONSOLE
        self.__showFileNameAndLineNum = False
        self.__isThreadLog = threadLog
        self.__logPath = ''
        self.__logFileMaxBytes = 0
        self.__logFileBackupCount=0
        self.__logCallbackObj = None

        logging.getLogger().addHandler(HandlerFactory.getLowerThanWarnHandler())
        logging.getLogger().addHandler(HandlerFactory.getWarningErrorHandler())
        logging.getLogger().setLevel(self.__logLevel)

    @staticmethod
    def getCurrentThreadID():
        return threading.current_thread().ident

    @staticmethod
    def getCurrentThreadName():
        return threading.current_thread().name

    def getLogFileName(self):
        logPath = os.path.abspath(self.__logPath)
        baseName = os.path.basename(logPath)
        baseDir = os.path.dirname(logPath)
        if self.__isThreadLog:
            baseName = '%d_%s_%s' % (self.getCurrentThreadID(), self.getCurrentThreadName(), baseName)
        if os.path.isdir(logPath):
            # only folder path provided, create a name for the log file
            return os.path.join(logPath, baseName)
        elif baseName and '.' not in baseName:
            # path is like '/tmp/a' and folder should be created
            os.makedirs(logPath)
            return os.path.join(logPath, baseName)
        else:
            return os.path.join(baseDir, baseName)

    def getLogger(self, loggerName=''):
        if not loggerName:
            loggerName = self.__mainThreadID

        if self.__isThreadLog:
            currentThreadID = str(self.getCurrentThreadID())
            # if log by thread, set the loggerName explicitly, otherwise
            # only use '' for logger name which represents the root logger
            if currentThreadID != self.__mainThreadID:
                loggerName = self.__mainThreadID + '.' + currentThreadID

        if loggerName not in self.__loggers:
            self.setLogger(loggerName)

        return self.__loggers[loggerName]

    def setLogger(self, loggerName):
        if loggerName not in self.__loggers:
            newLogger = logging.getLogger(loggerName)
            newLogger.setLevel(self.__logLevel)

            if self.__logPath:
                # log path will vary if log by thread is enabled
                logPath = self.getLogFileName()
                newLogger.addHandler(HandlerFactory.getRotatingFileHandler(
                    logPath, self.__logFileMaxBytes, self.__logFileBackupCount))

            self.__loggers[loggerName] = newLogger

    def setLogFilePath(self, filePath, maxBytes=0, backupCount=0):
        if filePath:
            self.__logPath = filePath
        if maxBytes:
            self.__logFileMaxBytes = maxBytes
        if backupCount:
            self.__logFileBackupCount = backupCount

    def setLogCallbackObj(self,callbackObj):
        self.__logCallbackObj = callbackObj

    def executeCallback(self,logLevel,logContent):
        if self.__logLevel <= logLevel \
            and self.__logCallbackObj != None \
            and hasattr(self.__logCallbackObj,"onLog") \
            and callable(getattr(self.__logCallbackObj,"onLog")):
            self.__logCallbackObj.onLog(logLevel,logContent)

    def setLogLevel(self, newLevel):
        self.__logLevel = newLevel
        for instanceLogger in self.__loggers.values():
            instanceLogger.setLevel(self.__logLevel)

    def setThreadLog(self, isThreadLog):
        self.__isThreadLog = isThreadLog
        # if thread log is enabled, only enable the main logger
        for instanceLogger in self.__loggers.values():
            instanceLogger.disabled = not self.__isThreadLog

        try:
            self.__loggers[self.__mainThreadID].disabled = self.__isThreadLog
        except KeyError:
            pass

    @property
    def showFileNameAndLineNum(self):
        return self.__showFileNameAndLineNum

    @showFileNameAndLineNum.setter
    def showFileNameAndLineNum(self, val):
        self.__showFileNameAndLineNum = val


def buildFinalLogContent(logContent):
    callerFileName = sys._getframe(2).f_code.co_filename
    callerFunNamer = sys._getframe(2).f_code.co_name
    lineNumber = sys._getframe(2).f_lineno
    if WBXTFLogex().showFileNameAndLineNum:
        finialLog = "[%s][%s line:%s] %s" % (callerFunNamer, callerFileName, lineNumber, logContent)
    else:
        finialLog = "[%s] %s" % (callerFunNamer, logContent)
    return finialLog


def WBXTFLogDebug(logContent):
    WBXTFLogex().getLogger().debug(buildFinalLogContent(logContent))
    WBXTFLogex().executeCallback(WBXTF_DEBUG,logContent)

def WBXTFLogInfo(logContent):
    WBXTFLogex().getLogger().info(buildFinalLogContent(logContent))
    WBXTFLogex().executeCallback(WBXTF_INFO, logContent)


def WBXTFLogWarning(logContent):
    WBXTFLogex().getLogger().warning(buildFinalLogContent(logContent))
    WBXTFLogex().executeCallback(WBXTF_WARNING, logContent)


def WBXTFLogError(logContent):
    WBXTFLogex().getLogger().error(buildFinalLogContent(logContent))
    WBXTFLogex().executeCallback(WBXTF_ERROR, logContent)


def WBXTFLogSetLogFilePath(filePath, maxBytes=0, backupCount=0):
    WBXTFLogex().setLogFilePath(filePath, maxBytes, backupCount)


def WBXTFLogSetLogLevel(newLevel, showFileName=False):
    WBXTFLogex().setLogLevel(newLevel)
    WBXTFLogex().showFileNameAndLineNum = showFileName

def WBXTFLogSetCallbackObj(callbackObj):
    WBXTFLogex().setLogCallbackObj(callbackObj)

def WBXTFThreadLog(threadLog):
    WBXTFLogex().setThreadLog(threadLog)


if __name__ == '__main__':
    def worker(message):
        WBXTFLogInfo(message + ' info')
        WBXTFLogDebug(message + ' debug')
        WBXTFLogWarning(message + ' warning')
        WBXTFLogError(message + ' error')

    WBXTFLogex().setLogFilePath('/tmp/testtt.txt')
    WBXTFLogex().setThreadLog(True)
    WBXTFLogex().setLogLevel(WBXTF_DEBUG)
    WBXTFLogDebug('debug')
    WBXTFLogWarning('warning')
    WBXTFLogInfo('info')
    WBXTFLogError('error')
    t1 = threading.Thread(target=worker, args=('worker 1',))
    t2 = threading.Thread(target=worker, args=('worker 2',))
    t1.start()
    t2.start()
