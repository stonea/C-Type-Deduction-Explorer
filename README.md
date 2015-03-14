# C-Type-Deduction-Explorer
A hacked up Python script to help developers explore and learn C++11's type deduction rules.

Briefly, this tool uses g++ with -std=c++11 to generate the below table.  Each row of the table lists what C++11 will deduce the value of T and x to be when instantiating one of the following templates.  

<pre>
 int        value            = 1;
 const int  constValue       = 2;
 int&       reference        = value;
 const int& constReference   = value;

template<typename T>
void lval(T& x) { whatTheHellAreYou(x); }

template<typename T>
void lvalConst(T const & x) { whatTheHellAreYou(x); }

template<typename T>
void rval(T&& x) { whatTheHellAreYou(x); }
</pre>

For example, if we were to call 'lval(constValue)',  the lval template will be instantiated with the type of T being 'int' and the type of 'x' being const 'int&'.


<pre>
 .-----------------------------------------------------------------------------------------------.
 | SUBSTITUTION                                    |            type of T |         type of expr |
 |-----------------------------------------------------------------------------------------------|
 | lval( value )                                   |                  int |                 int& |
 | lval( constValue )                              |            const int |           const int& |
 | lval( reference )                               |                  int |                 int& |
 | lval( constReference )                          |            const int |           const int& |
 | lval( 42 )                                      |                  int |                 int& |
 |                                                 |                      |                      |
 | lvalConst( value )                              |                  int |           const int& |
 | lvalConst( constValue )                         |                  int |           const int& |
 | lvalConst( reference )                          |                  int |           const int& |
 | lvalConst( constReference )                     |                  int |           const int& |
 | lvalConst( 42 )                                 |                  int |           const int& |
 |                                                 |                      |                      |
 | rval( value)                                    |                 int& |                 int& |
 | rval( constValue)                               |           const int& |           const int& |
 | rval( reference)                                |                 int& |                 int& |
 | rval( constReference)                           |           const int& |           const int& |
 | rval( 42 )                                      |                  int |                int&& |
 |                                                 |                      |                      |
 | whatTheHellAreYou( auto_value )                 |                 None |                  int |
 | whatTheHellAreYou( auto_constValue )            |                 None |                  int |
 | whatTheHellAreYou( auto_reference )             |                 None |                  int |
 | whatTheHellAreYou( auto_constReference )        |                 None |                  int |
 | whatTheHellAreYou( auto_42 )                    |                 None |       decltype(expr) |
 |                                                 |                      |                      |
 | whatTheHellAreYou( auto_ref_value )             |                 None |                 int& |
 | whatTheHellAreYou( auto_ref_constValue )        |                 None |           const int& |
 | whatTheHellAreYou( auto_ref_reference )         |                 None |                 int& |
 | whatTheHellAreYou( auto_ref_constReference )    |                 None |           const int& |
 |                                                 |                      |                      |
 | whatTheHellAreYou( auto_cref_value )            |                 None |           const int& |
 | whatTheHellAreYou( auto_cref_constValue )       |                 None |           const int& |
 | whatTheHellAreYou( auto_cref_reference )        |                 None |           const int& |
 | whatTheHellAreYou( auto_cref_constReference )   |                 None |           const int& |
 `----------------------------------------------------------------------------------------------'
 </pre>
 
This script generates this table by substituting the value in the "SUBSTITUTION" column, in the place marked SUBSTITUTION_POINT in this file: <https://github.com/stonea/C-Type-Deduction-Explorer/blob/master/templateFile.cpp>.  The script runs the file through file is then run through gcc and type information is extracted in gcc's error messages.

# How to Use

To run just execute generator.py.
To modify what to substitute modify the 'substitutions' list.

For more details, read the comments at the top of the generator file <https://github.com/stonea/C-Type-Deduction-Explorer/blob/master/generator.py>.
