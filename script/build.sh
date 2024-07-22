VENV=".venv"

uname_out="$(uname -s)"
case "${uname_out}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    MSYS_NT*)   machine=Git;;
    *)          machine="UNKNOWN:${unameOut}"
esac

if [ "$machine" = "Cygwin" ] || [ "$machine" = "MINGW" ] || [ "$machine" = "MSYS_NT" ]; then
    VENV="$VENV/Scripts/Activate.ps1"
else
    VENV="$VENV/bin/activate"
fi

source "$VENV"

pyinstaller --version 2> /dev/null > /dev/null
[ ! "$?" = "0" ] && pip install pyinstaller

[ ! -d build ] && mkdir build

pyinstaller main.py --onefile --console --name pyshell --add-data "LICENSE:dist/"