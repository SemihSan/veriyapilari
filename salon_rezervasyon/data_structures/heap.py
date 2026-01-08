"""
Heap ve Priority Queue Implementasyonu
======================================
Min-Heap, Max-Heap ve Öncelik Kuyruğu - Rezervasyonları öncelik sırasına
göre yönetmek için kullanılır (en erken bitiş, en yüksek öncelik vb.)

Zaman Karmaşıklığı:
- Ekleme (Insert/Push): O(log n)
- En üst elemanı çıkarma (Extract/Pop): O(log n)
- En üst elemana bakma (Peek): O(1)
- Heapify: O(n)

Uzay Karmaşıklığı: O(n)
"""

from typing import Any, Optional, List, Callable, Tuple
from dataclasses import dataclass, field


class MinHeap:
    """
    Min-Heap - En küçük eleman her zaman kökte
    
    Kullanım Alanları:
    - En erken biten rezervasyonu bulma
    - Dijkstra algoritması için öncelik kuyruğu
    - Görev zamanlayıcı (en yakın deadline)
    """
    
    def __init__(self, items: List[Any] = None, key_func: Callable = None):
        """
        Args:
            items: Başlangıç elemanları
            key_func: Karşılaştırma için anahtar fonksiyonu
        """
        self.heap: List[Any] = []
        self.key_func = key_func if key_func else lambda x: x
        
        if items:
            for item in items:
                self.push(item)
    
    def _parent(self, i: int) -> int:
        """Ebeveyn indeksini döndür"""
        return (i - 1) // 2
    
    def _left_child(self, i: int) -> int:
        """Sol çocuk indeksini döndür"""
        return 2 * i + 1
    
    def _right_child(self, i: int) -> int:
        """Sağ çocuk indeksini döndür"""
        return 2 * i + 2
    
    def _swap(self, i: int, j: int) -> None:
        """İki elemanın yerini değiştir"""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def _compare(self, i: int, j: int) -> bool:
        """i < j mi? (MinHeap için)"""
        return self.key_func(self.heap[i]) < self.key_func(self.heap[j])
    
    def _sift_up(self, i: int) -> None:
        """
        Elemanı yukarı taşı (heap özelliğini koru)
        
        Zaman Karmaşıklığı: O(log n)
        """
        while i > 0:
            parent = self._parent(i)
            if self._compare(i, parent):
                self._swap(i, parent)
                i = parent
            else:
                break
    
    def _sift_down(self, i: int) -> None:
        """
        Elemanı aşağı taşı (heap özelliğini koru)
        
        Zaman Karmaşıklığı: O(log n)
        """
        size = len(self.heap)
        
        while True:
            smallest = i
            left = self._left_child(i)
            right = self._right_child(i)
            
            if left < size and self._compare(left, smallest):
                smallest = left
            
            if right < size and self._compare(right, smallest):
                smallest = right
            
            if smallest != i:
                self._swap(i, smallest)
                i = smallest
            else:
                break
    
    def push(self, item: Any) -> None:
        """
        Heap'e eleman ekle
        
        Args:
            item: Eklenecek eleman
            
        Zaman Karmaşıklığı: O(log n)
        """
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)
    
    def pop(self) -> Any:
        """
        En küçük elemanı çıkar ve döndür
        
        Returns:
            En küçük eleman
            
        Raises:
            IndexError: Heap boşsa
            
        Zaman Karmaşıklığı: O(log n)
        """
        if not self.heap:
            raise IndexError("Heap boş")
        
        if len(self.heap) == 1:
            return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        
        return root
    
    def peek(self) -> Any:
        """
        En küçük elemana bak (çıkarmadan)
        
        Returns:
            En küçük eleman
            
        Raises:
            IndexError: Heap boşsa
            
        Zaman Karmaşıklığı: O(1)
        """
        if not self.heap:
            raise IndexError("Heap boş")
        return self.heap[0]
    
    def pushpop(self, item: Any) -> Any:
        """
        Eleman ekle ve en küçüğü çıkar (optimize edilmiş)
        
        Zaman Karmaşıklığı: O(log n)
        """
        if self.heap and self.key_func(self.heap[0]) < self.key_func(item):
            item, self.heap[0] = self.heap[0], item
            self._sift_down(0)
        return item
    
    def replace(self, item: Any) -> Any:
        """
        En küçüğü çıkar ve yeni eleman ekle (optimize edilmiş)
        
        Zaman Karmaşıklığı: O(log n)
        """
        if not self.heap:
            raise IndexError("Heap boş")
        
        root = self.heap[0]
        self.heap[0] = item
        self._sift_down(0)
        return root
    
    def heapify(self, items: List[Any]) -> None:
        """
        Listeyi heap'e dönüştür
        
        Args:
            items: Dönüştürülecek liste
            
        Zaman Karmaşıklığı: O(n)
        """
        self.heap = list(items)
        # Yapraklar hariç tüm düğümleri aşağı taşı
        for i in range(len(self.heap) // 2 - 1, -1, -1):
            self._sift_down(i)
    
    def get_sorted(self) -> List[Any]:
        """
        Heap'in sıralı halini döndür (heap bozulur)
        
        Returns:
            Küçükten büyüğe sıralı liste
            
        Zaman Karmaşıklığı: O(n log n)
        """
        result = []
        while self.heap:
            result.append(self.pop())
        return result
    
    def is_empty(self) -> bool:
        """Heap boş mu?"""
        return len(self.heap) == 0
    
    def clear(self) -> None:
        """Heap'i temizle"""
        self.heap = []
    
    def __len__(self) -> int:
        return len(self.heap)
    
    def __bool__(self) -> bool:
        return bool(self.heap)
    
    def __repr__(self):
        return f"MinHeap({self.heap})"


class MaxHeap(MinHeap):
    """
    Max-Heap - En büyük eleman her zaman kökte
    
    Kullanım Alanları:
    - En yüksek öncelikli rezervasyonu bulma
    - En uzun süreli toplantı
    """
    
    def _compare(self, i: int, j: int) -> bool:
        """i > j mi? (MaxHeap için)"""
        return self.key_func(self.heap[i]) > self.key_func(self.heap[j])
    
    def pushpop(self, item: Any) -> Any:
        """Eleman ekle ve en büyüğü çıkar"""
        if self.heap and self.key_func(self.heap[0]) > self.key_func(item):
            item, self.heap[0] = self.heap[0], item
            self._sift_down(0)
        return item
    
    def __repr__(self):
        return f"MaxHeap({self.heap})"


@dataclass(order=True)
class PriorityItem:
    """Öncelik kuyruğu için sarmalayıcı sınıf"""
    priority: Any
    item: Any = field(compare=False)
    insertion_order: int = field(default=0, compare=True)


class PriorityQueue:
    """
    Öncelik Kuyruğu - Elemanları önceliğe göre sıralar
    
    Kullanım Alanları:
    - VIP müşteri önceliği
    - Acil toplantı talepleri
    - Görev önceliklendirme
    """
    
    def __init__(self, min_priority: bool = True):
        """
        Args:
            min_priority: True ise düşük öncelik = yüksek priority (min-heap)
                         False ise yüksek öncelik = yüksek priority (max-heap)
        """
        self.min_priority = min_priority
        self._heap: List[PriorityItem] = []
        self._counter = 0  # FIFO için sayaç (aynı öncelikte)
    
    def _parent(self, i: int) -> int:
        return (i - 1) // 2
    
    def _left_child(self, i: int) -> int:
        return 2 * i + 1
    
    def _right_child(self, i: int) -> int:
        return 2 * i + 2
    
    def _swap(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
    
    def _compare(self, i: int, j: int) -> bool:
        """Karşılaştırma (min veya max heap'e göre)"""
        if self.min_priority:
            return self._heap[i] < self._heap[j]
        else:
            return self._heap[i] > self._heap[j]
    
    def _sift_up(self, i: int) -> None:
        while i > 0:
            parent = self._parent(i)
            if self._compare(i, parent):
                self._swap(i, parent)
                i = parent
            else:
                break
    
    def _sift_down(self, i: int) -> None:
        size = len(self._heap)
        
        while True:
            target = i
            left = self._left_child(i)
            right = self._right_child(i)
            
            if left < size and self._compare(left, target):
                target = left
            
            if right < size and self._compare(right, target):
                target = right
            
            if target != i:
                self._swap(i, target)
                i = target
            else:
                break
    
    def enqueue(self, item: Any, priority: Any = 0) -> None:
        """
        Kuyruğa eleman ekle
        
        Args:
            item: Eklenecek eleman
            priority: Öncelik değeri
            
        Zaman Karmaşıklığı: O(log n)
        """
        entry = PriorityItem(priority, item, self._counter)
        self._counter += 1
        self._heap.append(entry)
        self._sift_up(len(self._heap) - 1)
    
    def dequeue(self) -> Tuple[Any, Any]:
        """
        En yüksek öncelikli elemanı çıkar
        
        Returns:
            (item, priority) tuple
            
        Zaman Karmaşıklığı: O(log n)
        """
        if not self._heap:
            raise IndexError("Kuyruk boş")
        
        if len(self._heap) == 1:
            entry = self._heap.pop()
            return entry.item, entry.priority
        
        root = self._heap[0]
        self._heap[0] = self._heap.pop()
        self._sift_down(0)
        
        return root.item, root.priority
    
    def peek(self) -> Tuple[Any, Any]:
        """
        En yüksek öncelikli elemana bak
        
        Returns:
            (item, priority) tuple
            
        Zaman Karmaşıklığı: O(1)
        """
        if not self._heap:
            raise IndexError("Kuyruk boş")
        return self._heap[0].item, self._heap[0].priority
    
    def update_priority(self, item: Any, new_priority: Any) -> bool:
        """
        Elemanın önceliğini güncelle
        
        Args:
            item: Güncellenecek eleman
            new_priority: Yeni öncelik
            
        Returns:
            bool: Güncelleme başarılı ise True
            
        Zaman Karmaşıklığı: O(n)
        """
        for i, entry in enumerate(self._heap):
            if entry.item == item:
                old_priority = entry.priority
                self._heap[i] = PriorityItem(new_priority, item, entry.insertion_order)
                
                # Öncelik değişimine göre sift up veya down
                if self.min_priority:
                    if new_priority < old_priority:
                        self._sift_up(i)
                    else:
                        self._sift_down(i)
                else:
                    if new_priority > old_priority:
                        self._sift_up(i)
                    else:
                        self._sift_down(i)
                
                return True
        return False
    
    def remove(self, item: Any) -> bool:
        """
        Belirli bir elemanı kaldır
        
        Zaman Karmaşıklığı: O(n)
        """
        for i, entry in enumerate(self._heap):
            if entry.item == item:
                # Son elemanla değiştir ve kaldır
                if i == len(self._heap) - 1:
                    self._heap.pop()
                else:
                    self._heap[i] = self._heap.pop()
                    self._sift_down(i)
                    if i > 0:
                        self._sift_up(i)
                return True
        return False
    
    def contains(self, item: Any) -> bool:
        """Eleman kuyrukta mı?"""
        return any(entry.item == item for entry in self._heap)
    
    def get_priority(self, item: Any) -> Optional[Any]:
        """Elemanın önceliğini döndür"""
        for entry in self._heap:
            if entry.item == item:
                return entry.priority
        return None
    
    def get_all(self) -> List[Tuple[Any, Any]]:
        """Tüm elemanları öncelik sırasıyla döndür"""
        # Heap'in kopyasını al ve sırala
        temp = list(self._heap)
        result = []
        
        while temp:
            # En küçüğü/büyüğü bul
            if self.min_priority:
                min_idx = min(range(len(temp)), key=lambda i: temp[i])
            else:
                min_idx = max(range(len(temp)), key=lambda i: temp[i])
            
            entry = temp.pop(min_idx)
            result.append((entry.item, entry.priority))
        
        return result
    
    def is_empty(self) -> bool:
        return len(self._heap) == 0
    
    def clear(self) -> None:
        self._heap = []
        self._counter = 0
    
    def __len__(self) -> int:
        return len(self._heap)
    
    def __bool__(self) -> bool:
        return bool(self._heap)
    
    def __repr__(self):
        items = [(e.item, e.priority) for e in self._heap[:5]]
        suffix = "..." if len(self._heap) > 5 else ""
        return f"PriorityQueue({items}{suffix}, size={len(self._heap)})"


# Kullanım örneği ve test
if __name__ == "__main__":
    print("=" * 60)
    print("Heap ve Priority Queue Test")
    print("=" * 60)
    
    # MinHeap testi
    print("\n--- MinHeap Test ---")
    min_heap = MinHeap()
    
    values = [35, 33, 42, 10, 14, 19, 27, 44, 26, 31]
    print(f"Eklenecek değerler: {values}")
    
    for val in values:
        min_heap.push(val)
    
    print(f"Heap boyutu: {len(min_heap)}")
    print(f"En küçük (peek): {min_heap.peek()}")
    
    print("\nSıralı çıkarma:")
    sorted_values = []
    while min_heap:
        sorted_values.append(min_heap.pop())
    print(f"Sonuç: {sorted_values}")
    
    # MaxHeap testi
    print("\n--- MaxHeap Test ---")
    max_heap = MaxHeap()
    
    for val in values:
        max_heap.push(val)
    
    print(f"En büyük (peek): {max_heap.peek()}")
    
    print("Sıralı çıkarma (büyükten küçüğe):")
    sorted_desc = []
    while max_heap:
        sorted_desc.append(max_heap.pop())
    print(f"Sonuç: {sorted_desc}")
    
    # Rezervasyon senaryosu
    print("\n--- Rezervasyon Heap Senaryosu ---")
    
    # Rezervasyonları bitiş saatine göre sırala
    reservations = [
        {"id": 1, "name": "Toplantı A", "end_time": 600},   # 10:00
        {"id": 2, "name": "Toplantı B", "end_time": 720},   # 12:00
        {"id": 3, "name": "Toplantı C", "end_time": 540},   # 09:00
        {"id": 4, "name": "Toplantı D", "end_time": 660},   # 11:00
    ]
    
    reservation_heap = MinHeap(key_func=lambda r: r["end_time"])
    
    for res in reservations:
        reservation_heap.push(res)
    
    print("En erken biten rezervasyonlar:")
    while reservation_heap:
        res = reservation_heap.pop()
        end_h = res["end_time"] // 60
        end_m = res["end_time"] % 60
        print(f"  {res['name']} - Bitiş: {end_h:02d}:{end_m:02d}")
    
    # Priority Queue testi
    print("\n--- Priority Queue Test ---")
    pq = PriorityQueue(min_priority=True)  # Düşük sayı = yüksek öncelik
    
    # Rezervasyon talepleri (öncelik: 1=VIP, 2=Normal, 3=Düşük)
    requests = [
        ("Ahmet - Toplantı", 2),
        ("VIP Müşteri - Sunum", 1),
        ("Mehmet - Görüşme", 3),
        ("Ayşe - Proje Toplantısı", 2),
        ("CEO - Acil Toplantı", 1),
    ]
    
    print("Rezervasyon talepleri ekleniyor:")
    for name, priority in requests:
        pq.enqueue(name, priority)
        print(f"  {name} (Öncelik: {priority})")
    
    print("\nÖncelik sırasına göre işleme:")
    while pq:
        item, priority = pq.dequeue()
        priority_name = {1: "VIP", 2: "Normal", 3: "Düşük"}[priority]
        print(f"  [{priority_name}] {item}")
