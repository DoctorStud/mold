#ifndef PARSER_H
#define PARSER_H

#include "node.h"

typedef enum {
    TOK_VAR,
    TOK_NAME,
    TOK_DEF,
    TOK_EQUAL,
    TOK_LPAREN,
    TOK_RPAREN,
    TOK_COMMA,
    TOK_MOLD,
    TOK_WITH,
    TOK_SHAPE,
    TOK_SET,
    TOK_TO,
    TOK_EOF
} TokenType;

typedef struct {
    TokenType type;
    size_t position;
    char* name;
} Token;

typedef struct {
    const char* source;  
    size_t current; 
    int line;
    size_t token_count;
    Token** tokens;
} Lexer;

typedef struct {
    char* name;
    Node* lhs;
    Node* rhs;
} Shape;

typedef struct {
    size_t token_count;
    Token** tokens;
    size_t current;
    Shape* shapes; 

} Parser;


char* read_file(const char* path);

Lexer* initialize_lexer(const char* source);
void skip_whitespaces(Lexer* lexer);
void advance(Lexer* lexer);
char peek(Lexer* lexer);
void tokenize(Lexer* lexer);
Token* create_token(TokenType type, const char * name, size_t position);
void free_lexer(Lexer* lexer);
void add_token(Token* token, Lexer* lexer);
char* build_name(Lexer* lexer);


#endif