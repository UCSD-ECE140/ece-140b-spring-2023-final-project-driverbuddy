#include <imu.hpp>

volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady(){
    mpuInterrupt = true;
}

IMU::IMU(){}

IMU::~IMU(){
    Wire.end();
}

bool IMU::setup(Stream &serial) {
    Wire.begin();
    Wire.setClock(400000); // 400kHz I2C clock. Comment this line if having compilation difficulties

    // Initialize MPU6050 and test connection
    mpu.initialize();
    pinMode(INTERRUPT_PIN, INPUT);
    if (!mpu.testConnection()) {
        serial.println("MPU6050 connection failed");
        return false;
    }
    serial.println("MPU6050 connection successful");

    // Load and configure the DMP
    devStatus = mpu.dmpInitialize();
    // supply your own gyro offsets here, scaled for min sensitivity
    mpu.setXGyroOffset(220);
    mpu.setYGyroOffset(76);
    mpu.setZGyroOffset(-85);
    mpu.setZAccelOffset(1788);
    if (devStatus != 0) {
        serial.print("DMP Initialization failed (code ");
        serial.print(devStatus);
        serial.println(")");
        return false;
    }
    serial.println("DMP Initialization successful");

    // Generate offsets and calibrate our MPU6050
    mpu.CalibrateAccel(6);
    mpu.CalibrateGyro(6);

    // Turn on DMP
    serial.println(F("Enabling DMP..."));
    mpu.setDMPEnabled(true);

    // Enable Arduino interrupt detection
    serial.print(F("Enabling interrupt detection (Arduino external interrupt "));
    serial.print(digitalPinToInterrupt(INTERRUPT_PIN));
    serial.println(F(")..."));
    attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN), dmpDataReady, RISING);
    mpuIntStatus = mpu.getIntStatus();

    // Set DMP flag for use by this class in other methods
    serial.println(F("DMP ready! Waiting for first interrupt..."));
    dmpReady = true;

    // Get expected DMP packet size for later comparison
    packetSize = mpu.dmpGetFIFOPacketSize();
    return true;
}


String IMU::get_quat_string() {
    String q_string = "Quaternion:" + String(quaternion.w) + "," + String(quaternion.x) + "," + String(quaternion.y) + "," + String(quaternion.z);
    return q_string;
}

String IMU::get_ypr_string() {
    float yaw = euler[0] * 180 / M_PI;
    float pitch = euler[1] * 180 / M_PI;
    float roll = euler[2] * 180 / M_PI;
    String ypr_string = "YawPitchRoll:" + String(yaw) + "," + String(pitch) + "," + String(roll);
    return ypr_string;
}

String IMU::get_accel_string() {
    String accel_string = "Accel:" + String(accelWorld.x) + "," + String(accelWorld.y) + "," + String(accelWorld.z);
    return accel_string;
}


void IMU::update_and_get_data(StaticJsonDocument<CAPACITY>& data) {
    update();
    data["yaw"] = euler[0] * 180 / M_PI;
    data["pitch"] = euler[1] * 180 / M_PI;
    data["roll"] = euler[2] * 180 / M_PI;
    data["accel_x"] = accelWorld.x;
    data["accel_y"] = accelWorld.y;
    data["accel_z"] = accelWorld.z;
}


void IMU::update() {
    if (dmpReady) {
        if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
            mpu.dmpGetQuaternion(&quaternion, fifoBuffer);
            mpu.dmpGetGravity(&gravity, &quaternion);
            mpu.dmpGetYawPitchRoll(euler, &quaternion, &gravity);
            mpu.dmpGetAccel(&accel, fifoBuffer);
            mpu.dmpGetLinearAccel(&accelReal, &accel, &gravity);
            mpu.dmpGetLinearAccelInWorld(&accelWorld, &accelReal, &quaternion);
        }
    }
}

