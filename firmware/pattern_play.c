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
#include "track.h"
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

// pattern running info
extern volatile uint8_t curr_pattern_index;
extern volatile uint8_t pattern_buff[PATT_SIZE];    // the 'loaded' pattern buffer
extern uint16_t curr_patt;

// track runnning info
extern volatile uint8_t curr_track_index;
extern volatile uint16_t track_buff[TRACK_SIZE]; // the 'loaded' track buffer

// a chain can either hold patterns or tracks (depending on the mode
volatile uint8_t curr_chain[MAX_CHAIN];
volatile uint8_t curr_chain_index;
volatile uint8_t next_chain[MAX_CHAIN];
uint8_t buff_chain[MAX_CHAIN];
uint8_t buff_chain_len = 0;

// the currently-playing pitch shift and the upcoming pitch shift
extern int8_t curr_pitch_shift;
extern int8_t next_pitch_shift;

extern uint8_t curr_note;

uint8_t all_accent = 0;
uint8_t all_slide = 0;
uint8_t all_rest = 0; // all the time

uint8_t curr_bank = 0;
uint8_t next_bank = 0;

uint8_t playing;

volatile uint16_t tap_tempo_timer = 0;

// could be MIDISYNC, DINSYNC or SYNCOUT
#define function_changed (function != curr_function)

// both pattern and track play are similar enough in function
// (and codespace is small enough) that they're in the same
// function. eek
void do_patterntrack_play(void) {
  uint8_t i = 0, curr_function;
  uint8_t midi_cmd = 0;
  //uint8_t midi_data ;

  curr_function = function;

  if (sync == INTERNAL_SYNC) {
    turn_on_tempo();
  } else {
    turn_off_tempo();
  } 
  if (sync == DIN_SYNC) {
    dinsync_set_in();
  } else {
    dinsync_set_out();
  }

  clear_all_leds();
  clear_blinking_leds();
  next_chain[0] = curr_chain[0] = 0;
  next_chain[1] = curr_chain[1] = 0xFF;
  set_numkey_led(1);
 
  playing = FALSE;

  curr_track_index = 0;
  curr_pattern_index = 0;

  curr_patt = 0;

  curr_chain_index = 0;

  curr_pitch_shift = next_pitch_shift = 0;

  clear_bank_leds();
  if (ANYPATTERNPLAYFUNC)
    next_bank = curr_bank = bank;
  else  // TRACKPLAY
    next_bank = curr_bank = bank % 8;

  set_bank_led(bank);

  while (1) {
    read_switches();

    if (function_changed) {
      playing = FALSE;

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
      buff_chain_len = 0;  // 'start' to write a new chain
    }

    // releasing the chain key 'finalizes' the chain buffer
    if (just_released(KEY_CHAIN)) {
      /*
	putstring("buff'd chain = ");
	for (i=0; i<MAX_CHAIN; i++) {
	  if (buff_chain[i] >= 8)
	    break;
	  putnum_ud(buff_chain[i]);
	  uart_putchar(' ');
	}
	putstring("\n\r");
      */
      for (i=0; i<MAX_CHAIN; i++) {
	next_chain[i] = buff_chain[i];
      }
      // if we're not playing something right now, curr = next
      if (!playing) {
	for (i=0; i<MAX_CHAIN; i++)
	  curr_chain[i] = next_chain[i];
	curr_pitch_shift = next_pitch_shift;
	clear_led(LED_UP);
	clear_led(LED_DOWN);
      }
      clear_led(LED_CHAIN);
    }

    if (is_pressed(KEY_CHAIN)) {
      // display the current chain
      for (i=0; i<buff_chain_len; i++) {
	if (buff_chain[i] >= 8)
	  break;
	set_numkey_led(buff_chain[i]+1);
      }

      // ok lets add patterns/tracks to the buffer chain!
      i = get_lowest_numkey_just_pressed();
      if ((i != 0) && (buff_chain_len < MAX_CHAIN)) {
	buff_chain[buff_chain_len++] = i - 1;
	buff_chain[buff_chain_len] = 0xFF;
	/*
	  putstring("adding: ");
	  putnum_uh(buff_chain[buff_chain_len-1]);
	  putstring("\n\r");
	*/
	/*
	  putstring("buff'd chain = ");
	  for (i=0; i<MAX_CHAIN; i++) {
	  if (buff_chain[i] >= 8)
	  break;
	  putnum_ud(buff_chain[i]);
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
	  buff_chain[0] = next_chain[0] = i - 1;
	  buff_chain[1] = next_chain[1] = 0xFF;
	  
	  if (!playing)
	    for (i=0; i<MAX_CHAIN; i++) 
	      curr_chain[i] = next_chain[i];
	} else {
	  if (ANYPATTERNPLAYFUNC)
	    next_bank = bank;
	  else
	    next_bank = bank%8;

	  if (!playing)
	    curr_bank = next_bank;
	}
	if (!playing) {
	  clear_bank_leds();
	  set_bank_led(next_bank);
	  curr_pitch_shift = next_pitch_shift;
	}
      }
      
      // indicate current pattern & next pattern & shift 
      if (!chains_equiv(next_chain, curr_chain)) {
	if (next_chain[1] == END_OF_CHAIN && curr_chain[1] == END_OF_CHAIN) {
	  // basically single patterns. current blinks
	  set_numkey_led_blink(curr_chain[0]+1);
	}

	// otherwise, always just show the next chain in all solid lights
	for (i=0; i<MAX_CHAIN; i++) {
	  if (next_chain[i] > 8)
	    break;
	  set_numkey_led(next_chain[i] + 1);
	}
      } else {
	for (i=0; i<MAX_CHAIN; i++) {
	  if (curr_chain[i] > 8)
	    break;
	  if (playing && (curr_chain[i] == curr_chain[curr_chain_index])) {
	    if (! is_numkey_led_blink(curr_chain[i]+1) ) 
	      {
		// if playing, current pattern/track blinks
		clear_numkey_led(curr_chain[i]+1);
		set_numkey_led_blink(curr_chain[i]+1); 
	      }
	  } else {
	    // clear old blinking tracks/patterns
	    if (is_numkey_led_blink(curr_chain[i]+1))
	      clear_blinking_leds();
	    // all other patterns in chain solid
	    set_numkey_led(curr_chain[i] + 1); 
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
	playing = FALSE;
	note_off(0);
	midi_stop();
	if (sync != DIN_SYNC) 
	  dinsync_stop();

	clear_led(LED_RS);
	clear_blinking_leds();
	clear_bank_leds();
	if (ANYPATTERNPLAYFUNC)	
	  set_bank_led(bank);
	else
	  set_bank_led(bank % 8);
      }
    else if ( ((sync == INTERNAL_SYNC) && just_pressed(KEY_RS) && !playing) ||
	      ((sync == MIDI_SYNC) && 
	       ((midi_cmd == MIDI_START) || (midi_cmd == MIDI_CONTINUE))) ||
	      ((sync == DIN_SYNC) && dinsync_started()) )
      {
	set_led(LED_RS);
	//putstring("start\n\r");

	if (ANYPATTERNPLAYFUNC)
	  load_pattern(bank, curr_chain[0]);
	else {
	  load_track(bank%8, curr_chain[0]);
	  curr_patt = track_buff[0];
	  load_curr_patt(); // ignore pitch shift returned
	}
	curr_note = REST;
	/*
	  putstring("next pattern (bank ");
	  putnum_ud(bank);
	  putstring(", loc ");
	  putnum_ud(curr_pattern_location);
	  putstring("\n\r");
	*/
	
	// on midisync continue message, continue!
	if (! ((sync == MIDI_SYNC) && (midi_cmd == MIDI_CONTINUE))) {
	  curr_chain_index = 0;  // index into current chain
	  curr_pattern_index = 0;        // index into current pattern in chain
	  curr_track_index = 0;        // index into current pattern in chain
	}
	
	note_counter = 0;
	midisync_clocked = 0;
	dinsync_counter = 0;
	dinsync_clocked = 0;
	playing = TRUE;
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
  
  for (i=0; i < MAX_CHAIN; i++) {
    if (chain1[i] != chain2[i])
      return FALSE;
    if (chain1[i] == 0xFF) 
      return TRUE;
  }
  return TRUE;
}
