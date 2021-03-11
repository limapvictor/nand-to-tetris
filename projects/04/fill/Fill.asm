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

// Put your code here.

(INFINITE_LOOP)
    @KBD
    D=M
    @NOT_IDLE_KEYBOARD
    D;JGT
    @color
    M=0 
    @SET_SCREEN_ARGUMENTS
    0;JMP
    (NOT_IDLE_KEYBOARD)
    @color
    M=-1

    (SET_SCREEN_ARGUMENTS)
    @SCREEN
    D=A
    @current_screen_position
    M=D
    @i
    M=0

    (FILL_SCREEN_LOOP)
        @i
        D=M
        @8192
        D=A-D
        @END_SCREEN_LOOP
        D;JEQ

        @color
        D=M
        @current_screen_position
        A=M
        M=D

        @current_screen_position
        M=M+1
        @i
        M=M+1

        @FILL_SCREEN_LOOP
        0;JMP

    (END_SCREEN_LOOP)
@INFINITE_LOOP
0;JMP


 