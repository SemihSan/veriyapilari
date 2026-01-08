"""
Linked List ve Bekleme Listesi
==============================
Tek ve çift yönlü bağlı liste implementasyonları.
Bekleme listesi yönetimi için özelleştirilmiş varyant.

Zaman Karmaşıklığı:
- Başa/Sona Ekleme: O(1)
- Arama: O(n)
- Silme (referansla): O(1)
- Silme (değerle): O(n)

Uzay Karmaşıklığı: O(n)
"""

from typing import Any, Optional, List, Generic, TypeVar, Callable, Iterator
from dataclasses import dataclass, field
from datetime import datetime

T = TypeVar('T')


@dataclass
class ListNode(Generic[T]):
    """Bağlı liste düğümü"""
    data: T
    next: Optional['ListNode[T]'] = None
    prev: Optional['ListNode[T]'] = None  # Çift yönlü için


class LinkedList(Generic[T]):
    """
    Çift Yönlü Bağlı Liste (Doubly Linked List)
    
    Her iki yönde de gezinme imkanı sağlar.
    Başa ve sona ekleme O(1).
    """
    
    def __init__(self):
        self._head: Optional[ListNode[T]] = None
        self._tail: Optional[ListNode[T]] = None
        self._size: int = 0
    
    def append(self, data: T) -> ListNode[T]:
        """
        Sona eleman ekle
        
        Zaman Karmaşıklığı: O(1)
        """
        new_node = ListNode(data)
        
        if not self._head:
            self._head = new_node
            self._tail = new_node
        else:
            new_node.prev = self._tail
            self._tail.next = new_node
            self._tail = new_node
        
        self._size += 1
        return new_node
    
    def prepend(self, data: T) -> ListNode[T]:
        """
        Başa eleman ekle
        
        Zaman Karmaşıklığı: O(1)
        """
        new_node = ListNode(data)
        
        if not self._head:
            self._head = new_node
            self._tail = new_node
        else:
            new_node.next = self._head
            self._head.prev = new_node
            self._head = new_node
        
        self._size += 1
        return new_node
    
    def insert_after(self, node: ListNode[T], data: T) -> ListNode[T]:
        """
        Belirli bir düğümden sonra ekle
        
        Zaman Karmaşıklığı: O(1)
        """
        if node is None:
            return self.prepend(data)
        
        new_node = ListNode(data)
        new_node.prev = node
        new_node.next = node.next
        
        if node.next:
            node.next.prev = new_node
        else:
            self._tail = new_node
        
        node.next = new_node
        self._size += 1
        
        return new_node
    
    def insert_before(self, node: ListNode[T], data: T) -> ListNode[T]:
        """
        Belirli bir düğümden önce ekle
        
        Zaman Karmaşıklığı: O(1)
        """
        if node is None:
            return self.append(data)
        
        new_node = ListNode(data)
        new_node.next = node
        new_node.prev = node.prev
        
        if node.prev:
            node.prev.next = new_node
        else:
            self._head = new_node
        
        node.prev = new_node
        self._size += 1
        
        return new_node
    
    def remove_node(self, node: ListNode[T]) -> T:
        """
        Düğümü kaldır (referansla)
        
        Zaman Karmaşıklığı: O(1)
        """
        if node is None:
            raise ValueError("Düğüm None olamaz")
        
        if node.prev:
            node.prev.next = node.next
        else:
            self._head = node.next
        
        if node.next:
            node.next.prev = node.prev
        else:
            self._tail = node.prev
        
        self._size -= 1
        return node.data
    
    def remove_first(self) -> Optional[T]:
        """
        İlk elemanı kaldır
        
        Zaman Karmaşıklığı: O(1)
        """
        if not self._head:
            return None
        
        data = self._head.data
        self._head = self._head.next
        
        if self._head:
            self._head.prev = None
        else:
            self._tail = None
        
        self._size -= 1
        return data
    
    def remove_last(self) -> Optional[T]:
        """
        Son elemanı kaldır
        
        Zaman Karmaşıklığı: O(1)
        """
        if not self._tail:
            return None
        
        data = self._tail.data
        self._tail = self._tail.prev
        
        if self._tail:
            self._tail.next = None
        else:
            self._head = None
        
        self._size -= 1
        return data
    
    def remove_by_value(self, data: T, key: Callable = None) -> bool:
        """
        Değere göre kaldır
        
        Zaman Karmaşıklığı: O(n)
        """
        if key is None:
            key = lambda x: x
        
        target_key = key(data)
        current = self._head
        
        while current:
            if key(current.data) == target_key:
                self.remove_node(current)
                return True
            current = current.next
        
        return False
    
    def find(self, predicate: Callable[[T], bool]) -> Optional[ListNode[T]]:
        """
        Koşula göre düğüm bul
        
        Zaman Karmaşıklığı: O(n)
        """
        current = self._head
        while current:
            if predicate(current.data):
                return current
            current = current.next
        return None
    
    def find_all(self, predicate: Callable[[T], bool]) -> List[ListNode[T]]:
        """
        Koşula uyan tüm düğümleri bul
        
        Zaman Karmaşıklığı: O(n)
        """
        result = []
        current = self._head
        while current:
            if predicate(current.data):
                result.append(current)
            current = current.next
        return result
    
    def get_at(self, index: int) -> Optional[T]:
        """
        İndekse göre eleman al
        
        Zaman Karmaşıklığı: O(n)
        """
        if index < 0 or index >= self._size:
            return None
        
        # Yakın taraftan başla
        if index < self._size // 2:
            current = self._head
            for _ in range(index):
                current = current.next
        else:
            current = self._tail
            for _ in range(self._size - 1 - index):
                current = current.prev
        
        return current.data if current else None
    
    def move_to_front(self, node: ListNode[T]) -> None:
        """
        Düğümü başa taşı
        
        Zaman Karmaşıklığı: O(1)
        """
        if node is self._head:
            return
        
        # Düğümü çıkar
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self._tail = node.prev
        
        # Başa ekle
        node.prev = None
        node.next = self._head
        self._head.prev = node
        self._head = node
    
    def move_to_back(self, node: ListNode[T]) -> None:
        """
        Düğümü sona taşı
        
        Zaman Karmaşıklığı: O(1)
        """
        if node is self._tail:
            return
        
        # Düğümü çıkar
        if node.prev:
            node.prev.next = node.next
        else:
            self._head = node.next
        if node.next:
            node.next.prev = node.prev
        
        # Sona ekle
        node.next = None
        node.prev = self._tail
        self._tail.next = node
        self._tail = node
    
    def reverse(self) -> None:
        """
        Listeyi ters çevir
        
        Zaman Karmaşıklığı: O(n)
        """
        current = self._head
        self._head, self._tail = self._tail, self._head
        
        while current:
            current.prev, current.next = current.next, current.prev
            current = current.prev
    
    def to_list(self) -> List[T]:
        """Listeyi Python listesine dönüştür"""
        result = []
        current = self._head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def clear(self) -> None:
        """Listeyi temizle"""
        self._head = None
        self._tail = None
        self._size = 0
    
    def is_empty(self) -> bool:
        return self._size == 0
    
    @property
    def head(self) -> Optional[T]:
        return self._head.data if self._head else None
    
    @property
    def tail(self) -> Optional[T]:
        return self._tail.data if self._tail else None
    
    def __len__(self) -> int:
        return self._size
    
    def __iter__(self) -> Iterator[T]:
        current = self._head
        while current:
            yield current.data
            current = current.next
    
    def __reversed__(self) -> Iterator[T]:
        current = self._tail
        while current:
            yield current.data
            current = current.prev
    
    def __repr__(self):
        items = [str(item) for item in self][:5]
        suffix = "..." if len(self) > 5 else ""
        return f"LinkedList([{', '.join(items)}{suffix}], size={self._size})"


# ==================== BEKLEMELİSTESİ ====================

@dataclass
class WaitingEntry:
    """Bekleme listesi girişi"""
    customer_id: str
    customer_name: str
    room_preference: str = None
    requested_time: datetime = None
    priority: int = 0  # Düşük = yüksek öncelik
    created_at: datetime = field(default_factory=datetime.now)
    notes: str = ""
    
    def __repr__(self):
        return f"WaitingEntry({self.customer_name}, pref={self.room_preference}, priority={self.priority})"


class WaitingList:
    """
    Bekleme Listesi - Rezervasyon bekleme kuyruğu
    
    Özellikler:
    - Öncelik bazlı sıralama
    - Müşteri bazlı arama
    - Otomatik bildirim desteği
    - İstatistik takibi
    """
    
    def __init__(self, on_available: Callable[[WaitingEntry], None] = None):
        """
        Args:
            on_available: Yer açıldığında çağrılacak callback
        """
        self._list: LinkedList[WaitingEntry] = LinkedList()
        self._entry_nodes: dict = {}  # customer_id -> ListNode mapping
        self._on_available = on_available
        self._served_count = 0
    
    def add(self, entry: WaitingEntry) -> bool:
        """
        Bekleme listesine ekle (önceliğe göre)
        
        Zaman Karmaşıklığı: O(n) - öncelik sıralaması için
        """
        if entry.customer_id in self._entry_nodes:
            return False  # Zaten listede
        
        # Önceliğe göre doğru pozisyonu bul
        current = self._list._head
        
        while current:
            if current.data.priority > entry.priority:
                # Bu düğümden önce ekle
                node = self._list.insert_before(current, entry)
                self._entry_nodes[entry.customer_id] = node
                return True
            current = current.next
        
        # Sona ekle
        node = self._list.append(entry)
        self._entry_nodes[entry.customer_id] = node
        return True
    
    def remove(self, customer_id: str) -> Optional[WaitingEntry]:
        """
        Müşteriyi listeden çıkar
        
        Zaman Karmaşıklığı: O(1)
        """
        if customer_id not in self._entry_nodes:
            return None
        
        node = self._entry_nodes[customer_id]
        entry = self._list.remove_node(node)
        del self._entry_nodes[customer_id]
        
        return entry
    
    def get_next(self) -> Optional[WaitingEntry]:
        """
        Sıradaki müşteriyi al (çıkarmadan)
        
        Zaman Karmaşıklığı: O(1)
        """
        return self._list.head
    
    def serve_next(self) -> Optional[WaitingEntry]:
        """
        Sıradaki müşteriyi çıkar ve döndür
        
        Zaman Karmaşıklığı: O(1)
        """
        if self._list.is_empty():
            return None
        
        entry = self._list.remove_first()
        if entry:
            del self._entry_nodes[entry.customer_id]
            self._served_count += 1
        
        return entry
    
    def update_priority(self, customer_id: str, new_priority: int) -> bool:
        """
        Müşterinin önceliğini güncelle
        
        Zaman Karmaşıklığı: O(n)
        """
        entry = self.remove(customer_id)
        if entry:
            entry.priority = new_priority
            return self.add(entry)
        return False
    
    def find_by_customer(self, customer_id: str) -> Optional[WaitingEntry]:
        """
        Müşteri ID'sine göre bul
        
        Zaman Karmaşıklığı: O(1)
        """
        if customer_id in self._entry_nodes:
            return self._entry_nodes[customer_id].data
        return None
    
    def find_by_room_preference(self, room: str) -> List[WaitingEntry]:
        """
        Oda tercihine göre bul
        
        Zaman Karmaşıklığı: O(n)
        """
        result = []
        for entry in self._list:
            if entry.room_preference == room or entry.room_preference is None:
                result.append(entry)
        return result
    
    def get_position(self, customer_id: str) -> int:
        """
        Müşterinin sıradaki pozisyonunu döndür
        
        Zaman Karmaşıklığı: O(n)
        """
        position = 1
        for entry in self._list:
            if entry.customer_id == customer_id:
                return position
            position += 1
        return -1
    
    def notify_available(self, room: str = None) -> Optional[WaitingEntry]:
        """
        Yer açıldığında sıradaki müşteriyi bilgilendir
        
        Args:
            room: Açılan oda (None = herhangi bir oda)
            
        Returns:
            Bilgilendirilen müşteri
        """
        if room:
            # Belirli oda için bekleyenleri kontrol et
            for entry in self._list:
                if entry.room_preference == room or entry.room_preference is None:
                    if self._on_available:
                        self._on_available(entry)
                    return entry
        else:
            # Sıradaki ilk müşteri
            entry = self.get_next()
            if entry and self._on_available:
                self._on_available(entry)
            return entry
        
        return None
    
    def get_all(self) -> List[WaitingEntry]:
        """Tüm bekleyenlerin listesi"""
        return self._list.to_list()
    
    def get_statistics(self) -> dict:
        """Bekleme listesi istatistikleri"""
        entries = self.get_all()
        
        if not entries:
            return {
                "total_waiting": 0,
                "served_count": self._served_count,
                "priority_breakdown": {},
                "avg_wait_time": None
            }
        
        priority_counts = {}
        total_wait = 0
        
        for entry in entries:
            priority_counts[entry.priority] = priority_counts.get(entry.priority, 0) + 1
            wait_time = (datetime.now() - entry.created_at).total_seconds()
            total_wait += wait_time
        
        return {
            "total_waiting": len(entries),
            "served_count": self._served_count,
            "priority_breakdown": priority_counts,
            "avg_wait_time_seconds": total_wait / len(entries),
            "oldest_entry": min(entries, key=lambda e: e.created_at).customer_name,
            "newest_entry": max(entries, key=lambda e: e.created_at).customer_name
        }
    
    def is_empty(self) -> bool:
        return self._list.is_empty()
    
    def __len__(self) -> int:
        return len(self._list)
    
    def __contains__(self, customer_id: str) -> bool:
        return customer_id in self._entry_nodes
    
    def __iter__(self):
        return iter(self._list)
    
    def __repr__(self):
        return f"WaitingList(waiting={len(self)}, served={self._served_count})"


# Kullanım örneği ve test
if __name__ == "__main__":
    print("=" * 60)
    print("Linked List ve Bekleme Listesi Test")
    print("=" * 60)
    
    # LinkedList testi
    print("\n--- LinkedList Test ---")
    ll = LinkedList()
    
    # Ekleme
    print("\nElemanlar ekleniyor:")
    ll.append("B")
    ll.append("C")
    ll.prepend("A")
    ll.append("D")
    
    print(f"Liste: {ll.to_list()}")
    print(f"Head: {ll.head}")
    print(f"Tail: {ll.tail}")
    print(f"Boyut: {len(ll)}")
    
    # İndeksle erişim
    print(f"\nİndeks 2'deki eleman: {ll.get_at(2)}")
    
    # Ters gezinti
    print(f"Tersten: {list(reversed(ll))}")
    
    # Silme
    ll.remove_by_value("B")
    print(f"\n'B' silindikten sonra: {ll.to_list()}")
    
    # Tersine çevirme
    ll.reverse()
    print(f"Tersine çevrildikten sonra: {ll.to_list()}")
    
    # Bekleme Listesi testi
    print("\n" + "=" * 40)
    print("Bekleme Listesi Test")
    
    def on_available(entry):
        print(f"  [BİLDİRİM] {entry.customer_name} için yer açıldı!")
    
    waiting = WaitingList(on_available=on_available)
    
    # Müşterileri ekle
    customers = [
        WaitingEntry("C001", "Ahmet Yılmaz", "Salon A", priority=2),
        WaitingEntry("C002", "Mehmet Demir", "Salon B", priority=1),  # VIP
        WaitingEntry("C003", "Ayşe Kaya", None, priority=3),  # Düşük öncelik
        WaitingEntry("C004", "Fatma Şahin", "Salon A", priority=1),  # VIP
        WaitingEntry("C005", "Ali Öztürk", "Salon B", priority=2),
    ]
    
    print("\nMüşteriler ekleniyor:")
    for c in customers:
        waiting.add(c)
        print(f"  Eklendi: {c.customer_name} (Öncelik: {c.priority})")
    
    print(f"\nBekleme listesi (öncelik sıralı):")
    for i, entry in enumerate(waiting, 1):
        print(f"  {i}. {entry.customer_name} - Öncelik: {entry.priority}, Tercih: {entry.room_preference}")
    
    # Pozisyon kontrolü
    print(f"\nAhmet'in sıradaki pozisyonu: {waiting.get_position('C001')}")
    print(f"Mehmet'in sıradaki pozisyonu: {waiting.get_position('C002')}")
    
    # Oda tercihine göre bul
    print(f"\nSalon A tercih edenler:")
    for entry in waiting.find_by_room_preference("Salon A"):
        print(f"  - {entry.customer_name}")
    
    # Yer açıldı bildirimi
    print(f"\n--- Salon B için yer açıldı ---")
    notified = waiting.notify_available("Salon B")
    if notified:
        print(f"Bilgilendirilen: {notified.customer_name}")
    
    # Sıradakini çağır
    print(f"\n--- Sıradaki müşteri çağrılıyor ---")
    served = waiting.serve_next()
    if served:
        print(f"Çağrılan: {served.customer_name}")
    
    # İstatistikler
    print(f"\n--- İstatistikler ---")
    stats = waiting.get_statistics()
    print(f"Toplam bekleyen: {stats['total_waiting']}")
    print(f"Servis edilen: {stats['served_count']}")
    print(f"Öncelik dağılımı: {stats['priority_breakdown']}")
    
    # Öncelik güncelleme
    print(f"\n--- Öncelik Güncelleme ---")
    print(f"Ayşe'nin önceliği 3 -> 1 olarak güncelleniyor...")
    waiting.update_priority("C003", 1)
    
    print(f"\nGüncel bekleme listesi:")
    for i, entry in enumerate(waiting, 1):
        print(f"  {i}. {entry.customer_name} - Öncelik: {entry.priority}")
