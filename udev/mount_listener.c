#define POLL_TIMEOUT 2*1000

/*

poll() /proc/mounts and exits when changed

*/

#include <poll.h>
#include <stdio.h>
#include <fcntl.h>

int main(void)

{
  int fd_file;
  char filepath[] = "/proc/mounts";

  struct pollfd fdarray[1]; 

  int nfds, rc;


  if ((fd_file = open(filepath, O_RDONLY, 0)) < 0)
     perror("Error opening file ");


  for (;;) {
    fdarray[0].fd = fd_file;
    fdarray[0].events = POLLIN;
    nfds = 1;

    rc = poll(fdarray, nfds, POLL_TIMEOUT);

    if (rc < 0) {
      perror("error reading poll()\n");
      return;
    }

    if(rc > 0) {
     /* exit to leave work to script */
     return 0;
    }
  }
  // never here
  return 0;
}

