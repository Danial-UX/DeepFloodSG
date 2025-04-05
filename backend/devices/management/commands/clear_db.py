from django.core.management.base import BaseCommand
from devices.models import Device, DataLog
from birds.models import Birds, BirdLog

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
        bird_count = Birds.objects.count()
        bird_log_count = BirdLog.objects.count()

        # Delete all data logs first (due to foreign key constraints)
        BirdLog.objects.all().delete()
        DataLog.objects.all().delete()
        # Delete all devices
        Birds.objects.all().delete()
        Device.objects.all().delete()
        # delete all birds
        

        self.stdout.write(self.style.SUCCESS(
            f'Successfully deleted \n{device_count} devices\n{log_count} logs \n{bird_count} birds \n{bird_log_count} bird logs'
        ))