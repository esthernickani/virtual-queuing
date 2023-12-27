from unittest import TestCase
from linkedlist import Node, LinkedList

class LinkedListTestCase(TestCase):
    """test linked list and node class"""
    def test_construction(self):
        """test if a new empty list is created"""
        new_list = LinkedList()

        self.assertEqual(new_list.length, 0)
        self.assertEqual(new_list.head, None)
        self.assertEqual(new_list.tail, None)
    
    def test_make_new_node(self):
        """test a new node is made and the content is accurate"""
        new_node = Node(3)

        self.assertEqual(new_node.data, 3)
        self.assertEqual(new_node.next, None)
    
    def test_insert(self):
        """test inserts for a linked list"""
        new_list = LinkedList()
        node_one = Node(1)
        node_two = Node(2)
        node_three = Node(3)
        
        new_list.insert_at_begin(node_one)
        new_list.insert_at_end(node_two)



        self.assertEqual(node_one.data, 1)
        self.assertEqual(node_two.data, 2)
    
    def test_remove_with_idx(self):
        """test remove for a linked list"""
        new_list = LinkedList()
        node_one = Node(1)
        node_two = Node(2)
        node_three = Node(3)
        node_four = Node(4)

        new_list.insert_at_end(node_one)
        new_list.insert_at_end(node_two)
        new_list.insert_at_end(node_three)
        new_list.insert_at_end(node_four)

        removed_item = new_list.removeAtSpecificIdx(2)

        self.assertEqual(new_list.length, 3)

    def test_remove_first_node(self):
        """test remove for a linked list"""
        new_list = LinkedList()
        node_one = Node(1)
        node_two = Node(2)
        node_three = Node(3)
        node_four = Node(4)
        
        new_list.insert_at_end(node_one)
        new_list.insert_at_end(node_two)
        new_list.insert_at_end(node_three)
        new_list.insert_at_end(node_four)

        new_list.remove_first_node()

        self.assertEqual(new_list.length, 3)




