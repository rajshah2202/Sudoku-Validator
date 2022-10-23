figlet Welcome !!
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
echo "This is a simple script to automtically run the program"
echo "Extracting numbers from the file"

python ./src/number_extractor.py
echo "Numbers extracted"

if [ -f "./data/output.txt" ]
then
    gcc ./src/validate_solution.c -w
    ./src/a.out
else
   echo "Error: File not found\n"
fi

figlet Thank You !!
figlet Have a nice day !!

