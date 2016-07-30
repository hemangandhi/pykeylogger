#include <stdio.h>
#include <X11/Xlib.h>

int main(){
        printf("%d, %d, %ld, %ld\n", ButtonPress, ButtonRelease, PointerWindow, ButtonPressMask);
}
