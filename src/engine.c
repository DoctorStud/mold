#include "engine.h"
#include <stdlib.h>
#include <string.h>

void add_binding(Match* result, const char* name, Node* node) {
    result->count++;
    result->bindings = realloc(result->bindings, sizeof(Binding) * result->count);
    result->bindings[result->count - 1].var_name = strdup(name);
    result->bindings[result->count - 1].node = node; 
}

int match(Node* pattern, Node* target, Match* result) {
    if (!pattern || !target) return 0;

    switch (pattern -> type) {
        case NODE_VARIABLE:
            add_binding(result, pattern->name, target);
            return 1;
        case NODE_SYMBOL:
            if (strcmp(pattern->name, target->name) != 0) return 0;
            if (pattern->child_count != target->child_count) return 0;

            for (int i = 0; i < pattern->child_count; i++) {
                if (!match(pattern->children[i], target->children[i], result)) {
                    return 0;
                }
            }
            return 1;
        default:
            return 0;
    }
}

Node* substitute(Node* rhs, Match* result) {
    if (!rhs) return NULL;

    switch (rhs->type) {
        case NODE_VARIABLE:
            for (int i = 0; i< result->count; i++){
                if(strcmp(rhs->name, result->bindings[i].var_name) == 0){
                    return copy_node(result->bindings[i].node);
                }
            }
            return NULL;
        case NODE_SYMBOL:
            Node* new_node = create_node(NODE_SYMBOL, rhs->name);
            for (int i = 0; i < rhs->child_count; i++) {
                add_child(new_node, substitute(rhs->children[i], result));
            }
            return new_node;
        
        default:
            return NULL;
    }
}

void free_match(Match* result) {
    if(!result) return;

    for (int i = 0; i < result->count; i++) {
        free(result->bindings[i].var_name);
    }
    free(result->bindings);
    result->bindings = NULL;
    result->count = 0;
}