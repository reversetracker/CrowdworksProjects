class TreeNode(object):
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution(object):

    def inorderTraversal(self, root):
        """
        :type root: TreeNode
        :rtype: List[int]
        """
        result = []

        def inorder(node):
            if not node:
                return

            if node.left:
                inorder(node.left)
            result.append(node.val)
            if node.right:
                inorder(node.right)

        inorder(root)
        return result
