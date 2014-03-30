recursiverm(){
    for d in *; do
	if [ -d $d ]; then
	    (cd $d; recursiverm)
	fi
	rm *.pyc
	rm *~
    done
}

recursiverm