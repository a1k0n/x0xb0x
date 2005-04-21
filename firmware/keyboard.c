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

#include <avr/io.h>
#include <avr/interrupt.h>
#include "main.h"
#include "synth.h"
#include "delay.h"
#include "led.h"
#include "midi.h"
#include "switch.h"

extern uint8_t bank;
extern uint8_t function;
#define function_changed (function != KEYBOARD_MODE_FUNC)

// table from notes (C = 0, C' = 12) to note keys
const static uint8_t notekey_tab[13] = {
  KEY_C,
  KEY_CS,
  KEY_D,
  KEY_DS,
  KEY_E,
  KEY_F,
  KEY_FS,
  KEY_G,
  KEY_GS,
  KEY_A,
  KEY_AS,
  KEY_B,
  KEY_C2
};


void do_keyboard_mode(void) {
  signed int shift = 0;
  uint8_t accent=0, slide=0;
  uint8_t i, midi_addr, last_bank;
  
  // turn tempo off!
  turn_off_tempo();
    
  // show the current MIDI address
  midi_addr = get_midi_addr();
  clear_bank_leds();
  set_bank_led(midi_addr);

  last_bank = bank;

  while (1) {
    read_switches();

    if (function_changed) {
      midi_notesoff();           // turn all notes off
      return;
    }

    if (has_bank_knob_changed()) {
      // bank knob was changed, check if it was going up or down
      if (last_bank == (bank+1)%16) {
	if (midi_addr != 0)
	  midi_addr--;
      } else {
	if (midi_addr != 14)
	  midi_addr++;
      }
      // set the new midi address (burn to EEPROM) and display
      set_midi_addr(midi_addr);
      clear_bank_leds();
      set_bank_led(midi_addr);

      last_bank = bank;
    }

    // show the octave
    display_octave_shift(shift);

    for (i=0; i<13; i++) {
      // check if any notes were just pressed
      if (just_pressed(notekey_tab[i])) {
	note_on((C2+i) + shift*OCTAVE, slide, accent);
	midi_send_note_on( ((C2+i) + shift*OCTAVE) | (accent << 6));
	slide = TRUE;
      }
      
      // check if any notes were released
      if (just_released(notekey_tab[i])) {
	midi_send_note_off( ((C2+i) + shift*OCTAVE) | (accent << 6));
      }
    }



    if (just_pressed(KEY_UP)) {
      if (shift < 1)
	shift++;
    } else if (just_pressed(KEY_DOWN)) {
      if (shift > -1)
	shift--;
    } 

    // check if they turned accent on
    if (just_pressed(KEY_ACCENT)) {
      accent = !accent;
      if (accent)
	set_led(LED_ACCENT);
      else
	clear_led(LED_ACCENT);
    }
    
    // if no keys are held down and there was a note just playing
    // turn off the note.
    if ((NOTE_PIN & 0x3F) && no_keys_pressed()) {
      note_off(0);
      slide = FALSE;
    }

  }
}
