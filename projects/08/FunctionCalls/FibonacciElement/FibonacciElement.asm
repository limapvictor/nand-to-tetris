//Bootstrap code
//SP = 256
@256
D=A
@SP
M=D
@$ret.0
D=A
@SP
A=M
MD=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
MD=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
MD=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
MD=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
MD=D
@SP
M=M+1
@5
D=A
@0
D=D+A
@R13
M=D
@SP
D=M
@R13
D=D-M
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.init
0;JMP
($ret.0)
//function Main.fibonacci 0
(Main.fibonacci)
//push argument 0
@0
D=A
@ARG
A=M+D
D=M
@SP
A=M
MD=D
@SP
M=M+1
//push constant 2
@2
D=A
@SP
A=M
MD=D
@SP
M=M+1
//lt                     
@SP
M=M-1
@SP
A=M
D=M
@SP
M=M-1
@SP
A=M
MD=M-D
@COMPARISON_TRUE_0
D;JLT
D=0
@END_OF_COMPARISON_0
0;JMP
(COMPARISON_TRUE_0)
D=-1
(END_OF_COMPARISON_0)
@SP
A=M
MD=D
@SP
M=M+1
//if-goto IF_TRUE
@SP
M=M-1
@SP
A=M
D=M
@Main.fibonacci$IF_TRUE
D;JNE
//goto IF_FALSE
@Main.fibonacci$IF_FALSE
0;JMP
//label IF_TRUE          
(Main.fibonacci$IF_TRUE)
//push argument 0        
@0
D=A
@ARG
A=M+D
D=M
@SP
A=M
MD=D
@SP
M=M+1
//return
@LCL
D=M
@R15
M=D
@5
D=A
@R15
A=M-D
D=M
@R14
M=D
@SP
M=M-1
@SP
A=M
D=M
@ARG
A=M
M=D
@1
D=A
@ARG
D=M+D
@R13
M=D
@R13
D=M
@SP
M=D
@4
D=A
@R15
A=M-D
D=M
@LCL
M=D
@3
D=A
@R15
A=M-D
D=M
@ARG
M=D
@2
D=A
@R15
A=M-D
D=M
@THIS
M=D
@1
D=A
@R15
A=M-D
D=M
@THAT
M=D
@R14
A=M
0;JMP
//label IF_FALSE         
(Main.fibonacci$IF_FALSE)
//push argument 0
@0
D=A
@ARG
A=M+D
D=M
@SP
A=M
MD=D
@SP
M=M+1
//push constant 2
@2
D=A
@SP
A=M
MD=D
@SP
M=M+1
//sub
@SP
M=M-1
@SP
A=M
D=M
@SP
M=M-1
@SP
A=M
MD=M-D
@SP
M=M+1
//call Main.fibonacci 1  
@Main.fibonacci$ret.0
D=A
@SP
A=M
MD=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
MD=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
MD=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
MD=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
MD=D
@SP
M=M+1
@5
D=A
@1
D=D+A
@R13
M=D
@SP
D=M
@R13
D=D-M
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(Main.fibonacci$ret.0)
//push argument 0
@0
D=A
@ARG
A=M+D
D=M
@SP
A=M
MD=D
@SP
M=M+1
//push constant 1
@1
D=A
@SP
A=M
MD=D
@SP
M=M+1
//sub
@SP
M=M-1
@SP
A=M
D=M
@SP
M=M-1
@SP
A=M
MD=M-D
@SP
M=M+1
//call Main.fibonacci 1  
@Main.fibonacci$ret.1
D=A
@SP
A=M
MD=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
MD=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
MD=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
MD=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
MD=D
@SP
M=M+1
@5
D=A
@1
D=D+A
@R13
M=D
@SP
D=M
@R13
D=D-M
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(Main.fibonacci$ret.1)
//add                    
@SP
M=M-1
@SP
A=M
D=M
@SP
M=M-1
@SP
A=M
MD=M+D
@SP
M=M+1
//return
@LCL
D=M
@R15
M=D
@5
D=A
@R15
A=M-D
D=M
@R14
M=D
@SP
M=M-1
@SP
A=M
D=M
@ARG
A=M
M=D
@1
D=A
@ARG
D=M+D
@R13
M=D
@R13
D=M
@SP
M=D
@4
D=A
@R15
A=M-D
D=M
@LCL
M=D
@3
D=A
@R15
A=M-D
D=M
@ARG
M=D
@2
D=A
@R15
A=M-D
D=M
@THIS
M=D
@1
D=A
@R15
A=M-D
D=M
@THAT
M=D
@R14
A=M
0;JMP
//function Sys.init 0
(Sys.init)
//push constant 4
@4
D=A
@SP
A=M
MD=D
@SP
M=M+1
//call Main.fibonacci 1   
@Sys.init$ret.0
D=A
@SP
A=M
MD=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
MD=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
MD=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
MD=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
MD=D
@SP
M=M+1
@5
D=A
@1
D=D+A
@R13
M=D
@SP
D=M
@R13
D=D-M
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(Sys.init$ret.0)
//label WHILE
(Sys.init$WHILE)
//goto WHILE              
@Sys.init$WHILE
0;JMP
