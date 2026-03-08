from btree import Btree

tree = Btree(m=3)

# insert keys
for key in [10, 20, 5, 6, 12, 30, 7, 17]:
    tree.insert(key)

print("Initial tree:")
print(tree.dump())

# search example
print("\nSearch path info for key 12:")
print(tree.search(12))

# delete a key
tree.delete(6)

print("\nTree after deleting 6:")
print(tree.dump())