"""
Salon Rezervasyon Sistemi - Ana Modül
=====================================
Tüm veri yapılarını ve algoritmaları birleştiren ana iş mantığı.

Bu modül şunları içerir:
- Salon (Room) yönetimi
- Rezervasyon (Reservation) yönetimi
- Çakışma kontrolü ve çözümü
- Undo/Redo desteği
- Raporlama ve istatistikler
"""

from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid
import copy

# Veri yapılarını import et
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_structures.avl_tree import AVLTree
from data_structures.interval_tree import IntervalTree, Interval
from data_structures.heap import MinHeap, PriorityQueue
from data_structures.graph import Graph
from data_structures.sorting import quicksort, mergesort, heapsort, binary_search
from data_structures.stack_queue import Stack, Queue, UndoRedoManager, Action, ActionType
from data_structures.linked_list import LinkedList, WaitingList, WaitingEntry


class ReservationStatus(Enum):
    """Rezervasyon durumu"""
    PENDING = "pending"          # Onay bekliyor
    CONFIRMED = "confirmed"      # Onaylandı
    CANCELLED = "cancelled"      # İptal edildi
    COMPLETED = "completed"      # Tamamlandı
    NO_SHOW = "no_show"         # Gelmedi


class RoomType(Enum):
    """Salon türü"""
    MEETING = "meeting"         # Toplantı odası
    CONFERENCE = "conference"   # Konferans salonu
    TRAINING = "training"       # Eğitim salonu
    EXECUTIVE = "executive"     # Yönetim salonu
    AUDITORIUM = "auditorium"  # Konser/sunum salonu


@dataclass
class Room:
    """Salon bilgisi"""
    id: str
    name: str
    capacity: int
    room_type: RoomType
    floor: int = 1
    amenities: List[str] = field(default_factory=list)  # Projeksiyon, whiteboard vb.
    hourly_rate: float = 0.0
    is_active: bool = True
    
    def __hash__(self):
        return hash(self.id)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity,
            "room_type": self.room_type.value,
            "floor": self.floor,
            "amenities": self.amenities,
            "hourly_rate": self.hourly_rate,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Room':
        return cls(
            id=data["id"],
            name=data["name"],
            capacity=data["capacity"],
            room_type=RoomType(data["room_type"]),
            floor=data.get("floor", 1),
            amenities=data.get("amenities", []),
            hourly_rate=data.get("hourly_rate", 0.0),
            is_active=data.get("is_active", True)
        )


@dataclass
class Reservation:
    """Rezervasyon bilgisi"""
    id: str
    room_id: str
    customer_name: str
    customer_email: str
    start_time: datetime
    end_time: datetime
    status: ReservationStatus = ReservationStatus.PENDING
    priority: int = 2  # 1=VIP, 2=Normal, 3=Düşük
    title: str = ""
    description: str = ""
    attendees: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __hash__(self):
        return hash(self.id)
    
    @property
    def duration_minutes(self) -> int:
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    @property
    def duration_hours(self) -> float:
        return self.duration_minutes / 60
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "room_id": self.room_id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "status": self.status.value,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "attendees": self.attendees,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Reservation':
        return cls(
            id=data["id"],
            room_id=data["room_id"],
            customer_name=data["customer_name"],
            customer_email=data["customer_email"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            status=ReservationStatus(data.get("status", "pending")),
            priority=data.get("priority", 2),
            title=data.get("title", ""),
            description=data.get("description", ""),
            attendees=data.get("attendees", 1),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )


class ReservationSystem:
    """
    Ana Rezervasyon Sistemi
    
    Tüm veri yapılarını koordine eder:
    - AVL Tree: Rezervasyon ID'leri için hızlı erişim
    - Interval Tree: Çakışma kontrolü
    - Heap/PriorityQueue: Öncelik sıralaması
    - Graph: Salon bağlantıları ve yol bulma
    - Stack: Undo/Redo
    - Queue: Görev kuyruğu
    - LinkedList: Bekleme listesi
    """
    
    def __init__(self):
        self._rooms: Dict[str, Room] = {}
        self._room_tree = AVLTree()
        
        self._reservations: Dict[str, Reservation] = {}
        self._reservation_tree = AVLTree()
        
        self._room_intervals: Dict[str, IntervalTree] = {}
        self._pending_queue = PriorityQueue(min_priority=True)
        self._building_graph = Graph(directed=False)
        self._undo_manager = UndoRedoManager(max_history=100)
        self._waiting_list = WaitingList(on_available=self._notify_waiting_customer)
        self._action_log: List[dict] = []
    
    # ==================== SALON YÖNETİMİ ====================
    
    def add_room(self, room: Room) -> bool:
        """
        Yeni salon ekle
        
        Zaman Karmaşıklığı: O(log n) - AVL Tree ekleme
        """
        if room.id in self._rooms:
            return False
        
        self._rooms[room.id] = room
        self._room_tree.insert(room.id, room)
        self._room_intervals[room.id] = IntervalTree()
        self._building_graph.add_vertex(room.id, room)
        
        # Undo kaydı
        self._undo_manager.record_create("room", room.id, room.to_dict(), 
                                         f"Salon eklendi: {room.name}")
        
        self._log_action("add_room", room.id, f"Salon eklendi: {room.name}")
        return True
    
    def get_room(self, room_id: str) -> Optional[Room]:
        """
        Salon bilgisi al
        
        Zaman Karmaşıklığı: O(log n) - AVL Tree arama
        """
        return self._room_tree.search(room_id)
    
    def update_room(self, room_id: str, **kwargs) -> bool:
        """Salon bilgilerini güncelle"""
        room = self.get_room(room_id)
        if not room:
            return False
        
        old_state = room.to_dict()
        
        for key, value in kwargs.items():
            if hasattr(room, key):
                setattr(room, key, value)
        
        self._undo_manager.record_update("room", room_id, old_state, room.to_dict(),
                                         f"Salon güncellendi: {room.name}")
        
        self._log_action("update_room", room_id, f"Salon güncellendi: {room.name}")
        return True
    
    def delete_room(self, room_id: str) -> bool:
        """Salon sil (sadece rezervasyonu yoksa)"""
        room = self.get_room(room_id)
        if not room:
            return False
        
        # Aktif rezervasyon kontrolü
        interval_tree = self._room_intervals.get(room_id)
        if interval_tree and len(interval_tree) > 0:
            return False  # Rezervasyonları var
        
        old_state = room.to_dict()
        
        del self._rooms[room_id]
        self._room_tree.delete(room_id)
        del self._room_intervals[room_id]
        self._building_graph.remove_vertex(room_id)
        
        self._undo_manager.record_delete("room", room_id, old_state,
                                         f"Salon silindi: {room.name}")
        
        self._log_action("delete_room", room_id, f"Salon silindi: {room.name}")
        return True
    
    def get_all_rooms(self, sort_by: str = "name") -> List[Room]:
        """
        Tüm salonları listele
        
        Args:
            sort_by: Sıralama kriteri (name, capacity, floor)
        """
        rooms = list(self._rooms.values())
        
        if sort_by == "name":
            return mergesort(rooms, key=lambda r: r.name)
        elif sort_by == "capacity":
            return mergesort(rooms, key=lambda r: r.capacity, reverse=True)
        elif sort_by == "floor":
            return mergesort(rooms, key=lambda r: (r.floor, r.name))
        
        return rooms
    
    def search_rooms(self, capacity: int = None, room_type: RoomType = None,
                     amenities: List[str] = None) -> List[Room]:
        """Kriterlere göre salon ara"""
        results = []
        
        for room in self._rooms.values():
            if not room.is_active:
                continue
            
            if capacity and room.capacity < capacity:
                continue
            
            if room_type and room.room_type != room_type:
                continue
            
            if amenities:
                if not all(a in room.amenities for a in amenities):
                    continue
            
            results.append(room)
        
        return mergesort(results, key=lambda r: r.capacity)
    
    def connect_rooms(self, room1_id: str, room2_id: str, distance: float) -> bool:
        """İki salon arasında koridor bağlantısı ekle"""
        if room1_id not in self._rooms or room2_id not in self._rooms:
            return False
        
        self._building_graph.add_edge(room1_id, room2_id, distance)
        return True
    
    def find_shortest_path(self, from_room: str, to_room: str) -> Tuple[List[str], float]:
        """
        İki salon arasındaki en kısa yolu bul
        
        Zaman Karmaşıklığı: O((V + E) log V) - Dijkstra
        """
        path, distance = self._building_graph.dijkstra_path(from_room, to_room)
        
        # Salon isimlerini ekle
        named_path = []
        for room_id in path:
            room = self.get_room(room_id)
            named_path.append(room.name if room else room_id)
        
        return named_path, distance
    
    # ==================== REZERVASYON YÖNETİMİ ====================
    
    def create_reservation(self, reservation: Reservation) -> Tuple[bool, str]:
        """
        Yeni rezervasyon oluştur
        
        Returns:
            (başarılı, mesaj) tuple
            
        Zaman Karmaşıklığı: O(log n) - AVL ve Interval Tree işlemleri
        """
        # Salon kontrolü
        room = self.get_room(reservation.room_id)
        if not room:
            return False, "Salon bulunamadı"
        
        if not room.is_active:
            return False, "Salon aktif değil"
        
        # Kapasite kontrolü
        if reservation.attendees > room.capacity:
            return False, f"Katılımcı sayısı salon kapasitesini ({room.capacity}) aşıyor"
        
        # Çakışma kontrolü
        conflicts = self.check_conflict(reservation.room_id, 
                                        reservation.start_time,
                                        reservation.end_time)
        
        if conflicts:
            conflict_names = [c.title or c.customer_name for c in conflicts]
            return False, f"Çakışma var: {', '.join(conflict_names)}"
        
        # Rezervasyonu kaydet
        self._reservations[reservation.id] = reservation
        self._reservation_tree.insert(reservation.id, reservation)
        
        # Interval Tree'ye ekle
        interval = Interval(
            self._datetime_to_minutes(reservation.start_time),
            self._datetime_to_minutes(reservation.end_time),
            reservation
        )
        self._room_intervals[reservation.room_id].insert(interval)
        
        # Undo kaydı
        self._undo_manager.record_create("reservation", reservation.id, 
                                         reservation.to_dict(),
                                         f"Rezervasyon oluşturuldu: {reservation.title}")
        
        self._log_action("create_reservation", reservation.id, 
                        f"Rezervasyon: {reservation.customer_name} - {room.name}")
        
        return True, f"Rezervasyon başarıyla oluşturuldu (ID: {reservation.id})"
    
    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """
        Rezervasyon bilgisi al
        
        Zaman Karmaşıklığı: O(log n)
        """
        return self._reservation_tree.search(reservation_id)
    
    def update_reservation(self, reservation_id: str, **kwargs) -> Tuple[bool, str]:
        """Rezervasyon güncelle"""
        reservation = self.get_reservation(reservation_id)
        if not reservation:
            return False, "Rezervasyon bulunamadı"
        
        old_state = reservation.to_dict()
        old_room = reservation.room_id
        old_start = reservation.start_time
        old_end = reservation.end_time
        
        # Önce eski interval'ı kaldır
        old_interval = Interval(
            self._datetime_to_minutes(old_start),
            self._datetime_to_minutes(old_end),
            reservation
        )
        self._room_intervals[old_room].delete(old_interval)
        
        # Güncellemeleri uygula
        for key, value in kwargs.items():
            if hasattr(reservation, key):
                setattr(reservation, key, value)
        
        reservation.updated_at = datetime.now()
        
        # Yeni zaman için çakışma kontrolü
        if 'start_time' in kwargs or 'end_time' in kwargs or 'room_id' in kwargs:
            conflicts = self.check_conflict(reservation.room_id,
                                           reservation.start_time,
                                           reservation.end_time,
                                           exclude_id=reservation_id)
            
            if conflicts:
                # Geri al
                for key, value in old_state.items():
                    if hasattr(reservation, key):
                        if key in ['start_time', 'end_time', 'created_at', 'updated_at']:
                            setattr(reservation, key, datetime.fromisoformat(value))
                        elif key == 'status':
                            setattr(reservation, key, ReservationStatus(value))
                        else:
                            setattr(reservation, key, value)
                
                # Eski interval'ı geri ekle
                self._room_intervals[old_room].insert(old_interval)
                
                return False, "Çakışma var, güncelleme iptal edildi"
        
        # Yeni interval ekle
        new_interval = Interval(
            self._datetime_to_minutes(reservation.start_time),
            self._datetime_to_minutes(reservation.end_time),
            reservation
        )
        self._room_intervals[reservation.room_id].insert(new_interval)
        
        # Undo kaydı
        self._undo_manager.record_update("reservation", reservation_id,
                                         old_state, reservation.to_dict(),
                                         f"Rezervasyon güncellendi: {reservation.title}")
        
        self._log_action("update_reservation", reservation_id, 
                        f"Güncellendi: {reservation.customer_name}")
        
        return True, "Rezervasyon başarıyla güncellendi"
    
    def cancel_reservation(self, reservation_id: str, reason: str = "") -> Tuple[bool, str]:
        """Rezervasyon iptal et"""
        reservation = self.get_reservation(reservation_id)
        if not reservation:
            return False, "Rezervasyon bulunamadı"
        
        if reservation.status == ReservationStatus.CANCELLED:
            return False, "Rezervasyon zaten iptal edilmiş"
        
        old_state = reservation.to_dict()
        
        reservation.status = ReservationStatus.CANCELLED
        reservation.updated_at = datetime.now()
        
        # Interval'dan kaldır
        interval = Interval(
            self._datetime_to_minutes(reservation.start_time),
            self._datetime_to_minutes(reservation.end_time),
            reservation
        )
        self._room_intervals[reservation.room_id].delete(interval)
        
        # Undo kaydı
        self._undo_manager.record_update("reservation", reservation_id,
                                         old_state, reservation.to_dict(),
                                         f"Rezervasyon iptal edildi: {reservation.title}")
        
        # Bekleme listesine bildir
        self._waiting_list.notify_available(reservation.room_id)
        
        self._log_action("cancel_reservation", reservation_id,
                        f"İptal: {reservation.customer_name} - {reason}")
        
        return True, "Rezervasyon iptal edildi"
    
    def delete_reservation(self, reservation_id: str) -> bool:
        """Rezervasyonu tamamen sil"""
        reservation = self.get_reservation(reservation_id)
        if not reservation:
            return False
        
        old_state = reservation.to_dict()
        
        # Interval'dan kaldır
        interval = Interval(
            self._datetime_to_minutes(reservation.start_time),
            self._datetime_to_minutes(reservation.end_time),
            reservation
        )
        self._room_intervals[reservation.room_id].delete(interval)
        
        # Ağaçlardan kaldır
        del self._reservations[reservation_id]
        self._reservation_tree.delete(reservation_id)
        
        # Undo kaydı
        self._undo_manager.record_delete("reservation", reservation_id, old_state,
                                         f"Rezervasyon silindi: {reservation.title}")
        
        self._log_action("delete_reservation", reservation_id,
                        f"Silindi: {reservation.customer_name}")
        
        return True
    
    # ==================== ÇAKIŞMA YÖNETİMİ ====================
    
    def check_conflict(self, room_id: str, start_time: datetime, 
                       end_time: datetime, exclude_id: str = None) -> List[Reservation]:
        """
        Çakışma kontrolü yap
        
        Zaman Karmaşıklığı: O(log n + k) - k: çakışan sayısı
        """
        if room_id not in self._room_intervals:
            return []
        
        query_interval = Interval(
            self._datetime_to_minutes(start_time),
            self._datetime_to_minutes(end_time)
        )
        
        overlapping = self._room_intervals[room_id].find_overlapping(query_interval)
        
        conflicts = []
        for interval in overlapping:
            reservation = interval.data
            if reservation and (exclude_id is None or reservation.id != exclude_id):
                if reservation.status not in [ReservationStatus.CANCELLED, 
                                              ReservationStatus.COMPLETED]:
                    conflicts.append(reservation)
        
        return conflicts
    
    def suggest_alternatives(self, room_id: str, start_time: datetime, 
                            duration_minutes: int, search_days: int = 7) -> List[dict]:
        """
        Çakışma durumunda alternatif öner
        
        Returns:
            Alternatif slot listesi [{room, start, end}, ...]
        """
        alternatives = []
        duration = timedelta(minutes=duration_minutes)
        
        # Aynı salon için alternatif zamanlar
        for day_offset in range(search_days):
            check_date = start_time.date() + timedelta(days=day_offset)
            
            # Çalışma saatleri (09:00-18:00)
            day_start = datetime.combine(check_date, datetime.min.time().replace(hour=9))
            day_end = datetime.combine(check_date, datetime.min.time().replace(hour=18))
            
            available = self.find_available_slots(room_id, day_start, day_end, duration_minutes)
            
            for slot in available[:3]:  # Her gün için max 3 öneri
                alternatives.append({
                    "room_id": room_id,
                    "room_name": self.get_room(room_id).name,
                    "start": slot["start"],
                    "end": slot["end"],
                    "type": "same_room_different_time"
                })
        
        # Aynı zaman için farklı salonlar
        room = self.get_room(room_id)
        if room:
            similar_rooms = self.search_rooms(capacity=room.capacity)
            
            for other_room in similar_rooms:
                if other_room.id == room_id:
                    continue
                
                conflicts = self.check_conflict(other_room.id, start_time, 
                                               start_time + duration)
                
                if not conflicts:
                    alternatives.append({
                        "room_id": other_room.id,
                        "room_name": other_room.name,
                        "start": start_time,
                        "end": start_time + duration,
                        "type": "different_room_same_time"
                    })
        
        return alternatives[:10]  # Max 10 öneri
    
    def find_available_slots(self, room_id: str, start: datetime, 
                            end: datetime, duration_minutes: int) -> List[dict]:
        """
        Belirtilen aralıkta müsait slotları bul
        
        Zaman Karmaşıklığı: O(n log n) - sıralama dahil
        """
        if room_id not in self._room_intervals:
            return []
        
        # Mevcut rezervasyonları al
        query = Interval(
            self._datetime_to_minutes(start),
            self._datetime_to_minutes(end)
        )
        
        existing = self._room_intervals[room_id].find_overlapping(query)
        
        # Aktif rezervasyonları filtrele ve sırala
        active = []
        for interval in existing:
            res = interval.data
            if res and res.status not in [ReservationStatus.CANCELLED]:
                active.append((res.start_time, res.end_time))
        
        active = quicksort(active, key=lambda x: x[0])
        
        # Boşlukları bul
        available = []
        current = start
        
        for res_start, res_end in active:
            if current < res_start:
                gap = (res_start - current).total_seconds() / 60
                if gap >= duration_minutes:
                    available.append({
                        "start": current,
                        "end": res_start,
                        "duration_minutes": int(gap)
                    })
            
            if res_end > current:
                current = res_end
        
        # Son boşluk
        if current < end:
            gap = (end - current).total_seconds() / 60
            if gap >= duration_minutes:
                available.append({
                    "start": current,
                    "end": end,
                    "duration_minutes": int(gap)
                })
        
        return available
    
    def auto_reschedule(self, reservation_id: str) -> Tuple[bool, str]:
        """
        Çakışan rezervasyonu otomatik yeniden planla
        """
        reservation = self.get_reservation(reservation_id)
        if not reservation:
            return False, "Rezervasyon bulunamadı"
        
        duration = reservation.duration_minutes
        
        # Alternatif bul
        alternatives = self.suggest_alternatives(
            reservation.room_id,
            reservation.start_time,
            duration,
            search_days=14
        )
        
        if not alternatives:
            return False, "Alternatif bulunamadı"
        
        # İlk uygun alternatifi seç
        alt = alternatives[0]
        
        success, msg = self.update_reservation(
            reservation_id,
            room_id=alt["room_id"],
            start_time=alt["start"],
            end_time=alt["end"]
        )
        
        if success:
            return True, f"Rezervasyon {alt['room_name']} salonuna, {alt['start'].strftime('%d/%m/%Y %H:%M')} tarihine taşındı"
        
        return False, msg
    
    # ==================== SORGULAMA VE RAPORLAMA ====================
    
    def get_reservations_by_room(self, room_id: str, 
                                  date_filter: date = None) -> List[Reservation]:
        """Salona göre rezervasyonları listele"""
        results = []
        
        for res in self._reservations.values():
            if res.room_id != room_id:
                continue
            
            if res.status == ReservationStatus.CANCELLED:
                continue
            
            if date_filter:
                if res.start_time.date() != date_filter:
                    continue
            
            results.append(res)
        
        # Başlangıç saatine göre sırala
        return quicksort(results, key=lambda r: r.start_time)
    
    def get_reservations_by_date(self, target_date: date) -> List[Reservation]:
        """Tarihe göre tüm rezervasyonları listele"""
        results = []
        
        for res in self._reservations.values():
            if res.start_time.date() == target_date:
                if res.status != ReservationStatus.CANCELLED:
                    results.append(res)
        
        return quicksort(results, key=lambda r: (r.room_id, r.start_time))
    
    def get_reservations_by_customer(self, customer_email: str) -> List[Reservation]:
        """Müşteriye göre rezervasyonları listele"""
        results = []
        
        for res in self._reservations.values():
            if res.customer_email.lower() == customer_email.lower():
                results.append(res)
        
        return quicksort(results, key=lambda r: r.start_time, reverse=True)
    
    def get_upcoming_reservations(self, limit: int = 10) -> List[Reservation]:
        """Yaklaşan rezervasyonları listele (önceliğe göre)"""
        now = datetime.now()
        upcoming = []
        
        for res in self._reservations.values():
            if res.start_time > now and res.status in [ReservationStatus.PENDING, 
                                                        ReservationStatus.CONFIRMED]:
                upcoming.append(res)
        
        # Önce tarihe, sonra önceliğe göre sırala
        sorted_upcoming = quicksort(upcoming, key=lambda r: (r.start_time, r.priority))
        
        return sorted_upcoming[:limit]
    
    def search_reservations(self, query: str) -> List[Reservation]:
        """Metin araması (müşteri adı, başlık, açıklama)"""
        query_lower = query.lower()
        results = []
        
        for res in self._reservations.values():
            if (query_lower in res.customer_name.lower() or
                query_lower in res.title.lower() or
                query_lower in res.description.lower() or
                query_lower in res.customer_email.lower()):
                results.append(res)
        
        return quicksort(results, key=lambda r: r.start_time, reverse=True)
    
    def get_room_utilization(self, room_id: str, 
                             start_date: date, end_date: date) -> dict:
        """Salon kullanım oranını hesapla"""
        room = self.get_room(room_id)
        if not room:
            return {}
        
        total_minutes = 0
        used_minutes = 0
        reservation_count = 0
        
        current = start_date
        while current <= end_date:
            # Günlük çalışma saatleri (9 saat = 540 dakika)
            total_minutes += 540
            
            # O güne ait rezervasyonlar
            for res in self.get_reservations_by_room(room_id, current):
                if res.status != ReservationStatus.CANCELLED:
                    used_minutes += res.duration_minutes
                    reservation_count += 1
            
            current += timedelta(days=1)
        
        utilization = (used_minutes / total_minutes * 100) if total_minutes > 0 else 0
        
        return {
            "room_id": room_id,
            "room_name": room.name,
            "period": f"{start_date} - {end_date}",
            "total_available_minutes": total_minutes,
            "used_minutes": used_minutes,
            "utilization_percent": round(utilization, 2),
            "reservation_count": reservation_count
        }
    
    def get_daily_report(self, target_date: date) -> dict:
        """Günlük rapor oluştur"""
        reservations = self.get_reservations_by_date(target_date)
        
        total_revenue = 0
        by_room = {}
        by_status = {}
        
        for res in reservations:
            room = self.get_room(res.room_id)
            
            # Gelir hesabı
            if room:
                revenue = res.duration_hours * room.hourly_rate
                total_revenue += revenue
                
                # Salon bazlı
                if room.name not in by_room:
                    by_room[room.name] = {"count": 0, "minutes": 0, "revenue": 0}
                by_room[room.name]["count"] += 1
                by_room[room.name]["minutes"] += res.duration_minutes
                by_room[room.name]["revenue"] += revenue
            
            # Durum bazlı
            status = res.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "date": target_date.isoformat(),
            "total_reservations": len(reservations),
            "total_revenue": round(total_revenue, 2),
            "by_room": by_room,
            "by_status": by_status
        }
    
    # ==================== BEKLEME LİSTESİ ====================
    
    def add_to_waiting_list(self, customer_id: str, customer_name: str,
                            room_preference: str = None, priority: int = 2) -> bool:
        """Bekleme listesine ekle"""
        entry = WaitingEntry(
            customer_id=customer_id,
            customer_name=customer_name,
            room_preference=room_preference,
            priority=priority
        )
        return self._waiting_list.add(entry)
    
    def remove_from_waiting_list(self, customer_id: str) -> bool:
        """Bekleme listesinden çıkar"""
        entry = self._waiting_list.remove(customer_id)
        return entry is not None
    
    def get_waiting_list_position(self, customer_id: str) -> int:
        """Bekleme listesindeki pozisyonu al"""
        return self._waiting_list.get_position(customer_id)
    
    def get_waiting_list(self) -> List[WaitingEntry]:
        """Bekleme listesini al"""
        return self._waiting_list.get_all()
    
    def _notify_waiting_customer(self, entry: WaitingEntry):
        """Bekleme listesindeki müşteriye bildirim (callback)"""
        print(f"[BİLDİRİM] {entry.customer_name} için yer açıldı!")
        self._log_action("waiting_notification", entry.customer_id,
                        f"Bildirim gönderildi: {entry.customer_name}")
    
    # ==================== UNDO/REDO ====================
    
    def undo(self) -> Optional[str]:
        """Son işlemi geri al"""
        action = self._undo_manager.undo()
        if action:
            self._apply_undo_action(action)
            return f"Geri alındı: {action.description}"
        return None
    
    def redo(self) -> Optional[str]:
        """Geri alınan işlemi yinele"""
        action = self._undo_manager.redo()
        if action:
            self._apply_redo_action(action)
            return f"Yinelendi: {action.description}"
        return None
    
    def _apply_undo_action(self, action: Action):
        """Undo işlemini uygula"""
        if action.action_type == ActionType.CREATE:
            # Oluşturulanı sil
            if action.entity_type == "reservation":
                self._force_delete_reservation(action.entity_id)
            elif action.entity_type == "room":
                self._force_delete_room(action.entity_id)
        
        elif action.action_type == ActionType.UPDATE:
            # Eski duruma döndür
            if action.entity_type == "reservation":
                self._restore_reservation(action.entity_id, action.old_state)
            elif action.entity_type == "room":
                self._restore_room(action.entity_id, action.old_state)
        
        elif action.action_type == ActionType.DELETE:
            # Silinen geri yükle
            if action.entity_type == "reservation":
                self._restore_reservation(action.entity_id, action.old_state, create=True)
            elif action.entity_type == "room":
                self._restore_room(action.entity_id, action.old_state, create=True)
    
    def _apply_redo_action(self, action: Action):
        """Redo işlemini uygula"""
        if action.action_type == ActionType.CREATE:
            # Tekrar oluştur
            if action.entity_type == "reservation":
                self._restore_reservation(action.entity_id, action.new_state, create=True)
            elif action.entity_type == "room":
                self._restore_room(action.entity_id, action.new_state, create=True)
        
        elif action.action_type == ActionType.UPDATE:
            # Yeni duruma getir
            if action.entity_type == "reservation":
                self._restore_reservation(action.entity_id, action.new_state)
            elif action.entity_type == "room":
                self._restore_room(action.entity_id, action.new_state)
        
        elif action.action_type == ActionType.DELETE:
            # Tekrar sil
            if action.entity_type == "reservation":
                self._force_delete_reservation(action.entity_id)
            elif action.entity_type == "room":
                self._force_delete_room(action.entity_id)
    
    def _force_delete_reservation(self, reservation_id: str):
        """Rezervasyonu zorla sil (undo/redo için)"""
        if reservation_id in self._reservations:
            res = self._reservations[reservation_id]
            interval = Interval(
                self._datetime_to_minutes(res.start_time),
                self._datetime_to_minutes(res.end_time),
                res
            )
            if res.room_id in self._room_intervals:
                self._room_intervals[res.room_id].delete(interval)
            
            del self._reservations[reservation_id]
            self._reservation_tree.delete(reservation_id)
    
    def _force_delete_room(self, room_id: str):
        """Salonu zorla sil (undo/redo için)"""
        if room_id in self._rooms:
            del self._rooms[room_id]
            self._room_tree.delete(room_id)
            if room_id in self._room_intervals:
                del self._room_intervals[room_id]
            self._building_graph.remove_vertex(room_id)
    
    def _restore_reservation(self, reservation_id: str, state: dict, create: bool = False):
        """Rezervasyonu geri yükle"""
        reservation = Reservation.from_dict(state)
        
        if create or reservation_id not in self._reservations:
            self._reservations[reservation_id] = reservation
            self._reservation_tree.insert(reservation_id, reservation)
        else:
            # Mevcut olanı güncelle
            old_res = self._reservations[reservation_id]
            old_interval = Interval(
                self._datetime_to_minutes(old_res.start_time),
                self._datetime_to_minutes(old_res.end_time),
                old_res
            )
            self._room_intervals[old_res.room_id].delete(old_interval)
            
            self._reservations[reservation_id] = reservation
        
        # Interval ekle
        interval = Interval(
            self._datetime_to_minutes(reservation.start_time),
            self._datetime_to_minutes(reservation.end_time),
            reservation
        )
        if reservation.room_id in self._room_intervals:
            self._room_intervals[reservation.room_id].insert(interval)
    
    def _restore_room(self, room_id: str, state: dict, create: bool = False):
        """Salonu geri yükle"""
        room = Room.from_dict(state)
        
        if create or room_id not in self._rooms:
            self._rooms[room_id] = room
            self._room_tree.insert(room_id, room)
            if room_id not in self._room_intervals:
                self._room_intervals[room_id] = IntervalTree()
            self._building_graph.add_vertex(room_id, room)
        else:
            self._rooms[room_id] = room
    
    def can_undo(self) -> bool:
        return self._undo_manager.can_undo()
    
    def can_redo(self) -> bool:
        return self._undo_manager.can_redo()
    
    def get_undo_description(self) -> Optional[str]:
        return self._undo_manager.get_undo_description()
    
    def get_redo_description(self) -> Optional[str]:
        return self._undo_manager.get_redo_description()
    
    # ==================== YARDIMCI METODLAR ====================
    
    def _datetime_to_minutes(self, dt: datetime) -> int:
        """DateTime'ı dakikaya çevir (epoch'tan)"""
        return int(dt.timestamp() / 60)
    
    def _log_action(self, action: str, entity_id: str, description: str):
        """İşlem günlüğüne kaydet"""
        self._action_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "entity_id": entity_id,
            "description": description
        })
    
    def get_action_log(self, limit: int = 50) -> List[dict]:
        """İşlem geçmişini al"""
        return self._action_log[-limit:]
    
    def get_statistics(self) -> dict:
        """Genel sistem istatistikleri"""
        active_reservations = sum(1 for r in self._reservations.values() 
                                  if r.status in [ReservationStatus.PENDING, 
                                                  ReservationStatus.CONFIRMED])
        
        return {
            "total_rooms": len(self._rooms),
            "active_rooms": sum(1 for r in self._rooms.values() if r.is_active),
            "total_reservations": len(self._reservations),
            "active_reservations": active_reservations,
            "waiting_list_size": len(self._waiting_list),
            "undo_available": self._undo_manager.undo_count(),
            "redo_available": self._undo_manager.redo_count()
        }
    
    @staticmethod
    def generate_id() -> str:
        """Benzersiz ID oluştur"""
        return str(uuid.uuid4())[:8].upper()


# Test ve örnek kullanım
if __name__ == "__main__":
    print("=" * 70)
    print("SALON REZERVASYON SİSTEMİ - TEST")
    print("=" * 70)
    
    # Sistem oluştur
    system = ReservationSystem()
    
    # Salonları ekle
    print("\n--- Salonlar Ekleniyor ---")
    rooms = [
        Room("R001", "Toplantı Salonu A", 10, RoomType.MEETING, 1, 
             ["projeksiyon", "whiteboard"], 100.0),
        Room("R002", "Konferans Salonu", 50, RoomType.CONFERENCE, 2,
             ["projeksiyon", "mikrofon", "kayıt"], 250.0),
        Room("R003", "Eğitim Odası 1", 20, RoomType.TRAINING, 1,
             ["projeksiyon", "whiteboard", "bilgisayar"], 150.0),
        Room("R004", "Yönetim Salonu", 8, RoomType.EXECUTIVE, 3,
             ["projeksiyon", "video konferans"], 200.0),
    ]
    
    for room in rooms:
        system.add_room(room)
        print(f"  Eklendi: {room.name} (Kapasite: {room.capacity})")
    
    # Salon bağlantıları
    system.connect_rooms("R001", "R002", 30)
    system.connect_rooms("R001", "R003", 15)
    system.connect_rooms("R002", "R004", 50)
    system.connect_rooms("R003", "R004", 40)
    
    # Rezervasyonlar
    print("\n--- Rezervasyonlar Oluşturuluyor ---")
    
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    
    reservations = [
        Reservation(
            system.generate_id(), "R001", "Ahmet Yılmaz", "ahmet@email.com",
            tomorrow.replace(hour=9, minute=0), tomorrow.replace(hour=10, minute=30),
            title="Proje Toplantısı", attendees=8, priority=2
        ),
        Reservation(
            system.generate_id(), "R001", "Mehmet Demir", "mehmet@email.com",
            tomorrow.replace(hour=11, minute=0), tomorrow.replace(hour=12, minute=0),
            title="Müşteri Görüşmesi", attendees=5, priority=1
        ),
        Reservation(
            system.generate_id(), "R002", "Ayşe Kaya", "ayse@email.com",
            tomorrow.replace(hour=14, minute=0), tomorrow.replace(hour=17, minute=0),
            title="Şirket Sunumu", attendees=45, priority=1
        ),
    ]
    
    for res in reservations:
        success, msg = system.create_reservation(res)
        status = "✓" if success else "✗"
        print(f"  {status} {res.customer_name}: {res.title} - {msg}")
    
    # Çakışma testi
    print("\n--- Çakışma Testi ---")
    conflict_res = Reservation(
        system.generate_id(), "R001", "Fatma Şahin", "fatma@email.com",
        tomorrow.replace(hour=9, minute=30), tomorrow.replace(hour=11, minute=0),
        title="Çakışan Toplantı", attendees=6
    )
    
    success, msg = system.create_reservation(conflict_res)
    print(f"  Çakışan rezervasyon: {msg}")
    
    if not success:
        print("\n  Alternatif öneriler:")
        alternatives = system.suggest_alternatives(
            "R001", tomorrow.replace(hour=9, minute=30), 90
        )
        for i, alt in enumerate(alternatives[:3], 1):
            print(f"    {i}. {alt['room_name']} - {alt['start'].strftime('%H:%M')} - {alt['end'].strftime('%H:%M')}")
    
    # Müsait slotlar
    print("\n--- Müsait Zaman Aralıkları ---")
    available = system.find_available_slots(
        "R001", 
        tomorrow.replace(hour=8, minute=0),
        tomorrow.replace(hour=18, minute=0),
        60
    )
    
    print(f"  Salon A - {tomorrow.date()} için müsait 60+ dk slotlar:")
    for slot in available:
        print(f"    {slot['start'].strftime('%H:%M')} - {slot['end'].strftime('%H:%M')} ({slot['duration_minutes']} dk)")
    
    # Yol bulma
    print("\n--- Salon Arası Yol Bulma ---")
    path, distance = system.find_shortest_path("R001", "R004")
    print(f"  R001 -> R004: {' -> '.join(path)} (Mesafe: {distance}m)")
    
    # Undo/Redo
    print("\n--- Undo/Redo Testi ---")
    print(f"  Undo yapılabilir: {system.can_undo()} - {system.get_undo_description()}")
    
    undo_result = system.undo()
    print(f"  {undo_result}")
    
    print(f"  Redo yapılabilir: {system.can_redo()} - {system.get_redo_description()}")
    
    redo_result = system.redo()
    print(f"  {redo_result}")
    
    # Bekleme listesi
    print("\n--- Bekleme Listesi ---")
    system.add_to_waiting_list("W001", "Zeynep Arslan", "R001", priority=2)
    system.add_to_waiting_list("W002", "Can Yılmaz", "R001", priority=1)
    system.add_to_waiting_list("W003", "Deniz Kara", None, priority=3)
    
    print("  Bekleme listesi:")
    for entry in system.get_waiting_list():
        pos = system.get_waiting_list_position(entry.customer_id)
        print(f"    {pos}. {entry.customer_name} (Öncelik: {entry.priority})")
    
    # İstatistikler
    print("\n--- Sistem İstatistikleri ---")
    stats = system.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Günlük rapor
    print("\n--- Günlük Rapor ---")
    report = system.get_daily_report(tomorrow.date())
    print(f"  Tarih: {report['date']}")
    print(f"  Toplam rezervasyon: {report['total_reservations']}")
    print(f"  Toplam gelir: {report['total_revenue']} TL")
