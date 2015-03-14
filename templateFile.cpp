#include <iostream>
#include <vector>
using namespace std;

template<typename T>
class IAmA;

// We this macro to determine the what type some expression is deduced to be.
// This uses the trick described in "Effective Modern C++" item 4 (Know how to view deduced types).
#define whatTheHellAreYou(expr) \
    IAmA<decltype(expr)> blah; 

template<typename T>
void lval(T& x) { whatTheHellAreYou(x); }

template<typename T>
void lvalConst(T const & x) { whatTheHellAreYou(x); }

template<typename T>
void rval(T&& x) { whatTheHellAreYou(x); }


int main(int argc, char *argv[]) {
    int        value            = 1;
    const int  constValue       = 2;
    int&       reference        = value;
    const int& constReference   = value;

    auto auto_value           = value;
    auto auto_constValue      = constValue;
    auto auto_reference       = reference;
    auto auto_constReference  = constReference;

    auto& auto_ref_value          = value;
    auto& auto_ref_constValue     = constValue;
    auto& auto_ref_reference      = reference;
    auto& auto_ref_constReference = constReference;

    auto const & auto_cref_value          = value;
    auto const & auto_cref_constValue     = constValue;
    auto const & auto_cref_reference      = reference;
    auto const & auto_cref_constReference = constReference;

    SUBSTITUTION_POINT
}
