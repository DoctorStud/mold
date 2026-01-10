CC = gcc
CFLAGS = -Wall -Iinclude
TARGET = mold.exe

SRC = $(wildcard src/*.c)

OBJ_DIR = obj
OBJ = $(SRC:src/%.c=$(OBJ_DIR)/%.o)



$(TARGET): $(OBJ)
	$(CC) $(OBJ) -o $(TARGET)


$(OBJ_DIR)/%.o: src/%.c
	mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@


clean:
	rm -rf $(OBJ_DIR)
	rm -f $(TARGET)
