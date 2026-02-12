#include <termios.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <dirent.h>


#define OBD_SERIAL_PORT "/dev/ttyUSB0"




static char* auto_detect_elm327() {

    static char device_path[256];
    DIR *dir = opendir("/dev");
    if(!dir) {
        printf("Cannot open /dev directory\n");
        return NULL;

    }

    struct dirent *entry;

    while ((entry = readdir(dir)) != NULL) {

        if (strncmp(entry->d_name, "ttyUSB",6) == 0 ||
            strncmp(entry->d_name,"ttyACM", 6) == 0 ) {
            
            snprintf(device_path, sizeof(device_path), "/dev/%s", entry->d_name);
            printf("Trying device: %s\n", device_path);
            
            int fd = open(device_path, O_RDWR | O_NOCTTY | O_NDELAY);
            if (fd < 0) {
                continue;
            }

        set_interface_attributes(fd,B38400);
        set_blocking(fd,1);
        write(fd,"ATZ\r",4);
        usleep(500000);

        char buffer[256];
        memset(buffer,0,sizeof(buffer));
        int n = read(fd,buffer,sizeof(buffer) - 1);
        
        close(fd);

        if (n > 0 && strstr(buffer,"ELM327") != NULL) {
            printf("Found ELM327 at %s\n", device_path);
            closedir(dir);
            return device_path;
        }}}

closedir(dir);
printf("No ELM327 device found\n");
return NULL;

}


static int set_interface_attributes (int fd, int speed)
    {
        struct termios tty;
        memset(&tty,0,sizeof tty);
        if(tcgetattr (fd,&tty) != 0) {
            printf("error %d from tcgetattr", errno);
            return -1;
        }

        fcntl(fd,F_SETFL,0);

        tty.c_cflag |= (CLOCAL | CREAD);
        tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
        tty.c_oflag &= ~(OPOST);
        tty.c_cc[VMIN] = 0;
        tty.c_cc[VTIME] = 100;

        if(tcsetattr (fd,TCSANOW, &tty) != 0) {
            printf("error %d from tcsetattr", errno);
            return -1;
        }
        
        cfsetospeed(&tty,speed);
        cfsetispeed(&tty,speed);

        return 0;
        

    }

 static int set_blocking(int fd, int should_block) {

        struct termios tty;
        memset(&tty,0, sizeof tty);
        if (tcgetattr (fd, &tty) != 0) {
            printf("error %d from tggetattr", errno);
            return -1;
        }

        tty.c_cc[VMIN] = should_block ? 1 : 0;
        tty.c_cc[VTIME] = 5; 

        if (tcsetattr (fd,TCSANOW, &tty) != 0) {
            printf("error %d setting term attributes", errno);
            return -1;
            
        }

        return 0;
    }

static int open_serial_port_fd() {

        
        char *port_name = auto_detect_elm327();

        int serial_port_fd = open(port_name, O_RDWR | O_NOCTTY | O_NDELAY);
        if (serial_port_fd < 0) {
            printf("error %d opening %s:%s", errno, port_name, strerror(errno));
        }

        return serial_port_fd;
    }