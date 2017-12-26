#!/usr/bin/python
#coding:utf-8
'''
执行以下脚本导入超级断点工具

(lldb) command script import ~/workspace/3-lldb/bigdump.py
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
# Super breakpoint
def sbr(debugger, command, result, internal_dict):
    #用户是否输入了地址参数
    #command为输入参数
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
def dump(debugger, command, result, internal_dict):
	global filetemp
	if not command:
		print >>result, 'Please input the end address!'
		return
	ASLR = get_ASLR()
	if ASLR:
		print "ASLR:"+ASLR
		ASLR=int(ASLR,16)
		#end=int(command,16)
		end=0x4000
		temp=0x0
		startmid=temp+ASLR
		print "startmid:0x%x"%startmid
		endmid=startmid+0x300
		print "endmid:0x%x"%endmid
		temp+=0x400
		debugger.HandleCommand('memory read "%s+%s" -outfile /tmp/test.bin --binary -force' % (startmid, endmid))
		'''while(temp<=end):
			startmid=temp+ASLR
			endmid=startmid+0x400
			temp+=0x400
			debugger.HandleCommand('memory read "%s+%s" -outfile /tmp/test.bin --binary -force' % (startmid, endmid))
			if os.path.isfile("/tmp/test.bin"):
				f = open("/tmp/test.bin","rb")
				data = f.read()
				f.close()
				filetemp+=data
		file_object = open('/workspace/3-lldb/dump.bin','wb')
		file_object.write(filetemp)
		file_object.close()'''
		#memory read 0x1000 0x3000 -outfile /tmp/test.bin --binary -force
		#debugger.HandleCommand('memory read "%s+%s" -outfile /tmp/test.bin --binary -force' % (ASLR, command))
	else:
		print >>result, 'ASLR not found!'


def __lldb_init_module(debugger, internal_dict):
    # 'command script add sbr' : 给lldb增加一个'sbr'命令
    # '-f sbr.sbr' : ¸该命令调用了sbr文件的sbr
    debugger.HandleCommand('command script add bigd -f bigdump.dump')
    print 'The "bigdump" python command has been installed and is ready for use.'
