# C-Type-Deduction-Explorer
The C++ Type Deduction Explorer is a utility to help programmers learn and
explore how C++11 compilers perform type deduction.  Often the most effective
way to learn a new language feature is to play around with it.  However, trying
to determine how C++11 gives types to expressions, variables, and template
typenames is not always easy.

Programmers can get a string-based representation of an expressions type by
using "`typeid(expr).name()`".  However, the returned string is often cryptic
(with mangled names) or unreliable (C++11 requires that typeid present
information back as though the expression were passed to a template).  In
"Effective Modern C++" Scott Meyers presents a trick that overcomes these
issues by having the compiler produce a compile-time error, which presents type
information back to the user.  However, it can be tedious to repeadely set up
code to produce an error, run the compiler, and extract type information from
the ese error messages.  Luckily the "Type Deduction Explorer" tool eliminates
this tedius task by automating the process for you.

To understand what the Deduction Explorer does, it helps to understand the
trick Scott Meyer Presents in "Effective Modern C++".  I've recreated this
trick as the `whatTheHellAreYou` macro in the following code:

``` c++
template<typename T>
class IAmA;

#define whatTheHellAreYou(expr) \
    IAmA<decltype(expr)> blah;

int main(int argc, char \*argv[]) {
    int x = 42;
    int const & y = x;
    whatTheHellAreYou(y);
}
```

What the macro does is try and instantiate a template that is declared but not
defined.  When the compiler (in this case gcc 4.8.3) fails to instantiate the
undefined template it presents the following error:

'''
./test.cpp: In function ‘int main(int, char\*\*)’:
./test.cpp:6:26: error: aggregate ‘IAmA<const int&> blah’ has incomplete type and cannot be defined
     IAmA<decltype(expr)> blah;
                          ^
./test.cpp:11:5: note: in expansion of macro ‘whatTheHellAreYou’
     whatTheHellAreYou(y);
     ^
'''

The error message reveals that y's type is, as we
expect, a `const int&`.  Things get more interesting when we use
`whatTheHellAreYou` in the context of a template:

``` c++
template<typename T>
void foo(T&& param) {
    whatTheHellAreYou(param);
}

int main(int argc, char \*argv[]) {
    int x = 42;
    int const & y = x;
    foo(y);
}
```

In this context gcc presents the following error:

<pre>
./test.cpp: In instantiation of ‘void foo(T&&) [with T = const int&]’:
./test.cpp:16:10:   required from here
./test.cpp:6:26: error: ‘IAmA<const int&> blah’ has incomplete type
     IAmA<decltype(expr)> blah;
                          ^
./test.cpp:10:5: note: in expansion of macro ‘whatTheHellAreYou’
     whatTheHellAreYou(param);
     ^
</pre>

This message shows that both `T` and `param` are inferred to be `const int&`.

# How the tool helps

Briefly, this tool uses g++ with -std=c++11 to generate the below table.  Each
row of the table lists what C++11 will deduce the value of T and x to be when
instantiating one of the following templates.  

``` c++
 int        var              = 1;
 const int  constValue       = 2;
 int&       reference        = var;
 const int& constReference   = var;

template<typename T>
void lval(T x) { whatTheHellAreYou(x); }

template<typename T>
void lvalRef(T& x) { whatTheHellAreYou(x); }

template<typename T>
void lvalConstRef(T const & x) { whatTheHellAreYou(x); }

template<typename T>
void rvalRef(T&& x) { whatTheHellAreYou(x); }
```

For example, if we were to call 'lvalRef(constValue)',  the lvalRef template will be instantiated with the type of `T` being `int` and the type of `x` being `const int&`.

<pre>
 .---------------------------------------------------------------------------------------------------------,
 | SUBSTITUTION                          | type of T                      | type of expr                   |
 |---------------------------------------------------------------------------------------------------------|
 | whatTheHellAreYou( var )              | None                           | int                            |
 | whatTheHellAreYou( constVar )         | None                           | const int                      |
 | whatTheHellAreYou( reference )        | None                           | int&                           |
 | whatTheHellAreYou( constReference )   | None                           | const int&                     |
 | whatTheHellAreYou( 42 )               | None                           | int                            |
 |                                       |                                |                                |
 | lvalRef( var )                        | int                            | int&                           |
 | lvalRef( constVar )                   | const int                      | const int&                     |
 | lvalRef( reference )                  | int                            | int&                           |
 | lvalRef( constReference )             | const int                      | const int&                     |
 | lvalRef( 42 )                         | int                            | int&                           |
 |                                       |                                |                                |
 | lvalConstRef( var )                   | int                            | const int&                     |
 | lvalConstRef( constVar )              | int                            | const int&                     |
 | lvalConstRef( reference )             | int                            | const int&                     |
 | lvalConstRef( constReference )        | int                            | const int&                     |
 | lvalConstRef( 42 )                    | int                            | const int&                     |
 |                                       |                                |                                |
 | rvalRef( var )                        | int&                           | int&                           |
 | rvalRef( constVar )                   | const int&                     | const int&                     |
 | rvalRef( reference )                  | int&                           | int&                           |
 | rvalRef( constReference )             | const int&                     | const int&                     |
 | rvalRef( 42 )                         | int                            | int&&                          |
 |                                       |                                |                                |
 `---------------------------------------------------------------------------------------------------------'
</pre>
 
This script generates this table by substituting the value in the "SUBSTITUTION" column, in the place marked SUBSTITUTION_POINT in this file: <https://github.com/stonea/C-Type-Deduction-Explorer/blob/master/templateFile.cpp>.  The script runs the file through file is then run through gcc and type information is extracted in gcc's error messages.

# How to Use

* Make sure you have gcc installed.  This tool is known to work with gcc 4.8.3.
* To run just execute `generator.py`
* To modify what is substituted, modify the 'substitutions' list in `generator.py`

For more details, read the comments at the top of the generator file <https://github.com/stonea/C-Type-Deduction-Explorer/blob/master/generator.py>.
