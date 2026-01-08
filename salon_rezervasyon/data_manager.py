"""
JSON/CSV Import-Export Modülü
=============================
Veri kaydetme, yükleme ve dışa aktarma işlemleri.

Desteklenen formatlar:
- JSON: Tam sistem verisi
- CSV: Tablo formatında raporlar
"""

import json
import csv
import os
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from pathlib import Path

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reservation_system import (
    ReservationSystem, Room, Reservation, 
    RoomType, ReservationStatus
)


class DataManager:
    """
    Veri Yöneticisi - JSON/CSV okuma-yazma işlemleri
    """
    
    def __init__(self, data_dir: str = None):
        """
        Args:
            data_dir: Veri dosyalarının saklanacağı klasör
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "data")
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Varsayılan dosya adları
        self.rooms_file = self.data_dir / "rooms.json"
        self.reservations_file = self.data_dir / "reservations.json"
        self.config_file = self.data_dir / "config.json"
    
    # ==================== JSON İŞLEMLERİ ====================
    
    def save_rooms(self, rooms: List[Room], filepath: str = None) -> bool:
        """
        Salonları JSON dosyasına kaydet
        
        Args:
            rooms: Salon listesi
            filepath: Dosya yolu (opsiyonel)
        """
        filepath = Path(filepath) if filepath else self.rooms_file
        
        try:
            data = {
                "metadata": {
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "count": len(rooms)
                },
                "rooms": [room.to_dict() for room in rooms]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Hata: Salonlar kaydedilemedi - {e}")
            return False
    
    def load_rooms(self, filepath: str = None) -> List[Room]:
        """
        Salonları JSON dosyasından yükle
        
        Args:
            filepath: Dosya yolu (opsiyonel)
            
        Returns:
            Salon listesi
        """
        filepath = Path(filepath) if filepath else self.rooms_file
        
        if not filepath.exists():
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            rooms = []
            for room_data in data.get("rooms", []):
                try:
                    room = Room.from_dict(room_data)
                    rooms.append(room)
                except Exception as e:
                    print(f"Uyarı: Salon yüklenemedi - {e}")
            
            return rooms
        except Exception as e:
            print(f"Hata: Salonlar yüklenemedi - {e}")
            return []
    
    def save_reservations(self, reservations: List[Reservation], filepath: str = None) -> bool:
        """
        Rezervasyonları JSON dosyasına kaydet
        """
        filepath = Path(filepath) if filepath else self.reservations_file
        
        try:
            data = {
                "metadata": {
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "count": len(reservations)
                },
                "reservations": [res.to_dict() for res in reservations]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Hata: Rezervasyonlar kaydedilemedi - {e}")
            return False
    
    def load_reservations(self, filepath: str = None) -> List[Reservation]:
        """
        Rezervasyonları JSON dosyasından yükle
        """
        filepath = Path(filepath) if filepath else self.reservations_file
        
        if not filepath.exists():
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            reservations = []
            for res_data in data.get("reservations", []):
                try:
                    res = Reservation.from_dict(res_data)
                    reservations.append(res)
                except Exception as e:
                    print(f"Uyarı: Rezervasyon yüklenemedi - {e}")
            
            return reservations
        except Exception as e:
            print(f"Hata: Rezervasyonlar yüklenemedi - {e}")
            return []
    
    def save_system_state(self, system: ReservationSystem, prefix: str = "") -> bool:
        """
        Tüm sistem durumunu kaydet
        
        Args:
            system: Rezervasyon sistemi
            prefix: Dosya adı öneki (yedekleme için)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        rooms_path = self.data_dir / f"{prefix}rooms_{timestamp}.json" if prefix else self.rooms_file
        res_path = self.data_dir / f"{prefix}reservations_{timestamp}.json" if prefix else self.reservations_file
        
        rooms_saved = self.save_rooms(system.get_all_rooms(), rooms_path)
        
        # Tüm rezervasyonları al
        all_reservations = list(system._reservations.values())
        res_saved = self.save_reservations(all_reservations, res_path)
        
        return rooms_saved and res_saved
    
    def load_system_state(self, system: ReservationSystem) -> bool:
        """
        Sistem durumunu dosyalardan yükle
        
        Args:
            system: Doldurulacak rezervasyon sistemi
        """
        # Salonları yükle
        rooms = self.load_rooms()
        for room in rooms:
            system.add_room(room)
        
        # Rezervasyonları yükle
        reservations = self.load_reservations()
        for res in reservations:
            # Geçmiş rezervasyonları da yükle (çakışma kontrolü atla)
            system._reservations[res.id] = res
            system._reservation_tree.insert(res.id, res)
            
            if res.room_id in system._room_intervals:
                from data_structures.interval_tree import Interval
                interval = Interval(
                    int(res.start_time.timestamp() / 60),
                    int(res.end_time.timestamp() / 60),
                    res
                )
                system._room_intervals[res.room_id].insert(interval)
        
        print(f"Yüklendi: {len(rooms)} salon, {len(reservations)} rezervasyon")
        return True
    
    def create_backup(self, system: ReservationSystem) -> str:
        """
        Sistem yedeği oluştur
        
        Returns:
            Yedek dosya adı
        """
        backup_dir = self.data_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup_file = backup_dir / f"backup_{timestamp}.json"
        
        data = {
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "type": "full_backup"
            },
            "rooms": [room.to_dict() for room in system.get_all_rooms()],
            "reservations": [res.to_dict() for res in system._reservations.values()],
            "statistics": system.get_statistics()
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return str(backup_file)
    
    def restore_from_backup(self, backup_file: str, system: ReservationSystem) -> bool:
        """
        Yedekten geri yükle
        """
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Sistemi temizle
            system._rooms.clear()
            system._room_tree.clear()
            system._reservations.clear()
            system._reservation_tree.clear()
            system._room_intervals.clear()
            
            # Salonları yükle
            for room_data in data.get("rooms", []):
                room = Room.from_dict(room_data)
                system.add_room(room)
            
            # Rezervasyonları yükle
            for res_data in data.get("reservations", []):
                res = Reservation.from_dict(res_data)
                system.create_reservation(res)
            
            return True
        except Exception as e:
            print(f"Hata: Yedekten geri yükleme başarısız - {e}")
            return False
    
    # ==================== CSV İŞLEMLERİ ====================
    
    def export_rooms_csv(self, rooms: List[Room], filepath: str = None) -> bool:
        """
        Salonları CSV formatında dışa aktar
        """
        filepath = Path(filepath) if filepath else self.data_dir / "rooms_export.csv"
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Başlık satırı
                writer.writerow([
                    'ID', 'İsim', 'Kapasite', 'Tür', 'Kat', 
                    'Donanımlar', 'Saatlik Ücret', 'Aktif'
                ])
                
                # Veriler
                for room in rooms:
                    writer.writerow([
                        room.id,
                        room.name,
                        room.capacity,
                        room.room_type.value,
                        room.floor,
                        ', '.join(room.amenities),
                        room.hourly_rate,
                        'Evet' if room.is_active else 'Hayır'
                    ])
            
            return True
        except Exception as e:
            print(f"Hata: CSV dışa aktarma başarısız - {e}")
            return False
    
    def export_reservations_csv(self, reservations: List[Reservation], 
                                 rooms: Dict[str, Room] = None,
                                 filepath: str = None) -> bool:
        """
        Rezervasyonları CSV formatında dışa aktar
        """
        filepath = Path(filepath) if filepath else self.data_dir / "reservations_export.csv"
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Başlık satırı
                writer.writerow([
                    'ID', 'Salon', 'Müşteri', 'E-posta', 'Başlangıç', 'Bitiş',
                    'Süre (dk)', 'Durum', 'Öncelik', 'Başlık', 'Katılımcı',
                    'Oluşturma Tarihi'
                ])
                
                # Veriler
                for res in reservations:
                    room_name = res.room_id
                    if rooms and res.room_id in rooms:
                        room_name = rooms[res.room_id].name
                    
                    priority_map = {1: 'VIP', 2: 'Normal', 3: 'Düşük'}
                    
                    writer.writerow([
                        res.id,
                        room_name,
                        res.customer_name,
                        res.customer_email,
                        res.start_time.strftime('%Y-%m-%d %H:%M'),
                        res.end_time.strftime('%Y-%m-%d %H:%M'),
                        res.duration_minutes,
                        res.status.value,
                        priority_map.get(res.priority, 'Normal'),
                        res.title,
                        res.attendees,
                        res.created_at.strftime('%Y-%m-%d %H:%M')
                    ])
            
            return True
        except Exception as e:
            print(f"Hata: CSV dışa aktarma başarısız - {e}")
            return False
    
    def import_rooms_csv(self, filepath: str) -> List[Room]:
        """
        CSV dosyasından salonları içe aktar
        """
        rooms = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        room = Room(
                            id=row.get('ID', '').strip(),
                            name=row.get('İsim', row.get('Name', '')).strip(),
                            capacity=int(row.get('Kapasite', row.get('Capacity', 10))),
                            room_type=RoomType(row.get('Tür', row.get('Type', 'meeting')).lower()),
                            floor=int(row.get('Kat', row.get('Floor', 1))),
                            amenities=row.get('Donanımlar', row.get('Amenities', '')).split(','),
                            hourly_rate=float(row.get('Saatlik Ücret', row.get('HourlyRate', 0))),
                            is_active=row.get('Aktif', row.get('Active', 'Evet')).lower() in ['evet', 'yes', 'true', '1']
                        )
                        rooms.append(room)
                    except Exception as e:
                        print(f"Uyarı: Satır atlandı - {e}")
            
            return rooms
        except Exception as e:
            print(f"Hata: CSV içe aktarma başarısız - {e}")
            return []
    
    def import_reservations_csv(self, filepath: str, room_mapping: Dict[str, str] = None) -> List[Reservation]:
        """
        CSV dosyasından rezervasyonları içe aktar
        
        Args:
            filepath: CSV dosya yolu
            room_mapping: Salon adı -> ID eşlemesi
        """
        reservations = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        room_id = row.get('Salon', row.get('Room', ''))
                        if room_mapping and room_id in room_mapping:
                            room_id = room_mapping[room_id]
                        
                        priority_map = {'vip': 1, 'normal': 2, 'düşük': 3, 'low': 3}
                        priority = priority_map.get(
                            row.get('Öncelik', row.get('Priority', 'normal')).lower(), 
                            2
                        )
                        
                        res = Reservation(
                            id=row.get('ID', ReservationSystem.generate_id()),
                            room_id=room_id,
                            customer_name=row.get('Müşteri', row.get('Customer', '')).strip(),
                            customer_email=row.get('E-posta', row.get('Email', '')).strip(),
                            start_time=datetime.strptime(
                                row.get('Başlangıç', row.get('Start', '')), 
                                '%Y-%m-%d %H:%M'
                            ),
                            end_time=datetime.strptime(
                                row.get('Bitiş', row.get('End', '')), 
                                '%Y-%m-%d %H:%M'
                            ),
                            priority=priority,
                            title=row.get('Başlık', row.get('Title', '')).strip(),
                            attendees=int(row.get('Katılımcı', row.get('Attendees', 1)))
                        )
                        reservations.append(res)
                    except Exception as e:
                        print(f"Uyarı: Satır atlandı - {e}")
            
            return reservations
        except Exception as e:
            print(f"Hata: CSV içe aktarma başarısız - {e}")
            return []
    
    def export_daily_report_csv(self, system: ReservationSystem, 
                                target_date: date, filepath: str = None) -> bool:
        """
        Günlük raporu CSV olarak dışa aktar
        """
        filepath = Path(filepath) if filepath else self.data_dir / f"report_{target_date}.csv"
        
        report = system.get_daily_report(target_date)
        reservations = system.get_reservations_by_date(target_date)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Özet bilgiler
                writer.writerow(['Günlük Rapor', target_date.isoformat()])
                writer.writerow([])
                writer.writerow(['Toplam Rezervasyon', report['total_reservations']])
                writer.writerow(['Toplam Gelir (TL)', report['total_revenue']])
                writer.writerow([])
                
                # Salon bazlı özet
                writer.writerow(['Salon Bazlı Özet'])
                writer.writerow(['Salon', 'Rezervasyon Sayısı', 'Toplam Süre (dk)', 'Gelir (TL)'])
                for room_name, data in report['by_room'].items():
                    writer.writerow([room_name, data['count'], data['minutes'], data['revenue']])
                
                writer.writerow([])
                
                # Detaylı liste
                writer.writerow(['Detaylı Rezervasyon Listesi'])
                writer.writerow(['Saat', 'Salon', 'Müşteri', 'Başlık', 'Süre (dk)', 'Durum'])
                
                for res in reservations:
                    room = system.get_room(res.room_id)
                    writer.writerow([
                        res.start_time.strftime('%H:%M'),
                        room.name if room else res.room_id,
                        res.customer_name,
                        res.title,
                        res.duration_minutes,
                        res.status.value
                    ])
            
            return True
        except Exception as e:
            print(f"Hata: Rapor dışa aktarma başarısız - {e}")
            return False
    
    def export_utilization_report_csv(self, system: ReservationSystem,
                                      start_date: date, end_date: date,
                                      filepath: str = None) -> bool:
        """
        Kullanım oranı raporunu CSV olarak dışa aktar
        """
        filepath = Path(filepath) if filepath else self.data_dir / f"utilization_{start_date}_{end_date}.csv"
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                writer.writerow(['Salon Kullanım Oranı Raporu'])
                writer.writerow(['Dönem', f'{start_date} - {end_date}'])
                writer.writerow([])
                
                writer.writerow([
                    'Salon', 'Toplam Müsait (dk)', 'Kullanılan (dk)',
                    'Kullanım Oranı (%)', 'Rezervasyon Sayısı'
                ])
                
                for room in system.get_all_rooms():
                    util = system.get_room_utilization(room.id, start_date, end_date)
                    writer.writerow([
                        util['room_name'],
                        util['total_available_minutes'],
                        util['used_minutes'],
                        util['utilization_percent'],
                        util['reservation_count']
                    ])
            
            return True
        except Exception as e:
            print(f"Hata: Kullanım raporu dışa aktarma başarısız - {e}")
            return False
    
    # ==================== ÖRNEK VERİ ====================
    
    def create_sample_data(self, system: ReservationSystem) -> None:
        """
        Örnek veri oluştur (demo amaçlı)
        """
        from datetime import timedelta
        
        # Örnek salonlar
        sample_rooms = [
            Room("R001", "Toplantı Salonu A", 10, RoomType.MEETING, 1,
                 ["projeksiyon", "whiteboard"], 100.0),
            Room("R002", "Konferans Salonu", 50, RoomType.CONFERENCE, 2,
                 ["projeksiyon", "mikrofon", "kayıt sistemi"], 250.0),
            Room("R003", "Eğitim Odası 1", 20, RoomType.TRAINING, 1,
                 ["projeksiyon", "whiteboard", "bilgisayar"], 150.0),
            Room("R004", "Eğitim Odası 2", 15, RoomType.TRAINING, 1,
                 ["projeksiyon", "whiteboard"], 120.0),
            Room("R005", "Yönetim Salonu", 8, RoomType.EXECUTIVE, 3,
                 ["projeksiyon", "video konferans", "mini bar"], 200.0),
            Room("R006", "Sunum Salonu", 100, RoomType.AUDITORIUM, 0,
                 ["projeksiyon", "sahne", "mikrofon", "kayıt sistemi"], 500.0),
        ]
        
        for room in sample_rooms:
            system.add_room(room)
        
        # Salon bağlantıları
        connections = [
            ("R001", "R002", 30), ("R001", "R003", 15), ("R002", "R004", 20),
            ("R003", "R004", 10), ("R004", "R005", 45), ("R002", "R006", 60),
            ("R005", "R006", 40), ("R001", "R006", 80)
        ]
        
        for r1, r2, dist in connections:
            system.connect_rooms(r1, r2, dist)
        
        # Örnek rezervasyonlar (önümüzdeki 2 hafta)
        now = datetime.now()
        base_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        sample_reservations = [
            # Bugün
            ("R001", "Ahmet Yılmaz", "ahmet@example.com", 0, 9, 10, 30, "Proje Planlama", 8),
            ("R001", "Mehmet Demir", "mehmet@example.com", 0, 11, 12, 0, "Müşteri Görüşmesi", 5),
            ("R002", "Ayşe Kaya", "ayse@example.com", 0, 14, 17, 0, "Şirket Sunumu", 45),
            
            # Yarın
            ("R001", "Fatma Şahin", "fatma@example.com", 1, 9, 11, 0, "Sprint Review", 10),
            ("R003", "Can Öztürk", "can@example.com", 1, 10, 12, 0, "Python Eğitimi", 15),
            ("R005", "Zeynep Arslan", "zeynep@example.com", 1, 14, 15, 30, "Yönetim Toplantısı", 6),
            
            # 2 gün sonra
            ("R006", "Ali Yıldız", "ali@example.com", 2, 9, 12, 0, "Genel Kurul", 80),
            ("R002", "Deniz Kara", "deniz@example.com", 2, 14, 16, 0, "Ürün Lansmanı", 40),
            
            # Gelecek hafta
            ("R001", "Emre Çelik", "emre@example.com", 7, 10, 11, 30, "Haftalık Sync", 8),
            ("R003", "Selin Yılmaz", "selin@example.com", 7, 13, 17, 0, "Workshop", 18),
            ("R004", "Burak Demir", "burak@example.com", 8, 9, 12, 0, "Teknik Eğitim", 12),
        ]
        
        for room_id, name, email, day_offset, start_h, end_h, end_m, title, attendees in sample_reservations:
            res_date = base_date + timedelta(days=day_offset)
            
            res = Reservation(
                id=system.generate_id(),
                room_id=room_id,
                customer_name=name,
                customer_email=email,
                start_time=res_date.replace(hour=start_h, minute=0),
                end_time=res_date.replace(hour=end_h, minute=end_m),
                status=ReservationStatus.CONFIRMED,
                priority=2,
                title=title,
                attendees=attendees
            )
            
            success, _ = system.create_reservation(res)
            if not success:
                print(f"Uyarı: Örnek rezervasyon oluşturulamadı - {title}")
        
        # Bekleme listesi
        system.add_to_waiting_list("W001", "Hakan Yılmaz", "R001", priority=2)
        system.add_to_waiting_list("W002", "Elif Demir", "R002", priority=1)
        system.add_to_waiting_list("W003", "Murat Kaya", None, priority=3)
        
        print(f"Örnek veri oluşturuldu: {len(sample_rooms)} salon, {len(sample_reservations)} rezervasyon")


# Test
if __name__ == "__main__":
    print("=" * 60)
    print("Data Manager Test")
    print("=" * 60)
    
    # Sistem ve veri yöneticisi oluştur
    system = ReservationSystem()
    data_manager = DataManager()
    
    # Örnek veri oluştur
    print("\n--- Örnek Veri Oluşturuluyor ---")
    data_manager.create_sample_data(system)
    
    # JSON'a kaydet
    print("\n--- JSON Kaydetme ---")
    if data_manager.save_system_state(system):
        print(f"  Veriler kaydedildi: {data_manager.data_dir}")
    
    # CSV dışa aktar
    print("\n--- CSV Dışa Aktarma ---")
    
    rooms = system.get_all_rooms()
    if data_manager.export_rooms_csv(rooms):
        print(f"  Salonlar CSV: {data_manager.data_dir / 'rooms_export.csv'}")
    
    reservations = list(system._reservations.values())
    room_dict = {r.id: r for r in rooms}
    if data_manager.export_reservations_csv(reservations, room_dict):
        print(f"  Rezervasyonlar CSV: {data_manager.data_dir / 'reservations_export.csv'}")
    
    # Günlük rapor
    today = datetime.now().date()
    if data_manager.export_daily_report_csv(system, today):
        print(f"  Günlük rapor CSV: {data_manager.data_dir / f'report_{today}.csv'}")
    
    # Yedek oluştur
    print("\n--- Yedekleme ---")
    backup_file = data_manager.create_backup(system)
    print(f"  Yedek oluşturuldu: {backup_file}")
    
    # Yeni sistem oluştur ve yükle
    print("\n--- Veri Yükleme Testi ---")
    new_system = ReservationSystem()
    data_manager.load_system_state(new_system)
    
    print(f"  Yüklenen salonlar: {len(new_system.get_all_rooms())}")
    print(f"  Yüklenen rezervasyonlar: {len(new_system._reservations)}")
    
    # İstatistikler
    print("\n--- Sistem İstatistikleri ---")
    stats = new_system.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
