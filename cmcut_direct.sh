export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
EFFT=$3
ALLOWED_MARGIN=10
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
pyenv activate analysis
cd $(dirname $0)
if [ -e $2 ]
then
	python3 cmcut_direct.py $1 $2 > tmp.sh
	RES=`tail -1 tmp.sh|awk -F '#' '{print int($2)}'`
	DIFF=$((RES-EFFT)) 
	if [ $DIFF -gt -$ALLOWED_MARGIN -a $DIFF -lt $ALLOWED_MARGIN ]
	then
		echo "#$EFFT" >> tmp.sh
		echo "#!/bin/bash"
		cat tmp.sh
	else
		echo "#!/bin/bash"
		python3 cmcut_default.py $1
		echo "#$EFFT"
	fi
else
	echo "#!/bin/bash"
	python3 cmcut_default.py $1
	echo "#$EFFT"
fi
