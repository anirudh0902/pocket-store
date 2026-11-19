import os
import mimetypes
import boto3
from botocore.config import Config
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Uploads all local media files to Cloudflare R2 / AWS S3 persistent storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='List files to upload without actually transferring them.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        endpoint_url = os.environ.get('AWS_S3_ENDPOINT_URL')
        access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')

        if not all([access_key, secret_key, bucket_name]):
            self.stderr.write(
                self.style.ERROR(
                    "Missing S3/R2 credentials in environment variables.\n"
                    "Please set: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_ENDPOINT_URL"
                )
            )
            return

        self.stdout.write(self.style.NOTICE(f"Connecting to Cloudflare R2 Bucket: {bucket_name}..."))
        if endpoint_url:
            self.stdout.write(f"Endpoint: {endpoint_url}")

        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4'),
        )

        media_root = str(settings.MEDIA_ROOT)
        if not os.path.exists(media_root):
            self.stderr.write(self.style.ERROR(f"Media root does not exist: {media_root}"))
            return

        total_files = 0
        total_bytes = 0

        self.stdout.write(self.style.NOTICE(f"Scanning media files in {media_root}..."))

        for root, _, files in os.walk(media_root):
            for file in files:
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, media_root).replace('\\', '/')
                file_size = os.path.getsize(local_path)
                content_type, _ = mimetypes.guess_type(local_path)
                content_type = content_type or 'application/octet-stream'

                total_files += 1
                total_bytes += file_size

                if dry_run:
                    self.stdout.write(f"[DRY-RUN] Would upload: {rel_path} ({file_size / 1024:.1f} KB, {content_type})")
                else:
                    self.stdout.write(f"Uploading: {rel_path} ({file_size / 1024:.1f} KB)...")
                    with open(local_path, 'rb') as f:
                        s3_client.put_object(
                            Bucket=bucket_name,
                            Key=rel_path,
                            Body=f,
                            ContentType=content_type,
                        )

        status_text = "Simulated" if dry_run else "Transferred"
        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully {status_text} {total_files} media files ({total_bytes / (1024 * 1024):.2f} MB) to R2/S3 bucket '{bucket_name}'!"
            )
        )
