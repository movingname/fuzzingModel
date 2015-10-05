#include <iostream>
#include <fstream>
#include <stdlib.h>
#include <string.h>
#include "pin.H"
#include <map>


std::map<ADDRINT, UINT32> bbl_count;

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "mypin.out", "specify output file name");

	
VOID docount(ADDRINT addr, UINT32 size){
	
	if(bbl_count.find(addr) == bbl_count.end()){
		bbl_count[addr] = 0;
	}
	bbl_count[addr] += 1;
	
	return;
}	
	
// Pin calls this function every time a new basic block is encountered
// It inserts a call to docount
VOID Trace(TRACE trace, VOID *v)
{
    // Visit every basic block  in the trace
    for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
    {
        // Insert a call to docount for every bbl, passing the number of instructions.
        // IPOINT_ANYWHERE allows Pin to schedule the call anywhere in the bbl to obtain best performance.
        // Use a fast linkage for the call.
        BBL_InsertCall(bbl, IPOINT_ANYWHERE, AFUNPTR(docount), IARG_ADDRINT, BBL_Address(bbl), IARG_UINT32, BBL_Size(bbl), IARG_END);
    }
}

// This function is called when the application exits
VOID Fini(INT32 code, VOID *v)
{
        ofstream OutFile;
        OutFile.open(KnobOutputFile.Value().c_str());
        OutFile.setf(ios::showbase);

        for(std::map<ADDRINT, UINT32>::const_iterator it = bbl_count.begin(); it != bbl_count.end(); ++it)
        {
                OutFile << it->first << ": " << it->second << endl;
        }

        OutFile.close();
}

// argc, argv are the entire command line, including pin -t <toolname> -- ...
int main(int argc, char * argv[])
{
    // Initialize pin
    PIN_Init(argc, argv);

    // Register Instruction to be called to instrument instructions
    TRACE_AddInstrumentFunction(Trace, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 1;
}
