#ifndef _STACK_H_
#define _STACK_H_



typedef struct _node {
  int data;
  struct _node* next;
} Node;

typedef struct _stack {
  Node* head;
  Node* tail;
  int size;
} Stack;

extern Stack stack;
extern Stack *sp;


int init_stack(Stack* sp);

int is_stack_empty(Stack* sp);
int pop(Stack* sp, int* data);
void print_stack(const Stack* sp, void (*print) (int));
int push(Stack* sp, int data);
void destroy_stack(Stack* sp);

#endif
