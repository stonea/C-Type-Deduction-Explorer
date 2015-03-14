#include <iostream>
#include <vector>
using namespace std;

template<typename T>
class IAmA;

// We this macro to determine the what type some expression is deduced to be.
// This uses a trick described in "Effective Modern C++" item 4 (Know how to view deduced types).
#define whatTheHellAreYou(expr) \
    IAmA<decltype(expr)> blah; 

template<typename T>
void lval(T x) { whatTheHellAreYou(x); }

template<typename T>
void lvalRef(T& x) { whatTheHellAreYou(x); }

template<typename T>
void lvalConstRef(T const & x) { whatTheHellAreYou(x); }

template<typename T>
void rvalRef(T&& x) { whatTheHellAreYou(x); }

int main(int argc, char *argv[]) {
    int        var              = 1;
    const int  constVar         = 2;
    int&       reference        = var  ;
    const int& constReference   = var  ;

    auto auto_var             = var  ;
    auto auto_constVar        = constVar;
    auto auto_reference       = reference;
    auto auto_constReference  = constReference;

    auto& auto_ref_var            = var  ;
    auto& auto_ref_constVar       = constVar;
    auto& auto_ref_reference      = reference;
    auto& auto_ref_constReference = constReference;

    auto const & auto_cref_var            = var  ;
    auto const & auto_cref_constVar       = constVar;
    auto const & auto_cref_reference      = reference;
    auto const & auto_cref_constReference = constReference;

    int array[10];
    auto initList = {1,2,3,4,5};
    double fcn(int, int);
    double (*)(int, int) fcnPtr = fcn;

    rvalRef( 42 );
}
