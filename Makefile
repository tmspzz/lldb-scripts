.PHONY: install

install:
	cp .lldbinit ~/.lldbinit
	mkdir -p ~/.lldb
	cp -R scripts/. ~/.lldb/
