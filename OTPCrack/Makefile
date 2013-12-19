TARGET 		= crack
LIBS 		= -lm -lpthread -O3
CFLAGS 		= -Wall
CC 			= gcc

OBJECTS 	= $(patsubst %.S, %.o, $(wildcard *.S))
OBJECTS    += $(patsubst %.c, %.o, $(wildcard *.c))
HEADERS 	= $(wildcard *.h)

default: $(TARGET)
all: default

%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

%.o: %.S $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

.PRECIOUS: $(TARGET) $(OBJECTS)

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -Wall $(LIBS) -o $@

clean:
	-rm -f *.o
	-rm -f $(TARGET)

.PHONY: default all clean