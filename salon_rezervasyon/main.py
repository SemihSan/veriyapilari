"""
Salon Rezervasyon Sistemi - Ana Uygulama
=========================================

Veri Yapıları ve Algoritmalar Dersi Projesi

Bu proje aşağıdaki veri yapıları ve algoritmaları içermektedir:

1. Dengeli Arama Ağacı:
   - AVL Tree: Salon ve rezervasyon yönetimi

2. Interval Tree:
   - Zaman aralığı çakışma kontrolü
   - Boş slot bulma

3. Heap ve Priority Queue:
   - MinHeap, MaxHeap
   - Öncelikli rezervasyon kuyruğu

4. Graf ve Yol Bulma Algoritmaları:
   - BFS (Breadth-First Search)
   - DFS (Depth-First Search)
   - Dijkstra (En kısa yol)
   - A* (Heuristic arama)

5. Sıralama Algoritmaları:
   - QuickSort (3-way partitioning)
   - MergeSort (Recursive & Iterative)
   - HeapSort

6. Arama Algoritmaları:
   - Binary Search
   - Exponential Search

7. Stack ve Queue:
   - Stack: Undo/Redo desteği
   - Queue: FIFO kuyruk
   - Circular Queue: Sabit boyutlu kuyruk
   - Deque: Çift uçlu kuyruk

8. Linked List:
   - Doubly Linked List
   - Bekleme listesi yönetimi

Dosya Yapısı:
├── data_structures/
│   ├── __init__.py
│   ├── avl_tree.py
│   ├── interval_tree.py
│   ├── heap.py
│   ├── graph.py
│   ├── sorting.py
│   ├── stack_queue.py
│   └── linked_list.py
├── reservation_system.py
├── data_manager.py
├── cli.py
├── performance_analysis.py
└── main.py

Kullanım:
    python main.py              # CLI başlat
    python main.py --test       # Testleri çalıştır
    python main.py --benchmark  # Performans testi
    python main.py --demo       # Demo verileriyle çalıştır
"""

import sys
import os
import argparse
from datetime import datetime, date, timedelta
import random

# Proje kök dizinini path'e ekle
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import modüller
from reservation_system import (
    ReservationSystem, Room, Reservation,
    RoomType, ReservationStatus
)
from data_manager import DataManager
from cli import CLI
from performance_analysis import PerformanceAnalyzer

# Veri yapıları
from data_structures import (
    AVLTree, IntervalTree,
    MinHeap, MaxHeap, PriorityQueue,
    Graph,
    Stack, Queue, CircularQueue, Deque, UndoRedoManager,
    LinkedList, WaitingList,
    quicksort, mergesort, heapsort,
    binary_search
)


def run_tests():
    """Tüm veri yapıları ve algoritmaları test et"""
    print("\n" + "=" * 70)
    print(" SALON REZERVASYON SİSTEMİ - TEST RAPORU")
    print("=" * 70)
    
    all_passed = True
    
    # Test 1: AVL Tree
    print("\n[TEST 1] AVL Tree")
    print("-" * 40)
    try:
        tree = AVLTree()
        data = [50, 25, 75, 10, 30, 60, 90]
        for x in data:
            tree.insert(x)
        
        assert tree.search(50) is not None, "50 bulunamadi"
        assert tree.search(25) is not None, "25 bulunamadi"
        assert tree.search(100) is None, "100 yanlislikla bulundu"
        assert tree.get_min() == 10, "Min deger hatali"
        assert tree.get_max() == 90, "Max deger hatali"
        
        tree.delete(25)
        assert tree.search(25) is None, "25 silme basarisiz"
        
        range_result = tree.range_query(30, 75)
        keys = [k for k, v in range_result]
        assert 50 in keys and 60 in keys, f"Range query hatali: {range_result}"
        
        print("  ✓ Insert, Search, Delete, Range Query - BAŞARILI")
    except Exception as e:
        print(f"  ✗ HATA: {e}")
        all_passed = False
    
    # Test 2: Interval Tree
    print("\n[TEST 2] Interval Tree")
    print("-" * 40)
    try:
        from data_structures.interval_tree import Interval
        itree = IntervalTree()
        intervals = [(1, 5), (3, 8), (10, 15), (12, 18)]
        for i, (start, end) in enumerate(intervals):
            itree.insert(Interval(start, end, f"interval_{i}"))
        
        # Use find_overlapping instead of query_overlap
        query_interval = Interval(4, 6)
        overlaps = itree.find_overlapping(query_interval)
        assert len(overlaps) == 2, f"Overlap query hatali: {len(overlaps)}"
        
        # Use find_at_point instead of query_point
        point_query = itree.find_at_point(12)
        assert len(point_query) == 2, f"Point query hatali: {len(point_query)}"
        
        print("  ✓ Insert, Overlap Query, Point Query - BAŞARILI")
    except Exception as e:
        print(f"  ✗ HATA: {e}")
        all_passed = False
    
    # Test 3: Heap ve Priority Queue
    print("\n[TEST 3] Heap ve Priority Queue")
    print("-" * 40)
    try:
        # MinHeap
        min_heap = MinHeap()
        for x in [5, 3, 8, 1, 9]:
            min_heap.push(x)
        assert min_heap.pop() == 1, "MinHeap pop hatalı"
        assert min_heap.peek() == 3, "MinHeap peek hatalı"
        
        # MaxHeap
        max_heap = MaxHeap()
        for x in [5, 3, 8, 1, 9]:
            max_heap.push(x)
        assert max_heap.pop() == 9, "MaxHeap pop hatalı"
        
        # Priority Queue
        pq = PriorityQueue()
        pq.enqueue("low", 3)
        pq.enqueue("high", 1)
        pq.enqueue("medium", 2)
        item, priority = pq.dequeue()
        assert item == "high", f"PriorityQueue dequeue hatali: {item}"
        
        print("  ✓ MinHeap, MaxHeap, PriorityQueue - BAŞARILI")
    except Exception as e:
        print(f"  ✗ HATA: {e}")
        all_passed = False
    
    # Test 4: Graf Algoritmaları
    print("\n[TEST 4] Graf Algoritmaları")
    print("-" * 40)
    try:
        graph = Graph()
        for v in ['A', 'B', 'C', 'D', 'E']:
            graph.add_vertex(v)
        
        edges = [('A', 'B', 1), ('A', 'C', 4), ('B', 'C', 2), ('B', 'D', 5), ('C', 'D', 1), ('D', 'E', 3)]
        for u, v, w in edges:
            graph.add_edge(u, v, w)
        
        # BFS
        bfs_result = graph.bfs('A')
        assert 'A' in bfs_result and 'E' in bfs_result, "BFS hatalı"
        
        # DFS
        dfs_result = graph.dfs('A')
        assert 'A' in dfs_result and 'E' in dfs_result, "DFS hatalı"
        
        # Dijkstra
        path, distance = graph.dijkstra_path('A', 'E')
        assert path is not None and len(path) > 0, "Dijkstra yol bulamadi"
        assert distance == 7, f"Dijkstra mesafe hatali: {distance}"
        
        print("  ✓ BFS, DFS, Dijkstra - BAŞARILI")
    except Exception as e:
        print(f"  ✗ HATA: {e}")
        all_passed = False
    
    # Test 5: Sıralama Algoritmaları
    print("\n[TEST 5] Sıralama Algoritmaları")
    print("-" * 40)
    try:
        data = [64, 34, 25, 12, 22, 11, 90]
        
        # QuickSort (returns new sorted list)
        arr = quicksort(data)
        assert arr == sorted(data), "QuickSort hatali"
        
        # MergeSort (returns new sorted list)
        arr = mergesort(data)
        assert arr == sorted(data), "MergeSort hatali"
        
        # HeapSort (returns new sorted list)
        arr = heapsort(data)
        assert arr == sorted(data), "HeapSort hatali"
        
        # Binary Search
        sorted_arr = sorted(data)
        idx = binary_search(sorted_arr, 25)
        assert idx != -1 and sorted_arr[idx] == 25, "Binary Search hatali"
        
        print("  ✓ QuickSort, MergeSort, HeapSort, Binary Search - BAŞARILI")
    except Exception as e:
        print(f"  ✗ HATA: {e}")
        all_passed = False
    
    # Test 6: Stack ve Queue
    print("\n[TEST 6] Stack ve Queue")
    print("-" * 40)
    try:
        # Stack (LIFO)
        stack = Stack()
        for x in [1, 2, 3]:
            stack.push(x)
        assert stack.pop() == 3, "Stack LIFO hatalı"
        
        # Queue (FIFO)
        queue = Queue()
        for x in [1, 2, 3]:
            queue.enqueue(x)
        assert queue.dequeue() == 1, "Queue FIFO hatalı"
        
        # Circular Queue
        cq = CircularQueue(3)
        cq.enqueue(1)
        cq.enqueue(2)
        cq.enqueue(3)
        assert cq.is_full(), "CircularQueue full kontrolü hatalı"
        assert cq.dequeue() == 1, "CircularQueue dequeue hatalı"
        
        # Deque
        deque = Deque()
        deque.push_back(1)
        deque.push_front(0)
        assert deque.pop_front() == 0, "Deque pop_front hatali"
        
        print("  ✓ Stack, Queue, CircularQueue, Deque - BAŞARILI")
    except Exception as e:
        print(f"  ✗ HATA: {e}")
        all_passed = False
    
    # Test 7: Linked List
    print("\n[TEST 7] Linked List")
    print("-" * 40)
    try:
        ll = LinkedList()
        for x in [1, 2, 3]:
            ll.append(x)
        
        assert ll.get_at(0) == 1, "LinkedList get_at hatali"
        assert len(ll) == 3, "LinkedList length hatali"
        
        # Prepend test
        ll.prepend(0)
        assert ll.get_at(0) == 0, "LinkedList prepend hatali"
        assert len(ll) == 4, "LinkedList length after prepend hatali"
        
        print("  \u2713 Append, Prepend, Get - BA\u015eARILI")
    except Exception as e:
        print(f"  ✗ HATA: {e}")
        all_passed = False
    
    # Test 8: Undo/Redo
    print("\n[TEST 8] Undo/Redo")
    print("-" * 40)
    try:
        from data_structures.stack_queue import Action, ActionType
        
        undo_redo = UndoRedoManager(max_history=10)
        
        # Record a create action
        undo_redo.record_create("test", "id1", {"value": 10}, "Test olusturuldu")
        
        assert undo_redo.can_undo(), "Undo kullanilabilir olmali"
        assert not undo_redo.can_redo(), "Redo henuz kullanilamamali"
        
        # Check undo description
        desc = undo_redo.get_undo_description()
        assert desc is not None, "Undo description alinabilmeli"
        
        # Do undo
        action = undo_redo.undo()
        assert action is not None, "Undo calismali"
        assert undo_redo.can_redo(), "Redo artik kullanilabilir olmali"
        
        print("  \u2713 Record Action, Undo, Redo - BA\u015eARILI")
    except Exception as e:
        print(f"  ✗ HATA: {e}")
        all_passed = False
    
    # Test 9: Rezervasyon Sistemi
    print("\n[TEST 9] Rezervasyon Sistemi")
    print("-" * 40)
    try:
        system = ReservationSystem()
        
        # Salon ekle
        room = Room(
            id="R001",
            name="Test Salon",
            capacity=20,
            room_type=RoomType.MEETING,
            floor=1,
            hourly_rate=100.0
        )
        assert system.add_room(room), "Salon ekleme hatalı"
        
        # Rezervasyon yap
        start = datetime.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        
        reservation = Reservation(
            id="RES001",
            room_id="R001",
            customer_name="Test Müşteri",
            customer_email="test@example.com",
            start_time=start,
            end_time=end,
            status=ReservationStatus.CONFIRMED,
            priority=1
        )
        
        success, _ = system.create_reservation(reservation)
        assert success, "Rezervasyon oluşturma hatalı"
        
        # Çakışma kontrolü
        conflicts = system.check_conflict("R001", start, end)
        assert len(conflicts) == 1, "Çakışma kontrolü hatalı"
        
        # Undo test
        assert system.can_undo(), "Undo kullanılabilir olmalı"
        
        print("  ✓ Add Room, Create Reservation, Conflict Check, Undo - BAŞARILI")
    except Exception as e:
        print(f"  ✗ HATA: {e}")
        all_passed = False
    
    # Test 10: Data Manager
    print("\n[TEST 10] Data Manager")
    print("-" * 40)
    try:
        import tempfile
        import shutil
        
        # Geçici dizin oluştur
        temp_dir = tempfile.mkdtemp()
        dm = DataManager(temp_dir)
        
        system = ReservationSystem()
        dm.create_sample_data(system)
        
        # Kaydet
        assert dm.save_system_state(system), "Kaydetme hatalı"
        
        # Yeni sistem oluştur ve yükle
        system2 = ReservationSystem()
        dm.load_system_state(system2)
        
        assert len(system2.get_all_rooms()) > 0, "Yükleme hatalı"
        
        # Temizle
        shutil.rmtree(temp_dir)
        
        print("  ✓ Save, Load, Sample Data - BAŞARILI")
    except Exception as e:
        print(f"  ✗ HATA: {e}")
        all_passed = False
    
    # Sonuç
    print("\n" + "=" * 70)
    if all_passed:
        print(" TÜM TESTLER BAŞARILI! ✓")
    else:
        print(" BAZI TESTLER BAŞARISIZ! ✗")
    print("=" * 70 + "\n")
    
    return all_passed


def run_demo():
    """Demo verileriyle çalıştır"""
    print("\n" + "=" * 60)
    print(" DEMO MOD")
    print("=" * 60)
    
    system = ReservationSystem()
    data_manager = DataManager()
    
    # Örnek veriler oluştur
    data_manager.create_sample_data(system)
    
    # İstatistikler
    stats = system.get_statistics()
    print(f"\nOluşturulan veriler:")
    print(f"  - Salonlar: {stats['total_rooms']}")
    print(f"  - Rezervasyonlar: {stats['total_reservations']}")
    
    # CLI başlat
    cli = CLI(system, data_manager)
    cli.run()


def run_benchmark():
    """Performans testlerini çalıştır"""
    analyzer = PerformanceAnalyzer()
    analyzer.generate_full_report()


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description='Salon Rezervasyon Sistemi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py              # CLI başlat
  python main.py --test       # Testleri çalıştır
  python main.py --benchmark  # Performans testi
  python main.py --demo       # Demo verileriyle başlat
        """
    )
    
    parser.add_argument('--test', '-t', action='store_true',
                       help='Tüm testleri çalıştır')
    parser.add_argument('--benchmark', '-b', action='store_true',
                       help='Performans analizi yap')
    parser.add_argument('--demo', '-d', action='store_true',
                       help='Demo verileriyle başlat')
    parser.add_argument('--no-color', action='store_true',
                       help='Renksiz çıktı')
    
    args = parser.parse_args()
    
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    elif args.benchmark:
        run_benchmark()
    elif args.demo:
        run_demo()
    else:
        # Normal CLI
        print("\n" + "=" * 60)
        print("   SALON REZERVASYON SİSTEMİ")
        print("   Veri Yapıları ve Algoritmalar Projesi")
        print("=" * 60)
        
        system = ReservationSystem()
        data_manager = DataManager()
        
        # Mevcut verileri yükle
        data_manager.load_system_state(system)
        
        # CLI başlat
        cli = CLI(system, data_manager)
        
        try:
            cli.run()
        except KeyboardInterrupt:
            print("\n\nProgram sonlandırıldı.")
            data_manager.save_system_state(system)


if __name__ == "__main__":
    main()
