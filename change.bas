1 "CHANGE.BAS, from _BASIC Computer Games_ (1978), edited by David H. Ahl."
1 "Reproduced at https://www.atariarchives.org/basicgames/showpage.php?page=39"
1
1 "Adapted for Tiny BASIC in 2020."
1
1 PRINT "","","CHANGE"
2 PRINT "","CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY"
3 PRINT ""
4 PRINT ""
5 PRINT ""
6 PRINT "I, YOUR FRIENDLY MICROCOMPUTER, WILL DETERMINE"
7 PRINT "THE CORRECT CHANGE FOR ITEMS COSTING UP TO $100."
8 PRINT ""
9 PRINT ""
10 PRINT "COST OF ITEM"
11 INPUT A
12 PRINT "AMOUNT OF PAYMENT"
13 INPUT P
20 LET C=P-A
21 LET M=C
22 IF C<>0 THEN GOTO 90
25 PRINT "CORRECT AMOUNT, THANK YOU."
30 GOTO 251
90 IF C>0 THEN GOTO 120
95 PRINT "SORRY, YOU HAVE SHORT-CHANGED ME $",A-P
100 GOTO 10
120 PRINT "YOUR CHANGE, $",C
130 LET D=C/10
140 IF D=0 THEN GOTO 155
150 PRINT D,"TEN DOLLAR BILL(S)"
155 LET C=M-(D*10)
160 LET E=C/5
170 IF E=0 THEN GOTO 185
180 PRINT E,"FIVE DOLLARS BILL(S)"
185 LET C=M-(D*10+E*5)
190 LET F=C
200 IF F=0 THEN GOTO 215
210 PRINT F,"ONE DOLLAR BILL(S)"
215 PRINT "THANK YOU, COME AGAIN."
251 PRINT ""
252 GOTO 10
255 END
