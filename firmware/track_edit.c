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
#include "track.h"
#include "pattern.h"
#include "switch.h"
#include "led.h"
#include "main.h"
#include "eeprom.h"
#include "synth.h"
#include "delay.h"

extern uint8_t function, bank;

volatile uint8_t curr_track_index;
uint8_t play_loaded_track;
uint16_t curr_patt;
uint8_t track_location;
volatile uint16_t track_buff[TRACK_SIZE];

extern volatile uint8_t all_accent, all_slide, all_rest; // all the time
extern int8_t curr_pitch_shift;

extern uint8_t play_loaded_pattern, curr_pattern_index;

uint8_t in_stepwrite_mode, in_run_mode;

extern uint8_t sync;

void do_track_edit(void) {
  uint8_t i, prev_track_index = -1;

  turn_on_tempo();

  // initialize
  track_location = bank;
  in_stepwrite_mode = FALSE;
  in_run_mode = FALSE;
  play_loaded_track = FALSE;
  play_loaded_pattern = FALSE;
  curr_track_index = 0;
  curr_patt = END_OF_TRACK;
  sync = INTERNAL_SYNC;

  track_location = -1;

  clear_bank_leds();
  clear_blinking_leds();

  while (1) {
    read_switches();

    if (function != EDIT_TRACK_FUNC) {
      // oops i guess they want something else, return!
      note_off(0);
      clear_bank_leds();
      clear_key_leds();
      clock_leds();
      turn_off_tempo();
      return;
    }
    
    if (!in_stepwrite_mode && !in_run_mode) {
      // this is when they select which track to edit (1-16)
      if (track_location != bank) {
	track_location = bank;
	load_track(track_location);
	clear_blinking_leds();
      }
      set_bank_led_blink(track_location);  // show the track being edited
    } else {
      if (prev_track_index != curr_track_index) {
	prev_track_index = curr_track_index;
	clear_blinking_leds();
      }
      set_bank_led_blink(curr_track_index);  // show the current position in the edited track
      if (curr_patt == END_OF_TRACK) {
	clear_note_leds();
	set_led(LED_DONE);                   // the 'end of track' (0xFFFF) lights up DONE
      } else {
	clear_led(LED_DONE);                 // make sure DONE isn't on anymore
	set_bank_led((curr_patt >> 3) & 0xF);    // show the bank of the current pattern
	
	// show RAS
	if (curr_patt & TRACK_REST_FLAG)
	  set_led(LED_REST);
	else
	  clear_led(LED_REST);

	if (curr_patt & TRACK_ACCENT_FLAG)
	  set_led(LED_ACCENT);
	else
	  clear_led(LED_ACCENT);

	if (curr_patt & TRACK_SLIDE_FLAG)
	  set_led(LED_SLIDE);
	else
	  clear_led(LED_SLIDE);
      }
    }
    
    if (just_pressed(KEY_STEP) && !in_run_mode) {
      note_off(0);  // if something -was- playing, kill it

      if (in_stepwrite_mode) {
	// step forward in the track
	if (((curr_track_index+1) >= TRACK_SIZE) ||
	    (track_buff[curr_track_index] == END_OF_TRACK))
	  curr_track_index = 0;            // got to the end of the track, loop back to beginning
	else
	  curr_track_index++;
      } else {
	// starting stepwrite mdoe
	start_track_stepwrite_mode();
	curr_track_index = 0;
      }
      
      // grab the current pattern in the track
      curr_patt = track_buff[curr_track_index];
      if (curr_patt == END_OF_TRACK) {
	play_loaded_pattern = FALSE;      // clearly, dont play the pattern if its EOT marker
      } else {
	/*
	  putstring("curr patt = loc "); putnum_ud(curr_patt & 0x7);
	  putstring(" in bank "); putnum_ud(curr_patt>>3 & 0xF);
	  putstring("\n\r");
	*/
	load_pattern((curr_patt >> 3) & 0xF, curr_patt & 0x7);   // grab the pattern from EEPROM
	// get the pattern's RAS & pitch shift
	all_rest = (curr_patt & TRACK_REST_FLAG) >> 8;
	all_accent = (curr_patt & TRACK_ACCENT_FLAG) >> 8;
	all_slide = (curr_patt & TRACK_SLIDE_FLAG) >> 8;
	curr_pitch_shift = get_pitchshift_from_patt(curr_patt);

	curr_pattern_index = 0;                                  // start playing from beginning
	play_loaded_pattern = TRUE;                              // this will tell the tempo interrupt
	                                                         // to start playing the pattern
	clear_notekey_leds();
	clear_bank_leds();
      }
    }

    if (just_pressed(KEY_RS)) {
      if (in_run_mode) {
	// stop run mode
	stop_track_run_mode();
	play_loaded_pattern = FALSE; 
	play_loaded_track = FALSE;
	note_off(0);
      } else {
	// stop stepwrite mode
	if (in_stepwrite_mode) {
	  stop_track_stepwrite_mode();
	  play_loaded_pattern = FALSE; 
	  note_off(0);
	}

	start_track_run_mode();

	if (track_buff[0] == END_OF_TRACK) {
	  play_loaded_pattern = play_loaded_track = FALSE; 
	  // clearly, dont play the track if there aint no data
	} else {
	  // basically tell it to start at the end so its forced to reload the track
	  curr_track_index = -1;
	  curr_pattern_index = PATT_SIZE;
	  curr_patt = 0xFFFF;
	  // get the tempo interrupt to start playing
	  play_loaded_track = TRUE;
	}
      }
    }

    if (just_pressed(KEY_DONE)) {
      if (in_stepwrite_mode) {
	if (curr_track_index+1 < TRACK_SIZE)
	  track_buff[curr_track_index+1] = END_OF_TRACK;         // set an EOT marker if necc.
	curr_patt = END_OF_TRACK;  // cleans up LEDs
	stop_track_stepwrite_mode();                             // stop the mode, and any playing
	play_loaded_pattern = FALSE;
	clear_led(LED_DONE);
      }
      write_track(track_location);                               // and write it to memory
    }
  
    if (in_stepwrite_mode) {
      set_led(LED_STEP);                                         // show we're in this mode
      
      // handle RAS keypresses -> modifications to current pattern
      if (curr_patt != END_OF_TRACK) {
	if (just_pressed(KEY_REST)) {
	  curr_patt = (track_buff[curr_track_index] ^= TRACK_REST_FLAG);
	  all_rest = (curr_patt & TRACK_REST_FLAG) >> 8;
	}
	if (just_pressed(KEY_ACCENT)) {
	  curr_patt = (track_buff[curr_track_index] ^= TRACK_ACCENT_FLAG);
	  all_accent = (curr_patt & TRACK_ACCENT_FLAG) >> 8;
	}
	if (just_pressed(KEY_SLIDE)) {
	  curr_patt = (track_buff[curr_track_index] ^= TRACK_SLIDE_FLAG);
	  all_slide = (curr_patt & TRACK_SLIDE_FLAG) >> 8;
	}
      }

      // handle U/D keypresses -> pitch shifting
      if (is_pressed(KEY_UP) || is_pressed(KEY_DOWN)) {
	uint16_t notekey = get_lowest_notekey_pressed();
	
	if (just_pressed(KEY_UP) || just_pressed(KEY_DOWN)) {
	  clear_blinking_leds();
	  clear_notekey_leds();
	  clear_led(LED_UP);
	  clear_led(LED_DOWN);
	}
	
	if (is_pressed(KEY_UP)) {
	  set_led(LED_UP);
	  
	  if (notekey != -1) {
	    clear_blinking_leds();
	    // set the new pitchshift
	    curr_patt = (curr_patt & 0xE0FF) | (notekey << 8);
	    track_buff[curr_track_index] = curr_patt; 
	  }
	  // display the pitchshift
	  curr_pitch_shift = get_pitchshift_from_patt(curr_patt);
	  set_notekey_led_blink(curr_pitch_shift);
	} else if (is_pressed(KEY_DOWN)) {
	  set_led(LED_DOWN);
	  
	  if (notekey != -1) {
	    clear_blinking_leds();
	    // set the new pitchshift
	    curr_patt = (curr_patt & 0xE0FF) | (((notekey - 12) & 0x1F) << 8);
	    track_buff[curr_track_index] = curr_patt; 
	  }

	  curr_pitch_shift = get_pitchshift_from_patt(curr_patt);
	  set_notekey_led_blink(C3 - C2 + curr_pitch_shift);
	}
      } else {
	if (just_released(KEY_UP) || just_released(KEY_DOWN)) {
	  clear_led(LED_UP);
	  clear_led(LED_DOWN);
	  clear_blinking_leds();
	}

	set_numkey_led((curr_patt & 0x7) +1);    // show the location of the current pattern
	display_curr_pitch_shift_ud();

	// see if they changed the bank / pressed numkey -> change current pattern
	i = get_lowest_numkey_just_pressed();
	if ((i != 0) || has_bank_knob_changed()) {
	  clear_numkey_leds();
	  clear_bank_leds();
	  if (i == 0) {
	    if (curr_patt == END_OF_TRACK)
	      i = 0;
	    else
	      i = curr_patt & 0x7;
	  } else {
	    i--;
	  }
	  note_off(0);
	  curr_patt = (bank << 3) | i;
	  track_buff[curr_track_index] = curr_patt;
	  load_pattern(bank, i);
	  curr_pattern_index = 0;
	  all_rest = all_accent = all_slide = FALSE;
	  curr_pitch_shift = 0;
	  play_loaded_pattern = TRUE;
	}
      }
    }
    
    if (in_run_mode) {
      set_led(LED_RS);
      clear_numkey_leds();
      set_numkey_led((curr_patt & 0x7) +1);    // show the location of the current pattern
      // the tempo interrupt does virtually everything for run mode
      
      // show pitchshift
      display_curr_pitch_shift_ud();
    }
  }
}

int8_t get_pitchshift_from_patt(uint16_t patt) { 
 int8_t shift;

  shift = (patt >> 8) & 0x1F;
  if (shift & 0x10)
    shift |= 0xE0;      // extend signed 5-bit int

  return shift;

}
void display_curr_pitch_shift_ud(void) {
  if (curr_pitch_shift == 0) {
    clear_led(LED_UP);
    clear_led(LED_DOWN);
  } else if (curr_pitch_shift < 0) {
    clear_led(LED_UP);
    set_led(LED_DOWN);
  } else {
    set_led(LED_UP);
    clear_led(LED_DOWN);
  }
}

static void start_track_stepwrite_mode(void) {
  in_stepwrite_mode = TRUE;
}


static void stop_track_stepwrite_mode(void) {
  in_stepwrite_mode = FALSE;
  clear_led(LED_STEP);
  clear_all_leds();
  clear_blinking_leds();
}
 
static void start_track_run_mode(void) {
  in_run_mode = TRUE;
  all_rest = all_slide = all_accent = FALSE;
}

static void stop_track_run_mode(void) {
  in_run_mode = FALSE;   
  clear_all_leds();
  clear_blinking_leds();
}

void load_track(uint8_t track_loc) {
  uint8_t i;
  uint16_t track_addr;

  track_addr = TRACK_MEM + track_loc*TRACK_SIZE*2;
  for (i=0; i < TRACK_SIZE; i++) {
    track_buff[i] = spieeprom_read(track_addr + 2*i) << 8;
    track_buff[i] |= spieeprom_read(track_addr + 2*i + 1);
  }
}

void write_track(uint8_t track_loc) {
  uint8_t i;
  uint16_t track_addr;

  track_addr = TRACK_MEM + track_loc*TRACK_SIZE;  
  for (i=0; i < TRACK_SIZE; i++) {
    spieeprom_write(track_buff[i]>>8, track_addr + 2*i);
    spieeprom_write(track_buff[i] & 0xFF, track_addr + 2*i + 1);
  }
}
