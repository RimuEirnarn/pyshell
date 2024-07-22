## Usahle on Linux/Mac.

all: build

.PHONY: build clean
build:
	sh script/build.sh

clean:
	rm -rf build __pycache__ pyshell.spec
