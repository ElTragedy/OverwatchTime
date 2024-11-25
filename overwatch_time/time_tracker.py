# overwatch_time/time_tracker.py
import os
import csv
import datetime
import logging

from .utils import data_path

class TimeTracker:
    """
    A class to handle time tracking functionalities.
    """
    def __init__(self):
        # Paths
        self.TIME_LOG_FOLDER = data_path('')  # Points to AppData\Roaming\OverwatchTimeData
        self.TIME_LOG_PATH = data_path('time_log.csv')
        self.CLOCK_IN_STATUS_PATH = data_path('clock_in_status.csv')
        self.start_time = None

        # Ensure directories exist
        if not os.path.exists(self.TIME_LOG_FOLDER):
            os.makedirs(self.TIME_LOG_FOLDER)

    def clock_in(self):
        """
        Clock in the user and record the start time.
        """
        try:
            with open(self.CLOCK_IN_STATUS_PATH, 'w') as file:
                file.write('True')
                file.write('\n')
                file.write(str(datetime.datetime.now()))
            self.start_time = datetime.datetime.now()
            logging.info(f"User clocked in at {self.start_time}")
        except Exception as e:
            logging.error(f"Failed to clock in: {e}")
            raise e

    def clock_out(self):
        """
        Clock out the user, calculate duration, and save the session.

        Returns:
            datetime.timedelta: The duration of the session.
        """
        try:
            end_time = datetime.datetime.now()
            duration = end_time - self.start_time
            self.save_session(duration)
            with open(self.CLOCK_IN_STATUS_PATH, 'w') as file:
                file.write('False')
            logging.info(f"User clocked out at {end_time} after {duration}")
            return duration
        except Exception as e:
            logging.error(f"Failed to clock out: {e}")
            raise e

    def is_clocked_in(self):
        """
        Check if the user is currently clocked in.

        Returns:
            bool: True if clocked in, False otherwise.
        """
        try:
            with open(self.CLOCK_IN_STATUS_PATH, 'r') as file:
                status = file.readline().strip()
                return status == 'True'
        except FileNotFoundError:
            return False
        except Exception as e:
            logging.error(f"Failed to check clock-in status: {e}")
            raise e

    def save_session(self, duration):
        """
        Save the session duration to the time log.

        Parameters:
            duration (datetime.timedelta): Duration of the session.
        """
        try:
            with open(self.TIME_LOG_PATH, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([datetime.date.today(), duration.total_seconds()])
            logging.info(f"Session saved with duration {duration}")
        except Exception as e:
            logging.error(f"Failed to save session: {e}")
            raise e

    def read_sessions(self):
        """
        Read all sessions from the time log.

        Returns:
            list: A list of sessions.
        """
        if not os.path.exists(self.TIME_LOG_PATH):
            return []
        try:
            with open(self.TIME_LOG_PATH, 'r') as file:
                reader = csv.reader(file)
                sessions = list(reader)
            return sessions
        except Exception as e:
            logging.error(f"Failed to read sessions: {e}")
            raise e

    def weekly_summary(self, year, week_number):
        """
        Calculate the total tracked time for a specific week.

        Parameters:
            year (int): The year.
            week_number (int): The ISO week number.

        Returns:
            float: Total seconds tracked in the specified week.
        """
        sessions = self.read_sessions()
        total_seconds = 0.0
        for date_str, duration_str in sessions:
            try:
                session_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                session_year, session_week, _ = session_date.isocalendar()
                if (session_year, session_week) == (year, week_number):
                    total_seconds += float(duration_str)
            except Exception as e:
                logging.error(f"Failed to process session {date_str}, {duration_str}: {e}")
        return total_seconds

    def get_start_time(self):
        """
        Retrieve the start time from the clock-in status file.

        Returns:
            datetime.datetime: The start time.
        """
        try:
            with open(self.CLOCK_IN_STATUS_PATH, 'r') as file:
                lines = file.readlines()
                if len(lines) > 1:
                    self.start_time = datetime.datetime.strptime(lines[1].strip(), "%Y-%m-%d %H:%M:%S.%f")
                else:
                    self.start_time = datetime.datetime.now()
        except Exception as e:
            logging.error(f"Failed to get start time: {e}")
            self.start_time = datetime.datetime.now()
        return self.start_time

