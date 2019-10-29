import sys
import os

class Node:
  def __init__(self, segment):
    self.segment = segment
    self.target = None # If not None, then it's a leaf node
    self.target_type = None
    self.children = {}

  def printNode(self):
    print("Node(segment = %s, target = %s, children = %s)" % (self.segment, self.target, self.children.keys()))

def AddPath(path, target, node):
  # print("path = %s, target = %s, node = %s" % (path, target, node))
  if len(path) == 0:
    node.target = target
    node.target_type = "FILE"
    return

  segment = path[0]
  if segment not in node.children:
    node.children[segment] = Node(segment)

  AddPath(path[1:], target, node.children[segment])

def CheckFileSystem(target, expected_files):
  target_path = '/'.join(target)
  actual_files = os.listdir(target_path)
  actual_files.sort()
  expected_files.sort()
  # print("target = %s, actual_files = %s, expected_files = %s" % (target_path, actual_files, expected_files))
  # print("Result: " + str(actual_files == expected_files))
  return actual_files == expected_files

def TryShrink(node, check_file_system):
  target = node.children.values()[0].target
  if not target:
    return None
  target = target[:-1]

  files = []

  for child in node.children.values():
    if not child.target:
      return None
    if child.segment != child.target[-1]:
      return None
    if child.target[:-1] != target:
      return None
    files.append(child.segment)

  if check_file_system and not CheckFileSystem(target, files):
    return None

  return target

def ShrinkRunfilesTree(node, depth, check_file_system):
  if not node.children:
    return

  for child in node.children.values():
    ShrinkRunfilesTree(child, depth + 1, check_file_system)

  if depth == 0:
    return

  target = TryShrink(node, check_file_system)
  if target:
    node.target = target
    node.target_type = "DIR"
    node.children = {}

def GetNewRunfilesInfo(node, path, result):
  if node.target:
    # print(node.target_type + ": " + "/".join(path) + " " + "/".join(node.target))
    result["TOTAL"] = result["TOTAL"] + 1
    result[node.target_type] = result[node.target_type] + 1
    return
  for segment, child in node.children.items():
    GetNewRunfilesInfo(child, path + [segment], result)

def GetShrunkRunfilesTree(manifest_file, check_file_system = False):
  f = open(manifest_file, "r")
  root = Node("")
  original_runfiles_num = 0
  for line in f:
    line = line.strip()
    link, target = line.split(' ', 1)
    link_path = link.split('/')
    target_path = target.split('/')
    AddPath(link_path, target_path, root)
    original_runfiles_num = original_runfiles_num + 1

  ShrinkRunfilesTree(root, 0, check_file_system)

  result = {"ORI_TOTAL": original_runfiles_num, "TOTAL": 0, "FILE": 0, "DIR": 0}
  GetNewRunfilesInfo(root, [], result)
  return result

def main():
  manifest_file_list_file = open(sys.argv[1], "r")
  for line in manifest_file_list_file:
    line = line.strip()
    info_no_fs_check = GetShrunkRunfilesTree(line, False)
    info_fs_check = GetShrunkRunfilesTree(line, True)
    print("\t".join([line, str(info_no_fs_check["ORI_TOTAL"]), str(info_no_fs_check["TOTAL"]), "", str(info_no_fs_check["FILE"]), "", str(info_no_fs_check["DIR"]), "", str(info_fs_check["TOTAL"]), "", str(info_fs_check["FILE"]), "", str(info_fs_check["DIR"])]))

if __name__ == "__main__":
  main()