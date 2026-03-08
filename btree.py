"""
B-tree implementation in Python.

This implementation supports:
- insertion
- deletion
- node splitting and promotion
- sibling redistribution (rotation)
- node merging

The tree stores multiple keys per node and maintains balance after updates.
"""


from __future__ import annotations
import json
import math
from typing import List

# Node Class.
class Node():
    def  __init__(self,
                  keys     : List[int]  = None,
                  children : List[Node] = None,
                  parent   : Node = None):
        self.keys = keys if keys is not None else []
        self.children = children if children is not None else []
        self.parent = parent

# B-tree container
class Btree():
    def  __init__(self,
                  m    : int  = None,
                  root : Node = None):
        self.m    = m
        self.root = None

    # DO NOT MODIFY THIS CLASS METHOD.
    def dump(self) -> str:
        def _to_dict(node) -> dict:
            return {
                "k": node.keys,
                "c": [(_to_dict(child) if child is not None else None) for child in node.children]
            }
        if self.root == None:
            dict_repr = {}
        else:
            dict_repr = _to_dict(self.root)
        return json.dumps(dict_repr,indent=2)

    # Insert.
    def insert(self, key: int):
        if self.root is None:
            self.root = Node([key], [None,None], parent=None)
            return 

        #리프 찾아가기 

        current_node = self.root
        #커렌트의 자녀노드가 있으면 
        while current_node.children and current_node.children[0] is not None:
            i = 0 #키를 찾고 
            while i < len(current_node.keys) and key > current_node.keys[i]:
                i += 1 #커렌트 칠드런으로 내려간다.
            current_node = current_node.children[i]

        # 키 삽입
        current_node.keys.append(key)
        current_node.keys.sort()

        # 오버플로우 처리
        while len(current_node.keys) >= self.m:
            sibling = self.find_closest_sibling_with_space(current_node)
            if sibling:
                self.rotate_to_sibling(current_node, sibling)
            else:
                self.split_promote(current_node)
                
                # After split_promote, check if the current node is the root
                if current_node.parent is None:
                    break
                
                # Update the current_node to its parent for the next iteration
                current_node = current_node.parent
        # Delete.


    def delete(self, key: int):
        current_node = self.root

        # Find the node containing the key
        while current_node:
            i = 0
            while i < len(current_node.keys) and key > current_node.keys[i]:
                i += 1

            if i < len(current_node.keys) and current_node.keys[i] == key:
                break  # Key found

            if not current_node.children or len(current_node.children) == 0:
                current_node = None  # Key not found
                break

            current_node = current_node.children[i]

        if current_node is None:
            return  # Key not found

        # Delete the key from leaf node
        if not current_node.children:
            current_node.keys.remove(key)
        else:
            # Find the successor or predecessor and swap
            successor_node = self.find_successor(current_node, i)
            successor_key = successor_node.keys[0]
            current_node.keys[i] = successor_key
            successor_node.keys.remove(successor_key)

        # Handle underflow
        while len(current_node.keys) < math.ceil(self.m / 2) - 1:
            sibling = self.find_closest_sibling_with_extra_keys(current_node)
            if sibling:
                self.rotate_to_sibling(sibling, current_node)  # Note: sibling first for underflow
            else:
                self.merging(current_node)
                current_node = current_node.parent
                if current_node is None:
                    break
        

    # Search
    def search(self,key) -> str:
        current_node = self.root
        result = []

        while current_node:
            i = 0
            while i < len(current_node.keys) and key > current_node.keys[i]:
                i += 1
            
            if i < len(current_node.keys) and key == current_node.keys[i]:
                result.append(current_node.keys[i])  

            result.append(i)

            if current_node.children:
                current_node = current_node.children[i]
            else:
                break  


        return json.dumps(result)
    
    def find_successor(self, node: Node, i: int) -> Node:
        successor_node = node.children[i + 1]
        while successor_node.children is None:
            successor_node = successor_node.children[0]
        return successor_node

    
    def find_closest_sibling_with_space(self, node: Node):
        parent = node.parent
        if not parent:
            return None

        # Check if node is in parent's children list
        if node not in parent.children:
            print(f"Warning: Node {node.keys} is not in parent's children list")
            return None

        i = parent.children.index(node)

        # 왼쪽 형제 확인
        for j in range(i - 1, -1, -1):
            if len(parent.children[j].keys) < self.m - 1:
                return parent.children[j]

        # 오른쪽 형제 확인
        for j in range(i + 1, len(parent.children)):
            if len(parent.children[j].keys) < self.m - 1:
                return parent.children[j]

        return None

    # Helper method to find closest sibling with extra keys for deletion
    def find_closest_sibling_with_extra_keys(self, node: Node):
        parent = node.parent
        if not parent:
            return None

        i = parent.children.index(node)

        # Check left siblings
        for j in range(i - 1, -1, -1):
            if len(parent.children[j].keys) > math.ceil(self.m / 2) - 1:
                return parent.children[j]

        # Check right siblings
        for j in range(i + 1, len(parent.children)):
            if len(parent.children[j].keys) > math.ceil(self.m / 2) - 1:
                return parent.children[j]

        return None



    def rotate_to_sibling(self, node: Node, sibling: Node):
        parent = node.parent
        if not parent or not sibling:  # Check if parent or sibling is None
            return

        # Verify if 'node' is in 'parent.children' before finding its index
        if node not in parent.children:
            print(f"Error: Node {node.keys} is not in parent's children list. Aborting rotation.")
            return

        i = parent.children.index(node)
        sibling_index = parent.children.index(sibling)

        # Rotate with the left sibling.
        if sibling_index < i and sibling.keys:
            while sibling_index < i and sibling and sibling.keys:
                node.keys.insert(0, parent.keys[sibling_index])
                parent.keys[sibling_index] = sibling.keys.pop()

                # Check and adjust children
                if sibling.children and len(node.children) < len(node.keys) + 1:
                    child_to_move = sibling.children.pop()
                    node.children.insert(0, child_to_move)
                    if child_to_move:
                        child_to_move.parent = node

                i -= 1
                sibling_index -= 1
                sibling = parent.children[sibling_index] if sibling_index >= 0 else None

        # Rotate with the right sibling.
        elif sibling_index > i and sibling and sibling.keys:
            while sibling_index > i and sibling and sibling.keys:
                node.keys.append(parent.keys[i])
                parent.keys[i] = sibling.keys.pop(0)

                # Check and adjust children
                if sibling.children and len(node.children) < len(node.keys) + 1:
                    child_to_move = sibling.children.pop(0)
                    node.children.append(child_to_move)
                    if child_to_move:
                        child_to_move.parent = node

                i += 1
                sibling_index += 1
                sibling = parent.children[sibling_index] if sibling_index < len(parent.children) else None
                
    def checking_sibling_insert(self,node:Node):
        if node.parent is None:
            return None
        parent = node.parent
        i = parent.children.index(node)

        # 왼쪽 형제 확인
        if i > 0 and len(parent.children[i - 1].keys) < self.m - 1:
            return parent.children[i - 1]

        # 오른쪽 형제 확인
        elif i < len(parent.children) - 1 and len(parent.children[i + 1].keys) < self.m - 1:
            return parent.children[i + 1]
        
        return None
            
    def checking_sibling_delete(self,node:Node):

        if node.parent is None:
            return None
        parent = node.parent
        i = parent.index(node)
        if i > 0 and len(parent.children[i - 1].keys) > math.ceil(self.m) - 1:
            self.right_rotation(node)

        elif i < len(parent.children) - 1 and len(parent.children[i + 1].keys) < math.ceil(self.m) - 1:
            self.left_rotation(node)
        
        else:
            self.merging(self,node)
    
    def split_promote(self, node: Node):
        middle_idx = len(node.keys) // 2
        middle_key = node.keys[middle_idx]

        left_keys = node.keys[:middle_idx]
        right_keys = node.keys[middle_idx + 1:]

        left_node = Node(keys=left_keys, parent=node.parent)
        right_node = Node(keys=right_keys, parent=node.parent)

        # Split children and assign to left and right nodes
        if node.children and node.children[0] is not None:
            left_node.children = node.children[:middle_idx + 1]
            right_node.children = node.children[middle_idx + 1:]
            for child in left_node.children:
                if child:
                    child.parent = left_node
            for child in right_node.children:
                if child:
                    child.parent = right_node
        else:
            left_node.children = [None] * (len(left_keys) + 1)
            right_node.children = [None] * (len(right_keys) + 1)

        # Promote the middle key to the parent
        if node.parent:
            parent = node.parent
            insert_idx = 0
            while insert_idx < len(parent.keys) and middle_key > parent.keys[insert_idx]:
                insert_idx += 1
            parent.keys.insert(insert_idx, middle_key)

            # Replace the old node with left_node in the parent's children
            parent.children[parent.children.index(node)] = left_node

            # Insert right_node into the parent's children in the correct position
            parent.children.insert(insert_idx + 1, right_node)

            # Ensure the parent's children list is correctly updated
            if len(parent.children) > len(parent.keys) + 1:
                parent.children.pop()

            # Handle parent overflow if necessary
            if len(parent.keys) >= self.m:
                self.split_promote(parent)

        else:  # If node is root
            # Create a new root with the middle_key
            self.root = Node(keys=[middle_key], children=[left_node, right_node])
            left_node.parent = self.root
            right_node.parent = self.root

            # Ensure the new root's children list is correctly updated
            self.root.children = [left_node, right_node]

    def merging(self,node:Node):
        parent = node.parent
        if not parent:
            return
        i = parent.children.index(node)

        if i > 0:
            left_sibling = parent.children[i - 1]
            left_sibling.keys.append(parent.keys.pop(i - 1))
            left_sibling.keys.extend(node.keys)

            if node.children:
                left_sibling.children.extend(node.children)
                for child in node.children:
                    child.parent = left_sibling

            parent.children.pop(i)

        elif i < len(parent.children) - 1:
            right_sibling = parent.children[i + 1]
            node.keys.append(parent.keys.pop(i))

            node.keys.extend(right_sibling.keys)
            if right_sibling.children:
                node.children.extend(right_sibling.children)
                for child in right_sibling.children:
                    child.parent = node

            parent.children.pop(i + 1)

        if len(parent.keys) < math.ceil(self.m / 2) - 1 and parent.parent is not None:
            self.merging(parent)

        elif len(parent.keys) == 0:
            self.root = parent.children[0]
            self.root.parent = None

    

