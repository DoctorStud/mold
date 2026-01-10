#include "node.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

Node* create_node(NodeType type, const char* name) {
    Node* node = malloc(sizeof(Node));
    if (!node) return NULL;

    node->type = type;
    node->name = strdup(name);
    node->children = NULL;
    node->child_count = 0;
    
    return node;
}

void add_child(Node* parent, Node* child) {
    parent->child_count++;
    parent->children = realloc(parent->children, sizeof(Node*) * parent->child_count);
    parent->children[parent->child_count - 1] = child;
}

void free_node(Node* node) {
    if (!node) return;

    for (int i = 0; i < node->child_count; i++) {
        free_node(node->children[i]);
    }

    free(node->children);

    free(node->name);

    free(node);
}


void print_node(Node* node) {
    if (!node) return;

    printf("%s", node->name);

    if (node->child_count > 0) {
        printf("(");
        for (int i = 0; i < node->child_count; i++) {
            print_node(node->children[i]); 

            if (i < node->child_count - 1) {
                printf(", ");
            }
        }
        printf(")");
    }

}

Node* copy_node(Node* src) {
    if (!src) return NULL;

    Node* new_node = create_node(src->type, src->name);

    for (int i = 0; i < src->child_count; i++) {
        add_child(new_node, copy_node(src->children[i]));
    }

    return new_node;
}