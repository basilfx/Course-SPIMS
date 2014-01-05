from django.core.management.base import BaseCommand, CommandError

from otp_analyzer.forms import RecordImportForm

import urlparse

class Command(BaseCommand):
    help = "Import OTP data"
    args = "<data_file>"

    # Used for key remapping
    remap = {
        "model": "model",
        "startTime": "start_time",
        "endTime": "end_time",
        "sessionId": "session_id",
        "sensorDA2max": "sensor_da2_max",
        "maxAX": "max_ax",
        "maxAY": "max_ay",
        "maxAZ": "max_az",
        "minAX": "min_ax",
        "minAY": "min_ay",
        "minAZ": "min_az",
        "rounds": "rounds",
        "accChange": "acc_change"
    }

    def handle(self, *args, **options):
        items = 0

        # Verify command line
        if len(args) == 0:
            raise CommandError("Missing data file")

        # Open file and read each line
        with open(args[0], "r") as fp:
            for line in fp:
                # Convert to dict
                row = urlparse.parse_qs(line, keep_blank_values=True)

                # Remap keys and unpack
                try:
                    row = { Command.remap[x]: y[0] for x, y in row.items() }
                except KeyError:
                    # We let it fail when we try to save it
                    continue

                # Add extra fields
                row["duration"] = int(row["end_time"]) - int(row["start_time"])
                row["duration_round"] = float(row["duration"]) / float(row["rounds"])

                # Put it in a form
                form = RecordImportForm(data=row)

                if form.is_valid():
                    form.save()
                    items += 1

        # Done
        self.stdout.write("Imported %d items\r\n" % items)
