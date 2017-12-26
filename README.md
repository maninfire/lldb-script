# lldb-script
1.expression(或者缩写expr)  表达式 

expression $r6 = 1   // 设置r6寄存器的值

2.po 表达式

po $r6

3.print (type)表达式

print (int)$r6

4.bt [all]   --- 打印调用堆栈
    Frame info 打印当前堆块信息

5.breakpoint list     //打印断点列表
br l
breakpoint set -a 函数地址   --常规断点
br s 
breakpoint set --func-regex 函数关键字  
比如再某动态库中有 testA函数，那么常规做法是先 image list -o -f 查看模块基址 然后 image lookup -r -n 函数关键字找到偏移   然后再 br s -a 基址＋偏移!

再来一个对动态库函数下断的：
breakpoint set --shlib foo.dylib --name foo
这个也非常有用，可以进行断点过程中的一些自动化处理：
breakpoint command add 断点序号
禁用某个断点   br dis 6
Q启用某个断点    br en 6
删除某个断点     br del 6

6.c   继续执行
7.s 源码级别单步执行，遇到子函数则进入
8.si 单步执行，遇到子函数则进入
9.n 源码级别单步执行，遇到子函数不进入，直接步过
10.ni 单步执行，遇到子函数不进入，直接步过
11.finish/f 退出子函数
12.thread list 打印线程列表
13.image lookup -a 表达式、image list
例子：
image lookup -a $pc
返回如下：

      Address: debug[0x0000b236] (debug.__TEXT.__text + 1254)

      Summary: debug`main + 58 at main.m:16

打印加载模块列表

image list [-f -o 通常带这两个参数使用]
查找某个函数：

对于有调试符号的这样使用

image lookup -r -n <FUNC_REGEX>

对于无调试符号的这样使用：

image lookup -r -s <FUNC_REGEX>

14.disassemble -a 地址
disassemble -A thumb    
disassemble -c 5设置反汇编输出行数
可选：
thumbv4t
thumbv5
thumbv5e
thumbv6
thumbv6m
thumbv7
thumbv7f
thumbv7s
thumbv7k
thumbv7m
thumbv7em

///////////////////////////////////////////////
15.memory read [起始地址 结束地址]/寄存器 -outfile 输出路径
memory read $pc
memory read 0x35f1c 0x35f46 -outfile /tmp/test.txt  // 将内存区域保存到文件
默认情况下，memory read 只能读取 1024字节数据
--binary // 二进制输出
例：

memory read 0x1000 0x3000 -outfile /tmp/test.bin --binary -force

写内存：

memory write $rip 0xc3

memory write $rip+1 0x90




16.register read/格式、register write 寄存器名称 数值

例子：
register read/x
// 改写r9寄存器例子：
register write r9 2

17.display 表达式     undisplay 序号
例子：

display $R0

undisplay 1


18.内存断点 watchpoint set expression 地址    /  watchpoint set variable 变量名称 -- (源码调试用到，略过)
18.1.条件断点 watchpoint modify -c 表达式

watchpoint modify -c '*(int *)0x1457fa70 == 20'

19.查看当前堆栈
*thread backtrace
*bt
显示当前栈帧的参数和局部变量信息
*frame var -A
