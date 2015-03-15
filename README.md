# The C++ Type Deduction Explorer
The C++ Type Deduction Explorer is a utility to help programmers learn and
explore how C++11 compilers deduce types.  Often the most effective way to
learn a new language feature is to play around with it.  However, by itself
C++11 doesn't make it easy to explore what variables, expressions, and template
typenames are deduced to be.

Although programmers can get a string-based representation of an expression's
type by using `typeid(expr).name()`, this string is often cryptic (with mangled
names) or unreliable (C++11 requires that typeid present information back as
though the expression were passed to a template).  In "Effective Modern C++"
Scott Meyers presents a trick to overcome these issues.  He suggests using an
undefined template to produce a compile-time error that presents type
information back to the user.  The trick works, but it can be tedious to
repeatedly set up code to produce an error, run the compiler, and extract type
information from the error messages.  Luckily the "Type Deduction Explorer"
tool eliminates this tedious task by automating the process for you.

To understand what the Deduction Explorer does, it helps to understand the
trick Scott Meyer Presents in "Effective Modern C++".  I've recreated this
trick as the `whatTheHellAreYou` macro in the following code:

``` c++
template<typename T>
class IAmA;

#define whatTheHellAreYou(expr) \
    IAmA<decltype(expr)> blah;

int main(int argc, char *argv[]) {
    int x = 42;
    int const & y = x;
    whatTheHellAreYou(y);
}
```

What the macro does is try and instantiate a template that is declared but not
defined.  When the compiler (in this case gcc 4.8.3) fails to instantiate the
undefined template it presents the following error:

```
./test.cpp: In function ‘int main(int, char**)’:
./test.cpp:6:26: error: aggregate ‘IAmA<const int&> blah’ has incomplete type and cannot be defined
     IAmA<decltype(expr)> blah;
                          ^
./test.cpp:11:5: note: in expansion of macro ‘whatTheHellAreYou’
     whatTheHellAreYou(y);
     ^
```

The error message reveals that y's type is, as we
expect, a `const int&`.  Things get more interesting when we use
`whatTheHellAreYou` in the context of a template:

``` c++
template<typename T>
void foo(T&& param) {
    whatTheHellAreYou(param);
}

int main(int argc, char *argv[]) {
    int x = 42;
    int const & y = x;
    foo(y);
}
```

In this context gcc presents the following error:

```
./test.cpp: In instantiation of ‘void foo(T&&) [with T = const int&]’:
./test.cpp:16:10:   required from here
./test.cpp:6:26: error: ‘IAmA<const int&> blah’ has incomplete type
     IAmA<decltype(expr)> blah;
                          ^
./test.cpp:10:5: note: in expansion of macro ‘whatTheHellAreYou’
     whatTheHellAreYou(param);
     ^
```

This message shows that both `T` and `param` are inferred to be `const int&`.

# How the tool helps

Briefly, this tool calls g++ with `-std=c++11` and extracts error messages to
generate tables like the one below.  Each row in the following table lists what
C++11 deduces the value of `T` and `x` to be when instantiating one of the
following templates.  

``` c++
 int        var              = 1;
 const int  constValue       = 2;
 int&       reference        = var;
 const int& constReference   = var;

template<typename T>
void lval(T x) { whatTheHellAreYou(x); }

template<typename T>
void lvalConst(T const x) { whatTheHellAreYou(x); }

template<typename T>
void lvalRef(T& x) { whatTheHellAreYou(x); }

template<typename T>
void lvalConstRef(T const & x) { whatTheHellAreYou(x); }

template<typename T>
void rvalRef(T&& x) { whatTheHellAreYou(x); }
```

For example, if we were to call `lvalRef(constVar)`,  the `lvalRef` template
will be instantiated with the type of `T` being `int` and the type of `x` (the
parameter in the template) being `const int&`.

<pre>
 .---------------------------------------------------------------------------,
 | SUBSTITUTION                          | type of T       | type of expr    |
 |---------------------------------------------------------------------------|
 | whatTheHellAreYou( var )              | None            | int             |
 | whatTheHellAreYou( constVar )         | None            | const int       |
 | whatTheHellAreYou( reference )        | None            | int&            |
 | whatTheHellAreYou( constReference )   | None            | const int&      |
 | whatTheHellAreYou( 42 )               | None            | int             |
 |                                       |                 |                 |
 | lvalRef( var )                        | int             | int&            |
 | lvalRef( constVar )                   | const int       | const int&      |
 | lvalRef( reference )                  | int             | int&            |
 | lvalRef( constReference )             | const int       | const int&      |
 | lvalRef( 42 )                         | int             | int&            |
 |                                       |                 |                 |
 | lvalConstRef( var )                   | int             | const int&      |
 | lvalConstRef( constVar )              | int             | const int&      |
 | lvalConstRef( reference )             | int             | const int&      |
 | lvalConstRef( constReference )        | int             | const int&      |
 | lvalConstRef( 42 )                    | int             | const int&      |
 |                                       |                 |                 |
 | rvalRef( var )                        | int&            | int&            |
 | rvalRef( constVar )                   | const int&      | const int&      |
 | rvalRef( reference )                  | int&            | int&            |
 | rvalRef( constReference )             | const int&      | const int&      |
 | rvalRef( 42 )                         | int             | int&&           |
 |                                       |                 |                 |
 '---------------------------------------------------------------------------'
</pre>
 
This script generates this table by substituting the value in the
"SUBSTITUTION" column, in the place marked `SUBSTITUTION_POINT` in this file:
<https://github.com/stonea/C-Type-Deduction-Explorer/blob/master/templateFile.cpp>.
The script runs the generated file through gcc, extracts type
information presented in the error messages, and presents the results to the
user in tabular form.

# How to Use

* Make sure you have gcc installed.  This tool is known to work with gcc 4.8.3.
* To run just execute `generator.py`
* To modify what is substituted, modify the 'substitutions' list in `generator.py`.

For more details, read the comments at the top of the generator file <https://github.com/stonea/C-Type-Deduction-Explorer/blob/master/generator.py>.

---

# So, let's learn some type deduction rules

In this section I use the Deduction Explorer tool to describe how C++11 deduces
types.  For a more complete description refer to Scott Meyers' "Effective
Modern C++".  The information here basically summarizes of the first two items
of the book.

In C++11, there are three different places type deduction occurs:

* In templates
* With `auto`
* With `decltype`

In C++11, decltype simply resolves to the type passed to it.  We'll explorer
the first two of these cases individually:

## Template Type Deduction

Given a template: `template<typename T> void foo(...param-decl...)`.  There are
different forms param-decl might take:

* `template<typename T> void foo(T param)` (without any qualifiers)
* `template<typename T> void foo(T* param)` (a pointer)
* `template<typename T> void foo(T& param)` (an l-value reference)
* `template<typename T> void foo(T&& param)` (a universal reference)

The way template type deduction works differs depending on the form param-decl
takes.  Specifically, whether 

* (1) param-decl is not qualified as either a pointer nor reference, or if
* (2) param-decl is qualified as a pointer or reference type, or if
* (3) param-decl is qualified as a universal reference (i.e. T&&).

So, recall our four templates:

``` c++
template<typename T>
void lval(T x) { whatTheHellAreYou(x); }

template<typename T>
void lvalRef(T& x) { whatTheHellAreYou(x); }

template<typename T>
void lvalConstRef(T const & x) { whatTheHellAreYou(x); }

template<typename T>
void rvalRef(T&& x) { whatTheHellAreYou(x); }
```

and the following variables:
``` c++
 int        var              = 1;
 const int  constValue       = 2;
 int&       reference        = var;
 const int& constReference   = var;
```

In **case 1** (Param-decl is neither a pointer nor reference) we can see that whether a variable is a
const or reference doesn't matter to how `T` is deduced:

```
 .-------------------------------------------------------------------,
 | SUBSTITUTION                  | type of T       | type of expr    |
 |-------------------------------------------------------------------|
 | lval( var )                   | int             | int             |
 | lval( constVar )              | int             | int             |
 | lval( reference )             | int             | int             |
 | lval( constReference )        | int             | int             |
 | lval( 42 )                    | int             | int             |
 |                               |                 |                 |
 | lvalConst( var )              | int             | const int       |
 | lvalConst( constVar )         | int             | const int       |
 | lvalConst( reference )        | int             | const int       |
 | lvalConst( constReference )   | int             | const int       |
 | lvalConst( 42 )               | int             | const int       |
 '-------------------------------------------------------------------'
```

And why should it?  When you pass an argument to a function by value, you make
a copy of it.  Thus the template's parameter can be changed all it wants
without modifying the actual argument.

However, in **case 2** (Param-decl is to a pointer or reference type), `T`
strips the reference of a variable (if there), then to get the type for param
we stick a reference (or pointer) qualifier on.  Notice that 'const' is sticky:
when a const is passed to the template it stays a const in the type of `T` and
the type of `param`.  This make sense.  If we passed a constant-variable to a
template by reference we would be suprised if the template were able to modify
it!

```
 .---------------------------------------------------------------------------,
 | SUBSTITUTION                          | type of T       | type of expr    |
 |---------------------------------------------------------------------------|
 | lvalRef( var )                        | int             | int&            |
 | lvalRef( constVar )                   | const int       | const int&      |
 | lvalRef( reference )                  | int             | int&            |
 | lvalRef( constReference )             | const int       | const int&      |
 | lvalRef( 42 )                         | int             | int&            |
 '---------------------------------------------------------------------------'
```

**Case 3** is a little bit less intuitive, but its critical to understand in
order to understand C++11.  With universal references (see Item 24 in
"Effective Modern C++") if what's passed in is an lvalue then `T` becomes an
lvalue-reference, and if what's passed in is an rvalue `T` becomes an rvalue
reference.  We can see an rvalue reference passed to a template that takes a
universal reference, in the `rvalRef( 42 )` row in the following table.  Also
note that even though var does not have a reference type (it's just an `int`),
T will deduce to the reference `int&`.

``` 
 .-----------------------------------------------------------------,
 | SUBSTITUTION                | type of T       | type of expr    |
 |-----------------------------------------------------------------|
 | rvalRef( var )              | int&            | int&            |
 | rvalRef( constVar )         | const int&      | const int&      |
 | rvalRef( reference )        | int&            | int&            |
 | rvalRef( constReference )   | const int&      | const int&      |
 | rvalRef( 42 )               | int             | int&&           |
 '-----------------------------------------------------------------'
```
 
## Auto Type Deduction

Now, to learn auto type deduction, suppose we have the following variables:

``` c++
int returnInt() { return 42; }
int const returnConstInt() { return 42; }
int& returnRefToInt() { static var = 42; return var; }
int const & returnRefToConstInt()  { static var = 42; return var; }

auto auto_var             = var;                         //            var is an:  int
auto auto_constVar        = constVar;                    //       constVar is an:  int const
auto auto_reference       = reference;                   //      reference is an:  int&
auto auto_constReference  = constReference;              // constReference is an:  int & const

auto& auto_ref_var            = var;                     //            var is an:  int
auto& auto_ref_constVar       = constVar;                //       constVar is an:  int const
auto& auto_ref_reference      = reference;               //      reference is an:  int&
auto& auto_ref_constReference = constReference;          // constReference is an:  int & const

auto const & auto_cref_var            = var;             //            var is an:  int
auto const & auto_cref_constVar       = constVar;        //       constVar is an:  int const
auto const & auto_cref_reference      = reference;       //      reference is an:  int&
auto const & auto_cref_constReference = constReference;  // constReference is an:  int & const

auto&& auto_rref_var            = var;              //            var is an:  int
auto&& auto_rref_constVar       = constVar;         //       constVar is an:  int const
auto&& auto_rref_reference      = reference;        //      reference is an:  int&
auto&& auto_rref_constReference = constReference;   // constReference is an:  int & const
auto&& auto_rref_42             = 42;               
auto&& auto_rref_rvalue_int     = returnInt();
auto&& auto_rref_rvalue_cint    = returnConstInt();
auto&& auto_rref_value_rint     = returnRefToInt();
auto&& auto_rref_value_crint    = returnRefToConstInt();
```

Auto type deduction works like template type deduction.  For auto's that are
not to a pointer, reference, or universal reference type (**case 1**), the deduced type
will have it's 'const' and 'reference' qualifiers stripped away:

```
 .-----------------------------------------------------------,
 | SUBSTITUTION                               | type of expr |
 |-----------------------------------------------------------|
 | whatTheHellAreYou( auto_var )              | int          |
 | whatTheHellAreYou( auto_constVar )         | int          |
 | whatTheHellAreYou( auto_reference )        | int          |
 | whatTheHellAreYou( auto_constReference )   | int          |
 '-----------------------------------------------------------'
```

When we use `auto&` or `auto const&` (**case 2**), we can think of the
reference being removed (if there was one to begin with) and then the
qualifiers on auto being stuck on.

```
 .----------------------------------------------------------------,
 | SUBSTITUTION                                    | type of expr |
 |----------------------------------------------------------------|
 | whatTheHellAreYou( auto_ref_var )               | int&         |
 | whatTheHellAreYou( auto_ref_constVar )          | const int&   |
 | whatTheHellAreYou( auto_ref_reference )         | int&         |
 | whatTheHellAreYou( auto_ref_constReference )    | const int&   |
 |                                                 |              |
 | whatTheHellAreYou( auto_cref_var )              | const int&   |
 | whatTheHellAreYou( auto_cref_constVar )         | const int&   |
 | whatTheHellAreYou( auto_cref_reference )        | const int&   |
 | whatTheHellAreYou( auto_cref_constReference )   | const int&   |
 '----------------------------------------------------------------'
```

In **case 3**, as with template deduction, if what's assigned to auto&& is an l-value,
the resulting type is an l-value reference, and if what's assigned to auto&& is an
r-value, what results is an r-value.

```
 .----------------------------------------------------------------,
 | SUBSTITUTION                                    | type of expr |
 |----------------------------------------------------------------|
 | whatTheHellAreYou( auto_rref_var )              | int&         |
 | whatTheHellAreYou( auto_rref_constVar )         | const int&   |
 | whatTheHellAreYou( auto_rref_reference )        | int&         |
 | whatTheHellAreYou( auto_rref_constReference )   | const int&   |
 | whatTheHellAreYou( auto_rref_42 )               | int&&        |
 | whatTheHellAreYou( auto_rref_rvalue_int )       | int&&        |
 | whatTheHellAreYou( auto_rref_rvalue_cint )      | int&&        |
 | whatTheHellAreYou( auto_rref_value_rint )       | int&         |
 | whatTheHellAreYou( auto_rref_value_crint )      | const int&   |
 '----------------------------------------------------------------'
```

There is one way type deduction of auto differs with type deduction of
templates: when things are enclosed in curly braces.  For auto curly braces
deduce to an initializor list, for templates the braces are an error
(hence we list None in the column):

```
 .---------------------------------------------------------------,
 | SUBSTITUTION                    | type of expr                |
 |---------------------------------------------------------------|
 | whatTheHellAreYou( initList )   | std::initializer_list<int>  |
 | lval( {1,2,3,4,5} )             | None                        |
 | lvalConst( {1,2,3,4,5} )        | None                        |
 | lvalRef( {1,2,3,4,5} )          | None                        |
 | lvalConstRef( {1,2,3,4,5} )     | None                        |
 | rvalRef( {1,2,3,4,5} )          | None                        |
 '---------------------------------------------------------------------------------------------'
```

And that's it!  See C++11 type deduction isn't too hairy.

Here's some ideas of additional things you can explore with the tool:


* Get a grasp of how function and array types decay by defining an array such
as `int array[10];` and declaring a function like `double fcn(int, int);` and
passing them to the `whatTheHellAreYou` maro.

* Get a grasp on how std::move works.  For example by trying
`whatTheHellAreYou(std::move( var ))`.

* Get a grasp on how std::forward works by making new functions in templateFile.cpp such as:
```
template<typename T>
void lval_fwd(T x) { whatTheHellAreYou(std::forward<decltype(x)>(x)); }
```

