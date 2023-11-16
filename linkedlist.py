import pdb
"""Linked list class ---> logic for managing a queue"""
class Node:
    def __init__(self, data):
        """Function to create a node"""
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        """Function to create a linked list"""
        self.head = None
        self.tail = None
        self.length = 0

    def insert_at_begin(self, val):
        """insert at beginning of linked list"""
        new_node = Node(val)
        if self.head == None:
            self.head = new_node
            self.tail = new_node
            self.length += 1
            return
        else:
            new_node.next = self.head
            self.head = new_node
            self.length += 1
            return
    
    def remove_first_node(self):
        """remove the first value and return it"""
        removed_item = None

        if self.head == None:
            return
        elif self.head == self.tail:
            removed_item = self.tail.data
            self.tail = None
            self.length = 0
        else:
            removed_item = self.head.data
            self.head = self.head.next
            self.length -= 1

        return removed_item
        
    def removeAtSpecificIdx(self, idx):
        """remove a value at a specific index"""
        if self.head == None:
            return
        
        current_node = self.head
        current_position = 0
        previous_node = None
        removed_item = None


        if current_position == idx:
            self.remove_first_node()
            return 
    
        while current_node != None:
            if current_position == idx:
                break
            previous_node = current_node
            current_node = current_node.next
            current_position += 1

        if current_node != None:
            removed_item = current_node
            previous_node.next = current_node.next
            self.length -= 1
        else:
            print('Index not present')

        return removed_item

    def insert_at_end(self, val):
        """insert at the end of a linked list"""
        new_node = Node(val)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
            self.length += 1
            return
        else:
            self.tail.next = new_node
            self.tail = new_node
        
        self.length += 1
    
    def __repr__(self):
        """return a human readable version of linked list"""
        linked_list_list = []
        if self.head == None and self.tail == None:
            return str(linked_list_list)
        else:
            current_node = self.head
            while current_node:
                linked_list_list.append(current_node.data)
                current_node = current_node.next
        return f"{linked_list_list}"
        