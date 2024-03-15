from configparser import ConfigParser
from tiagaincontrol import TIAGainControl

class Configuration:

    MOTOR_MAX_SPEED = 4680  # [RPM]

    def __init__(self, interface, config_path, serial_device):

        self.interface = interface
        self.serial_device = serial_device

        self.saved_config = ConfigParser()
        self.saved_config.read(config_path)

        try:
            self.motor_speed_percent = int(self.saved_config.get('Capture Settings', 'MOTOR_SPEED_PERCENT'))
            self.rotations_per_frame = int(self.saved_config.get('Capture Settings', 'ROTATIONS_PER_FRAME'))
            self.tia_gain = int(self.saved_config.get('Capture Settings', 'TIA_GAIN'))
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
        self.tia_gain_temp = None

        self.tia_dig_rheostat = TIAGainControl()
        self.tia_dig_rheostat.write_value(self.tia_gain)

        self.applied = True

        self.reset()
        self.apply_config()

    def update_statistics(self, samples, dt):
        dt_in_seconds = dt * 1e-6
        self.actual_motor_speed = round(self.get_rotations_per_frame() * 60 / dt_in_seconds)
        self.samples_per_second = round(samples / dt_in_seconds)
        self.samples_per_frame = samples
        self.integration_time = dt_in_seconds * 1e3
        self.frames_per_second = 1 / dt_in_seconds
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

    def update_tia_gain(self, tia_gain):
        self.interface.gain_value.setValue(tia_gain)
        self.tia_gain_temp = tia_gain
        self.applied = False
        self.changes_made()

    def apply_config(self):
        self.motor_speed_percent = self.motor_speed_percent_temp
        self.rotations_per_frame = self.rotations_per_frame_temp
        self.tia_gain = self.tia_gain_temp

        self.tia_dig_rheostat.write_value(self.tia_gain)
        self.serial_device.write(b'c' + int.to_bytes(self.rotations_per_frame))

        # TODO: Add command to update RPi Pico -> b'c' + self.rotations_per_frame.to_bytes(1)

        self.applied = True
        self.changes_made()

        print(f"Applied current configuration parameters successfully. "
              f"Motor Speed: {self.motor_speed_percent}%  "
              f"Rotations/Frame: {self.rotations_per_frame}  "
              f"TIA Gain: {self.tia_gain}")

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
