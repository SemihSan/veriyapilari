"""
CLI (Command Line Interface) Menü Sistemi
==========================================
Kullanıcı dostu konsol arayüzü ile rezervasyon sistemi yönetimi.
"""

import os
import sys
from datetime import datetime, timedelta, date
from typing import Optional, Callable

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reservation_system import (
    ReservationSystem, Room, Reservation,
    RoomType, ReservationStatus
)
from data_manager import DataManager


class CLI:
    """
    Komut Satırı Arayüzü
    
    Renk kodları ve formatlama ile kullanıcı dostu deneyim.
    """
    
    # ANSI renk kodları
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
    }
    
    def __init__(self, system: ReservationSystem = None, data_manager: DataManager = None):
        self.system = system or ReservationSystem()
        self.data_manager = data_manager or DataManager()
        self.running = True
        
        # Windows için renk desteği
        if sys.platform == 'win32':
            os.system('color')
    
    def color(self, text: str, color: str, bold: bool = False) -> str:
        """Metni renklendir"""
        prefix = self.COLORS.get('bold', '') if bold else ''
        return f"{prefix}{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"
    
    def clear_screen(self):
        """Ekranı temizle"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Başlık yazdır"""
        width = 60
        print()
        print(self.color("=" * width, 'cyan', bold=True))
        print(self.color(f"{title:^{width}}", 'cyan', bold=True))
        print(self.color("=" * width, 'cyan', bold=True))
    
    def print_section(self, title: str):
        """Bölüm başlığı yazdır"""
        print()
        print(self.color(f"--- {title} ---", 'yellow', bold=True))
    
    def print_success(self, message: str):
        """Başarı mesajı"""
        print(self.color(f"✓ {message}", 'green'))
    
    def print_error(self, message: str):
        """Hata mesajı"""
        print(self.color(f"✗ {message}", 'red'))
    
    def print_warning(self, message: str):
        """Uyarı mesajı"""
        print(self.color(f"⚠ {message}", 'yellow'))
    
    def print_info(self, message: str):
        """Bilgi mesajı"""
        print(self.color(f"ℹ {message}", 'blue'))
    
    def get_input(self, prompt: str, default: str = None) -> str:
        """Kullanıcıdan girdi al"""
        if default:
            prompt = f"{prompt} [{default}]: "
        else:
            prompt = f"{prompt}: "
        
        value = input(self.color(prompt, 'white')).strip()
        return value if value else (default or '')
    
    def get_int(self, prompt: str, default: int = None, min_val: int = None, max_val: int = None) -> Optional[int]:
        """Sayısal girdi al"""
        while True:
            value = self.get_input(prompt, str(default) if default else None)
            
            if not value and default is not None:
                return default
            
            try:
                num = int(value)
                if min_val is not None and num < min_val:
                    self.print_error(f"Değer en az {min_val} olmalı")
                    continue
                if max_val is not None and num > max_val:
                    self.print_error(f"Değer en fazla {max_val} olmalı")
                    continue
                return num
            except ValueError:
                self.print_error("Geçerli bir sayı girin")
    
    def get_date(self, prompt: str, default: date = None) -> Optional[date]:
        """Tarih girdisi al"""
        if default is None:
            default = date.today()
        
        while True:
            value = self.get_input(f"{prompt} (YYYY-MM-DD)", default.isoformat())
            
            try:
                return date.fromisoformat(value)
            except ValueError:
                self.print_error("Geçerli bir tarih girin (örn: 2024-01-15)")
    
    def get_time(self, prompt: str, default: str = "09:00") -> Optional[str]:
        """Saat girdisi al"""
        while True:
            value = self.get_input(f"{prompt} (HH:MM)", default)
            
            try:
                parts = value.split(':')
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
                
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return f"{hour:02d}:{minute:02d}"
                else:
                    raise ValueError()
            except (ValueError, IndexError):
                self.print_error("Geçerli bir saat girin (örn: 14:30)")
    
    def get_choice(self, prompt: str, options: list) -> Optional[str]:
        """Seçenek listesinden seçim"""
        print()
        for i, opt in enumerate(options, 1):
            print(f"  {self.color(str(i), 'cyan')}. {opt}")
        
        choice = self.get_int(prompt, min_val=1, max_val=len(options))
        return options[choice - 1] if choice else None
    
    def confirm(self, prompt: str, default: bool = False) -> bool:
        """Onay al"""
        suffix = "[E/h]" if default else "[e/H]"
        value = self.get_input(f"{prompt} {suffix}").lower()
        
        if not value:
            return default
        return value in ['e', 'evet', 'y', 'yes']
    
    def pause(self):
        """Devam etmek için bekle"""
        input(self.color("\nDevam etmek için Enter'a basın...", 'white'))
    
    # ==================== ANA MENÜ ====================
    
    def show_main_menu(self):
        """Ana menüyü göster"""
        self.print_header("SALON REZERVASYON SİSTEMİ")
        
        stats = self.system.get_statistics()
        print()
        print(f"  Salonlar: {self.color(str(stats['total_rooms']), 'green')}")
        print(f"  Aktif Rezervasyonlar: {self.color(str(stats['active_reservations']), 'green')}")
        print(f"  Bekleme Listesi: {self.color(str(stats['waiting_list_size']), 'yellow')}")
        
        if self.system.can_undo():
            print(f"  Geri Al: {self.color(self.system.get_undo_description(), 'blue')}")
        
        print()
        print(self.color("  1.", 'cyan') + " Salon Yönetimi")
        print(self.color("  2.", 'cyan') + " Rezervasyon Yönetimi")
        print(self.color("  3.", 'cyan') + " Arama ve Sorgulama")
        print(self.color("  4.", 'cyan') + " Raporlar")
        print(self.color("  5.", 'cyan') + " Bekleme Listesi")
        print(self.color("  6.", 'cyan') + " Veri İşlemleri")
        print(self.color("  7.", 'cyan') + " Geri Al / Yinele")
        print(self.color("  0.", 'red') + " Çıkış")
        
        return self.get_int("\nSeçiminiz", min_val=0, max_val=7)
    
    def run(self):
        """Ana döngü"""
        # Mevcut verileri yükle
        self.data_manager.load_system_state(self.system)
        
        while self.running:
            self.clear_screen()
            choice = self.show_main_menu()
            
            if choice == 0:
                if self.confirm("Çıkmak istediğinize emin misiniz?"):
                    self.save_and_exit()
            elif choice == 1:
                self.room_menu()
            elif choice == 2:
                self.reservation_menu()
            elif choice == 3:
                self.search_menu()
            elif choice == 4:
                self.report_menu()
            elif choice == 5:
                self.waiting_list_menu()
            elif choice == 6:
                self.data_menu()
            elif choice == 7:
                self.undo_redo_menu()
    
    def save_and_exit(self):
        """Kaydet ve çık"""
        self.print_info("Veriler kaydediliyor...")
        self.data_manager.save_system_state(self.system)
        self.print_success("Veriler kaydedildi. Güle güle!")
        self.running = False
    
    # ==================== SALON MENÜSÜ ====================
    
    def room_menu(self):
        """Salon yönetimi menüsü"""
        while True:
            self.clear_screen()
            self.print_header("SALON YÖNETİMİ")
            
            print()
            print(self.color("  1.", 'cyan') + " Salonları Listele")
            print(self.color("  2.", 'cyan') + " Yeni Salon Ekle")
            print(self.color("  3.", 'cyan') + " Salon Detayı Görüntüle")
            print(self.color("  4.", 'cyan') + " Salon Düzenle")
            print(self.color("  5.", 'cyan') + " Salon Sil")
            print(self.color("  6.", 'cyan') + " Salon Ara")
            print(self.color("  7.", 'cyan') + " Salon Bağlantıları")
            print(self.color("  0.", 'yellow') + " Ana Menüye Dön")
            
            choice = self.get_int("\nSeçiminiz", min_val=0, max_val=7)
            
            if choice == 0:
                break
            elif choice == 1:
                self.list_rooms()
            elif choice == 2:
                self.add_room()
            elif choice == 3:
                self.view_room()
            elif choice == 4:
                self.edit_room()
            elif choice == 5:
                self.delete_room()
            elif choice == 6:
                self.search_rooms()
            elif choice == 7:
                self.room_connections()
    
    def list_rooms(self):
        """Salonları listele"""
        self.print_section("Salon Listesi")
        
        sort_options = ["İsim", "Kapasite", "Kat"]
        sort_by = self.get_choice("Sıralama kriteri", sort_options)
        
        sort_map = {"İsim": "name", "Kapasite": "capacity", "Kat": "floor"}
        rooms = self.system.get_all_rooms(sort_by=sort_map.get(sort_by, "name"))
        
        if not rooms:
            self.print_warning("Kayıtlı salon yok")
        else:
            print()
            print(f"{'ID':<8} {'İsim':<25} {'Kapasite':>10} {'Tür':<15} {'Kat':>5} {'Ücret':>10}")
            print("-" * 80)
            
            for room in rooms:
                status = self.color("●", 'green') if room.is_active else self.color("○", 'red')
                print(f"{status} {room.id:<6} {room.name:<25} {room.capacity:>10} "
                      f"{room.room_type.value:<15} {room.floor:>5} {room.hourly_rate:>10.0f} TL")
        
        self.pause()
    
    def add_room(self):
        """Yeni salon ekle"""
        self.print_section("Yeni Salon Ekle")
        
        room_id = self.get_input("Salon ID (boş bırakılırsa otomatik)")
        if not room_id:
            room_id = self.system.generate_id()
        
        name = self.get_input("Salon Adı")
        if not name:
            self.print_error("Salon adı zorunlu")
            self.pause()
            return
        
        capacity = self.get_int("Kapasite", default=10, min_val=1, max_val=1000)
        
        room_types = [rt.value for rt in RoomType]
        room_type = self.get_choice("Salon Türü", room_types)
        
        floor = self.get_int("Kat", default=1, min_val=-5, max_val=100)
        hourly_rate = self.get_int("Saatlik Ücret (TL)", default=100, min_val=0)
        
        amenities_input = self.get_input("Donanımlar (virgülle ayırın)", "projeksiyon, whiteboard")
        amenities = [a.strip() for a in amenities_input.split(',') if a.strip()]
        
        room = Room(
            id=room_id,
            name=name,
            capacity=capacity,
            room_type=RoomType(room_type),
            floor=floor,
            amenities=amenities,
            hourly_rate=float(hourly_rate),
            is_active=True
        )
        
        if self.system.add_room(room):
            self.print_success(f"Salon eklendi: {name} (ID: {room_id})")
        else:
            self.print_error("Salon eklenemedi (ID zaten mevcut olabilir)")
        
        self.pause()
    
    def view_room(self):
        """Salon detayı görüntüle"""
        self.print_section("Salon Detayı")
        
        room_id = self.select_room()
        if not room_id:
            return
        
        room = self.system.get_room(room_id)
        if not room:
            self.print_error("Salon bulunamadı")
            self.pause()
            return
        
        print()
        print(f"  ID: {self.color(room.id, 'cyan')}")
        print(f"  İsim: {self.color(room.name, 'green', bold=True)}")
        print(f"  Kapasite: {room.capacity} kişi")
        print(f"  Tür: {room.room_type.value}")
        print(f"  Kat: {room.floor}")
        print(f"  Saatlik Ücret: {room.hourly_rate:.0f} TL")
        print(f"  Donanımlar: {', '.join(room.amenities) if room.amenities else 'Yok'}")
        print(f"  Durum: {self.color('Aktif', 'green') if room.is_active else self.color('Pasif', 'red')}")
        
        # Bugünkü rezervasyonlar
        today_reservations = self.system.get_reservations_by_room(room_id, date.today())
        if today_reservations:
            print()
            print(self.color("  Bugünkü Rezervasyonlar:", 'yellow'))
            for res in today_reservations:
                print(f"    {res.start_time.strftime('%H:%M')}-{res.end_time.strftime('%H:%M')}: {res.title or res.customer_name}")
        
        self.pause()
    
    def edit_room(self):
        """Salon düzenle"""
        self.print_section("Salon Düzenle")
        
        room_id = self.select_room()
        if not room_id:
            return
        
        room = self.system.get_room(room_id)
        if not room:
            self.print_error("Salon bulunamadı")
            self.pause()
            return
        
        print(f"\nDüzenlenen: {self.color(room.name, 'green')}")
        print("(Değiştirmek istemediğiniz alanları boş bırakın)")
        
        name = self.get_input("Yeni İsim", room.name)
        capacity = self.get_int("Yeni Kapasite", default=room.capacity, min_val=1)
        hourly_rate = self.get_int("Yeni Ücret", default=int(room.hourly_rate), min_val=0)
        
        updates = {}
        if name != room.name:
            updates['name'] = name
        if capacity != room.capacity:
            updates['capacity'] = capacity
        if hourly_rate != room.hourly_rate:
            updates['hourly_rate'] = float(hourly_rate)
        
        if updates:
            if self.system.update_room(room_id, **updates):
                self.print_success("Salon güncellendi")
            else:
                self.print_error("Güncelleme başarısız")
        else:
            self.print_info("Değişiklik yapılmadı")
        
        self.pause()
    
    def delete_room(self):
        """Salon sil"""
        self.print_section("Salon Sil")
        
        room_id = self.select_room()
        if not room_id:
            return
        
        room = self.system.get_room(room_id)
        if not room:
            self.print_error("Salon bulunamadı")
            self.pause()
            return
        
        self.print_warning(f"Silinecek salon: {room.name}")
        
        if self.confirm("Bu salonu silmek istediğinize emin misiniz?"):
            if self.system.delete_room(room_id):
                self.print_success("Salon silindi")
            else:
                self.print_error("Salon silinemedi (aktif rezervasyonları olabilir)")
        
        self.pause()
    
    def search_rooms(self):
        """Salon ara"""
        self.print_section("Salon Ara")
        
        capacity = self.get_int("Minimum kapasite", default=0, min_val=0)
        
        room_types = ["Tümü"] + [rt.value for rt in RoomType]
        type_choice = self.get_choice("Salon türü", room_types)
        room_type = None if type_choice == "Tümü" else RoomType(type_choice)
        
        results = self.system.search_rooms(
            capacity=capacity if capacity > 0 else None,
            room_type=room_type
        )
        
        if not results:
            self.print_warning("Kriterlere uygun salon bulunamadı")
        else:
            print()
            print(f"{'İsim':<25} {'Kapasite':>10} {'Tür':<15} {'Ücret':>10}")
            print("-" * 65)
            
            for room in results:
                print(f"{room.name:<25} {room.capacity:>10} {room.room_type.value:<15} {room.hourly_rate:>10.0f} TL")
        
        self.pause()
    
    def room_connections(self):
        """Salon bağlantıları"""
        self.print_section("Salon Bağlantıları ve Yol Bulma")
        
        print()
        print(self.color("  1.", 'cyan') + " Bağlantı Ekle")
        print(self.color("  2.", 'cyan') + " En Kısa Yol Bul")
        print(self.color("  0.", 'yellow') + " Geri")
        
        choice = self.get_int("\nSeçiminiz", min_val=0, max_val=2)
        
        if choice == 1:
            print("\nBağlantı eklenecek salonları seçin:")
            room1 = self.select_room("Salon 1")
            room2 = self.select_room("Salon 2")
            
            if room1 and room2:
                distance = self.get_int("Mesafe (metre)", default=10, min_val=1)
                if self.system.connect_rooms(room1, room2, distance):
                    self.print_success(f"Bağlantı eklendi: {room1} <-> {room2} ({distance}m)")
                else:
                    self.print_error("Bağlantı eklenemedi")
        
        elif choice == 2:
            print("\nYol aranacak salonları seçin:")
            start = self.select_room("Başlangıç")
            end = self.select_room("Hedef")
            
            if start and end:
                path, distance = self.system.find_shortest_path(start, end)
                if path:
                    print(f"\nEn kısa yol ({distance:.0f}m):")
                    print(f"  {' -> '.join(path)}")
                else:
                    self.print_warning("Yol bulunamadı")
        
        self.pause()
    
    def select_room(self, prompt: str = "Salon seçin") -> Optional[str]:
        """Salon seçim yardımcısı"""
        rooms = self.system.get_all_rooms()
        
        if not rooms:
            self.print_warning("Kayıtlı salon yok")
            return None
        
        print()
        for i, room in enumerate(rooms, 1):
            status = "●" if room.is_active else "○"
            print(f"  {self.color(str(i), 'cyan')}. {status} {room.name} (Kapasite: {room.capacity})")
        
        choice = self.get_int(f"\n{prompt}", min_val=1, max_val=len(rooms))
        return rooms[choice - 1].id if choice else None
    
    # ==================== REZERVASYON MENÜSÜ ====================
    
    def reservation_menu(self):
        """Rezervasyon yönetimi menüsü"""
        while True:
            self.clear_screen()
            self.print_header("REZERVASYON YÖNETİMİ")
            
            print()
            print(self.color("  1.", 'cyan') + " Yeni Rezervasyon")
            print(self.color("  2.", 'cyan') + " Rezervasyonları Listele")
            print(self.color("  3.", 'cyan') + " Rezervasyon Detayı")
            print(self.color("  4.", 'cyan') + " Rezervasyon Güncelle")
            print(self.color("  5.", 'cyan') + " Rezervasyon İptal")
            print(self.color("  6.", 'cyan') + " Müsait Zamanları Gör")
            print(self.color("  7.", 'cyan') + " Çakışma Kontrolü")
            print(self.color("  0.", 'yellow') + " Ana Menüye Dön")
            
            choice = self.get_int("\nSeçiminiz", min_val=0, max_val=7)
            
            if choice == 0:
                break
            elif choice == 1:
                self.create_reservation()
            elif choice == 2:
                self.list_reservations()
            elif choice == 3:
                self.view_reservation()
            elif choice == 4:
                self.update_reservation()
            elif choice == 5:
                self.cancel_reservation()
            elif choice == 6:
                self.show_available_slots()
            elif choice == 7:
                self.check_conflicts()
    
    def create_reservation(self):
        """Yeni rezervasyon oluştur"""
        self.print_section("Yeni Rezervasyon")
        
        # Salon seç
        room_id = self.select_room()
        if not room_id:
            return
        
        room = self.system.get_room(room_id)
        
        # Müşteri bilgileri
        customer_name = self.get_input("Müşteri Adı")
        if not customer_name:
            self.print_error("Müşteri adı zorunlu")
            self.pause()
            return
        
        customer_email = self.get_input("E-posta")
        title = self.get_input("Toplantı Başlığı", "Rezervasyon")
        attendees = self.get_int("Katılımcı Sayısı", default=1, min_val=1, max_val=room.capacity)
        
        # Tarih ve saat
        res_date = self.get_date("Tarih", date.today())
        start_time = self.get_time("Başlangıç Saati", "09:00")
        end_time = self.get_time("Bitiş Saati", "10:00")
        
        # Öncelik
        priority_options = ["VIP (1)", "Normal (2)", "Düşük (3)"]
        priority_choice = self.get_choice("Öncelik", priority_options)
        priority = int(priority_choice.split('(')[1].rstrip(')'))
        
        # DateTime oluştur
        start_parts = start_time.split(':')
        end_parts = end_time.split(':')
        
        start_dt = datetime.combine(res_date, datetime.min.time().replace(
            hour=int(start_parts[0]), minute=int(start_parts[1])))
        end_dt = datetime.combine(res_date, datetime.min.time().replace(
            hour=int(end_parts[0]), minute=int(end_parts[1])))
        
        if end_dt <= start_dt:
            self.print_error("Bitiş saati başlangıçtan sonra olmalı")
            self.pause()
            return
        
        reservation = Reservation(
            id=self.system.generate_id(),
            room_id=room_id,
            customer_name=customer_name,
            customer_email=customer_email or "",
            start_time=start_dt,
            end_time=end_dt,
            status=ReservationStatus.CONFIRMED,
            priority=priority,
            title=title,
            attendees=attendees
        )
        
        success, message = self.system.create_reservation(reservation)
        
        if success:
            self.print_success(message)
        else:
            self.print_error(message)
            
            # Alternatif öner
            if "Çakışma" in message:
                if self.confirm("Alternatif zamanları görmek ister misiniz?"):
                    duration = int((end_dt - start_dt).total_seconds() / 60)
                    alternatives = self.system.suggest_alternatives(room_id, start_dt, duration)
                    
                    if alternatives:
                        print("\nAlternatif öneriler:")
                        for i, alt in enumerate(alternatives[:5], 1):
                            print(f"  {i}. {alt['room_name']} - "
                                  f"{alt['start'].strftime('%d/%m %H:%M')} - "
                                  f"{alt['end'].strftime('%H:%M')}")
        
        self.pause()
    
    def list_reservations(self):
        """Rezervasyonları listele"""
        self.print_section("Rezervasyon Listesi")
        
        print()
        print(self.color("  1.", 'cyan') + " Bugünkü rezervasyonlar")
        print(self.color("  2.", 'cyan') + " Belirli bir tarih")
        print(self.color("  3.", 'cyan') + " Belirli bir salon")
        print(self.color("  4.", 'cyan') + " Yaklaşan rezervasyonlar")
        
        choice = self.get_int("\nSeçiminiz", min_val=1, max_val=4)
        
        reservations = []
        
        if choice == 1:
            reservations = self.system.get_reservations_by_date(date.today())
            title = "Bugünkü Rezervasyonlar"
        elif choice == 2:
            target_date = self.get_date("Tarih")
            reservations = self.system.get_reservations_by_date(target_date)
            title = f"{target_date} Rezervasyonları"
        elif choice == 3:
            room_id = self.select_room()
            if room_id:
                reservations = self.system.get_reservations_by_room(room_id)
                room = self.system.get_room(room_id)
                title = f"{room.name} Rezervasyonları"
        elif choice == 4:
            reservations = self.system.get_upcoming_reservations(20)
            title = "Yaklaşan Rezervasyonlar"
        
        if not reservations:
            self.print_warning("Rezervasyon bulunamadı")
        else:
            print(f"\n{self.color(title, 'yellow')} ({len(reservations)} adet)")
            print()
            print(f"{'ID':<10} {'Tarih':<12} {'Saat':<13} {'Salon':<20} {'Müşteri':<20} {'Durum':<12}")
            print("-" * 90)
            
            for res in reservations:
                room = self.system.get_room(res.room_id)
                room_name = room.name[:18] if room else res.room_id
                
                status_colors = {
                    ReservationStatus.CONFIRMED: 'green',
                    ReservationStatus.PENDING: 'yellow',
                    ReservationStatus.CANCELLED: 'red',
                    ReservationStatus.COMPLETED: 'blue'
                }
                status_color = status_colors.get(res.status, 'white')
                
                print(f"{res.id:<10} {res.start_time.strftime('%Y-%m-%d'):<12} "
                      f"{res.start_time.strftime('%H:%M')}-{res.end_time.strftime('%H:%M'):<7} "
                      f"{room_name:<20} {res.customer_name[:18]:<20} "
                      f"{self.color(res.status.value, status_color):<12}")
        
        self.pause()
    
    def view_reservation(self):
        """Rezervasyon detayı"""
        self.print_section("Rezervasyon Detayı")
        
        res_id = self.get_input("Rezervasyon ID")
        if not res_id:
            return
        
        reservation = self.system.get_reservation(res_id)
        if not reservation:
            self.print_error("Rezervasyon bulunamadı")
            self.pause()
            return
        
        room = self.system.get_room(reservation.room_id)
        
        print()
        print(f"  ID: {self.color(reservation.id, 'cyan')}")
        print(f"  Başlık: {self.color(reservation.title or 'Belirtilmemiş', 'green', bold=True)}")
        print(f"  Salon: {room.name if room else reservation.room_id}")
        print(f"  Müşteri: {reservation.customer_name}")
        print(f"  E-posta: {reservation.customer_email}")
        print(f"  Tarih: {reservation.start_time.strftime('%Y-%m-%d')}")
        print(f"  Saat: {reservation.start_time.strftime('%H:%M')} - {reservation.end_time.strftime('%H:%M')}")
        print(f"  Süre: {reservation.duration_minutes} dakika")
        print(f"  Katılımcı: {reservation.attendees} kişi")
        
        priority_names = {1: 'VIP', 2: 'Normal', 3: 'Düşük'}
        print(f"  Öncelik: {priority_names.get(reservation.priority, 'Normal')}")
        
        status_colors = {
            ReservationStatus.CONFIRMED: 'green',
            ReservationStatus.PENDING: 'yellow',
            ReservationStatus.CANCELLED: 'red',
            ReservationStatus.COMPLETED: 'blue'
        }
        print(f"  Durum: {self.color(reservation.status.value, status_colors.get(reservation.status, 'white'))}")
        print(f"  Oluşturma: {reservation.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        if room:
            print(f"\n  Tahmini Ücret: {reservation.duration_hours * room.hourly_rate:.0f} TL")
        
        self.pause()
    
    def update_reservation(self):
        """Rezervasyon güncelle"""
        self.print_section("Rezervasyon Güncelle")
        
        res_id = self.get_input("Rezervasyon ID")
        if not res_id:
            return
        
        reservation = self.system.get_reservation(res_id)
        if not reservation:
            self.print_error("Rezervasyon bulunamadı")
            self.pause()
            return
        
        print(f"\nGüncellenen: {self.color(reservation.title or reservation.customer_name, 'green')}")
        print("(Değiştirmek istemediğiniz alanları boş bırakın)")
        
        title = self.get_input("Yeni Başlık", reservation.title)
        attendees = self.get_int("Yeni Katılımcı Sayısı", default=reservation.attendees, min_val=1)
        
        updates = {}
        if title != reservation.title:
            updates['title'] = title
        if attendees != reservation.attendees:
            updates['attendees'] = attendees
        
        if updates:
            success, message = self.system.update_reservation(res_id, **updates)
            if success:
                self.print_success(message)
            else:
                self.print_error(message)
        else:
            self.print_info("Değişiklik yapılmadı")
        
        self.pause()
    
    def cancel_reservation(self):
        """Rezervasyon iptal"""
        self.print_section("Rezervasyon İptal")
        
        res_id = self.get_input("Rezervasyon ID")
        if not res_id:
            return
        
        reservation = self.system.get_reservation(res_id)
        if not reservation:
            self.print_error("Rezervasyon bulunamadı")
            self.pause()
            return
        
        print(f"\nİptal edilecek: {reservation.title or reservation.customer_name}")
        print(f"  Tarih: {reservation.start_time.strftime('%Y-%m-%d %H:%M')}")
        
        if self.confirm("Bu rezervasyonu iptal etmek istediğinize emin misiniz?"):
            reason = self.get_input("İptal nedeni (opsiyonel)")
            success, message = self.system.cancel_reservation(res_id, reason)
            
            if success:
                self.print_success(message)
            else:
                self.print_error(message)
        
        self.pause()
    
    def show_available_slots(self):
        """Müsait zamanları göster"""
        self.print_section("Müsait Zaman Aralıkları")
        
        room_id = self.select_room()
        if not room_id:
            return
        
        target_date = self.get_date("Tarih", date.today())
        duration = self.get_int("Minimum süre (dakika)", default=30, min_val=15)
        
        start = datetime.combine(target_date, datetime.min.time().replace(hour=8))
        end = datetime.combine(target_date, datetime.min.time().replace(hour=20))
        
        available = self.system.find_available_slots(room_id, start, end, duration)
        
        room = self.system.get_room(room_id)
        
        if not available:
            self.print_warning(f"{room.name} için {target_date} tarihinde uygun slot yok")
        else:
            print(f"\n{self.color(room.name, 'green')} - {target_date}")
            print(f"Minimum {duration} dakikalık müsait aralıklar:\n")
            
            for slot in available:
                print(f"  {self.color('●', 'green')} {slot['start'].strftime('%H:%M')} - "
                      f"{slot['end'].strftime('%H:%M')} ({slot['duration_minutes']} dk)")
        
        self.pause()
    
    def check_conflicts(self):
        """Çakışma kontrolü"""
        self.print_section("Çakışma Kontrolü")
        
        room_id = self.select_room()
        if not room_id:
            return
        
        res_date = self.get_date("Tarih", date.today())
        start_time = self.get_time("Başlangıç Saati", "09:00")
        end_time = self.get_time("Bitiş Saati", "10:00")
        
        start_parts = start_time.split(':')
        end_parts = end_time.split(':')
        
        start_dt = datetime.combine(res_date, datetime.min.time().replace(
            hour=int(start_parts[0]), minute=int(start_parts[1])))
        end_dt = datetime.combine(res_date, datetime.min.time().replace(
            hour=int(end_parts[0]), minute=int(end_parts[1])))
        
        conflicts = self.system.check_conflict(room_id, start_dt, end_dt)
        
        if not conflicts:
            self.print_success("Çakışma yok! Bu zaman aralığı müsait.")
        else:
            self.print_warning(f"{len(conflicts)} çakışan rezervasyon bulundu:")
            print()
            
            for res in conflicts:
                print(f"  {self.color('●', 'red')} {res.start_time.strftime('%H:%M')}-"
                      f"{res.end_time.strftime('%H:%M')}: {res.title or res.customer_name}")
        
        self.pause()
    
    # ==================== ARAMA MENÜSÜ ====================
    
    def search_menu(self):
        """Arama menüsü"""
        self.clear_screen()
        self.print_header("ARAMA VE SORGULAMA")
        
        print()
        print(self.color("  1.", 'cyan') + " Metin Araması")
        print(self.color("  2.", 'cyan') + " Müşteri Rezervasyonları")
        print(self.color("  0.", 'yellow') + " Ana Menüye Dön")
        
        choice = self.get_int("\nSeçiminiz", min_val=0, max_val=2)
        
        if choice == 1:
            query = self.get_input("Arama terimi")
            if query:
                results = self.system.search_reservations(query)
                
                if not results:
                    self.print_warning("Sonuç bulunamadı")
                else:
                    print(f"\n{len(results)} sonuç bulundu:\n")
                    
                    for res in results[:20]:
                        room = self.system.get_room(res.room_id)
                        print(f"  [{res.id}] {res.start_time.strftime('%Y-%m-%d')} - "
                              f"{res.customer_name} - {room.name if room else res.room_id}")
        
        elif choice == 2:
            email = self.get_input("Müşteri E-postası")
            if email:
                results = self.system.get_reservations_by_customer(email)
                
                if not results:
                    self.print_warning("Bu müşteriye ait rezervasyon yok")
                else:
                    print(f"\n{email} için {len(results)} rezervasyon:\n")
                    
                    for res in results:
                        room = self.system.get_room(res.room_id)
                        status_symbol = "✓" if res.status == ReservationStatus.CONFIRMED else "○"
                        print(f"  {status_symbol} [{res.id}] {res.start_time.strftime('%Y-%m-%d %H:%M')} - "
                              f"{room.name if room else res.room_id} - {res.title}")
        
        self.pause()
    
    # ==================== RAPOR MENÜSÜ ====================
    
    def report_menu(self):
        """Rapor menüsü"""
        self.clear_screen()
        self.print_header("RAPORLAR")
        
        print()
        print(self.color("  1.", 'cyan') + " Günlük Rapor")
        print(self.color("  2.", 'cyan') + " Salon Kullanım Oranı")
        print(self.color("  3.", 'cyan') + " Sistem İstatistikleri")
        print(self.color("  4.", 'cyan') + " Raporu CSV Olarak Dışa Aktar")
        print(self.color("  0.", 'yellow') + " Ana Menüye Dön")
        
        choice = self.get_int("\nSeçiminiz", min_val=0, max_val=4)
        
        if choice == 1:
            target_date = self.get_date("Rapor tarihi", date.today())
            report = self.system.get_daily_report(target_date)
            
            print(f"\n{self.color(f'Günlük Rapor - {target_date}', 'yellow', bold=True)}")
            print()
            print(f"  Toplam Rezervasyon: {self.color(str(report['total_reservations']), 'green')}")
            revenue_str = f"{report['total_revenue']:.0f} TL"
            print(f"  Toplam Gelir: {self.color(revenue_str, 'green')}")
            
            if report['by_room']:
                print(f"\n  {self.color('Salon Bazlı:', 'cyan')}")
                for room_name, data in report['by_room'].items():
                    print(f"    {room_name}: {data['count']} rez., {data['minutes']} dk, {data['revenue']:.0f} TL")
        
        elif choice == 2:
            room_id = self.select_room()
            if room_id:
                start = self.get_date("Başlangıç tarihi", date.today() - timedelta(days=7))
                end = self.get_date("Bitiş tarihi", date.today())
                
                util = self.system.get_room_utilization(room_id, start, end)
                
                room_name = util['room_name']
                print(f"\n{self.color(f'Kullanım Raporu - {room_name}', 'yellow', bold=True)}")
                print(f"  Dönem: {start} - {end}")
                print()
                print(f"  Toplam Müsait: {util['total_available_minutes']} dk")
                print(f"  Kullanılan: {util['used_minutes']} dk")
                util_str = f"{util['utilization_percent']}%"
                print(f"  Kullanım Oranı: {self.color(util_str, 'green')}")
                print(f"  Rezervasyon Sayısı: {util['reservation_count']}")
        
        elif choice == 3:
            stats = self.system.get_statistics()
            
            print(f"\n{self.color('Sistem İstatistikleri', 'yellow', bold=True)}")
            print()
            print(f"  Toplam Salon: {self.color(str(stats['total_rooms']), 'cyan')}")
            print(f"  Aktif Salon: {self.color(str(stats['active_rooms']), 'green')}")
            print(f"  Toplam Rezervasyon: {self.color(str(stats['total_reservations']), 'cyan')}")
            print(f"  Aktif Rezervasyon: {self.color(str(stats['active_reservations']), 'green')}")
            print(f"  Bekleme Listesi: {self.color(str(stats['waiting_list_size']), 'yellow')}")
            print(f"  Geri Alınabilir: {stats['undo_available']}")
            print(f"  Yinelenebilir: {stats['redo_available']}")
        
        elif choice == 4:
            target_date = self.get_date("Rapor tarihi", date.today())
            if self.data_manager.export_daily_report_csv(self.system, target_date):
                self.print_success(f"Rapor dışa aktarıldı: {self.data_manager.data_dir}")
            else:
                self.print_error("Rapor dışa aktarılamadı")
        
        self.pause()
    
    # ==================== BEKLEME LİSTESİ MENÜSÜ ====================
    
    def waiting_list_menu(self):
        """Bekleme listesi menüsü"""
        self.clear_screen()
        self.print_header("BEKLEME LİSTESİ")
        
        print()
        print(self.color("  1.", 'cyan') + " Listeyi Görüntüle")
        print(self.color("  2.", 'cyan') + " Listeye Ekle")
        print(self.color("  3.", 'cyan') + " Listeden Çıkar")
        print(self.color("  4.", 'cyan') + " Sıradakini Çağır")
        print(self.color("  0.", 'yellow') + " Ana Menüye Dön")
        
        choice = self.get_int("\nSeçiminiz", min_val=0, max_val=4)
        
        if choice == 1:
            entries = self.system.get_waiting_list()
            
            if not entries:
                self.print_info("Bekleme listesi boş")
            else:
                print(f"\n{len(entries)} kişi bekliyor:\n")
                
                for i, entry in enumerate(entries, 1):
                    priority_names = {1: 'VIP', 2: 'Normal', 3: 'Düşük'}
                    priority = priority_names.get(entry.priority, 'Normal')
                    pref = entry.room_preference or "Herhangi"
                    
                    print(f"  {self.color(str(i), 'cyan')}. {entry.customer_name} "
                          f"(Öncelik: {priority}, Tercih: {pref})")
        
        elif choice == 2:
            customer_id = self.system.generate_id()
            customer_name = self.get_input("Müşteri Adı")
            
            if customer_name:
                room_id = self.select_room("Salon Tercihi (opsiyonel)")
                
                priority_options = ["VIP (1)", "Normal (2)", "Düşük (3)"]
                priority_choice = self.get_choice("Öncelik", priority_options)
                priority = int(priority_choice.split('(')[1].rstrip(')'))
                
                if self.system.add_to_waiting_list(customer_id, customer_name, room_id, priority):
                    pos = self.system.get_waiting_list_position(customer_id)
                    self.print_success(f"{customer_name} bekleme listesine eklendi (Sıra: {pos})")
                else:
                    self.print_error("Eklenemedi")
        
        elif choice == 3:
            entries = self.system.get_waiting_list()
            if entries:
                print("\nÇıkarılacak müşteriyi seçin:")
                for i, entry in enumerate(entries, 1):
                    print(f"  {i}. {entry.customer_name}")
                
                idx = self.get_int("Seçim", min_val=1, max_val=len(entries))
                if idx:
                    if self.system.remove_from_waiting_list(entries[idx-1].customer_id):
                        self.print_success(f"{entries[idx-1].customer_name} listeden çıkarıldı")
            else:
                self.print_info("Bekleme listesi boş")
        
        elif choice == 4:
            entries = self.system.get_waiting_list()
            if entries:
                next_customer = entries[0]
                self.print_info(f"Sıradaki: {next_customer.customer_name}")
                
                if self.confirm("Bu müşteriyi çağırmak istiyor musunuz?"):
                    self.system.remove_from_waiting_list(next_customer.customer_id)
                    self.print_success(f"{next_customer.customer_name} çağrıldı ve listeden çıkarıldı")
            else:
                self.print_info("Bekleme listesi boş")
        
        self.pause()
    
    # ==================== VERİ MENÜSÜ ====================
    
    def data_menu(self):
        """Veri işlemleri menüsü"""
        self.clear_screen()
        self.print_header("VERİ İŞLEMLERİ")
        
        print()
        print(self.color("  1.", 'cyan') + " Verileri Kaydet")
        print(self.color("  2.", 'cyan') + " Yedek Oluştur")
        print(self.color("  3.", 'cyan') + " Yedekten Geri Yükle")
        print(self.color("  4.", 'cyan') + " CSV Dışa Aktar")
        print(self.color("  5.", 'cyan') + " Örnek Veri Oluştur")
        print(self.color("  0.", 'yellow') + " Ana Menüye Dön")
        
        choice = self.get_int("\nSeçiminiz", min_val=0, max_val=5)
        
        if choice == 1:
            if self.data_manager.save_system_state(self.system):
                self.print_success(f"Veriler kaydedildi: {self.data_manager.data_dir}")
            else:
                self.print_error("Kaydetme başarısız")
        
        elif choice == 2:
            backup_file = self.data_manager.create_backup(self.system)
            self.print_success(f"Yedek oluşturuldu: {backup_file}")
        
        elif choice == 3:
            backup_dir = self.data_manager.data_dir / "backups"
            if backup_dir.exists():
                backups = list(backup_dir.glob("backup_*.json"))
                if backups:
                    print("\nMevcut yedekler:")
                    for i, b in enumerate(sorted(backups, reverse=True)[:10], 1):
                        print(f"  {i}. {b.name}")
                    
                    idx = self.get_int("Seçim", min_val=1, max_val=len(backups))
                    if idx:
                        backup_file = sorted(backups, reverse=True)[idx-1]
                        if self.confirm("Mevcut veriler silinecek. Devam?"):
                            if self.data_manager.restore_from_backup(str(backup_file), self.system):
                                self.print_success("Yedekten geri yüklendi")
                            else:
                                self.print_error("Geri yükleme başarısız")
                else:
                    self.print_warning("Yedek bulunamadı")
            else:
                self.print_warning("Yedek klasörü bulunamadı")
        
        elif choice == 4:
            rooms = self.system.get_all_rooms()
            reservations = list(self.system._reservations.values())
            room_dict = {r.id: r for r in rooms}
            
            self.data_manager.export_rooms_csv(rooms)
            self.data_manager.export_reservations_csv(reservations, room_dict)
            self.print_success(f"CSV dosyaları oluşturuldu: {self.data_manager.data_dir}")
        
        elif choice == 5:
            if self.confirm("Mevcut verilere örnek veriler eklenecek. Devam?"):
                self.data_manager.create_sample_data(self.system)
                self.print_success("Örnek veriler oluşturuldu")
        
        self.pause()
    
    # ==================== UNDO/REDO MENÜSÜ ====================
    
    def undo_redo_menu(self):
        """Geri al / Yinele menüsü"""
        self.clear_screen()
        self.print_header("GERİ AL / YİNELE")
        
        print()
        
        if self.system.can_undo():
            print(f"  Geri alınabilir: {self.color(self.system.get_undo_description(), 'yellow')}")
        else:
            print(f"  Geri alınabilir işlem yok")
        
        if self.system.can_redo():
            print(f"  Yinelenebilir: {self.color(self.system.get_redo_description(), 'blue')}")
        else:
            print(f"  Yinelenebilir işlem yok")
        
        print()
        print(self.color("  1.", 'cyan') + " Geri Al (Undo)")
        print(self.color("  2.", 'cyan') + " Yinele (Redo)")
        print(self.color("  0.", 'yellow') + " Ana Menüye Dön")
        
        choice = self.get_int("\nSeçiminiz", min_val=0, max_val=2)
        
        if choice == 1:
            result = self.system.undo()
            if result:
                self.print_success(result)
            else:
                self.print_warning("Geri alınacak işlem yok")
        
        elif choice == 2:
            result = self.system.redo()
            if result:
                self.print_success(result)
            else:
                self.print_warning("Yinelenecek işlem yok")
        
        self.pause()


def main():
    """Ana fonksiyon"""
    print("\n" + "=" * 60)
    print("   SALON REZERVASYON SİSTEMİ")
    print("   Veri Yapıları ve Algoritmalar Projesi")
    print("=" * 60)
    
    cli = CLI()
    
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\nProgram sonlandırıldı.")
        cli.data_manager.save_system_state(cli.system)


if __name__ == "__main__":
    main()
