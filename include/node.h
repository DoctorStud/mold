#ifndef NODE_H
#define NODE_H


typedef enum {
    NODE_SYMBOL,
    NODE_VARIABLE
} NodeType;

typedef struct Node {
    NodeType type;
    char* name;
    struct Node** children;
    int child_count;
} Node;

Node* create_node(NodeType type, const char* name);
void add_child(Node* parent, Node* child);
void free_node(Node* node);
void print_node(Node* node);
Node* copy_node(Node* src);

#endif
