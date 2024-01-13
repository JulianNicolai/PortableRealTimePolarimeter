class Configuration:
    MOTOR_MAX_SPEED = 3840  # [RPM]
    MOTOR_SPEED_PERCENT = 100  # [%]
    ROTATIONS_PER_FRAME = 5
    SAMPLES_PER_ROTATION = 1562

    def __init__(self, interface):

        self.interface = interface

        self.motor_speed_percent = self.MOTOR_SPEED_PERCENT
        self.rotations_per_frame = self.ROTATIONS_PER_FRAME
        self.samples_per_rotation = self.SAMPLES_PER_ROTATION

        self.set_motor_speed = None
        self.actual_motor_speed = None
        self.samples_per_frame = None
        self.integration_time = None
        self.frames_per_second = None
        self.samples_per_second = None

        self.motor_speed_percent_temp = None
        self.rotations_per_frame_temp = None
        self.samples_per_rotation_temp = None

        self.set_motor_speed_temp = None
        self.samples_per_frame_temp = None
        self.integration_time_temp = None
        self.frames_per_second_temp = None
        self.samples_per_second_temp = None

        self.applied = True

        self.reset()
        self.apply_config()

    def calc_set_motor_speed(self):
        return round(self.motor_speed_percent_temp * self.MOTOR_MAX_SPEED / 100)

    def calc_samples_per_frame(self):
        return round(self.rotations_per_frame_temp * self.samples_per_rotation_temp)

    def calc_integration_time(self):
        return self.rotations_per_frame_temp * 60000 / self.actual_motor_speed

    def calc_frames_per_second(self):
        return 1000 / self.integration_time_temp

    def calc_samples_per_second(self):
        return round(self.samples_per_rotation_temp * self.actual_motor_speed / 60)

    def update_actual_motor_speed(self, current_motor_speed):
        self.actual_motor_speed = current_motor_speed
        self.integration_time_temp = self.calc_integration_time()
        self.frames_per_second_temp = self.calc_frames_per_second()
        self.samples_per_second_temp = self.calc_samples_per_second()
        self.interface.motor_speed_status_value.setValue(current_motor_speed)
        self.interface.integration_time_value.setValue(self.integration_time_temp)
        self.interface.fps_value.setValue(self.frames_per_second_temp)
        self.interface.samples_second_value.setValue(self.samples_per_second_temp)

    def update_motor_speed_percent(self, motor_speed_percent):
        self.interface.motor_speed_value.setValue(motor_speed_percent)
        self.motor_speed_percent_temp = self.interface.motor_speed_value.value()
        self.set_motor_speed_temp = self.calc_set_motor_speed()
        self.interface.motor_speed_set_value.setValue(self.set_motor_speed_temp)
        self.update_actual_motor_speed(self.set_motor_speed_temp)  # REMOVE WHEN ACTUAL MOTOR SPEED CAN BE FOUND
        self.applied = False
        self.changes_made()

    def update_rotations_per_frame(self, rotations_per_frame):
        self.interface.rotations_frame_value.setValue(rotations_per_frame)
        self.rotations_per_frame_temp = self.interface.rotations_frame_value.value()
        self.samples_per_frame_temp = self.calc_samples_per_frame()
        self.integration_time_temp = self.calc_integration_time()
        self.frames_per_second_temp = self.calc_frames_per_second()
        self.interface.samples_frame_value.setValue(self.samples_per_frame_temp)
        self.interface.integration_time_value.setValue(self.integration_time_temp)
        self.interface.fps_value.setValue(self.frames_per_second_temp)
        self.applied = False
        self.changes_made()

    def update_samples_per_rotation(self, samples_per_rotation):
        if samples_per_rotation >= 20:
            self.samples_per_rotation_temp = samples_per_rotation
            self.samples_per_second_temp = self.calc_samples_per_second()
            if self.samples_per_second_temp > 100000:
                self.samples_per_rotation_temp = round(100000 * 60 / self.actual_motor_speed)
                self.samples_per_second_temp = self.calc_samples_per_second()
                self.samples_per_frame_temp = self.calc_samples_per_frame()
            else:
                self.samples_per_frame_temp = self.calc_samples_per_frame()
            self.interface.samples_frame_value.setValue(self.samples_per_frame_temp)
            self.interface.samples_second_value.setValue(self.samples_per_second_temp)
            self.interface.samples_rotation_value.setValue(self.samples_per_rotation_temp)
            self.applied = False
            self.changes_made()

    def apply_config(self):
        self.motor_speed_percent = self.motor_speed_percent_temp
        self.rotations_per_frame = self.rotations_per_frame_temp
        self.samples_per_rotation = self.samples_per_rotation_temp
        self.set_motor_speed = self.set_motor_speed_temp
        self.samples_per_frame = self.samples_per_frame_temp
        self.integration_time = self.integration_time_temp
        self.frames_per_second = self.frames_per_second_temp
        self.samples_per_second = self.samples_per_second_temp
        self.applied = True
        self.changes_made()

        print(f"Applied current configuration parameters successfully:"
              f"Motor Speed: {self.motor_speed_percent}"
              f"Rotations/Frame: {self.rotations_per_frame}"
              f"Samples/Rotation: {self.samples_per_rotation}")

    def changes_made(self):
        if not self.applied:
            self.interface.apply_config_button.setText("*Apply")
        else:
            self.interface.apply_config_button.setText("Apply")

    def reset(self):
        self.motor_speed_percent_temp = self.motor_speed_percent
        self.rotations_per_frame_temp = self.rotations_per_frame
        self.samples_per_rotation_temp = self.samples_per_rotation

        self.set_motor_speed_temp = self.calc_set_motor_speed()
        self.actual_motor_speed = self.set_motor_speed_temp
        self.samples_per_frame_temp = self.calc_samples_per_frame()
        self.integration_time_temp = self.calc_integration_time()
        self.frames_per_second_temp = self.calc_frames_per_second()
        self.samples_per_second_temp = self.calc_samples_per_second()

        self.interface.motor_speed_value.setValue(self.motor_speed_percent_temp)
        self.interface.rotations_frame_value.setValue(self.rotations_per_frame_temp)
        self.interface.samples_rotation_value.setValue(self.samples_per_rotation_temp)

        self.interface.motor_speed_set_value.setValue(self.set_motor_speed_temp)
        self.interface.motor_speed_status_value.setValue(self.actual_motor_speed)
        self.interface.samples_frame_value.setValue(self.samples_per_frame_temp)
        self.interface.fps_value.setValue(self.frames_per_second_temp)
        self.interface.integration_time_value.setValue(self.integration_time_temp)
        self.interface.samples_second_value.setValue(self.samples_per_second_temp)

        self.applied = True
        self.changes_made()

    def get_set_motor_speed(self):
        return self.set_motor_speed

    def get_actual_motor_speed(self):
        return self.actual_motor_speed

    def get_rotations_per_frame(self):
        return self.rotations_per_frame

    def get_samples_per_rotation(self):
        return self.samples_per_rotation

    def get_samples_per_frame(self):
        return self.samples_per_frame
