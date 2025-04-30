from django.core.management.base import BaseCommand
from devices.models import Device, DataLog

class Command(BaseCommand):
    help = 'Delete everything from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', 
            action='store_true',
            help='Force deletion without confirmation',
        )

    def handle(self, *args, **options):
        if not options['force']:
            confirm = input('This will delete ALL devices and logs. Are you sure? (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Operation cancelled'))
                return

        log_count = DataLog.objects.count()
        device_count = Device.objects.count()

        # Delete all data logs first (due to foreign key constraints)
        DataLog.objects.all().delete()
        # Delete all devices
        Device.objects.all().delete()        

        self.stdout.write(self.style.SUCCESS(
            f'Successfully deleted \n{device_count} devices\n{log_count} logs'
        ))