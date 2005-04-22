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
#include <avr/interrupt.h>
#include "pattern.h"
#include "switch.h"
#include "led.h"
#include "main.h"
#include "synth.h"
#include "delay.h"
#include "dinsync.h"
#include "midi.h"

extern uint8_t function, bank;

extern uint8_t sync;

extern volatile uint8_t note_counter;
extern volatile uint8_t dinsync_counter;
extern volatile int16_t dinsync_clocked, midisync_clocked;

extern volatile uint8_t curr_pattern_index;
extern uint8_t play_loaded_pattern; // are we playing?
extern volatile uint8_t pattern_buff[PATT_SIZE];    // the 'loaded' pattern buffer

// play a few patterns in sequence...
volatile uint8_t curr_pattern_chain[MAX_PATT_CHAIN];
volatile uint8_t curr_pattern_chain_index;
volatile uint8_t next_pattern_chain[MAX_PATT_CHAIN];
uint8_t buff_pattern_chain[MAX_PATT_CHAIN];
uint8_t buff_patt_chain_len = 0;

extern int8_t curr_pitch_shift;
extern int8_t next_pitch_shift;

uint8_t all_accent = 0;
uint8_t all_slide = 0;
uint8_t all_rest = 0; // all the time

uint8_t curr_bank = 0;
uint8_t next_bank = 0;

uint8_t playing = FALSE;

volatile uint16_t tap_tempo_timer = 0;

// could be MIDISYNC, DINSYNC or SYNCOUT
#define function_changed (function != curr_function)

void do_pattern_play(void) {
  uint8_t i = 0, curr_function;
  uint8_t midi_cmd = 0;
  uint8_t midi_data = 0;

  curr_function = function;

  if (sync == INTERNAL_SYNC)
    turn_on_tempo();
  else {
    turn_off_tempo();
    if (sync == DIN_SYNC) {
      dinsync_set_in();
    } else {
      dinsync_set_out();
    }
  }

  clear_all_leds();
  clear_blinking_leds();
  next_bank = curr_bank = bank;
  next_pattern_chain[0] = curr_pattern_chain[0] = 0;
  next_pattern_chain[1] = curr_pattern_chain[1] = 0xFF;
  set_numkey_led(1);
 
  play_loaded_pattern = FALSE;
  curr_pattern_index = 0;
  curr_pattern_chain_index = 0;
  curr_pitch_shift = next_pitch_shift = 0;

  clear_bank_leds();
  set_bank_led(bank);

  clock_leds();

  while (1) {
    read_switches();

    if (function_changed) {
      playing = 0;

      dinsync_stop();
      midi_stop();
      curr_pitch_shift = next_pitch_shift = 0;
      all_accent = all_rest = all_slide = 0;

      clear_all_leds();
      clear_blinking_leds();
      clock_leds();
      return;
    }

    // detect 'tap tempo' requests by timing between KEY_DONE strikes
    if (just_pressed(KEY_DONE)) {
      if ((tap_tempo_timer < 3334) //  more than 3s between taps = 20BPM
	  && (tap_tempo_timer > 333)) // less than .3ms between taps = 200BPM
	{
	  tap_tempo_timer = 60000UL/tap_tempo_timer; // convert to BPM
	  change_tempo(tap_tempo_timer);
	}
      tap_tempo_timer = 0;
    }

    // start a new chain if just pressed
    if (just_pressed(KEY_CHAIN)) {
      clear_notekey_leds();
      clear_blinking_leds();
      set_led(LED_CHAIN);
      buff_patt_chain_len = 0;  // 'start' to write a new chain
    }

    // releasing the chain key 'finalizes' the chain buffer
    if (just_released(KEY_CHAIN)) {
      for (i=0; i<MAX_PATT_CHAIN; i++)
	next_pattern_chain[i] = buff_pattern_chain[i];

      // if we're not playing something right now, curr = next
      if (!playing) {
	for (i=0; i<MAX_PATT_CHAIN; i++)
	  curr_pattern_chain[i] = next_pattern_chain[i];
	curr_pitch_shift = next_pitch_shift;
	clear_led(LED_UP);
	clear_led(LED_DOWN);
      }

      clear_led(LED_CHAIN);
    }

    if (is_pressed(KEY_CHAIN)) {
      // display the current pattern chain
      for (i=0; i<buff_patt_chain_len; i++) {
	if (buff_pattern_chain[i] >= 8)
	  break;
	set_numkey_led(buff_pattern_chain[i]+1);
      }

      // ok lets add patterns to the buffer chain!
      i = get_lowest_numkey_just_pressed();
      if ((i != 0) && (buff_patt_chain_len < MAX_PATT_CHAIN)) {
	buff_pattern_chain[buff_patt_chain_len++] = i - 1;
	buff_pattern_chain[buff_patt_chain_len] = 0xFF;

	/*
	putstring("buffered pattern chain = ");
	for (i=0; i<MAX_PATT_CHAIN; i++) {
	  if (buff_pattern_chain[i] >= 8)
	    break;
	  putnum_ud(buff_pattern_chain[i]);
	  uart_putchar(' ');
	}
	putstring("\n\r");
	*/

      }
    }
    // if they press U or D, show the current pitch shift and allow pitch shift adjust
    else if (is_pressed(KEY_UP) || is_pressed(KEY_DOWN)) {
      int8_t notekey = get_lowest_notekey_pressed();

      // clear any pattern indicator leds
      if (just_pressed(KEY_UP) || just_pressed(KEY_DOWN)) {
	clear_notekey_leds();
	clear_blinking_leds();
	clear_led(LED_CHAIN);
      }

      // check if they are changing the shift
      if (is_pressed(KEY_UP)) {
	clear_led(LED_DOWN);
	set_led(LED_UP);

	if (notekey != -1) 
	  next_pitch_shift = notekey; 
	if (curr_pitch_shift >= 0) {
	  if (! is_notekey_led_blink(curr_pitch_shift)) {
	    clear_blinking_leds();
	    set_notekey_led_blink(curr_pitch_shift);
	  }
	}
	if (next_pitch_shift != curr_pitch_shift)
	  set_notekey_led(next_pitch_shift);
      } else if (is_pressed(KEY_DOWN)) {
	clear_led(LED_UP);
	set_led(LED_DOWN);

	if (notekey != -1)
	  next_pitch_shift = notekey - OCTAVE;  // invert direction 

	if (curr_pitch_shift <= 0) {
	  if (!is_notekey_led_blink(OCTAVE + curr_pitch_shift)) {
	    clear_blinking_leds();
	    set_notekey_led_blink(OCTAVE + curr_pitch_shift);
	  }
	}
	if (next_pitch_shift != curr_pitch_shift)
	  set_notekey_led(OCTAVE + next_pitch_shift);
      }

      // if not playing something right now,
      // make the pitch shift effective immediately
      if (!playing)
	curr_pitch_shift = next_pitch_shift;      

    } else {
      if (just_released(KEY_UP) || just_released(KEY_DOWN)) {
	// clear any pitch shift indicators
	clear_notekey_leds();
	clear_blinking_leds();
      }

      // if they just pressed a numkey, make a chain thats
      // one pattern long
      i = get_lowest_numkey_pressed();
      if ((i != 0) || has_bank_knob_changed()) {
	if (i != 0) {
	  clear_numkey_leds();
	  next_pattern_chain[0] = i - 1;
	  next_pattern_chain[1] = 0xFF;
	  if (!playing)
	    for (i=0; i<MAX_PATT_CHAIN; i++) 
	      curr_pattern_chain[i] = next_pattern_chain[i];
	} else {
	  next_bank = bank;
	  if (!playing)
	    curr_bank = bank;
	}
	if (!playing) {
	  clear_bank_leds();
	  set_bank_led(bank);
	  curr_pitch_shift = next_pitch_shift;
	}
      }
      
      // indicate current pattern & next pattern & shift 
      if (!chains_equiv(next_pattern_chain, curr_pattern_chain)) {
	if (next_pattern_chain[1] == 0xFF && curr_pattern_chain[1] == 0xFF) {
	  // basically single patterns. current blinks
	  set_numkey_led_blink(curr_pattern_chain[0]+1);
	}

	// otherwise, always just show the next chain in all solid lights
	for (i=0; i<MAX_PATT_CHAIN; i++) {
	  if (next_pattern_chain[i] > 8)
	    break;
	  set_numkey_led(next_pattern_chain[i] + 1);
	}
      } else {
	for (i=0; i<MAX_PATT_CHAIN; i++) {
	  if (curr_pattern_chain[i] > 8)
	    break;
	  if (playing && (curr_pattern_chain[i] == curr_pattern_chain[curr_pattern_chain_index])) {
	    if (! is_numkey_led_blink(curr_pattern_chain[i]+1) ) 
	      {
		clear_numkey_led(curr_pattern_chain[i]+1);
		set_numkey_led_blink(curr_pattern_chain[i]+1); // if playing, current pattern blinks
	      }
	  } else {
	    if (is_numkey_led_blink(curr_pattern_chain[i]+1))
	      clear_blinking_leds();
	    set_numkey_led(curr_pattern_chain[i] + 1);  // all other patterns in chain solid
	  }
	}
      }
      display_curr_pitch_shift_ud();
    }

    
    if (playing)
      {
	// midi sync clock ticks
	if ((sync == MIDI_SYNC) && (midisync_clocked > 0)) {
	  midisync_clocked -= MIDISYNC_PPQ/8;
	  do_tempo();
	  continue;
	}
	// din sync clock ticks
	else if ((sync == DIN_SYNC) && (dinsync_clocked > 0)) {
	  dinsync_clocked -= DINSYNC_PPQ/8;
	  do_tempo();
	  continue;
	}
      }
    



    // if syncing by MIDI, look for midi commands
    if (sync == MIDI_SYNC) {
      midi_cmd = midi_recv_cmd(); // returns 0 if no midi commands waiting
      /*
      // pattern bank/location control via midi
      if ((midi_cmd == MIDI_SONG_SELECT) && midi_getch()) {
	midi_data = midi_getchar(); 
	if (! (midi_data & 0x80))  {
	  next_bank = midi_data / 8; // override the bank!
	  next_pattern_chain[0] = midi_data % 8;
	  next_pattern_chain[1] = 0xFF;
	  clear_numkey_leds();
	  set_numkey_led(next_pattern_chain[0]+1);
	}
      }
      */
    }
    if ( ((sync == INTERNAL_SYNC) && just_pressed(KEY_RS) && playing) ||
	 ((sync == MIDI_SYNC) && (midi_cmd == MIDI_STOP)) ||
	 ((sync == DIN_SYNC) && dinsync_stopped()) ) 
      {
	//putstring("stop\n\r");
	playing = 0;
	play_loaded_pattern = 0;
	note_off(0);
	midi_stop();
	if (sync != DIN_SYNC) 
	  dinsync_stop();

	clear_led(LED_RS);
	clear_blinking_leds();
	clear_bank_leds();
	set_bank_led(bank);
      }
    else if ( ((sync == INTERNAL_SYNC) && just_pressed(KEY_RS) && !playing) ||
	      ((sync == MIDI_SYNC) && 
	       ((midi_cmd == MIDI_START) || (midi_cmd == MIDI_CONTINUE))) ||
	      ((sync == DIN_SYNC) && dinsync_started()) )
      {
	set_led(LED_RS);
	//putstring("start\n\r");

	load_pattern(bank, curr_pattern_chain[0]);
	/*
	  putstring("next pattern (bank ");
	  putnum_ud(bank);
	  putstring(", loc ");
	  putnum_ud(curr_pattern_location);
	  putstring("\n\r");
	*/
	
	// on midisync continue message, continue!
	if (! ((sync == MIDI_SYNC) && (midi_cmd == MIDI_CONTINUE))) {
	  curr_pattern_chain_index = 0;  // index into current chain
	  curr_pattern_index = 0;        // index into current pattern in chain
	}
	
	play_loaded_pattern = 1;
	playing = 1;
	note_counter = 0;
	midisync_clocked = 0;
	dinsync_counter = 0;
	dinsync_clocked = 0;
	midi_putchar(MIDI_START);
	if (sync != DIN_SYNC)
	  dinsync_start();
      } 

    if (just_pressed(KEY_SLIDE)) {
      all_slide = !all_slide;
      if (all_slide)
	set_led(LED_SLIDE);
      else
	clear_led(LED_SLIDE);
    }
    
    if (just_pressed(KEY_ACCENT)) {
      all_accent = !all_accent;
      if (all_accent) 
	set_led(LED_ACCENT);
      else
	clear_led(LED_ACCENT);    
    }
    
    if (just_pressed(KEY_REST)) {
      all_rest = !all_rest;
      if (all_rest) 
	set_led(LED_REST);
      else
	clear_led(LED_REST);
    }
  }
}

uint8_t chains_equiv(volatile uint8_t *chain1, volatile uint8_t *chain2) {
  uint8_t i;
  
  for (i=0; i < MAX_PATT_CHAIN; i++) {
    if (chain1[i] != chain2[i])
      return FALSE;
    if (chain1[i] == 0xFF) 
      return TRUE;
  }
  return TRUE;
}
