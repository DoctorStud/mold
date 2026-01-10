#ifndef ENGINE_H
#define ENGINE_H

#include "node.h"


typedef struct {
    char* var_name;
    Node* node;
} Binding;

typedef struct {
    Binding* bindings;
    int count;
} Match;

void free_match(Match* result);

void add_binding(Match* result, const char* name, Node* node);
int match(Node* pattern, Node* target, Match* result);

Node* substitute(Node* rhs, Match* result);

#endif