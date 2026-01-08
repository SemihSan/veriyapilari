"""
Stack, Queue ve Undo/Redo Manager
=================================
Stack ve Queue veri yapıları ile Undo/Redo yönetimi.
Rezervasyon işlemlerini geri alma/yineleme için kullanılır.

Zaman Karmaşıklığı:
- Push/Pop: O(1)
- Enqueue/Dequeue: O(1) - circular array veya linked list ile
- Peek: O(1)

Uzay Karmaşıklığı: O(n)
"""

from typing import Any, Optional, List, Generic, TypeVar, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import copy

T = TypeVar('T')


class Stack(Generic[T]):
    """
    Stack (Yığın) - LIFO (Last In, First Out)
    
    Kullanım Alanları:
    - Undo/Redo işlemleri
    - DFS (Derinlik Öncelikli Arama)
    - Parantez eşleştirme
    - Expression evaluation
    """
    
    def __init__(self, max_size: int = None):
        """
        Args:
            max_size: Maksimum boyut (None = sınırsız)
        """
        self._items: List[T] = []
        self._max_size = max_size
    
    def push(self, item: T) -> bool:
        """
        Stack'e eleman ekle
        
        Args:
            item: Eklenecek eleman
            
        Returns:
            bool: Ekleme başarılı ise True
            
        Zaman Karmaşıklığı: O(1)
        """
        if self._max_size and len(self._items) >= self._max_size:
            return False
        
        self._items.append(item)
        return True
    
    def pop(self) -> T:
        """
        En üstteki elemanı çıkar ve döndür
        
        Returns:
            En üstteki eleman
            
        Raises:
            IndexError: Stack boşsa
            
        Zaman Karmaşıklığı: O(1)
        """
        if not self._items:
            raise IndexError("Stack boş")
        return self._items.pop()
    
    def peek(self) -> T:
        """
        En üstteki elemana bak (çıkarmadan)
        
        Returns:
            En üstteki eleman
            
        Raises:
            IndexError: Stack boşsa
            
        Zaman Karmaşıklığı: O(1)
        """
        if not self._items:
            raise IndexError("Stack boş")
        return self._items[-1]
    
    def is_empty(self) -> bool:
        """Stack boş mu?"""
        return len(self._items) == 0
    
    def is_full(self) -> bool:
        """Stack dolu mu?"""
        return self._max_size is not None and len(self._items) >= self._max_size
    
    def size(self) -> int:
        """Stack boyutu"""
        return len(self._items)
    
    def clear(self) -> None:
        """Stack'i temizle"""
        self._items.clear()
    
    def to_list(self) -> List[T]:
        """Stack'i liste olarak döndür (üstten alta)"""
        return list(reversed(self._items))
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __bool__(self) -> bool:
        return bool(self._items)
    
    def __repr__(self):
        return f"Stack({self._items})"
    
    def __iter__(self):
        """Üstten alta iterasyon"""
        return reversed(self._items)


class Queue(Generic[T]):
    """
    Queue (Kuyruk) - FIFO (First In, First Out)
    
    Kullanım Alanları:
    - BFS (Genişlik Öncelikli Arama)
    - Görev kuyruğu
    - Bekleme listesi
    - Mesaj kuyruğu
    """
    
    def __init__(self, max_size: int = None):
        """
        Args:
            max_size: Maksimum boyut (None = sınırsız)
        """
        self._items: List[T] = []
        self._max_size = max_size
    
    def enqueue(self, item: T) -> bool:
        """
        Kuyruğa eleman ekle
        
        Args:
            item: Eklenecek eleman
            
        Returns:
            bool: Ekleme başarılı ise True
            
        Zaman Karmaşıklığı: O(1) amortized
        """
        if self._max_size and len(self._items) >= self._max_size:
            return False
        
        self._items.append(item)
        return True
    
    def dequeue(self) -> T:
        """
        Kuyruğun başındaki elemanı çıkar ve döndür
        
        Returns:
            Baştaki eleman
            
        Raises:
            IndexError: Kuyruk boşsa
            
        Zaman Karmaşıklığı: O(n) - liste için, O(1) - deque ile
        """
        if not self._items:
            raise IndexError("Kuyruk boş")
        return self._items.pop(0)
    
    def front(self) -> T:
        """
        Baştaki elemana bak (çıkarmadan)
        
        Zaman Karmaşıklığı: O(1)
        """
        if not self._items:
            raise IndexError("Kuyruk boş")
        return self._items[0]
    
    def rear(self) -> T:
        """
        Sondaki elemana bak (çıkarmadan)
        
        Zaman Karmaşıklığı: O(1)
        """
        if not self._items:
            raise IndexError("Kuyruk boş")
        return self._items[-1]
    
    def is_empty(self) -> bool:
        """Kuyruk boş mu?"""
        return len(self._items) == 0
    
    def is_full(self) -> bool:
        """Kuyruk dolu mu?"""
        return self._max_size is not None and len(self._items) >= self._max_size
    
    def size(self) -> int:
        """Kuyruk boyutu"""
        return len(self._items)
    
    def clear(self) -> None:
        """Kuyruğu temizle"""
        self._items.clear()
    
    def to_list(self) -> List[T]:
        """Kuyruğu liste olarak döndür (baştan sona)"""
        return list(self._items)
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __bool__(self) -> bool:
        return bool(self._items)
    
    def __repr__(self):
        return f"Queue({self._items})"
    
    def __iter__(self):
        """Baştan sona iterasyon"""
        return iter(self._items)


class CircularQueue(Generic[T]):
    """
    Circular Queue - Sabit boyutlu, döngüsel kuyruk
    
    Daha verimli dequeue işlemi için circular array kullanır.
    
    Zaman Karmaşıklığı:
    - Enqueue: O(1)
    - Dequeue: O(1)
    """
    
    def __init__(self, capacity: int):
        """
        Args:
            capacity: Kuyruk kapasitesi
        """
        self._capacity = capacity
        self._items: List[Optional[T]] = [None] * capacity
        self._front = 0
        self._rear = -1
        self._size = 0
    
    def enqueue(self, item: T) -> bool:
        """Kuyruğa eleman ekle - O(1)"""
        if self.is_full():
            return False
        
        self._rear = (self._rear + 1) % self._capacity
        self._items[self._rear] = item
        self._size += 1
        return True
    
    def dequeue(self) -> T:
        """Baştaki elemanı çıkar - O(1)"""
        if self.is_empty():
            raise IndexError("Kuyruk boş")
        
        item = self._items[self._front]
        self._items[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._size -= 1
        return item
    
    def front(self) -> T:
        """Baştaki elemana bak - O(1)"""
        if self.is_empty():
            raise IndexError("Kuyruk boş")
        return self._items[self._front]
    
    def is_empty(self) -> bool:
        return self._size == 0
    
    def is_full(self) -> bool:
        return self._size == self._capacity
    
    def size(self) -> int:
        return self._size
    
    def __len__(self) -> int:
        return self._size
    
    def __repr__(self):
        items = []
        idx = self._front
        for _ in range(self._size):
            items.append(self._items[idx])
            idx = (idx + 1) % self._capacity
        return f"CircularQueue({items})"


class Deque(Generic[T]):
    """
    Double-Ended Queue (Çift Uçlu Kuyruk)
    
    Her iki uçtan da ekleme ve çıkarma yapılabilir.
    Stack ve Queue özelliklerini birleştirir.
    """
    
    def __init__(self, max_size: int = None):
        self._items: List[T] = []
        self._max_size = max_size
    
    def push_front(self, item: T) -> bool:
        """Başa ekle - O(n)"""
        if self._max_size and len(self._items) >= self._max_size:
            return False
        self._items.insert(0, item)
        return True
    
    def push_back(self, item: T) -> bool:
        """Sona ekle - O(1)"""
        if self._max_size and len(self._items) >= self._max_size:
            return False
        self._items.append(item)
        return True
    
    def pop_front(self) -> T:
        """Baştan çıkar - O(n)"""
        if not self._items:
            raise IndexError("Deque boş")
        return self._items.pop(0)
    
    def pop_back(self) -> T:
        """Sondan çıkar - O(1)"""
        if not self._items:
            raise IndexError("Deque boş")
        return self._items.pop()
    
    def front(self) -> T:
        """Baştaki elemana bak"""
        if not self._items:
            raise IndexError("Deque boş")
        return self._items[0]
    
    def back(self) -> T:
        """Sondaki elemana bak"""
        if not self._items:
            raise IndexError("Deque boş")
        return self._items[-1]
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    def size(self) -> int:
        return len(self._items)
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __repr__(self):
        return f"Deque({self._items})"


# ==================== UNDO/REDO MANAGER ====================

class ActionType(Enum):
    """İşlem türleri"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    BATCH = "batch"  # Birden fazla işlem


@dataclass
class Action:
    """Geri alınabilir işlem"""
    action_type: ActionType
    entity_type: str  # "reservation", "room", vb.
    entity_id: Any
    old_state: Any = None  # Önceki durum (undo için)
    new_state: Any = None  # Yeni durum (redo için)
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    
    def __repr__(self):
        return f"Action({self.action_type.value}, {self.entity_type}, id={self.entity_id})"


class UndoRedoManager:
    """
    Undo/Redo İşlem Yöneticisi
    
    Stack yapısı kullanarak işlemlerin geri alınması ve yinelenmesini sağlar.
    Command Pattern implementasyonu.
    
    Kullanım:
    1. İşlem yapmadan önce record_action() ile kaydet
    2. Geri almak için undo()
    3. Yinelemek için redo()
    """
    
    def __init__(self, max_history: int = 100, on_state_change: Callable = None):
        """
        Args:
            max_history: Maksimum geçmiş boyutu
            on_state_change: Durum değişikliğinde çağrılacak callback
        """
        self._undo_stack: Stack[Action] = Stack(max_size=max_history)
        self._redo_stack: Stack[Action] = Stack(max_size=max_history)
        self._max_history = max_history
        self._on_state_change = on_state_change
        self._batch_mode = False
        self._batch_actions: List[Action] = []
    
    def record_action(self, action: Action) -> None:
        """
        Yeni işlemi kaydet
        
        Args:
            action: Kaydedilecek işlem
        """
        if self._batch_mode:
            self._batch_actions.append(action)
        else:
            self._undo_stack.push(action)
            # Yeni işlem kaydedildiğinde redo stack temizlenir
            self._redo_stack.clear()
            
            if self._on_state_change:
                self._on_state_change()
    
    def record_create(self, entity_type: str, entity_id: Any, 
                      new_state: Any, description: str = "") -> None:
        """Oluşturma işlemini kaydet"""
        action = Action(
            action_type=ActionType.CREATE,
            entity_type=entity_type,
            entity_id=entity_id,
            new_state=copy.deepcopy(new_state),
            description=description or f"{entity_type} oluşturuldu"
        )
        self.record_action(action)
    
    def record_update(self, entity_type: str, entity_id: Any,
                      old_state: Any, new_state: Any, description: str = "") -> None:
        """Güncelleme işlemini kaydet"""
        action = Action(
            action_type=ActionType.UPDATE,
            entity_type=entity_type,
            entity_id=entity_id,
            old_state=copy.deepcopy(old_state),
            new_state=copy.deepcopy(new_state),
            description=description or f"{entity_type} güncellendi"
        )
        self.record_action(action)
    
    def record_delete(self, entity_type: str, entity_id: Any,
                      old_state: Any, description: str = "") -> None:
        """Silme işlemini kaydet"""
        action = Action(
            action_type=ActionType.DELETE,
            entity_type=entity_type,
            entity_id=entity_id,
            old_state=copy.deepcopy(old_state),
            description=description or f"{entity_type} silindi"
        )
        self.record_action(action)
    
    def begin_batch(self) -> None:
        """Toplu işlem modunu başlat"""
        self._batch_mode = True
        self._batch_actions = []
    
    def end_batch(self, description: str = "Toplu işlem") -> None:
        """Toplu işlem modunu sonlandır ve kaydet"""
        if not self._batch_mode:
            return
        
        self._batch_mode = False
        
        if self._batch_actions:
            batch_action = Action(
                action_type=ActionType.BATCH,
                entity_type="batch",
                entity_id=None,
                old_state=self._batch_actions,  # Alt işlemler
                description=description
            )
            self._undo_stack.push(batch_action)
            self._redo_stack.clear()
        
        self._batch_actions = []
        
        if self._on_state_change:
            self._on_state_change()
    
    def cancel_batch(self) -> None:
        """Toplu işlem modunu iptal et"""
        self._batch_mode = False
        self._batch_actions = []
    
    def can_undo(self) -> bool:
        """Geri alınabilir işlem var mı?"""
        return not self._undo_stack.is_empty()
    
    def can_redo(self) -> bool:
        """Yinelenebilir işlem var mı?"""
        return not self._redo_stack.is_empty()
    
    def undo(self) -> Optional[Action]:
        """
        Son işlemi geri al
        
        Returns:
            Geri alınan işlem veya None
        """
        if not self.can_undo():
            return None
        
        action = self._undo_stack.pop()
        self._redo_stack.push(action)
        
        if self._on_state_change:
            self._on_state_change()
        
        return action
    
    def redo(self) -> Optional[Action]:
        """
        Geri alınan işlemi yinele
        
        Returns:
            Yinelenen işlem veya None
        """
        if not self.can_redo():
            return None
        
        action = self._redo_stack.pop()
        self._undo_stack.push(action)
        
        if self._on_state_change:
            self._on_state_change()
        
        return action
    
    def get_undo_description(self) -> Optional[str]:
        """Geri alınacak işlemin açıklaması"""
        if self.can_undo():
            return self._undo_stack.peek().description
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """Yinelenecek işlemin açıklaması"""
        if self.can_redo():
            return self._redo_stack.peek().description
        return None
    
    def get_history(self, limit: int = 10) -> List[Action]:
        """Son işlemlerin listesi"""
        return list(self._undo_stack)[:limit]
    
    def clear(self) -> None:
        """Tüm geçmişi temizle"""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._batch_actions = []
        self._batch_mode = False
        
        if self._on_state_change:
            self._on_state_change()
    
    def undo_count(self) -> int:
        """Geri alınabilir işlem sayısı"""
        return len(self._undo_stack)
    
    def redo_count(self) -> int:
        """Yinelenebilir işlem sayısı"""
        return len(self._redo_stack)
    
    def __repr__(self):
        return f"UndoRedoManager(undo={self.undo_count()}, redo={self.redo_count()})"


# ==================== GÖREV KUYRUĞU ====================

@dataclass
class Task:
    """Görev tanımı"""
    id: str
    name: str
    priority: int = 0  # Düşük = yüksek öncelik
    created_at: datetime = field(default_factory=datetime.now)
    data: Any = None


class TaskQueue:
    """
    Görev Kuyruğu
    
    Rezervasyon taleplerini sırayla işlemek için kullanılır.
    FIFO mantığıyla çalışır, öncelik desteği opsiyonel.
    """
    
    def __init__(self, max_size: int = None):
        self._queue: Queue[Task] = Queue(max_size=max_size)
        self._processing: Optional[Task] = None
        self._completed: List[Task] = []
    
    def add_task(self, task: Task) -> bool:
        """Kuyruğa görev ekle"""
        return self._queue.enqueue(task)
    
    def get_next_task(self) -> Optional[Task]:
        """Sıradaki görevi al (işleme başla)"""
        if self._queue.is_empty():
            return None
        
        self._processing = self._queue.dequeue()
        return self._processing
    
    def complete_current_task(self) -> Optional[Task]:
        """Mevcut görevi tamamla"""
        if self._processing:
            completed = self._processing
            self._completed.append(completed)
            self._processing = None
            return completed
        return None
    
    def cancel_current_task(self) -> Optional[Task]:
        """Mevcut görevi iptal et (kuyruğa geri ekle)"""
        if self._processing:
            task = self._processing
            self._processing = None
            self._queue.enqueue(task)
            return task
        return None
    
    def pending_count(self) -> int:
        """Bekleyen görev sayısı"""
        return len(self._queue)
    
    def completed_count(self) -> int:
        """Tamamlanan görev sayısı"""
        return len(self._completed)
    
    def is_processing(self) -> bool:
        """Şu an bir görev işleniyor mu?"""
        return self._processing is not None
    
    def current_task(self) -> Optional[Task]:
        """Şu an işlenen görev"""
        return self._processing
    
    def get_pending_tasks(self) -> List[Task]:
        """Bekleyen görevlerin listesi"""
        return self._queue.to_list()
    
    def get_completed_tasks(self) -> List[Task]:
        """Tamamlanan görevlerin listesi"""
        return list(self._completed)
    
    def __repr__(self):
        return f"TaskQueue(pending={self.pending_count()}, processing={self.is_processing()}, completed={self.completed_count()})"


# Kullanım örneği ve test
if __name__ == "__main__":
    print("=" * 60)
    print("Stack, Queue ve Undo/Redo Manager Test")
    print("=" * 60)
    
    # Stack testi
    print("\n--- Stack Test ---")
    stack = Stack()
    
    operations = ["Rezervasyon A oluştur", "Rezervasyon B oluştur", "Rezervasyon A güncelle"]
    for op in operations:
        stack.push(op)
        print(f"Push: {op}")
    
    print(f"\nStack boyutu: {len(stack)}")
    print(f"En üstteki (peek): {stack.peek()}")
    
    print("\nPop işlemleri:")
    while stack:
        print(f"  Pop: {stack.pop()}")
    
    # Queue testi
    print("\n--- Queue Test (Bekleme Listesi) ---")
    waiting_list = Queue()
    
    customers = ["Müşteri 1", "Müşteri 2", "Müşteri 3", "Müşteri 4"]
    for customer in customers:
        waiting_list.enqueue(customer)
        print(f"Kuyruğa eklendi: {customer}")
    
    print(f"\nKuyruk boyutu: {len(waiting_list)}")
    print(f"Sıradaki (front): {waiting_list.front()}")
    
    print("\nSırayla çağrılıyor:")
    while waiting_list:
        print(f"  Çağrıldı: {waiting_list.dequeue()}")
    
    # Circular Queue testi
    print("\n--- Circular Queue Test ---")
    cq = CircularQueue(capacity=3)
    
    print("Kapasite 3 olan circular queue:")
    cq.enqueue("A")
    cq.enqueue("B")
    cq.enqueue("C")
    print(f"Kuyruk dolu: {cq}")
    print(f"Ekleme deneme (dolu): {cq.enqueue('D')}")
    
    print(f"Dequeue: {cq.dequeue()}")
    print(f"Ekleme: {cq.enqueue('D')}")
    print(f"Kuyruk: {cq}")
    
    # Undo/Redo Manager testi
    print("\n--- Undo/Redo Manager Test ---")
    undo_manager = UndoRedoManager(max_history=50)
    
    # Rezervasyon işlemleri simülasyonu
    print("\nRezervasyonlar oluşturuluyor:")
    
    reservations = {
        "R001": {"id": "R001", "room": "Salon A", "date": "2024-01-15", "status": "active"},
        "R002": {"id": "R002", "room": "Salon B", "date": "2024-01-16", "status": "active"},
    }
    
    # Oluşturma işlemlerini kaydet
    undo_manager.record_create("reservation", "R001", reservations["R001"], "Salon A rezervasyonu oluşturuldu")
    undo_manager.record_create("reservation", "R002", reservations["R002"], "Salon B rezervasyonu oluşturuldu")
    
    print(f"  {reservations['R001']}")
    print(f"  {reservations['R002']}")
    
    # Güncelleme
    old_state = copy.deepcopy(reservations["R001"])
    reservations["R001"]["room"] = "Salon C"
    undo_manager.record_update("reservation", "R001", old_state, reservations["R001"], "Salon A -> Salon C değiştirildi")
    
    print(f"\nGüncelleme: R001 salonu değiştirildi")
    print(f"  Yeni durum: {reservations['R001']}")
    
    print(f"\nUndo/Redo durumu: {undo_manager}")
    print(f"Geri alınabilir: {undo_manager.can_undo()} - {undo_manager.get_undo_description()}")
    
    # Undo
    print("\n--- Undo işlemi ---")
    action = undo_manager.undo()
    if action:
        print(f"Geri alındı: {action.description}")
        # Gerçek sistemde burada state restore edilir
        reservations["R001"] = action.old_state
        print(f"Durum: {reservations['R001']}")
    
    print(f"\nYinelenebilir: {undo_manager.can_redo()} - {undo_manager.get_redo_description()}")
    
    # Redo
    print("\n--- Redo işlemi ---")
    action = undo_manager.redo()
    if action:
        print(f"Yinelendi: {action.description}")
        reservations["R001"] = action.new_state
        print(f"Durum: {reservations['R001']}")
    
    # Toplu işlem (Batch)
    print("\n--- Toplu İşlem (Batch) Test ---")
    undo_manager.begin_batch()
    
    for i in range(3):
        res_id = f"R00{i+3}"
        res = {"id": res_id, "room": f"Salon {chr(65+i+2)}", "status": "active"}
        undo_manager.record_create("reservation", res_id, res)
        print(f"  Oluşturuldu: {res}")
    
    undo_manager.end_batch("3 yeni rezervasyon toplu eklendi")
    
    print(f"\nToplu işlem kaydedildi")
    print(f"Undo durumu: {undo_manager}")
    
    # Tek undo ile 3 işlem geri alınabilir
    action = undo_manager.undo()
    if action:
        print(f"\nToplu geri alma: {action.description}")
        print(f"  Alt işlem sayısı: {len(action.old_state)}")
    
    # Görev Kuyruğu testi
    print("\n--- Görev Kuyruğu Test ---")
    task_queue = TaskQueue()
    
    # Görevler ekle
    tasks = [
        Task("T1", "Rezervasyon R001 onayla"),
        Task("T2", "Rezervasyon R002 iptal et"),
        Task("T3", "Salon temizlik planla"),
    ]
    
    for task in tasks:
        task_queue.add_task(task)
        print(f"Görev eklendi: {task.name}")
    
    print(f"\nKuyruk durumu: {task_queue}")
    
    # Görevleri işle
    print("\nGörevler işleniyor:")
    while task_queue.pending_count() > 0:
        task = task_queue.get_next_task()
        print(f"  İşleniyor: {task.name}")
        task_queue.complete_current_task()
        print(f"  Tamamlandı!")
    
    print(f"\nSon durum: {task_queue}")
