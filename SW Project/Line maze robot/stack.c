#include <stdio.h>
#include <stdlib.h>

#include "stack.h"

int init_stack(Stack* sp) {
  sp->head = (Node*) malloc(sizeof(Node));
  sp->tail = (Node*) malloc(sizeof(Node));

  sp->head->next = sp->tail;
  sp->tail->next = sp->tail;
  sp->size = 0;
}

int is_stack_empty(Stack* sp) {
  return sp->head->next == 0;
}

int push(Stack* sp, int data) {
  if (sp == NULL) return -1;

  Node* new_node = (Node*) malloc(sizeof(Node));
  if (new_node == NULL) return -1;
  new_node->data = data;

  new_node->next = sp->head->next;
  sp->head->next = new_node;
  sp->size++;

  return 0;
}

int pop(Stack* sp, int* data) {
  if (sp == NULL) return -1;
  if (is_stack_empty(sp) == 1) return -1;

  Node* del = sp->head->next;
  sp->head->next = del->next;
  *data = del->data;
  free(del);

  sp->size--;

  return 0;
}

void print_stack(const Stack* sp, void (*print) (int)) {
  if (sp == NULL) return;

  Node* cur = sp->head->next;

  while(cur != sp->tail) {
    print(cur->data);
    cur = cur->next;
  }
  printf(" \n");

  return;
}

void destroy_stack(Stack* sp) {
  Node* cur = sp->head->next;
  Node* del = cur;

  while(cur != sp->tail) {
    cur = cur->next;
    free(del);
    del = cur;
  }

  free(sp->head);
  free(sp->tail);

  return;
}

