



import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

class ImageHandler(FileSystemEventHandler):
    def __init__(self, target_directory, max_size_kb=100, max_retries=3, delay=4, write_delay=4):
        self.target_directory = target_directory
        self.max_size_kb = max_size_kb
        self.max_retries = max_retries
        self.delay = delay
        self.write_delay = write_delay
        self.processed_files = set()

    def on_created(self, event):
        self.handle_event(event)

    def on_modified(self, event):
        self.handle_event(event)

    def on_moved(self, event):
        self.handle_event(event)

    def handle_event(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.jpg'):
            if (event.src_path not in self.processed_files and
                not event.src_path.lower().endswith('jpg.temp.jpg') and
                '_compressed' not in event.src_path.lower()):
                logging.info(f"Yeni dosya tespit edildi: {event.src_path}")
                time.sleep(self.write_delay)
                self.process_image(event.src_path)

    def process_image(self, file_path):
        for attempt in range(self.max_retries):
            try:
                with Image.open(file_path) as img:
                    img = self.downscale_image(img)
                    quality = self.calculate_quality(img, file_path)
                    base, ext = os.path.splitext(file_path)
                    compressed_path = base + "_compressed" + ext
                    img.save(compressed_path, "JPEG", optimize=True, quality=quality)
                logging.info(f"{file_path} başarıyla işlendi.")
                self.processed_files.add(file_path)
                break
            except (PermissionError, OSError) as e:
                logging.error(f"Hata: {str(e)}: {file_path} yeniden deneniyor {self.delay} saniye sonra.")
                time.sleep(self.delay)
            except Exception as e:
                logging.error(f"{file_path} işlenemedi: {str(e)}.")
                break

    def calculate_quality(self, img, file_path):
        temp_path = file_path + ".temp.jpg"
        initial_quality = 95
        step_size = 5
        min_quality = 30
        while initial_quality >= min_quality:
            img.save(temp_path, "JPEG", optimize=True, quality=initial_quality)
            if os.path.getsize(temp_path) <= self.max_size_kb * 1024:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return initial_quality
            initial_quality -= step_size
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return min_quality

    def downscale_image(self, img, max_width=1920, max_height=1080):
        """Görüntüyü belirtilen maksimum boyutlara ölçeklendirir."""
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height))
        return img

def main():

    path3 = r'G:\2026 Sample Picture\LAB_PICTURE-2026'
    path4 = r'G:\2026 Sample Picture\Nirvana_Picture'

    event_handler3 = ImageHandler(target_directory=path3)
    event_handler4 = ImageHandler(target_directory=path4)

    observer3 = Observer()
    observer4 = Observer()
 
    observer3.schedule(event_handler3, path3, recursive=True)
    observer4.schedule(event_handler4, path4, recursive=True)
    

    observer3.start()
    observer4.start()

    logging.info(f"Dizin izlenmeye başlandı: {path3}")
    logging.info(f"Dizin izlenmeye başlandı: {path4}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:

        observer3.stop()
        observer4.stop()
        

    observer3.join()
    observer4.join()

if __name__ == "__main__":
    main()
