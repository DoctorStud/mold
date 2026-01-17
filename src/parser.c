#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdbool.h>
#include "node.h"
#include "parser.h"
#include "engine.h"


char* read_file(const char* path){
    FILE* file = fopen(path, "rb");
    if (!file) {
        fprintf(stderr, "Could not open file \"%s\".\n", path);
        fclose(file);
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
    if(!lexer) return NULL;

    lexer->source = source;
    lexer->current = 0;
    lexer->line = 1;
    lexer->token_count = 0;
    lexer->tokens = NULL;

    return lexer;
}

void free_lexer(Lexer* lexer){
    if (!lexer) return;

    if (lexer->tokens) {
        for (size_t i = 0; i < lexer->token_count; i++) {
            Token* tok = lexer->tokens[i];
            if (tok) {
                free(tok->name);
                free(tok);
            }
        }
    
        free(lexer->tokens);
    }

    free(lexer);
}

Token* create_token(TokenType type, const char * name, size_t position){
    Token* token = malloc(sizeof(Token));
    if(!token) return NULL;

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

char peek(Lexer* lexer)
{
    if (lexer->source[lexer->current] == '\0') return '\0';
    return lexer->source[lexer->current + 1];
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
            case '?':
                size_t start = lexer->current;
                advance(lexer);
                
                char* name = build_name(lexer);
                add_token(create_token(TOK_VAR, name, start), lexer);
                free(name);

                continue;
            case ':':
                add_token(create_token(TOK_DEF, ":", lexer->current), lexer);
                break;
            case '=':
                if (peek(lexer) == '>') {
                    add_token(create_token(TOK_TO, "=>", lexer->current), lexer);
                    advance(lexer);
                } else {
                    add_token(create_token(TOK_NAME, "=", lexer->current), lexer);
                }
                break;
            case '(':
                add_token(create_token(TOK_LPAREN, "(", lexer->current), lexer);
                break;
            case ')':
                add_token(create_token(TOK_RPAREN, ")", lexer->current), lexer);
                break;
            case '{':
                add_token(create_token(TOK_LBRACE, "{", lexer->current), lexer);
                break;
            case '}':
                add_token(create_token(TOK_RBRACE, "}", lexer->current), lexer);
                break;
            case ',':
                add_token(create_token(TOK_COMMA, ",", lexer->current), lexer);
                break;
            case '/':
                if (peek(lexer) == '/') {
                    while(lexer->source[lexer->current] != '\n' && lexer->source[lexer->current] != '\0') { 
                        advance(lexer);
                    }   
                } else {
                    add_token(create_token(TOK_NAME, "/", lexer->current), lexer);
                } 
                break;
            default:
                if (isalnum((unsigned char)c) || c == '_'){
                    size_t start = lexer->current;
                    char* name = build_name(lexer);

                    TokenType type = TOK_NAME;
                    if (strcmp(name, "mold") == 0){
                        type = TOK_MOLD;
                    } else if (strcmp(name, "with") == 0) {
                        type = TOK_WITH;
                    } else if (strcmp(name, "set") == 0) {
                        type = TOK_SET;
                    } else if (strcmp(name, "shape") == 0) {
                        type = TOK_SHAPE;
                    }
                    add_token(create_token(type, name, start), lexer);
                    free(name);

                    continue;
                }
                break;
        }
        advance(lexer);
    }
}

char* build_name(Lexer* lexer) {
    size_t start = lexer->current;
    char c = lexer->source[lexer->current];
    while (isalnum(c) || c == '_') {
        advance(lexer);
        c = lexer->source[lexer->current];
    }

    size_t length = lexer->current - start;
    char* string = malloc(length + 1);
    memcpy(string, &lexer->source[start], length);
    string[length] = '\0';

    return string;
}

Shape* create_shape(char* name, Node* lhs, Node* rhs) {
    Shape* shape = malloc(sizeof(Shape));
    if (!shape) return NULL;

    shape->name = strdup(name);
    shape->lhs = lhs;
    shape->rhs = rhs;

    return shape;
}

void add_shape(Parser* parser, Shape* shape) {
    parser->shape_count++;
    parser->shapes = realloc(parser->shapes, sizeof(Shape*) * parser->shape_count); //TODO: optimize
    parser->shapes[parser->shape_count-1] = shape;
}

void free_shape(Shape* shape){
    if(!shape) return;

    free(shape->name);
    free_node(shape->lhs);
    free_node(shape->rhs);
    free(shape);
}

Statement* create_set(char* name, Node* expr) {
    Statement* statement = malloc(sizeof(Statement));
    if(!statement) return NULL;

    statement->type = STMT_SET;
    statement->name = name ? strdup(name) : NULL;
    statement->expr = expr;
    statement->shape = NULL;

    return statement;
}

Statement* create_mold(char* name, Node* expr, char* shape) {
    Statement* statement = malloc(sizeof(Statement));
    if(!statement) return NULL;

    statement->type = STMT_MOLD;
    statement->name = name ? strdup(name) : NULL;
    statement->expr = expr;

    statement->shape = shape ? strdup(shape) : NULL;

    return statement;
}

void add_statement(Parser* parser, Statement* statement) {
    parser->statement_count++;
    parser->statements = realloc(parser->statements, sizeof(Statement*) * parser->statement_count); //TODO: optimize
    parser->statements[parser->statement_count-1] = statement;
}

void free_statment(Statement* statement) {
    if (!statement) return;

    if(statement->name) free(statement->name);
    if(statement->expr) free_node(statement->expr);
    if(statement->shape) free(statement->shape);

    free(statement);
}

Parser* initialize_parser(Lexer* lexer) {
    Parser* parser = malloc(sizeof(Parser));
    if (!parser) return NULL;

    parser->current_token = 0;

    parser->token_count = lexer->token_count;
    parser->tokens = lexer->tokens;
    lexer->tokens = NULL;
    lexer->token_count = 0;

    parser->shape_count = 0;
    parser->shapes = NULL;

    parser->statement_count = 0;
    parser->statements = NULL;

    return parser;
}


void free_parser(Parser* parser){
    if (!parser) return;

    if (parser->tokens){
        for (size_t i = 0; i < parser->token_count; i++) {
            Token* tok = parser->tokens[i];
            if (tok) {
                free(tok->name);
                free(tok);
            }
        }
        free(parser->tokens);
    }

    if (parser->shapes) {
        for (size_t i = 0; i < parser->shape_count; i++) {
            free_shape(parser->shapes[i]);
        }
    
        free(parser->shapes);
    }

    if (parser->statements) {
        for (size_t i = 0; i < parser->statement_count; i++) {
            free_statment(parser->statements[i]);
        }
        free(parser->statements);
    }

    free(parser);
}

void raise(char* message){
    fprintf(stderr, "[ERROR] %s\n", message);
    exit(EXIT_FAILURE);
}

Token* expect(Parser * parser, TokenType expected_type) {
    if (parser->current_token >= parser->token_count) {
        raise("Token expected");
    }

    Token* token = parser->tokens[parser->current_token];
    
    if(token->type != expected_type){
        raise("Token expected");
    } 
    
    advance_parser(parser);
    return token;
}

bool accept(Parser* parser, TokenType accepted_type) {
    if (parser->current_token >= parser->token_count) return false;
    if (parser->tokens[parser->current_token]->type == accepted_type) {
        advance_parser(parser);
        return true;
    }
    return false;
}

void advance_parser(Parser* parser){
    if (parser->current_token < parser->token_count){
        parser->current_token++;
        return;
    }
    raise("Expected token");
}

void retreat_parser(Parser* parser) { //mmmmm
    if (parser->current_token > 0){
        parser->current_token--;
        return;
    }
}



void parse(Parser* parser) {
    while(parser->current_token < parser->token_count){
        Token* token = parser->tokens[parser->current_token];
        
        switch (token->type) {
            case TOK_SHAPE:
                parse_shape(parser);
                break;
            case TOK_SET:
                parse_set(parser);
                break;
            case TOK_MOLD:
                parse_mold(parser);
                break;
            default:
                advance_parser(parser);
                break;
        }
    }
        

    return;
}


Node* parse_expression(Parser* parser) {
    Node* node = NULL;
    if (accept(parser, TOK_NAME)) {
        char* name = parser->tokens[parser->current_token -1]->name;
        node = create_node(NODE_SYMBOL, name);
        if (accept(parser, TOK_LPAREN)) {
            Node * child = parse_expression(parser);
            add_child(node, child);
            while(accept(parser, TOK_COMMA)){
                Node * child = parse_expression(parser);
                add_child(node, child);
            }
            expect(parser, TOK_RPAREN);
        } else {
            return node;
        }
        
        
    } else if (accept(parser, TOK_VAR)) {
        char* name = parser->tokens[parser->current_token - 1]->name;
        node = create_node(NODE_VARIABLE, name);
    } 

    if (!node){
        raise("Expected token");
    }
    return node;
}

void parse_shape(Parser* parser) {
    advance_parser(parser);
    Token* name_token = expect(parser, TOK_NAME);
    expect(parser, TOK_DEF);
    Node* lhs = parse_expression(parser);
    expect(parser, TOK_TO);
    Node* rhs = parse_expression(parser);
    add_shape(parser, create_shape(name_token->name, lhs, rhs));
}

void parse_set(Parser* parser) {
    advance_parser(parser);
    Token* name_token = expect(parser, TOK_NAME);
    expect(parser, TOK_DEF);
    Node* expr = parse_expression(parser);
    
    add_statement(parser, create_set(name_token->name, expr));
}

void parse_mold(Parser* parser) {
    advance_parser(parser);
    Node* expr = parse_expression(parser);
    expect(parser, TOK_WITH);
    Token* shape = expect(parser, TOK_NAME);
    
    add_statement(parser, create_mold(NULL, expr, shape->name));
}


void run(Parser* parser) {
    for (int i = 0; i < parser->statement_count;i++){
        if (parser->statements[i]->type == STMT_MOLD){
            Statement* mold = parser->statements[i];
            Shape* shape = NULL;
            for (size_t s = 0; s < parser->shape_count; s++){
                if (strcmp(parser->shapes[s]->name, mold->shape) == 0) {
                    shape = parser->shapes[s];
                }
            }

            Match result = {NULL, 0};
            if(match(shape->lhs, mold->expr, &result)) {
                printf ("\nBINDINGS:\n");
                for (int i = 0; i<result.count; i++) {
                    printf("%s -> ", result.bindings[i].var_name);
                    print_node(result.bindings[i].node);
                    printf("\n");
                }
            }

            Node* output = substitute(shape->rhs, &result);
            printf("\nOUTPUT:\n");
            print_node(output);
        } else if (parser->statements[i]->type == STMT_SET) {
        }
    }
}