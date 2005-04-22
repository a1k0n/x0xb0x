/* 
 * The software for the x0xb0x is available for use in accordance with the 
 * following open source license (MIT License). For more information about
 * OS licensing, please visit -> http://www.opensource.org/
 *
 * For more information about the x0xb0x project, please visit
 * -> http://www.ladyada.net/make/x0xb0x
 *
 *                                     *****
 * Copyright (c) 2005 Limor Fried
 *
 * Permission is hereby granted, free of charge, to any person obtaining a 
 * copy of this software and associated documentation files (the "Software"), 
 * to deal in the Software without restriction, including without limitation 
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, 
 * and/or sell copies of the Software, and to permit persons to whom the 
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in 
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
 * IN THE SOFTWARE.
 *                                     *****
 *
 */

#include <inttypes.h>
#include <stdio.h>
#include <avr/io.h>
#include "pattern.h"
#include "switch.h"
#include "led.h"
#include "main.h"
#include "compcontrol.h"

extern volatile uint8_t pattern_buff[PATT_SIZE];

extern uint8_t function, bank, switches[3];

#define function_changed (function != COMPUTER_CONTROL_FUNC)

void do_computer_control() {
  char c;
  uint8_t b, pl;

  print_menu();
  do {
    read_switches();
    if (function_changed) {
      // oops i guess they want something else, return!
      clear_all_leds();
      clock_leds();
      return;
    }
    
    if (uart_getch()) {
      c = uart_getchar();
      uart_putchar(c);
      putstring("\n\r");
      switch(c) {
      case 'd': {
	putstring("bank: ");
	b = input_uint8();
	putstring("\n\rloc: ");
	pl = input_uint8();
	load_pattern(b, pl);
	break;
      }
      case 'w': {
	putstring("bank: ");
	b = input_uint8();
	putstring("\n\rloc: ");
	pl = input_uint8();
	for (c=0; c<PATT_SIZE; c++) {
	  putstring("\n\r");
	  putnum_ud(c);
	  putstring("> ");
	  pattern_buff[(uint8_t)c] = input_uint8();
	  if (function_changed)
	    return;
	}
	write_pattern(b, pl); // writes the buffer into memory
	break;
      }
      }
      print_menu();
    }
  } while(1);
}

// read in decimal byte from uart
uint8_t input_uint8() {
  uint8_t i = 0;
  char c;
  
  while (1) {
    read_switches();
    if (function_changed)
      return i;
    if (uart_getch()) {
      c = uart_getchar();
      if (c == '\n' || c == '\r')
	return i;
      if (i > 25)
	continue;
      if (c < '0' || c > '9')
	continue;
      uart_putchar(c);
      i = i*10 + (c - '0');
    }
  }
}





void print_menu(void) {
  putstring("\n\r-------------------\n\rw> Write pattern\n\rp> Play pattern\n\rd> Display pattern\n\r >");
}
  
