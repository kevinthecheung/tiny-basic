;
;
;  STATEMENT EXECUTOR WRITTEN IN IL (INTERPRETIVE LANGUAGE)
;  THIS IS WRITTEN IN MACROS FOR THE INTEL INTELEC 8/MOD 80
;  SYSTEM USING INTEL'S ASSEMBLER.
;
;  CONTROL SECTION
;
START:	INIT		;INITIALIZE
ERRENT: NLINE		;WRITE A CR-LF
CO:	GETLN		;WRITE PROMPT AND GET A LINE
	TSTL	XEC	;IF NO LINE NUMBER GO EXECUTE IT
	INSRT		;INSERT OR DELETE THE LINE
	IJMP	CO	;LOOP FOR ANOTHER LINE
XEC:	XINIT		;INITIALIZE FOR EXECUTION
;
;
;  STATEMENT EXECUTOR
;
STMT:	TST	S1,'LET'	;CHECK FOR 'LET'
SE1:	TSTV	SE1	;ERROR IF NO VARIABLE!
SE2:	TST	SE2,'='	;ERROR IF NO "="
	ICALL	EXPR	;PUT EXPRESSION ON AESTK
	DONE		;CHECK FOR CR LINE TERMINATOR
	STORE		;PUT VALUE OF EXPRESSION IN ITS CELL
	NXT		;CONTINUE NEXT LINE
;
;
S1:	TST	S3,'GO'	;CHECK FOR 'GO'
	TST	S2,'TO'	;CHECK FOR 'GOTO'
	ICALL	EXPR	;GET THE LABEL
	DONE		;CHECK FOR CR LINE TERMINATOR
	XFER		;DO A 'GOTO' TO THE LABEL
	NXT
;
;
S2:	TST	S2,'SUB'	;CHECK FOR 'GOSUB', FAILURE IS AN ERROR!
	ICALL	EXPR	;PUT EXPRESSION ON AESTK
	DONE		;CHECK FOR CR LINE TERMINATOR
	SAV		;SAVE NEXT LINE NUMBER IN BASIC TEXT
	XFER		;DO A 'GOSUB' TO THE LABEL
	NXT
;
;
S3:	TST	S8,'PRINT'	;CHECK FOR 'PRINT'
S4:	TST	S7,'"'	;CHECK FOR '"' TO BEGIN A STRING
	PRS		;PRINT THE DATA ENCLOSED IN QUOTES
	HOP	S5
S7:	ICALL	EXPR
	PRN
S5:	TST	S6,','	;',' MEANS MORE TO COME
	SPC		;SPACE TO NEXT ZONE
	HOP	S4	;GO BACK FOR MORE
S6:	DONE		;CHECK FOR CR LINE TERMINATOR
	NLINE
	NXT		;CONTINUE NEXT LINE
;
;
S8:	TST	S9,'IF'	;CHECK FOR 'IF'
	ICALL	EXPR	;GET THE FIRST EXPRESSION
	ICALL	RELOP	;GET THE RELATIONAL OPERATOR
	ICALL	EXPR	;GET THE SECOND EXPRESSION
S8A:	TST	S8A,'THEN'	;CHECK FOR 'THEN'
	CMPR		;IF NOT TRUE CONTINUE NEXT LINE
	IJMP	STMT	;IF TRUE PROCESS THE REST OF THIS LINE
;
;
S9:	TST	S12,'INPUT'	;CHECK FOR 'INPUT'
S10:	TSTV	S10	;GET THE VARIABLE'S INDEX
	INNUM		;GET THE NUMBER FROM THE TELETYPE
	STORE		;PUT THE VALUE OF THE VARIABLE IN ITS CELL
	TST	S11,','	;',' MEANS MORE DATA
	HOP	S10
S11:	DONE		;CHECK FOR CR LINE TERMINATOR
	NXT		;CONTINUE NEXT LINE
;
;
S12:	TST	S13,'RETURN'	;CHECK FOR 'RETURN'
	DONE		;CHECK FOR CR LINE TERMINATOR
	RSTR		;RETURN TO CALLER
	NXT
;
;
S13:	TST	S14,'END'	;CHECK FOR 'END'
	FIN		;GO BACK TO CONTROL MODE
;
;
S14:	TST	S15,'LIST'	;CHECK FOR 'LIST'
	DONE		;CHECK FOR CR LINE TERMINATOR
	LST		;TYPE OUT THE BASIC PROGRAM
	NXT		;CONTINUE NEXT LINE
;
;
S15:	TST	S16,'RUN'	;CHECK FOR 'RUN'
	DONE		;CHECK FOR CR LINE TERMINATOR
	IJMP	XEC
;
;
S16:	TST	S16,'CLEAR'	;CHECK FOR 'CLEAR', FAILURE IS AN ERROR!
	IJMP	START	;REINITIALIZE EVERYTHING!
;
;
;
;  INTERPRETIVE LANGUAGE SUBROUTINES
;
EXPR:	TST	E0,'-'	;TEST FOR UNARY '-'
	ICALL	TERM	;PUT TERM ON AESTK
	NEG		;NEGATE VALUE ON AESTK
	HOP	E1	;GO GET A TERM
;
E0:	TST	E01,'+'	;TEST FOR UNARY '+'
E01:	ICALL	TERM	;PUT TERM ON AESTK
E1:	TST	E2,'+'	;TEST FOR ADDITION
	ICALL	TERM	;GET SECOND TERM
	ADD		;PUT SUM OF TERMS ON AESTK
	HOP	E01	;LOOP AROUND FOR MORE
;
E2:	TST	E3,'-'	;TEST FOR SUBTRACTION
	ICALL	TERM	;GET SECOND TERM
	SUB		;PUT DIFFERENCE OF TERMS ON AESTK
	HOP	E1	;LOOP AROUND FOR MORE
;
E3:	RTN		;THIS CAN BE RECURSIVE
;
;
;
TERM:	ICALL	FACT	;GET ONE FACTOR
T0:	TST	T1,'*'	;TEST FOR MULTIPLICATION
	ICALL	FACT	;GET A FACTOR
	MPY		;PUT THE PRODUCT ON AESTK
	HOP	T0	;LOOP AROUND FOR MORE
;
T1:	TST	T2,'/'	;TEST FOR DIVISION
	ICALL	FACT	;GET THE QUOTIENT
	DIV		;PUT QUOTIENT ON AESTK
	HOP	T0	;LOOP FOR MORE
;
T2:	RTN		;RETURN TO CALLER
;
;
;
FACT:	TSTV	F0	;TEST FOR VARIABLE
	IND		;GET INDEX OF THE VARIABLE
	RTN
F0:	TSTN	F1	;TEST FOR NUMBER
	RTN
F1:	TST	F2,'('	;TEST FOR '('
	ICALL	EXPR	;THIS IS A RECURSIVE PROCESS
;
FE1:	TST	FE1,')'	;EVERY '(' HAS TO HAVE A ')'
F2:	RTN
;
;
;
RELOP:	TST	R0,'='	;CHECK FOR '='
	LIT	0	;0 = '='
	RTN
;
R0:	TST	R4,'<'	;CHECK FOR '<'
	TST	R1,'='	;
	LIT	2	;2 = '<='
	RTN
;
R1:	TST	R3,'>'	;CHECK FOR '>'
	LIT	3	;3 = '<>' (ALSO '><')
	RTN
;
R3:	LIT	1	;1 = '<'
	RTN
;
R4:	TST	R4,'>'
	TST	R5,'='
	LIT	5	;5 = '>='
	RTN
;
R5:	TST	R6,'<'
	LIT	3	;3 = '><' (ALSO '<>')
	RTN
;
R6:	LIT	4	;4 = '>'
	RTN
