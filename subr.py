#!/usr/bin/python
#coding:utf-8
'''
执行以下脚本导入超级断点工具

(lldb) command script import ~/workspace/3-lldb/subr.py
The "sbr" python command has been installed and is ready for use.
(lldb)
输出安装成功，只需就收一个地址就可工作
subr 地址

(lldb) br delete
About to delete all breakpoints, do you want to do that?: [Y/n] y
All breakpoints removed. (1 breakpoint)
(lldb) subr 0x00000001000093dd
Breakpoint 2: where = Calculator`___lldb_unnamed_function161$$Calculator, address = 0x000000010cb033dd
(lldb)
对于经常使用的脚本，可以在lldb的初始化文件里添加命令加载脚本，启动自定义的命令
修改~/.lldbinit文件，在文件里加入一行

command script import ~/sbr.py
'''
import lldb
import commands
import optparse
import shlex
import re
import time
# 获取ASLR的偏移地址
def get_ASLR():
    # 获取‘image list -o’命令的返回结果
    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('image list -o', returnObject)
    output = returnObject.GetOutput();
    # 正则匹配出第一个0x开头的16进制地址
    match = re.search(r'(1\]\s)(0x[0-9a-fA-F]+)', output)
    if match:
        return match.group(2)
    else:
        return None
def get_sp():
    # 获取‘image list -o’命令的返回结果
    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('register read/x sp', returnObject)
    output = returnObject.GetOutput();
    # 正则匹配出第一个0x开头的16进制地址
    match = re.match(r'.+(0x[0-9a-fA-F]+)', output)
    if match:
        return match.group(1)
    else:
        return None
def get_pc():
    # 获取‘image list -o’命令的返回结果
    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('register read/x pc', returnObject)
    output = returnObject.GetOutput();
    # 正则匹配出第一个0x开头的16进制地址
    match = re.match(r'.+(0x[0-9a-fA-F]+)', output)
    if match:
        return match.group(1)
    else:
        return None
#得到最后断点的标号
def getbrlistn():
    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('br list', returnObject)
    output = returnObject.GetOutput();
    # 正则匹配出所有的断点代号
    match = re.findall(r'(^\d{1,4})(:\saddress)', output,re.M)
    if match:
        num=len(match)
        strlast=match[num-1]
        brnum=strlast[0]
        #print brnum
        return brnum
    else:
        return None
# Super breakpoint
def sni(debugger, command, result, internal_dict):
    ADDRESS = get_pc()
    #增加断点
    if not command:
        if ADDRESS:
            debugger.HandleCommand('br set -a "%s+4"' % (ADDRESS))
            print 'br set success:"%s+4"'%ADDRESS
            #执行到断点
            debugger.HandleCommand('c')
            NUM = getbrlistn()
        #删除断点
            if NUM:
                time.sleep(1)
                debugger.HandleCommand('br dele %s' % (NUM))
                print "br dele success:%s"%NUM
            else:
                print >>result, 'br list number not found!'
        else:
            print >>result, 'ADDRESS not found!'
    else:
        offby=int(command,16)*4
        if ADDRESS:
            debugger.HandleCommand('br set -a "%s+%x"' % (ADDRESS,offby))
            print 'br set success:"%s+%x"'%(ADDRESS,offby)
            #执行到断点
            debugger.HandleCommand('c')
            NUM = getbrlistn()
            #删除断点
            if NUM:
                time.sleep(1)
                debugger.HandleCommand('br dele %s' % (NUM))
                print "br dele success:%s"%NUM
            else:
                print >>result, 'br list number not found!'
        else:
            print >>result, 'ADDRESS not found!'
def spaddr(debugger, command, result, internal_dict):
    SPADD=get_sp()
    if not SPADD:
        print "nothing found sp"
    if not command:
        debugger.HandleCommand('memory read $sp')   
    else:
        debugger.HandleCommand('memory read "%s+%s"' % (SPADD, command))
def spaddrbig(debugger, command, result, internal_dict):
    SPADD=get_sp()
    if not SPADD:
        print "nothing found sp"
    if not command:
        debugger.HandleCommand('memory read $sp')   
    else:
        debugger.HandleCommand('memory read "%s+%s" "%s+%s+0x400"' % (SPADD, command,SPADD, command))
def idaposi(debugger, command, result, internal_dict):
	ASLR=get_ASLR()
	if not command:
		PCADD=get_pc()
		print "ASLR:",ASLR
		print "trueADDR:",PCADD
		if (ASLR!=None)&(PCADD!=None):
			#print ASLR
			#print PCADD
			addr=int(PCADD,16)-int(ASLR,16)
			print "idaposition_address:ox%x"%addr
		else:
			print "get info error"
	else:
		INNERADDR=command
		print "ASLR:",ASLR
		print "INNERADDR:",INNERADDR
		if (ASLR!=None)&(INNERADDR!=None):
			#print ASLR
			#print PCADD
			addr=int(INNERADDR,16)-int(ASLR,16)
			print "idaposition_address:ox%x"%addr
		else:
			print "get info error"

def conn(debugger, command, result, internal_dict):
    
    IPconn = command
    #删除断点
    if IPconn:
        #print "%d"%NUM
        debugger.HandleCommand('process connect connect://%s:1234' % (IPconn))
        #print NUM
    else:
        debugger.HandleCommand('process connect connect://192.168.1.117:1234')
        print >>result, 'default ip!'
# And the initialization code to add your commands 
# Super breakpoint
def sbr(debugger, command, result, internal_dict):
    #用户是否输入了地址参数
    if not command:
        print >>result, 'Please input the address!'
        return
    ASLR = get_ASLR()
    if ASLR:
        #如果找到了ASLR偏移，就设置断点
        debugger.HandleCommand('br set -a "%s+%s"' % (ASLR, command))
    else:
        print >>result, 'ASLR not found!'
# And the initialization code to add your commands 
def inaddr(debugger, command, result, internal_dict):
    #用户是否输入了地址参数
    if not command:
        print >>result, 'Please input the address!'
        return
    ASLR = get_ASLR()
    if ASLR:
        #如果找到了ASLR偏移，就设置断点
        #debugger.HandleCommand('br set -a "%s+%s"' % (ASLR, command))
        addr=int(command,16)+int(ASLR,16)
        print "innternal starage address is 0x%x"%addr

    else:
        print >>result, 'ASLR not found!'
# And the initialization code to add your commands 
def __lldb_init_module(debugger, internal_dict):
    # 'command script add sbr' : 给lldb增加一个'sbr'命令
    # '-f sbr.sbr' : ¸该命令调用了sbr文件的sbr
    debugger.HandleCommand('command script add subr -f subr.sbr')
    debugger.HandleCommand('command script add sni -f subr.sni')
    debugger.HandleCommand('command script add idap -f subr.idaposi')
    debugger.HandleCommand('command script add conn -f subr.conn')
    debugger.HandleCommand('command script add spaddr -f subr.spaddr')
    debugger.HandleCommand('command script add spaddrbig -f subr.spaddrbig')
    debugger.HandleCommand('command script add inaddr -f subr.inaddr')
    print 'The "sbr" python command has been installed and is ready for use.'
