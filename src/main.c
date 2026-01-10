#include <stdio.h>
#include <stdlib.h>
#include "node.h"
#include "engine.h"
#include "parser.h"


int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Not enough arguments provided.");
        return 0;
    }

    //printf("%s\n", argv[1]);
    char* content = read_file(argv[1]);
    printf("%s\n", content);

    Lexer* lexer = initialize_lexer(content);
    tokenize(lexer);

    for (int i = 0; i<lexer->token_count;i++){
        printf("%zu -> %s\n", lexer->tokens[i]->position, lexer->tokens[i]->name);
    }
    
    free_lexer(lexer);
    free(content);

    // Node * lhs = create_node(NODE_SYMBOL, "pair");
    // add_child(lhs, create_node(NODE_VARIABLE, "x"));
    // add_child(lhs, create_node(NODE_VARIABLE, "y"));
    
    // Node * rhs = create_node(NODE_SYMBOL, "pair");
    // add_child(rhs, create_node(NODE_VARIABLE, "y"));
    // add_child(rhs, create_node(NODE_VARIABLE, "x"));

    // printf("\nTRANSFORMATION:\n");
    // print_node(lhs); printf(" => "); print_node(rhs); printf("\n");
    
    // Node * pair = create_node(NODE_SYMBOL, "pair");
    // add_child(pair, create_node(NODE_SYMBOL, "A"));
    // add_child(pair, create_node(NODE_SYMBOL, "B"));
    
    // printf("\nNODE:\n");
    // print_node(pair); printf("\n");

    // Match result = {NULL, 0};
    // if(match(lhs, pair, &result)) {
    //     printf ("\nBINDINGS:\n");
    //     for (int i = 0; i<result.count; i++) {
    //         printf("%s -> ", result.bindings[i].var_name);
    //         print_node(result.bindings[i].node);
    //         printf("\n");
    //     }
    
        
    //     Node* output = substitute(rhs, &result);
    //     printf("\nOUTPUT:\n");
    //     print_node(output);
    
    //     free_match(&result);    
    // }

    return 0;
}