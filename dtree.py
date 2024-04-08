#!/usr/bin/env python3
import json
import sys
import os

def parse_input():
	if len(sys.argv) < 2:
		q = sys.stdin.read()
		parts = q.split("/")
	else:
		parts = sys.argv[1].split(".")

	if parts == [""]: parts.pop()
	return list(reversed(parts))


#get total fiolename for key and prevenyt doubles
def get_matching_file(head):

	name = None
	cns = set()
	for candidate in os.listdir():
		cn = candidate.split(".")[0] #files only mathc on part before .

		if cn in cns:
			raise KeyError(f"FS collision: {os.abspath(candidate)} collides with existing field name {cn}", file=sys.stderr)

		cns.add(cn)
		if head == cn:
			name = candidate

	if not name:
		raise KeyError(f"Cannot find file corresponding to key '{head}' in directory {os.getcwd()}")

	return name



class Handler():
	def __init__(self, selectorFunc, navigationFunc):
		self.can_nav_key = selectorFunc
		self.nav = navigationFunc



#Executable File handler
executable_handler = Handler(
	lambda key, _, file: os.path.isfile(file) and os.access(file, os.X_OK),
	lambda key, tail, file: os.execv(f"./{file}", [file, ".".join(reversed(tail))]),
)

#JSON File handler

def handle_json(key, tail, file):
	with open(file, "r") as f:
		s = f.read()

	obj = json.loads(s)

	for node in tail:
		obj = obj[node]

	if isinstance(obj, (list, dict)):
		json.dump(obj, sys.stdout)
	else:
		print(obj, end="")
	exit()


json_handler = Handler(
	lambda key, _, file: os.path.isfile(file) and file.rsplit(".")[-1] == "json",
	handle_json,
)

class Handlers():

	#Dir handler
	dir_handler = Handler(
		lambda key, _, file: os.path.isdir(file),
		lambda key, _, file: os.chdir(file),
	)

	#Opaque File handler
	file_handler = Handler(
		lambda key, _, file: os.path.isfile(file),
		lambda key, _, file: handle_emit(file),
	)

	def __init__(self, handlers=[]):

		self.__handlers = handlers
		self.__handlers.append(self.dir_handler)
		self.__handlers.append(self.file_handler)


	def nav(self, nodes):

		key = nodes.pop()
		file = get_matching_file(key)

		for handler in self.__handlers:
			if handler.can_nav_key(key, nodes, file):
				handler.nav(key, nodes, file)
				return

		raise KeyError(f"No handler registered for this kind of file '{file}'")




def handle_emit(file):

	with open(file, "rb") as f:
		sys.stdout.buffer.write(f.read())
		exit()

def run(nodes, handlers):
	while nodes:
		handlers.nav(nodes)

	#we should have ecited or execv await by now
	raise KeyError("Node chain ended")