#include "mbed.h"
#include "MPU6050.h"

Serial pc(USBTX, USBRX);
MPU6050 mpu(p9, p10);
InterruptIn irq(p8);
Timer timer;

int accel[3];
int gyro[3];

void measure() {
    mpu.getAcceleroRaw(accel);
    mpu.getGyroRaw(gyro);
    
    //writing current accelerometer and gyro position 
    pc.printf("%d;%d;%d;%d;%d;%d;%d\r\n", timer.read_us(), accel[0], accel[1], accel[2], gyro[0], gyro[1], gyro[2]);
}

int main()
{
    pc.baud(230400);
    pc.printf("# MPU6050 booting\r\n");

    // Testing
    pc.printf("# MPU6050 testing...");

    if (mpu.testConnection() == 0x68) {
        pc.printf("ok\r\n");
    } else {
        pc.printf("failed\r\n");
    }
   
    // Configure
    pc.printf("# MPU6050 configuring...");
    mpu.setBW(MPU6050_BW_5);
    mpu.setAcceleroRange(MPU6050_ACCELERO_RANGE_2G); 
    mpu.setGyroRange(MPU6050_GYRO_RANGE_1000);
    mpu.setIntDataReadyEnabled(true);
    pc.printf("ok\r\n");
 
    timer.start();
    irq.rise(&measure);
    
    // Logging
    while(1);
}
