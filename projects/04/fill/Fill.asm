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
    @i
    D=M
    @8192
    D=D-A
    @LOOP
    D;JGE
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
    @i
    M=M+1
    @WRITE_LOOP
    0;JMP