
template<typename T>
class IAmA;

#define whatTheHellAreYou(expr) \
    IAmA<decltype(expr)> blah;

template<typename T>
void foo(T&& param) {
    whatTheHellAreYou(param);
}

int main(int argc, char *argv[]) {
    int x = 42;
    int const & y = x;
    foo(y);
}

