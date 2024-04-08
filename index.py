#!/usr/bin/env python3
from dtree import *

if __name__ == "__main__":

	nodes = parse_input()
	handlers = Handlers([executable_handler, json_handler])

	run(nodes, handlers)
