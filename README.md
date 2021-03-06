# Tiny BASIC and Tiny BASIC Extended in Python

Tiny BASIC is a limited subset of BASIC intended to run on low-memory (2-4K)
machines. It was originally published in 1975 in the _People's Computer Company
newsletter_ (Vol. 4, Nos. 2-3) and republished in the first issue of _Dr Dobb's
Journal_.

Tiny BASIC Extended (TBX), published in the first issue of _Dr Dobb's Journal_,
added support for arrays and `FOR` loops.

Tiny BASIC and TBX were implemented in two parts: 1) a BASIC interpreter,
written in Tiny BASIC interpretive language (IL), a special-purpose assembly-
like language for an abstract machine; and 2) an IL interpreter, written for
the target platform. The Tiny BASIC interpreter in IL was printed in
_PCC_/_DDJ_, but the implementation of the IL interpreter was left as an
exercise to the reader. TBX was published with both an updated BASIC
interpreter in IL and an IL interpreter for 8080 machines.

This repository contains complete Tiny BASIC and TBX implementations, in three
parts:

- `tinybasic.il`: the Tiny BASIC interpreter, written in IL, as published in
  _PCC_/_DDJ_ with some modern corrections.
- `tbx.il`: the TBX interpreter, written in IL, as published in _DDJ_ with some
  modern corrections.
- `tinybasic.py`: an IL interpreter, written in Python.

## Language limitations

Because Tiny BASIC was designed to run on low-speed, low-memory microcomputers
from the 1970s, it is quite limited, even for its time. Compared to its
contemporaries, Tiny BASIC:

- Only supports integer variables; no arrays, strings or floating-point values
- Only supports 26 variables, named `A`-`Z`
- Only supports programs of up to 255 lines (this limitation is completely
  artificial in the Python IL interpreter, however; you can override it by
  passing an argument to the constructor)
- Only supports the following commands: `CLEAR`, `RUN`, `LIST`, `PRINT`,
  `INPUT`, `LET`, `GOTO`, `GOSUB`, `RETURN`, and `IF`-`THEN`

To Tiny BASIC, TBX added:

- One- and two- dimensional arrays.
- `FOR` loops and the `NXT` statement.
- The `RN` function, which generates random numbers.
- Two new print spacing commands: `;` to insert one space and `SP(n)` to insert
  _n_ spaces.
- Multiple statements per line, separated by `$`.
- Programs of up to 65,535 lines.

TBX also abbreviated some keywords: `NEW` (instead of `CLEAR`), `LST`, `PR`,
`IN`, and `RET`.

## Examples

### Tiny BASIC

```
$ python3 tinybasic.py

Tiny BASIC
As published in Dr Dobb's Journal, Vol.1, No.1 (Jan 1976).

Press ^C to break and ^D to quit.

? 10 let x=1
? 20 print "N", "N^2", "N^3"
? 30 print x, x*x, x*x*x
? 40 if x=10 then end
? 50 let x=x+1
? 60 goto 30
? run
N       N^2     N^3
1       1       1
2       4       8
3       9       27
4       16      64
5       25      125
6       36      216
7       49      343
8       64      512
9       81      729
10      100     1000
? ^D
```

```
$ python3 tinybasic.py -f change.bas

Tiny BASIC
As published in Dr Dobb's Journal, Vol.1, No.1 (Jan 1976).

Press ^C to break and ^D to quit.

? 1 PRINT "","","CHANGE"
? 2 PRINT "","CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY"
? 3 PRINT ""
? 4 PRINT "","(Adapted for Tiny BASIC in 2020.)"
? 5 PRINT ""
? 6 PRINT "I, YOUR FRIENDLY MICROCOMPUTER, WILL DETERMINE"
? 8 PRINT "THE CORRECT CHANGE FOR ITEMS COSTING UP TO $100."
? 9 PRINT ""
? 10 PRINT "COST OF ITEM"
? 11 INPUT A
? 12 PRINT "AMOUNT OF PAYMENT"
? 13 INPUT P
? 20 LET C=P-A
? 21 LET M=C
? 22 IF C<>0 THEN GOTO 90
? 25 PRINT "CORRECT AMOUNT, THANK YOU."
? 30 GOTO 400
? 90 IF C>0 THEN GOTO 120
? 95 PRINT "SORRY, YOU HAVE SHORT-CHANGED ME $",A-P
? 100 GOTO 10
? 120 PRINT "YOUR CHANGE, $",C
? 130 LET D=C/10
? 140 IF D=0 THEN GOTO 155
? 150 PRINT D,"TEN DOLLAR BILL(S)"
? 155 LET C=M-(D*10)
? 160 LET E=C/5
? 170 IF E=0 THEN GOTO 185
? 180 PRINT E,"FIVE DOLLARS BILL(S)"
? 185 LET C=M-(D*10+E*5)
? 190 LET F=C
? 200 IF F=0 THEN GOTO 215
? 210 PRINT F,"ONE DOLLAR BILL(S)"
? 215 PRINT "THANK YOU, COME AGAIN."
? 251 PRINT ""
? 252 GOTO 10
? 255 END
? run
                CHANGE
        CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY

        (Adapted for Tiny BASIC in 2020.)

I, YOUR FRIENDLY MICROCOMPUTER, WILL DETERMINE
THE CORRECT CHANGE FOR ITEMS COSTING UP TO $100.

COST OF ITEM
# 42
AMOUNT OF PAYMENT
# 60
YOUR CHANGE, $  18
1       TEN DOLLAR BILL(S)
1       FIVE DOLLARS BILL(S)
3       ONE DOLLAR BILL(S)
THANK YOU, COME AGAIN.

COST OF ITEM
# ^C
? ^D
```

### TBX

```
% python3 tinybasic.py -x -f chomp.bas

Tiny BASIC Extended (TBX)

As published in Dr Dobb's Journal of Computer Calisthenics
    and Orthodontia, Vol.1, Nos.1-2 (1976).

Press ^C to break and ^D to quit.

: 1 "CHOMP.BAS, from _BASIC Computer Games_ (1978), edited by David H. Ahl."
: 1 "Reproduced at https://www.atariarchives.org/basicgames/showpage.php?page=44"
: 1
: 1 "Adapted for Tiny BASIC in 2020."
: 1
: 10 PR SP(33);"CHOMP"
: 20 PR SP(15);"CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY"
: 30 PR$PR$PR
: 40 DIM A(10,10)

...

: 1020 PR 
: 1030 PR "AGAIN (1=YES, 0=NO!)";
: 1040 IN R
: 1050 IF R=1 GOTO 340
: 1060 END
: RUN
                                  CHOMP
                CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY




THIS IS THE GAME OF CHOMP (SCIENTIFIC AMERICAN, JAN 1973)
DO YOU WANT THE RULES (1=YES, 0=NO!) ? 0

HERE WE GO...

HOW MANY PLAYERS ? 2

HOW MANY ROWS ? 9

HOW MANY COLUMNS ? 9



        1  2  3  4  5  6  7  8  9
1       P  *  *  *  *  *  *  *  *  
2       *  *  *  *  *  *  *  *  *  
3       *  *  *  *  *  *  *  *  *  
4       *  *  *  *  *  *  *  *  *  
5       *  *  *  *  *  *  *  *  *  
6       *  *  *  *  *  *  *  *  *  
7       *  *  *  *  *  *  *  *  *  
8       *  *  *  *  *  *  *  *  *  
9       *  *  *  *  *  *  *  *  *  

PLAYER 1
COORDINATES OF CHOMP (ROW,COLUMN) ? 2,1


        1  2  3  4  5  6  7  8  9
1       P  *  *  *  *  *  *  *  *  
2       








PLAYER 2
COORDINATES OF CHOMP (ROW,COLUMN) ? 1,2


        1  2  3  4  5  6  7  8  9
1       P  









PLAYER 1
COORDINATES OF CHOMP (ROW,COLUMN) ? 1,1

YOU LOSE, PLAYER 1

AGAIN (1=YES, 0=NO!) ? 0


: ^D
```

## References

- [Dr. Dobb's Journal of Computer Calisthenics & Orthodontia, Vol. 1, No. 1](https://archive.org/details/dr_dobbs_journal_vol_01)
