#include <termios.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <dirent.h>


static int set_interface_attributes (int fd, int speed);
static int set_blocking(int fd, int should_block);
static int read_until_prompt(int fd, char *buf, int bufsize);
static char* auto_detect_elm327();



static char* auto_detect_elm327() {
    static char device_path[512];

    DIR *dir = opendir("/dev");
    if (!dir) {
        fprintf(stderr, "Cannot open /dev directory\n");
        return NULL;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strncmp(entry->d_name, "ttyUSB", 6) == 0 ||
            strncmp(entry->d_name, "ttyACM", 6) == 0) {

            snprintf(device_path, sizeof(device_path), "/dev/%s", entry->d_name);
            printf("Trying device: %s\n", device_path);

            int fd = open(device_path, O_RDWR | O_NOCTTY);
            if (fd < 0) continue;

            set_interface_attributes(fd, B38400);
            set_blocking(fd, 1);

            write(fd, "ATZ\r", 4);
            usleep(1500000);

            char buffer[256];
            memset(buffer, 0, sizeof(buffer));
            read_until_prompt(fd, buffer, sizeof(buffer));
            close(fd);

            if (strstr(buffer, "ELM327") != NULL) {
                printf("Found ELM327 at %s\n", device_path);
                closedir(dir);
                return device_path;
            }
        }
    }

    closedir(dir);
    fprintf(stderr, "No ELM327 device found\n");
    return NULL;
}


static int set_interface_attributes(int fd, int speed) {
    struct termios tty;
    memset(&tty, 0, sizeof tty);

    if (tcgetattr(fd, &tty) != 0) {
        fprintf(stderr, "error %d from tcgetattr: %s\n", errno, strerror(errno));
        return -1;
    }

    cfmakeraw(&tty);
    cfsetospeed(&tty, speed);
    cfsetispeed(&tty, speed);

    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cc[VMIN]  = 0;
    tty.c_cc[VTIME] = 10;

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        fprintf(stderr, "error %d from tcsetattr: %s\n", errno, strerror(errno));
        return -1;
    }

    return 0;
}

 static int set_blocking(int fd, int should_block) {

        struct termios tty;
        memset(&tty,0, sizeof tty);
        if (tcgetattr (fd, &tty) != 0) {
            fprintf(stderr,"error %d from tggetattr: %s\n", errno,strerror(errno));
            return -1;}

        tty.c_cc[VMIN] = should_block ? 1 : 0;
        tty.c_cc[VTIME] = 10;

        if (tcsetattr (fd,TCSANOW, &tty) != 0) {
            fprintf(stderr,"error %d setting term attributes: %s\n", errno,strerror(errno));
            return -1;
            
        }

        return 0;
    }

static int open_serial_port_fd() {

        
        char *port_name = auto_detect_elm327();

        if (!port_name) {
            fprintf(stderr,"No ELM Device Found\n");
            return -1;}

        int serial_port_fd = open(port_name, O_RDWR | O_NOCTTY);
        if (serial_port_fd < 0) {
            fprintf(stderr,"error %d opening %s:%s", errno, port_name, strerror(errno));
            return -1;
        }

        set_interface_attributes(serial_port_fd,B38400);
        set_blocking(serial_port_fd,1);

        return serial_port_fd;
    }


static int read_until_prompt(int fd, char *buf, int bufsize) {
    int total = 0;
    char c;
    while (total < bufsize - 1) {
        int n = read(fd, &c, 1);
        if (n <= 0) break;
        if (c == '>') break;
        buf[total++] = c;
    }
    buf[total] = '\0';
    return total;
}

int py_open_port(void) {
    return open_serial_port_fd();
}

int py_send_command(int fd, const char *cmd, char *out_buf, int buf_len) {
    write(fd, cmd, strlen(cmd));
    return read_until_prompt(fd, out_buf, buf_len);
}

void py_close_port(int fd) {
    close(fd);
}

