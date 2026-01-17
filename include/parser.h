#ifndef PARSER_H
#define PARSER_H

#include <stddef.h>
#include <stdbool.h>
#include "node.h"

typedef enum {
    TOK_VAR,
    TOK_NAME,
    TOK_DEF,
    TOK_EQUAL,
    TOK_LPAREN,
    TOK_RPAREN,
    TOK_LBRACE,
    TOK_RBRACE,
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

typedef enum {
    STMT_SET,
    STMT_MOLD
} StatementType;

typedef struct {
    StatementType type;
    char* name;
    Node* expr;
    char* shape;
} Statement;

typedef struct {
    size_t token_count;
    Token** tokens;

    size_t current_token;

    size_t shape_count;
    Shape** shapes;

    size_t statement_count;
    Statement** statements; 

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

Parser* initialize_parser(Lexer* lexer);
void free_parser(Parser* parser);

Shape* create_shape(char* name, Node* lhs, Node* rhs); 
void add_shape(Parser* parser, Shape* shape);
void free_shape(Shape* shape);

Statement* create_set(char* name, Node* expr); //mmmmm
Statement* create_mold(char* name, Node* expr, char* shape);
void add_statement(Parser* parser, Statement* statement);
void free_statment(Statement* statement);

void parse(Parser* parser);
void advance_parser(Parser* parser);
void retreat_parser(Parser* parser);
Token* expect(Parser * parser, TokenType expected_type);
bool accept(Parser* parser, TokenType accepted_type);

Node* parse_expression(Parser* parser);
void parse_shape(Parser* parser);
void parse_set(Parser* parser);
void parse_mold(Parser* parser);



void raise(char* message);

#endif