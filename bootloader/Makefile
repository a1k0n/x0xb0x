# MCU name
MCU = atmega162

# Output format. (can be srec, ihex, binary)
FORMAT = ihex 


# Programming support using avrdude.
AVRDUDE = avrdude

# Programming support using avrdude. Settings and variables.
AVRDUDE_PROGRAMMER = stk500



AVRDUDE_PORT = com1	   # programmer connected to serial device
#AVRDUDE_PORT = lpt1	# programmer connected to parallel port

AVRDUDE_FLAGS = -p $(MCU) -P $(AVRDUDE_PORT) -c $(AVRDUDE_PROGRAMMER)

# Uncomment the following if you want avrdude's erase cycle counter.
# Note that this counter needs to be initialized first using -Yn,
# see avrdude manual.
#AVRDUDE_ERASE += -y

# Uncomment the following if you do /not/ wish a verification to be
# performed after programming the device.
#AVRDUDE_FLAGS += -V

# Increase verbosity level.  Please use this when submitting bug
# reports about avrdude. See <http://savannah.nongnu.org/projects/avrdude> 
# to submit bug reports.
#AVRDUDE_FLAGS += -v -v




# ---------------------------------------------------------------------------

# Define directories, if needed.
DIRAVR = c:/winavr
DIRAVRBIN = $(DIRAVR)/bin
DIRAVRUTILS = $(DIRAVR)/utils/bin
DIRINC = .
DIRLIB = $(DIRAVR)/avr/lib

# Programming support using avrdude.
AVRDUDE = avrdude


# Program the device.  
program:
	$(AVRDUDE) $(AVRDUDE_FLAGS) -u -U lfuse:w:0xff:m -U hfuse:w:0xd4:m -U efuse:w:0xf9:m 
	$(AVRDUDE) $(AVRDUDE_FLAGS) -U flash:w:x0xb0x_boot.hex


verify:
	$(AVRDUDE) $(AVRDUDE_FLAGS) -U flash:v:x0xb0x_full.hex

read:
	$(AVRDUDE) $(AVRDUDE_FLAGS) -U flash:r:x0xb0x_full.hex
