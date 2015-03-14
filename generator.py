#!/usr/bin/python

# This is a hairbrained script that extracts gcc's error messages in order to generate a pretty table describing
# how template and auto type deduction works in C++11.
#
# This script assumes you have gcc version 4.8.3 installed.  Since this script relies on regexp to extract content
# from gcc's error messages, it's pretty brittle and will likely break with future versions of gcc.  If you've got
# said future version, then then have some fun and update the regexp! :-).
#
#
# More specifically, this script does the following:
#
#    - We have a list of substitutions below in a list called 'substitutions'.
#    - We open the file 'templateFile.cpp', then
#       - for each substitution:
#          - we replace the word SUBSTITUTION_POINT (in templateFile.cpp) with the substitution, then
#          - we compile the substituted code with gcc, then
#          - gcc will fail when it it tries to instantiate the IAmA template (invoked via the whatTheHellAreYou macro).
#             - If the 'whatTheHellAreYou' macro is invoked within a template then we can extract the type T for the
#               template.
#             - Regardless of where 'whatTheHellAreYou' is invoked, we can extract the type of the expression passed to
#               this macro.
#
#   For example, if (in templateFile.cpp) we substitute SUBSTITUTION_POINT with 'lval(value)', then compile it
#   with 'gcc -std=c++ templatefile.cpp', gcc will print the following (cryptic) error messages:
#
#       ./templateFile.cpp: In instantiation of 'void lval(T&) [with T = int]':
#       ./templateFile.cpp:27:15:   required from here
#       ./templateFile.cpp:9:26: error: 'IAmA<int&> blah' has incomplete type
#            IAmA<decltype(expr)> blah;
#                                 ^
#       ./templateFile.cpp:12:19: note: in expansion of macro 'whatTheHellAreYou'
#        void lval(T& x) { whatTheHellAreYou(x); }
#
#   Notice this reveals that the type of T in our call to lval is int, and the type of x (as is passed to the IAmA
#   template) is int&.
#
#   The nice thing this script does for you is repeatedly call gcc with different substitutions, parse the error messages,
#   and then present the results in a table.

import subprocess;
import re;

# Substitutions to make.  Have fun and insert your own:
# Have even more fun, change the code in 'templateFile.cpp'.
substitutions = ["lval( value )",
                 "lval( constValue )",
                 "lval( reference )",
                 "lval( constReference )",
                 "lval( 42 )",
                 "",
                 "lvalConst( value )",
                 "lvalConst( constValue )",
                 "lvalConst( reference )",
                 "lvalConst( constReference )",
                 "lvalConst( 42 )",
                 "",
                 "rval( value)",
                 "rval( constValue)",
                 "rval( reference)",
                 "rval( constReference)",
                 "rval( 42 )",
                 "",
                 "whatTheHellAreYou( auto_value )",
                 "whatTheHellAreYou( auto_constValue )",
                 "whatTheHellAreYou( auto_reference )",
                 "whatTheHellAreYou( auto_constReference )",
                 "whatTheHellAreYou( auto_42 )",
                 "",
                 "whatTheHellAreYou( auto_ref_value )",
                 "whatTheHellAreYou( auto_ref_constValue )",
                 "whatTheHellAreYou( auto_ref_reference )",
                 "whatTheHellAreYou( auto_ref_constReference )",
                 "",
                 "whatTheHellAreYou( auto_cref_value )",
                 "whatTheHellAreYou( auto_cref_constValue )",
                 "whatTheHellAreYou( auto_cref_reference )",
                 "whatTheHellAreYou( auto_cref_constReference )"
                ];

#-------------------------------
# Open templateFile.cpp and print out its contents to the user #
#-------------------------------

inputFile  = open("templateFile.cpp").readlines();
print "recall, our Code is:"
print
print '    ', '     '.join(inputFile)


#-------------------------------
# Print table header                                      
#-------------------------------

subColWidth = len(max(substitutions, key=len)) + 2
print " .%s%s" % ("-" * subColWidth, "------------------------------------------------.")
print " | SUBSTITUTION%s%s" % (" " * (subColWidth - len("SUBSTITUTION")), " |            type of T |         type of expr |")
print " |%s%s" % ("-" * subColWidth, "------------------------------------------------|")
tableFormat = " | %%-%ds | %%20s | %%20s |" % subColWidth

#-------------------------------
# Generate rows of table (one row for each substitution to make)
#-------------------------------
for sub in substitutions:
    # Do a break in the table if sub is an empty string
    if sub == "":
        print tableFormat % ("", "", "")
        continue

    # Open output file, and substitute 'SUBSTITUTION_POINT' with sub
    outputFile = open("generateFile.cpp", 'w');
    for line in inputFile:
        line = line.replace("SUBSTITUTION_POINT", sub + ";");
        outputFile.write(line)
    outputFile.close()

    # Run gcc and capture its error messages
    gccProcess = subprocess.Popen(["gcc", "-std=c++11", "generateFile.cpp"], stderr=subprocess.PIPE);
    output = gccProcess.communicate()[1]

    # Using regexp, get the type for T and the expression passed to the 'whatTheHellAreYou' macro
    tType     = None
    paramType = None
    for line in output.splitlines():
        if tType == None:
            m = re.search(r"\[with T = (.*)\]", line)
            if m:
                tType = m.group(1)

        if paramType == None:
            m = re.search(r"IAmA<(.*)>", line)
            if m:
                paramType = m.group(1)

    # Print the row
    print tableFormat % (sub, tType, paramType)

#-------------------------------
# Print table footer                                      
#-------------------------------
print " `%s%s" % ("-" * subColWidth, "-----------------------------------------------'")
