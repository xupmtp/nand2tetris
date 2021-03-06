// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
// ===========以下偽代碼==========
// while true:
//     color=0, i=0;
//     D = RAM[24576]; // 取得鍵盤輸入
//     if D > 0:
//         color=-1;
//     for (;i<8192;): // 渲染螢幕
//         RAM[@SCREEN+i] = color;
//         i++;
(LOOP)
    @color
    M=0
    @i
    M=0
    @24576
    D=M
    @BLACK
    D;JGT
    @WRITE_LOOP
    0;JMP
    @LOOP
    0;JMP

(BLACK)
    @color
    M=-1
    @WRITE_LOOP
    0;JMP

(WRITE_LOOP)
    // 條件
    @i
    D=M
    @8192
    D=D-A
    @LOOP
    D;JGE
    // 渲染
    @SCREEN
    D=A
    @i
    D=D+M
    @addr
    M=D
    @color
    D=M
    @addr
    A=M
    M=D
    // i++
    @i
    M=M+1
    @WRITE_LOOP
    0;JMP