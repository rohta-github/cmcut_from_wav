export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
pyenv activate analysis
if [ -e $2 ]
then
	python3 src/cmcut_direct.py $1 $2
else
	python3 src/cmcut_default.py $1
fi
