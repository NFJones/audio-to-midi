recursivepydoc(){
    for d in *; do
    if [ -d $d ]; then
        (cd $d; recursivepydoc)
    fi
    pydoc -w *.py
    done
}

recursivepydoc