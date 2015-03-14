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
#   For example, if (in templateFile.cpp) we substitute SUBSTITUTION_POINT with 'lvalRef(var)', where var is an integer
#   variable and lval is the following function template:
#
#      template<typename T>
#      void lvalRef(T& x) { whatTheHellAreYou(x); }
#
#   then when we compile it with 'gcc -std=c++ templatefile.cpp', gcc will print the following (cryptic) error messages:
#
#       ./templateFile.cpp: In instantiation of 'void lvalRef(T&) [with T = int]':
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
substitutions = [
                 "whatTheHellAreYou( var )",
                 "whatTheHellAreYou( constVar )",
                 "whatTheHellAreYou( reference )",
                 "whatTheHellAreYou( constReference )",
                 "whatTheHellAreYou( 42 )",
                 "",
                 "lvalRef( var )",
                 "lvalRef( constVar )",
                 "lvalRef( reference )",
                 "lvalRef( constReference )",
                 "lvalRef( 42 )",
                 "",
                 "lvalConstRef( var )",
                 "lvalConstRef( constVar )",
                 "lvalConstRef( reference )",
                 "lvalConstRef( constReference )",
                 "lvalConstRef( 42 )",
                 "",
                 "rvalRef( var )",
                 "rvalRef( constVar )",
                 "rvalRef( reference )",
                 "rvalRef( constReference )",
                 "rvalRef( 42 )",
                 ""
                 #"whatTheHellAreYou( auto_var )",
                 #"whatTheHellAreYou( auto_constVar )",
                 #"whatTheHellAreYou( auto_reference )",
                 #"whatTheHellAreYou( auto_constReference )",
                 #"",
                 #"whatTheHellAreYou( auto_ref_var )",
                 #"whatTheHellAreYou( auto_ref_constVar )",
                 #"whatTheHellAreYou( auto_ref_reference )",
                 #"whatTheHellAreYou( auto_ref_constReference )",
                 #"",
                 #"whatTheHellAreYou( auto_cref_var )",
                 #"whatTheHellAreYou( auto_cref_constVar )",
                 #"whatTheHellAreYou( auto_cref_reference )",
                 #"whatTheHellAreYou( auto_cref_constReference )"
                 #"",
                 #"whatTheHellAreYou( array )",
                 #"justVal( array )",
                 #"lval( array )",
                 #"" ,
                 #"whatTheHellAreYou( initList )",
                 #"justVal( initList )",
                 #"lval( initList )",
                 #"" ,
                 #"whatTheHellAreYou( fcn )",
                 #"justVal( fcn )",
                 #"lval( fcn )",
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
typeColWidth = 30;
colHeader0 = "SUBSTITUTION"
colHeader1 = "type of T"
colHeader2 = "type of expr"
col0SpaceAfterLabel = subColWidth  - len(colHeader0)
col1SpaceAfterLabel = typeColWidth - len(colHeader1)
col2SpaceAfterLabel = typeColWidth - len(colHeader2)
tableFormat = " | %%-%ds | %%-%ds | %%-%ds |" % (subColWidth, typeColWidth, typeColWidth)

print " .%s%s," % ("-" * (subColWidth), "-" * (typeColWidth*2+8))
print " | %s%s | %s%s | %s%s |" % (
     colHeader0, " " * col0SpaceAfterLabel,
     colHeader1, " " * col1SpaceAfterLabel,
     colHeader2, " " * col2SpaceAfterLabel)
print " |%s|" % ("-" * (subColWidth + typeColWidth*2 + 8))


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
print " `%s%s'" % ("-" * (subColWidth), "-" * (typeColWidth*2+8))
