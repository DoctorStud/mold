#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include "parser.h"


char* read_file(const char* path){
    FILE* file = fopen(path, "rb");
    if (file == NULL) {
        fprintf(stderr, "Could not open file \"%s\".\n", path);
        exit(74);
    }

    fseek(file, 0L, SEEK_END);
    size_t fileSize = ftell(file);
    rewind(file);

    char* buffer = (char*)malloc(fileSize + 1);
    if (buffer == NULL) {
        fprintf(stderr, "Not enough memory to read \"%s\".\n", path);
        exit(74);
    }

    size_t bytesRead = fread(buffer, sizeof(char), fileSize, file);
    if (bytesRead < fileSize) {
        fprintf(stderr, "Could not read file \"%s\".\n", path);
        exit(74);
    }

    buffer[bytesRead] = '\0';

    fclose(file);
    return buffer;
}

Lexer* initialize_lexer(const char* source) {
    Lexer* lexer = malloc(sizeof(Lexer));
    lexer->source = source;
    lexer->current = 0;
    lexer->line = 1;
    lexer->token_count = 0;
    lexer->tokens = NULL;

    return lexer;
}

void free_lexer(Lexer* lexer){
    if (!lexer) return;

    for (int i = 0; i < lexer->token_count; i++) {
        Token* tok = lexer->tokens[i];
        if (tok) {
            free(tok->name);
            free(tok);
        }
    }

    free(lexer->tokens);
    lexer->tokens = NULL;
    lexer->token_count = 0;

    free(lexer);
}

Token* create_token(TokenType type, const char * name, size_t position){
    Token* token = malloc(sizeof(Token));
    token->type = type;
    token->name = strdup(name); 
    token->position = position;
    return token;
}

void add_token(Token* token, Lexer* lexer){
    lexer->token_count++;
    lexer->tokens = realloc(lexer->tokens, sizeof(Token*) * lexer->token_count); //TODO: optimize
    lexer->tokens[lexer->token_count-1] = token;
}

char peek(Lexer* lexer){
    return lexer->source[lexer->current+1];
}

void advance(Lexer* lexer){
    if(lexer->source[lexer->current] == '\n'){
        lexer->line++;
    }
    lexer->current++;
}

void skip_whitespaces(Lexer* lexer) {
    for (;;) { 
        char c = lexer->source[lexer->current];
        switch (c) {
            case ' ':
            case '\t':
            case '\r':
                advance(lexer);
                break;
            default:
                return; 
        }
    }
}

void tokenize(Lexer* lexer){
    while(lexer->source[lexer->current] != '\0'){
        skip_whitespaces(lexer);
        char c = lexer->source[lexer->current];
        switch (c){
            case ':':
                if (peek(lexer) == '=') {
                    add_token(create_token(TOK_DEF, ":=", lexer->current), lexer);
                    advance(lexer);
                } else{
                    add_token(create_token(TOK_STRING, ":", lexer->current), lexer);
                }
                break;
            case '=':
                add_token(create_token(TOK_EQUAL, "=", lexer->current), lexer);
                break;
            case '(':
                add_token(create_token(TOK_LPAREN, "(", lexer->current), lexer);
                break;
            case ')':
                add_token(create_token(TOK_RPAREN, ")", lexer->current), lexer);
                break;
            case ',':
                add_token(create_token(TOK_COMMA, ",", lexer->current), lexer);
                break;
            default:
                if (isalnum(c) || c == '_'){
                    size_t start = lexer->current;
                    while (isalnum(c) || c == '_') {
                        advance(lexer);
                        c = lexer->source[lexer->current];
                    }

                    size_t length = lexer->current - start;
                    char* string = malloc(length + 1);
                    memcpy(string, &lexer->source[start], length);
                    string[length] = '\0';

                    add_token(create_token(TOK_STRING, string, start), lexer);
                    free(string);

                    continue;
                }
                break;
        }
        advance(lexer);
    }
}