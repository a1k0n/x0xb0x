; Copyright (C) 2004 Limor Fried
; x0xb0x bootloader

;This program is free software; you can redistribute it and/or modify it under
;the terms of the GNU General Public License as published by the Free Software
;Foundation; either version 2 of the License, or (at your option) any later version.

;This program is distgtributed in the hope that it will be useful, but WITHOUT
;ANY WARRANTY without even the implied warranty of MERCHANTABILITY or FITNESS
;FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

;You should have received a copy of the GNU General Public License along with
;this program; if not, write to the Free Software Foundation, Inc., 59 Temple
;Place, Suite 330, Boston, MA 02111-1307 USA

.include "m162def.inc" 
.equ	FREQ   	= 	16000000    ; in Hz
.equ	WAITSEC =	3         	; in seconds
.equ	BAUD	=	19200		; Baud rate
.equ	UBR		=	FREQ / (16 * BAUD) - 1

;**************** constants

.equ	DevType	=	0xA2	; Device type for ATmega162

.equ	HW_VER	=	0x02
.equ	SW_MAJ_VER	=	0x01
.equ	SW_MIN_VER	=	0x0f

.equ	SB1		=	0x04
.equ	SB2		=	0x94
.equ	SB3		=	0x1e


; for atmega162 (define which uart to use)
.equ	UART_DR		=	UDR1
.equ	UBRRL		=	UBRR1L
.equ 	UCSRA		=	UCSR1A
.equ 	UCSRB		=	UCSR1B

.EQU	MYBOOTSTART 	= 0x1F00		; for atmega162
.equ	ERASE_MAX		= 0x1F00
.equ	USERCODE_RESET 	= 0x0000		; for bootloader-reset atmels (like, everything but the attiny)
;**************** Registers
.def	temp3   =   R21
.def	temp	=	R24	; Temporary register
.def	temp2	=	R25
.def	Delay	=	R17
.def	Delay2	=	R18
.def	char	=	R20		; UART character
.def	DataL	=	R22
.def	DataH	=	R23
.def	AddrL	=	R26     ; also known as register X
.def	AddrH 	= 	R27

.CSEG

.org USERCODE_RESET
 .DB 0xFF, 0xFF


.ORG MYBOOTSTART
BOOTLOADER:	
	ldi		temp, high(RAMEND)
	out		SPH, temp
	ldi		temp, low(RAMEND)
	out		SPL, temp

	ldi		temp, 250
	rcall	DELAY_MS

	; Setup UART 19.2Kbps 
	ldi		temp, UBR
	out		UBRRL, temp
	ldi		temp, (1<<RXEN)|(1<<TXEN)
	out		UCSRB, temp



; see if we have anything to bootload!
; if the spot we use to store the resetvector is 0xFF then go straight to bootloader
	ldi		ZH, high(2*USERCODE_RESET)
	ldi		ZL, low(2*USERCODE_RESET)
	lpm		temp, Z
	cpi		temp, 0xFF
	breq	L_BOOTLOADER

	ldi		temp, 250
	rcall	DELAY_MS


; Check to see if the user selected bootloadmode!
	ldi		temp, 0xC0	; led latch (o), rotary com (o), rot1, rot2, rot4, ro8, tempoa, tempob
	out		DDRA, temp
	ldi		temp, 0x7C	; pullups on rotary1,2,4,8, function knob read
	out		PORTA, temp

	ldi		temp, 250
	rcall	DELAY_MS

	in		temp, PINA 	; read func switches into temp
	andi	temp, (0xF << 2)	; mask off 4 pins (2-5)

	cpi		temp, (0x6  << 2)   ; position #6 is bootload
	breq	L_BOOTLOADER
		
	; ok not bootloading...run the code!
	jmp		USERCODE_RESET

L_BOOTLOADER:
	rcall	UART_RX
	cpi		char, 0x1B
	breq	L_MAINLOOP

HALT:
	rjmp	HALT


L_MAINLOOP:

	rcall	UART_RX
	cpi		char, 0x1B       ; escape char
	breq	L_MAINLOOP

	cpi		char, 'a'
	brne	L_NOT_AUTOINCREMENT
	ldi		char, 'Y'
	rjmp	L_END_SEND_CHAR

L_NOT_AUTOINCREMENT:
	cpi		char, 'A'
	brne	L_NOT_WRITEADDR
	rcall	UART_RX
	mov		AddrH, char
	rcall	UART_RX
	mov		AddrL, char
	lsl		AddrL
	rol		AddrH
	rjmp	L_END_WITH_CR

L_NOT_WRITEADDR:
	cpi		char, 'c'
	brne	L_NOT_WRITEMEM_LOW
	rcall	UART_RX
	mov		DataL, char
	rjmp	L_END_WITH_CR

L_NOT_WRITEMEM_LOW:
	cpi		char, 'C'
	brne	L_NOT_WRITEMEM_HIGH
	rcall	UART_RX
	mov		DataH, char
	movw	ZL, AddrL
	movw	R0, DataL
	ldi		temp, 0x1
	out		SPMCR, temp
	spm
	adiw	AddrL, 2
	rjmp	L_END_WITH_CR

L_NOT_WRITEMEM_HIGH:
	cpi		char, 'e'
	brne	L_NOT_CHIPERASE
	; for (addr=1; addr < ERASE_MAX; addr+= (2*PAGESIZE))
	ldi		AddrL, 1
	clr		AddrH
	rjmp	L_ERASECHIP_TEST
L_ERASECHIP:
	movw	ZL, AddrL
	; wait for spm to finish
L_ERASECHIP_WAIT:
	in		temp, SPMCR
	sbrc	temp, SPMEN
	rjmp	L_ERASECHIP_WAIT

	ldi		temp, 0x3
	out		SPMCR, temp
	spm
	subi	AddrL, low(-2*PAGESIZE)
	sbci	AddrH, high(-2*PAGESIZE)
L_ERASECHIP_TEST:
	ldi		temp, low(2*ERASE_MAX)
	ldi		temp2, high(2*ERASE_MAX)
	cp		AddrL, temp
	cpc		AddrH, temp2
	brlo	L_ERASECHIP
	rjmp	L_END_WITH_CR

L_NOT_CHIPERASE:
	cpi		char, 'm'
	brne	L_NOT_WRITEPAGE
	movw	ZL, AddrL
	ldi		temp, 0x05
	out		SPMCR, temp
	spm
	nop
	rjmp	L_END_WITH_CR

L_NOT_WRITEPAGE:
	cpi		char, 'p'
	brne	L_NOT_PROGTYPE
	ldi		char, 'S'
	rjmp	L_END_SEND_CHAR

L_NOT_PROGTYPE:
	cpi		char, 'R'
	brne	L_NOT_READPROGMEM
	movw	ZL, AddrL
	lpm		temp, Z+
	lpm		char, Z+
	rcall	UART_TX
	movw	AddrL, ZL
	mov		char, temp
	rjmp	L_END_SEND_CHAR

L_NOT_READPROGMEM:
	cpi		char, 'D'
	brne	L_NOT_WRITEEEPROM
	rcall	UART_RX
	out		EEDR, char
	ldi		temp, 0x6
	rcall	EEPROMtalk
	rjmp	L_END_WITH_CR

L_NOT_WRITEEEPROM:
	cpi		char, 'd'
	brne	L_NOT_READEEPROM
	ldi		temp, 0x1
	rcall	EEPROMtalk
	rcall	L_END_SEND_CHAR
	
L_NOT_READEEPROM:
	cpi		char, 'F'
	brne	L_NOT_READFUSE
	clr		ZL
	rjmp	L_END_readFuseAndLock
	
L_NOT_READFUSE:
	cpi		char, 'r'
	brne	L_NOT_READLOCK
	ldi		ZL, 0x1
	rjmp	L_END_readFuseAndLock

L_NOT_READLOCK:
	cpi		char, 'N'
	brne	L_NOT_READFUSE_HIGH
	ldi		ZL, 0x3
L_END_readFuseAndLock:
	rcall	readFuseAndLock
	rjmp	L_END_SEND_CHAR

L_NOT_READFUSE_HIGH:
	cpi		char, 't'
	brne	L_NOT_REQSUPPORTED
	ldi		char, DEVTYPE
	rcall	UART_TX
	clr		char
	rjmp	L_END_SEND_CHAR

L_NOT_REQSUPPORTED:
	cpi		char, 'l'
	breq	L_WRITELOCK
	cpi		char, 'x'
	breq	L_SETLED
	cpi		char, 'y'
	breq	L_CLRLED
	cpi		char, 'T'
	brne	L_NOT_SETDEVTYPE
	rcall	UART_RX
	rjmp	L_END_WITH_CR

L_SETLED:
	rcall	UART_RX
L_WRITELOCK:                ; unsupported?
	rjmp	L_END_WITH_CR

L_CLRLED:
	rcall	UART_RX
	rjmp	L_END_WITH_CR

L_NOT_SETDEVTYPE:
	cpi		char, 'S'
	brne	L_NOT_SOFTID

	ldi		ZL, low(2*SOFT_ID)
	ldi		ZH, high(2*SOFT_ID)
L_SOFTID:
	lpm		char, Z+
	tst		char
	breq	L_END
	rcall	UART_TX
	rjmp	L_SOFTID

L_NOT_SOFTID:
	cpi		char, 'V'
	brne	L_NOT_SOFTVER
	ldi		char, '1'
	rcall	UART_TX
	ldi		char, '2'
	rjmp	L_END_SEND_CHAR	

L_NOT_SOFTVER:
	cpi		char, 's'
	brne	L_NOT_SENDSB
	ldi		char, SB1
	rcall	UART_TX
	ldi		char, SB2
	rcall	UART_TX
	ldi		char, SB3
	rjmp	L_END_SEND_CHAR

L_NOT_SENDSB:
	cpi		char, 'P'
	breq	L_END_WITH_CR
	cpi		char, 'L'
	breq	L_END_WITH_CR


; fast read and write FLASH
	cpi		char, 'z'
	brne	L_NOT_FASTREAD
	; return 1 page
	movw	ZL, AddrL
	ldi		TEMP2, PAGESIZE    ; PAGESIZE words
L_FASTREAD_LOOP:
	lpm		char, Z+
	rcall	UART_TX
	lpm		char, Z+
	rcall	UART_TX
	dec		TEMP2
	brne	L_FASTREAD_LOOP
	movw	AddrL, ZL
	rjmp	L_END

; fast write flash

L_NOT_FASTREAD:
	cpi		char, 'Z'
	brne	L_NOT_FASTWRITE
	movw	ZL, AddrL

; FIXME? make sure ZL < erasemax??

	ldi		temp2, PAGESIZE
L_FASTWRITE_LOOP:
	rcall	UART_RX
	mov		R0, char
	rcall	UART_RX
	mov		R1, char
	ldi		temp, 0x1
	out		SPMCR, temp
	spm
	dec		TEMP2
	breq	L_FASTWRITE_FLUSHPAGE
	adiw	ZL, 2
	rjmp	L_FASTWRITE_LOOP

L_FASTWRITE_FLUSHPAGE:
; write out the page
	ldi		temp, 0x05
	out		SPMCR, temp
	spm
	adiw	ZL, 2
	movw	AddrL, ZL
	rjmp	L_END_WITH_CR


L_NOT_FASTWRITE:
L_ELSE:
	ldi		char, '?'
	rjmp	L_END_SEND_CHAR
L_END_WITH_CR:
	ldi		char, 13
L_END_SEND_CHAR:
	rcall	UART_TX
L_END:
	rjmp	L_MAINLOOP

readFuseAndLock:
	clr		ZH
	ldi		temp, 0x9
	out		SPMCR, temp
	lpm		char, Z
	ret

EEPROMtalk:
	out		EEARL, AddrL
	out		EEARH, AddrH
	adiw	AddrL,1
	sbrc	temp, 1
	sbi		EECR, EEMWE
	out		EECR, temp
L_EEPROM:
	sbic	EECR, EEWE
	rjmp	L_EEPROM
	in		char, EEDR
	ret



; reads a byte in from the UART and put it in register "CHAR"
UART_RX:
	sbis	UCSRA, RXC
	rjmp	UART_RX
	in		char, UART_DR
	ret

; takes a byte in register "CHAR" and sends it on the UART
UART_TX:
	sbis	UCSRA, UDRE
	rjmp	UART_TX
	out		UART_DR, char
	ret


DELAY_MS:
	rcall 	DELAY_1MS
	dec 	TEMP
	brne	DELAY_MS
	ret

DELAY_1MS:
	ldi		DELAY2, FREQ / (1033*6*50)   ; the 1034 is there as a tweak.
L_DELAY2:
	ldi		DELAY, 50
L_DELAY1:            ; this loop takes 3 cycles on avg
	dec		DELAY
	brne	L_DELAY1

	dec		DELAY2
	brne	L_DELAY2
	ret


SOFT_ID: .DB	"x0xb0x1", 0

