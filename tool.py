import os
import sys


def list_files():
  current_dir = os.getcwd()
  files_and_folders = os.listdir(current_dir)
  for item in files_and_folders:
    print(item)


def print_all_help():
  print("Pass")


def main():
  if len(sys.argv) == 1:
    print("Usage: tls <command>")
    return
  if sys.argv[1] == "ls":
    list_files()
  else:
    print("Command not recognized")


if __name__ == "__main__":
  main()
