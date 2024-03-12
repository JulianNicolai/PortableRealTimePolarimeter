from configparser import ConfigParser

class Configuration:

    MOTOR_MAX_SPEED = 4680  # [RPM]

    def __init__(self, interface, config_path):

        self.interface = interface

        self.saved_config = ConfigParser()
        self.saved_config.read(config_path)

        try:
            self.motor_speed_percent = int(self.saved_config.get('Capture Settings', 'MOTOR_SPEED_PERCENT'))
            self.rotations_per_frame = int(self.saved_config.get('Capture Settings', 'ROTATIONS_PER_FRAME'))
        except ValueError:
            print("Configuration error! One or more configuration values contain non-numeric characters or non-integer "
                  "values (floats are invalid). Verify the config is correct or save the configuration through the "
                  "interface. Falling back to default values.")

            self.motor_speed_percent = 100
            self.rotations_per_frame = 5

        self.actual_motor_speed = 0
        self.samples_per_frame = 0
        self.integration_time = 0
        self.frames_per_second = 0
        self.samples_per_second = 0

        self.motor_speed_percent_temp = None
        self.rotations_per_frame_temp = None

        self.applied = True

        self.reset()
        self.apply_config()

    def update_statistics(self, samples, dt):
        self.actual_motor_speed = self.get_rotations_per_frame() * 60 / (dt * 1e-6)
        self.samples_per_second = samples / dt
        self.samples_per_frame = samples
        self.integration_time = dt * 1e-3
        self.frames_per_second = 1 / self.integration_time
        self.update_display()

    def update_display(self):
        self.interface.motor_speed_status_value.setValue(self.actual_motor_speed)
        self.interface.samples_frame_value.setValue(self.samples_per_frame)
        self.interface.samples_second_value.setValue(self.samples_per_second)
        self.interface.integration_time_value.setValue(self.integration_time)
        self.interface.fps_value.setValue(self.frames_per_second)

    def update_motor_speed_percent(self, motor_speed_percent):
        self.interface.motor_speed_value.setValue(motor_speed_percent)
        self.motor_speed_percent_temp = motor_speed_percent
        self.applied = False
        self.changes_made()

    def update_rotations_per_frame(self, rotations_per_frame):
        self.interface.rotations_frame_value.setValue(rotations_per_frame)
        self.rotations_per_frame_temp = rotations_per_frame
        self.applied = False
        self.changes_made()

    def apply_config(self):
        self.motor_speed_percent = self.motor_speed_percent_temp
        self.rotations_per_frame = self.rotations_per_frame_temp

        # TODO: Add command to update RPi Pico -> b'c' + self.rotations_per_frame.to_bytes(1)

        self.applied = True
        self.changes_made()

        print(f"Applied current configuration parameters successfully. "
              f"Motor Speed: {self.motor_speed_percent}%  "
              f"Rotations/Frame: {self.rotations_per_frame}  ")

    def save_config(self):

        self.apply_config()

        self.saved_config.set('Capture Settings', 'MOTOR_SPEED_PERCENT', str(self.motor_speed_percent))
        self.saved_config.set('Capture Settings', 'ROTATIONS_PER_FRAME', str(self.rotations_per_frame))

        with open('config.ini', 'w') as file:
            self.saved_config.write(file)

        print("Configuration saved to disk successfully.")

    def changes_made(self):
        if not self.applied:
            self.interface.apply_config_button.setText("*Apply")
        else:
            self.interface.apply_config_button.setText("Apply")

    def reset(self):
        self.motor_speed_percent_temp = self.motor_speed_percent
        self.rotations_per_frame_temp = self.rotations_per_frame

        self.interface.motor_speed_value.setValue(self.motor_speed_percent_temp)
        self.interface.rotations_frame_value.setValue(self.rotations_per_frame_temp)

        self.applied = True
        self.changes_made()

    def get_actual_motor_speed(self):
        return self.actual_motor_speed

    def get_rotations_per_frame(self):
        return self.rotations_per_frame

    def get_samples_per_frame(self):
        return self.samples_per_frame
