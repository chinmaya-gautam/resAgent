"""
This file is running at server to get sys info(cpu/memory/net/io)
Based on WBXTF, as a python tool.
                                                                         
Author: Fei Liang
Time: 2010-11-25
"""
import os

import WBXTFBusiness


class SysInfo:
    def __init__(self):
        self.__m_psMonitors = []

    def setProcessMonitor(self,processes):
        self.__m_psMonitors = processes
        return True

    def getProcessMonitor(self):
        return self.__m_psMonitors
    
    def __getTopInfo(self):
        ress = []
        try:
            nCmd = "top -bn 1"
            sh = os.popen(nCmd)
            ress = sh.readlines()
            sh.close()
            return ress
        except Exception,e:
            print "execute get top shell exception %s"%e
        return ress

    def __parseTopInfo(self,ressLines,processMonitors):
        taskTag = "Tasks:"
        CpuTag ="Cpu(s):"
        MemTag ="Mem:"
        SwapTag ="Swap:"
        topInfo = {}
        processInfos = []
        processInfoKeys = []
        processNameNum = -1
        try:
            for line in ressLines:
                ######################################################
                ##Parse Process Key Info
                if(line.find("PID")>=0 and line.find("COMMAND")>0 and line.find("CPU")>0 and line.find("MEM")>0):
                    line = line.replace("\n","").replace("\t","")
                    processInfoKeys = line.split()
                    processNameIndex = 0
                    while(processNameIndex<len(processInfoKeys)):
                        if(processInfoKeys[processNameIndex]=="COMMAND"):
                            processNameNum = processNameIndex
                            break
                        processNameIndex +=1
            print processInfoKeys
            
            for line in ressLines:
                line = line.replace("\n","").replace("\t","")
                
                ######################################################
                ##Parse Task Info
                if(line.find(taskTag)==0):
                    taskInfos = {}
                    taskStr = line[len(taskTag):]
                    print taskStr
                    taskAttrs = taskStr.split(",")
                    print taskAttrs
                    for taskAttr in taskAttrs:
                        KeyValues = taskAttr.split()
                        if(len(KeyValues)==2):
                            taskInfos[KeyValues[1]]=int(KeyValues[0])
                    topInfo["task"] = taskInfos 
                
                ######################################################
                ##Parse CPU Info
                elif(line.find(CpuTag)==0):
                    cpuInfos = {}
                    cpuStr = line[len(CpuTag):]
                    cpuAttrs = cpuStr.split(",")
                    for cpuAttr in cpuAttrs:
                        KeyValues = cpuAttr.split("%")
                        if(len(KeyValues)==2):
                            cpuInfos[KeyValues[1]]=float(KeyValues[0])
                    topInfo["cpu"] = cpuInfos
     
                ######################################################
                ##Parse Memory Info
                elif(line.find(MemTag)==0):
                    memInfos = {}
                    memStr = line[len(MemTag):]
                    memAttrs = memStr.split(",")
                    for memAttr in memAttrs:
                        KeyValues = memAttr.split("k ")
                        if(len(KeyValues)==2):
                            memInfos[KeyValues[1]]=float(KeyValues[0])
                    topInfo["mem"] = memInfos
    
                ######################################################
                ##Parse Swap Info
                elif(line.find(SwapTag)==0):
                    swapInfos = {}
                    swapStr = line[len(SwapTag):]
                    swapAttrs = swapStr.split(",")
                    for swapAttr in swapAttrs:
                        KeyValues = swapAttr.split("k ")
                        if(len(KeyValues)==2):
                            swapInfos[KeyValues[1]]=float(KeyValues[0])
                    topInfo["swap"] = swapInfos                
    
                
                ######################################################
                ##Parse Process Value Info  
                else:
                    for ps in processMonitors:
                        if(line.find(ps)>0):
                            psValues = line.split()
                            if (len(psValues)== len(processInfoKeys)):
                                processInfo = {}
                                psValueIndex = 0
                                while(psValueIndex<len(processInfoKeys)):
                                    processInfo[processInfoKeys[psValueIndex]]=psValues[psValueIndex]    
                                    psValueIndex +=1
                                processInfos.append(processInfo)
            topInfo["process"] = processInfos 
        except Exception,e:
            print "parse topinfo exception:%s"%e              
        return topInfo
    
    def getTopInfo(self):
        #ress = ['top - 15:43:59 up 72 days,  3:14,  3 users,  load average: 0.00, 0.00, 0.00\n', 'Tasks:  92 total,   1 running,  88 sleeping,   3 stopped,   0 zombie\n', 'Cpu(s):  0.0%us,  0.0%sy,  0.0%ni,100.0%id,  0.0%wa,  0.0%hi,  0.0%si,  0.0%st\n', 'Mem:   1026936k total,   997956k used,    28980k free,    66816k buffers\n', 'Swap:  2008084k total,     6988k used,  2001096k free,   831700k cached\n', '\n', '  PID USER      PR  NI  VIRT  RES  SHR S %CPU %MEM    TIME+  COMMAND            \n', '    1 root      15   0 10348  120   88 S  0.0  0.0   0:00.87 init               \n', '    2 root      RT  -5     0    0    0 S  0.0  0.0   0:01.46 migration/0        \n', '    3 root      34  19     0    0    0 S  0.0  0.0   0:00.00 ksoftirqd/0        \n', '    4 root      RT  -5     0    0    0 S  0.0  0.0   0:00.00 watchdog/0         \n', '    5 root      RT  -5     0    0    0 S  0.0  0.0   0:01.19 migration/1        \n', '    6 root      34  19     0    0    0 S  0.0  0.0   0:00.00 ksoftirqd/1        \n', '    7 root      RT  -5     0    0    0 S  0.0  0.0   0:00.00 watchdog/1         \n', '    8 root      RT  -5     0    0    0 S  0.0  0.0   0:01.20 migration/2        \n', '    9 root      34  19     0    0    0 S  0.0  0.0   0:00.00 ksoftirqd/2        \n', '   10 root      RT  -5     0    0    0 S  0.0  0.0   0:00.00 watchdog/2         \n', '   11 root      RT  -5     0    0    0 S  0.0  0.0   0:01.19 migration/3        \n', '   12 root      34  19     0    0    0 S  0.0  0.0   0:00.00 ksoftirqd/3        \n', '   13 root      RT  -5     0    0    0 S  0.0  0.0   0:00.00 watchdog/3         \n', '   14 root      10  -5     0    0    0 S  0.0  0.0   0:00.06 events/0           \n', '   15 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 events/1           \n', '   16 root      10  -5     0    0    0 S  0.0  0.0   0:00.01 events/2           \n', '   17 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 events/3           \n', '   18 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 khelper            \n', '   27 root      11  -5     0    0    0 S  0.0  0.0   0:00.00 kthread            \n', '   34 root      10  -5     0    0    0 S  0.0  0.0   0:00.01 kblockd/0          \n', '   35 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 kblockd/1          \n', '   36 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 kblockd/2          \n', '   37 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 kblockd/3          \n', '   38 root      14  -5     0    0    0 S  0.0  0.0   0:00.00 kacpid             \n', '  200 root      13  -5     0    0    0 S  0.0  0.0   0:00.00 cqueue/0           \n', '  201 root      13  -5     0    0    0 S  0.0  0.0   0:00.00 cqueue/1           \n', '  202 root      14  -5     0    0    0 S  0.0  0.0   0:00.00 cqueue/2           \n', '  203 root      14  -5     0    0    0 S  0.0  0.0   0:00.00 cqueue/3           \n', '  206 root      13  -5     0    0    0 S  0.0  0.0   0:00.00 khubd              \n', '  208 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 kseriod            \n', '  299 root      10  -5     0    0    0 S  0.0  0.0   0:12.11 kswapd0            \n', '  300 root      15  -5     0    0    0 S  0.0  0.0   0:00.00 aio/0              \n', '  301 root      16  -5     0    0    0 S  0.0  0.0   0:00.00 aio/1              \n', '  302 root      17  -5     0    0    0 S  0.0  0.0   0:00.00 aio/2              \n', '  303 root      17  -5     0    0    0 S  0.0  0.0   0:00.00 aio/3              \n', '  509 root      11  -5     0    0    0 S  0.0  0.0   0:00.00 kpsmoused          \n', '  574 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 mpt_poll_0         \n', '  575 root      13  -5     0    0    0 S  0.0  0.0   0:00.00 scsi_eh_0          \n', '  586 root      13  -5     0    0    0 S  0.0  0.0   0:00.00 kstriped           \n', '  607 root      10  -5     0    0    0 S  0.0  0.0   0:07.78 kjournald          \n', '  629 root      11  -5     0    0    0 S  0.0  0.0   0:00.00 kauditd            \n', '  658 root      21  -4 12644    0    0 S  0.0  0.0   0:00.12 udevd              \n', ' 1735 root      20  -5     0    0    0 S  0.0  0.0   0:00.00 ata/0              \n', ' 1736 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 ata/1              \n', ' 1737 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 ata/2              \n', ' 1738 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 ata/3              \n', ' 1739 root      20  -5     0    0    0 S  0.0  0.0   0:00.00 ata_aux            \n', ' 2006 root      20  -5     0    0    0 S  0.0  0.0   0:00.00 kmpathd/0          \n', ' 2007 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 kmpathd/1          \n', ' 2008 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 kmpathd/2          \n', ' 2009 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 kmpathd/3          \n', ' 2010 root      20  -5     0    0    0 S  0.0  0.0   0:00.00 kmpath_handlerd    \n', ' 2042 root      10  -5     0    0    0 S  0.0  0.0   0:04.02 kjournald          \n', ' 2044 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 kjournald          \n', ' 2046 root      10  -5     0    0    0 S  0.0  0.0   0:00.11 kjournald          \n', ' 2048 root      10  -5     0    0    0 S  0.0  0.0   0:00.88 kjournald          \n', ' 2050 root      10  -5     0    0    0 S  0.0  0.0   0:00.00 kjournald          \n', ' 2304 root      15   0 10104  228  168 S  0.0  0.0   0:00.05 syslogd            \n', ' 2307 root      15   0  3800    0    0 S  0.0  0.0   0:00.00 klogd              \n', ' 2318 root      15   0 10728  276  204 S  0.0  0.0   0:20.04 irqbalance         \n', ' 2330 rpc       17   0  8048    0    0 S  0.0  0.0   0:00.00 portmap            \n', ' 2354 root      20   0 15232    4    4 S  0.0  0.0   0:00.00 rpc.statd          \n', ' 2410 root      15   0 19184 4880 3780 S  0.0  0.5   0:00.01 ntpd               \n', ' 2413 root      16   0 52120  648  648 S  0.0  0.1   0:00.00 login              \n', ' 2414 root      18   0  3788  384  384 S  0.0  0.0   0:00.00 mingetty           \n', ' 2415 root      18   0  3788  384  384 S  0.0  0.0   0:00.00 mingetty           \n', ' 2416 root      18   0  3788  384  384 S  0.0  0.0   0:00.00 mingetty           \n', ' 2417 root      18   0  3788  384  384 S  0.0  0.0   0:00.00 mingetty           \n', ' 2418 root      18   0  3788  384  384 S  0.0  0.0   0:00.00 mingetty           \n', ' 2419 root      18   0  3796  424  424 S  0.0  0.0   0:00.00 agetty             \n', ' 2483 root      15   0 66148  604  604 S  0.0  0.1   0:00.02 bash               \n', ' 2517 root      15   0  6020  448  448 T  0.0  0.0   0:00.00 ping               \n', ' 2518 root      15   0  6020  448  448 T  0.0  0.0   0:00.00 ping               \n', ' 2521 root      15   0 74476  520  520 S  0.0  0.1   0:00.06 vi                 \n', ' 3062 root      15   0 60676  356  248 S  0.0  0.0   0:00.02 sshd               \n', '15946 root      15   0 63236 2972 2352 S  0.0  0.3   0:00.08 sshd               \n', '15992 root      17   0  437m  12m 6948 S  0.0  1.2   0:51.54 STAFProc           \n', '16820 root      17   0 1010m  16m 9044 S  0.0  1.7   0:00.48 java               \n', '16833 root      16   0 63236 2964 2348 S  0.0  0.3   0:00.06 sshd               \n', '16837 root      15   0 66168 1728 1304 S  0.0  0.2   0:00.01 bash               \n', '16865 root      15   0 78580 3252 1740 T  0.0  0.3   0:00.00 python             \n', '16874 root      17   0 72132 2912 1500 S  0.0  0.3   0:00.00 python             \n', '16875 root      15   0 12756 1020  760 R  0.0  0.1   0:00.00 top                \n', '22059 root      15   0     0    0    0 S  0.0  0.0   0:00.27 pdflush            \n', '24686 root      15   0     0    0    0 S  0.0  0.0   0:00.38 pdflush            \n', '31044 root      15   0 99.8m 3420 2928 S  0.0  0.3   0:00.08 WBXTFDemo1         \n', '32102 root      15   0 63236  760  760 S  0.0  0.1   0:00.27 sshd               \n', '32106 root      15   0 66168   64   64 S  0.0  0.0   0:00.01 bash               \n', '32138 root      17   0 99012   60   60 S  0.0  0.0   0:00.00 su                 \n', '32139 root      16   0 66060   64   64 S  0.0  0.0   0:00.00 bash               \n', '32151 root      18   0 99012   60   60 S  0.0  0.0   0:00.00 su                 \n', '32152 root      15   0 66172   72   72 S  0.0  0.0   0:00.13 bash               \n', '\n']
        ress = self.__getTopInfo()
        return self.__parseTopInfo(ress,self.__m_psMonitors)

    def __getSarInfo(self):
        ress = ""
        try:
            nCmd = "sar -P ALL 1 1"
            sh = os.popen(nCmd)
            ress = sh.read()
            sh.close()
            return ress
        except Exception,e:
            print "execute get sar shell exception %s"%e
        return ress

    def __parseSarInfo(self,res):
        validStr = "Average:"
        sarInfos = []
        try:
            ress = res.split("\n\n")
            for sarBlock in ress:
                if(sarBlock.find(validStr)>=0):
                    sarInfoKeys = []
                    
                    sarLines = sarBlock.split("\n")
                    sarKeyLine = sarLines[0].replace(validStr,"").replace("%","")
                    sarInfoKeys = sarKeyLine.split()
                    lineIndex =1
                    while lineIndex <len(sarLines):
                        sarValueLine = sarLines[lineIndex].replace(validStr,"")
                        values = sarValueLine.split()
                        if(len(sarInfoKeys)==len(values)):
                            sarInfo = {}
                            keyIndex =0
                            while(keyIndex<len(sarInfoKeys)):
                                sarInfo[sarInfoKeys[keyIndex]]=values[keyIndex]
                                keyIndex +=1
                            sarInfos.append(sarInfo)
                        lineIndex +=1
        except Exception,e:
            print "parse sar info exception :%s"%e
        return sarInfos
            
    def getSarInfo(self):
        ress = self.__getSarInfo()
        #ress = "Average:          CPU     %user     %nice   %system   %iowait    %steal     %idle\nAverage:          all      0.06      0.00      0.12      0.00      0.00     99.81\nAverage:            0      0.00      0.00      0.00      0.00      0.00    100.00"
        return self.__parseSarInfo(ress)

    def __getIOIStatOInfo(self):
        ress = ""
        try:
            nCmd = "iostat -x"
            sh = os.popen(nCmd)
            ress = sh.read()
            sh.close()
            return ress
        except Exception,e:
            print "execute get iostat shell exception %s"%e
        return ress


    def __parseIOStatInfo(self,res):
        validStr = "Device:"
        iostatInfos = []
        try:
            ress = res.split("\n\n")
            for statBlock in ress:
                if(statBlock.find(validStr)>=0):
                    iostatKeys = []
                    
                    iostatLines = statBlock.split("\n")
                    
                    keyLine = iostatLines[0].replace(":","").replace("%","").replace("/s","")
                    iostatKeys = keyLine.split()
                    lineIndex =1
                    while lineIndex <len(iostatLines):
                        valueLine = iostatLines[lineIndex]
                        values = valueLine.split()
                        if(len(iostatKeys)==len(values)):
                            iostatInfo = {}
                            keyIndex =0
                            while(keyIndex<len(iostatKeys)):
                                iostatInfo[iostatKeys[keyIndex]]=values[keyIndex]
                                keyIndex +=1
                            iostatInfos.append(iostatInfo)
                        lineIndex +=1
        except Exception,e:
            print "parse iostat info exception :%s"%e
        return iostatInfos
    
    def getIOStatInfo(self):
        ress = self.__getIOIStatOInfo()
        return self.__parseIOStatInfo(ress)

sysinfo = SysInfo()

WBXTFBusiness.setRoot(globals())
WBXTFBusiness.runAsTool("sysinfo")
#ress= sysinfo.getTopInfo()
