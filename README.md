# C-Type-Deduction-Explorer
A hacked up Python script to help developers explore and learn C++11's type deduction rules.

Briefly, this tool uses g++ with -std=c++11 to generate the following table:

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
By repeadetly substituting the value in the "SUBSTITUTION" column, in the place marked SUBSTITUTION_POINT in this file:
<https://github.com/stonea/C-Type-Deduction-Explorer/blob/master/templateFile.cpp>.

Too run just execute generator.py.
To modify what to substitute modify the 'substitutions' list.

For more details, read the comments at the top of the generator file <https://github.com/stonea/C-Type-Deduction-Explorer/blob/master/generator.py>.
