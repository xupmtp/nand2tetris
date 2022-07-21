// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.
// ==========以下偽代碼==========
// if (R0 < 0 && R1 < 0) END
// var sum=0, i=0;
// for (;i<@R2;){
//     sum+=@R1
//     i++;
// }
// if (sum >= 32768) END;
// else @R2=sum;
// END;

    // 宣告變數
    @i
    M=0
    @sum
    M=0
    // 判斷R0&R1為正數，否則停止
    @R0
    D=M
    @R1
    D=D|M
    @END
    D;JLT
    // R0,R1為0時不會跑loop, 但R2須為0
    @R2
    M=0

(LOOP)
    // condition
    @i
    D=M
    @R1
    D=D-M
    @BREAK
    D;JGE
    // i++, sum+=R0
    @i
    M=M+1
    @R0
    D=M
    @sum
    M=M+D
    @LOOP
    0;JMP

(BREAK) // 計算值沒溢位(>= 32768)時set給R2
    @sum
    D=M
    @32767 // 32768會溢位，判斷需用32767
    D=D-A
    @END
    D;JGT
    @sum
    D=M
    @R2
    M=D

(END)
    @END
    0;JMP