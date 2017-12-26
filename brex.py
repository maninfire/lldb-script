#!/usr/bin/python
#coding:utf-8
'''
执行以下脚本导入超级断点工具

(lldb) command script import ~/workspace/3-lldb/brex.py
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
    match = re.search(r'(7\]\s)(0x[0-9a-fA-F]+)', output)
    if match:
        return match.group(2)
    else:
        return None
def exbr(debugger, command, result, internal_dict):
    #用户是否输入了地址参数
    if not command:
        print >>result, 'Please input the address!'
        return
    ASLR = get_ASLR()
    if ASLR:
        #如果找到了ASLR偏移，就设置断点
        print ASLR
        debugger.HandleCommand('br set -a "%s+%s"' % (ASLR, command))   
    else:
        print >>result, 'ASLR not found!'
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
def exidaposi(debugger, command, result, internal_dict):
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
def get_bigpaddr(debugger, command, result, internal_dict):
    if not command:
        print "need arg"
        return None
    addr = get_addr(command)
    endaddr = addr+"+0x400"
    print endaddr
    print "addr contain is %s"%addr
    debugger.HandleCommand('memory read %s %s' % (addr,endaddr))
def get_paddr(debugger, command, result, internal_dict):
    if not command:
        print "need arg"
        return None
    addr = get_addr(command)
    endaddr = addr+"+0x400"
    print endaddr
    print "addr contain is %s"%addr
    debugger.HandleCommand('memory read %s ' % addr)

def get_contain():
    addr=get_addr("$sp+0x20")
    tar_addr = addr+"+0x160"
    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('memory read %s'%tar_addr, returnObject)
    output = returnObject.GetOutput();
    match = re.search(r'(&sig=)', output)
    if match:
        #print match.group(1)
        return True
    else:
        #print "no found"
        return False
def get_addr(paddr):
    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('memory read %s'%paddr, returnObject)
    output = returnObject.GetOutput();
    firstline = output.splitlines()[0]
    tmp = firstline.split()
    addr = "0x"+tmp[8]+tmp[7]+tmp[6]+tmp[5]+tmp[4]+tmp[3]+tmp[2]+tmp[1]
    return addr
def getaddr(debugger, command, result, internal_dict):
    if not command:
        print "you need arg"
        return None
    addr=get_addr(command)
    print "point addr is %s"%addr

def watch_break(debugger, command, result, internal_dict):
    addr=get_addr("$sp+0x20")
    tar_addr = addr+"+0x160"
    debugger.HandleCommand('watchpoint set expression %s'%tar_addr)
    tmp=0
    #get_contain()
    ''''''
    while not get_contain():
        tmp=tmp+1
        if tmp<50:
            debugger.HandleCommand('c')
            #time.sleep(0.1)
            print "continue"
        else:
            print "wrong result"
            return None
    print "you get it"
# And the initialization code to add your commands 
def __lldb_init_module(debugger, internal_dict):
    # 'command script add sbr' : 给lldb增加一个'sbr'命令
    # '-f sbr.sbr' : ¸该命令调用了sbr文件的sbr
    debugger.HandleCommand('command script add exbr -f brex.exbr')
    debugger.HandleCommand('command script add exidap -f brex.exidaposi')
    debugger.HandleCommand('command script add paddr -f brex.get_paddr')
    debugger.HandleCommand('command script add pbaddr -f brex.get_bigpaddr')
    debugger.HandleCommand('command script add wbr -f brex.watch_break')
    debugger.HandleCommand('command script add getaddr -f brex.getaddr')
    print 'The "exbr" python command has been installed and is ready for use.'
