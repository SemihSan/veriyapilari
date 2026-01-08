"""
Performans Analizi ve Karmaşıklık Tabloları
=============================================
Tüm veri yapıları ve algoritmaların zaman/alan karmaşıklığı analizi.
"""

import time
import random
import sys
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Callable, Tuple
from datetime import datetime, timedelta

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_structures import (
    AVLTree, IntervalTree,
    MinHeap, MaxHeap, PriorityQueue,
    Graph,
    Stack, Queue, CircularQueue, Deque,
    LinkedList,
    quicksort, mergesort, heapsort,
    binary_search
)


@dataclass
class ComplexityInfo:
    """Karmaşıklık bilgisi"""
    operation: str
    time_best: str
    time_average: str
    time_worst: str
    space: str
    notes: str = ""


class PerformanceAnalyzer:
    """
    Performans analiz sınıfı
    
    Tüm veri yapıları ve algoritmaların:
    - Teorik karmaşıklık tabloları
    - Ampirik performans ölçümleri
    """
    
    # ==================== KARMAŞIKLIK TABLOLARI ====================
    
    @staticmethod
    def get_avl_tree_complexity() -> List[ComplexityInfo]:
        """AVL Ağacı Karmaşıklıkları"""
        return [
            ComplexityInfo("Insert", "O(log n)", "O(log n)", "O(log n)", "O(1)",
                          "Dengeli yapı sayesinde her durumda logaritmik"),
            ComplexityInfo("Delete", "O(log n)", "O(log n)", "O(log n)", "O(1)",
                          "Silme sonrası dengeleme gerekebilir"),
            ComplexityInfo("Search", "O(log n)", "O(log n)", "O(log n)", "O(1)",
                          "İkili arama prensibi"),
            ComplexityInfo("Min/Max", "O(log n)", "O(log n)", "O(log n)", "O(1)",
                          "En sol/sağ yaprak"),
            ComplexityInfo("Range Query", "O(log n + k)", "O(log n + k)", "O(log n + k)", "O(k)",
                          "k: sonuç sayısı"),
            ComplexityInfo("Traversal", "O(n)", "O(n)", "O(n)", "O(h)",
                          "h: ağaç yüksekliği"),
            ComplexityInfo("Build", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)",
                          "n eleman için"),
        ]
    
    @staticmethod
    def get_interval_tree_complexity() -> List[ComplexityInfo]:
        """Interval Tree Karmaşıklıkları"""
        return [
            ComplexityInfo("Insert", "O(log n)", "O(log n)", "O(log n)", "O(1)",
                          "AVL tabanlı, dengeli"),
            ComplexityInfo("Delete", "O(log n)", "O(log n)", "O(log n)", "O(1)",
                          "AVL silme + max güncelleme"),
            ComplexityInfo("Overlap Query", "O(log n + k)", "O(log n + k)", "O(log n + k)", "O(k)",
                          "k: çakışan aralık sayısı"),
            ComplexityInfo("Point Query", "O(log n + k)", "O(log n + k)", "O(log n + k)", "O(k)",
                          "Belirli noktayı içeren aralıklar"),
            ComplexityInfo("Stab Query", "O(log n + k)", "O(log n + k)", "O(log n + k)", "O(k)",
                          "Kesişim sorgusu"),
        ]
    
    @staticmethod
    def get_heap_complexity() -> List[ComplexityInfo]:
        """Heap Karmaşıklıkları"""
        return [
            ComplexityInfo("Push", "O(1)", "O(log n)", "O(log n)", "O(1)",
                          "Amortize O(1) veya O(log n) percolate up"),
            ComplexityInfo("Pop", "O(log n)", "O(log n)", "O(log n)", "O(1)",
                          "Kök çıkarma + heapify down"),
            ComplexityInfo("Peek", "O(1)", "O(1)", "O(1)", "O(1)",
                          "Sadece kök erişimi"),
            ComplexityInfo("Heapify", "O(n)", "O(n)", "O(n)", "O(1)",
                          "Bottom-up yaklaşım"),
            ComplexityInfo("Update Key", "O(log n)", "O(log n)", "O(log n)", "O(1)",
                          "Priority Queue'da"),
        ]
    
    @staticmethod
    def get_graph_complexity() -> List[ComplexityInfo]:
        """Graf Algoritmaları Karmaşıklıkları"""
        return [
            ComplexityInfo("BFS", "O(V + E)", "O(V + E)", "O(V + E)", "O(V)",
                          "V: düğüm, E: kenar sayısı"),
            ComplexityInfo("DFS", "O(V + E)", "O(V + E)", "O(V + E)", "O(V)",
                          "Recursive stack space"),
            ComplexityInfo("Dijkstra", "O((V+E) log V)", "O((V+E) log V)", "O((V+E) log V)", "O(V)",
                          "Min-heap ile"),
            ComplexityInfo("A*", "O(E)", "O(E)", "O(b^d)", "O(V)",
                          "b: dallanma, d: derinlik"),
            ComplexityInfo("Add Vertex", "O(1)", "O(1)", "O(1)", "O(1)", ""),
            ComplexityInfo("Add Edge", "O(1)", "O(1)", "O(1)", "O(1)", ""),
        ]
    
    @staticmethod
    def get_sorting_complexity() -> List[ComplexityInfo]:
        """Sıralama Algoritmaları Karmaşıklıkları"""
        return [
            ComplexityInfo("QuickSort", "O(n log n)", "O(n log n)", "O(n²)", "O(log n)",
                          "Pivot seçimine bağlı, pratikte hızlı"),
            ComplexityInfo("MergeSort", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)",
                          "Kararlı, extra bellek gerektirir"),
            ComplexityInfo("HeapSort", "O(n log n)", "O(n log n)", "O(n log n)", "O(1)",
                          "In-place, kararsız"),
            ComplexityInfo("Binary Search", "O(1)", "O(log n)", "O(log n)", "O(1)",
                          "Sıralı dizi gerektirir"),
            ComplexityInfo("Exponential Search", "O(1)", "O(log n)", "O(log n)", "O(1)",
                          "Sınır bilinmediğinde"),
        ]
    
    @staticmethod
    def get_stack_queue_complexity() -> List[ComplexityInfo]:
        """Stack ve Queue Karmaşıklıkları"""
        return [
            ComplexityInfo("Stack.push", "O(1)", "O(1)", "O(1)", "O(1)", "LIFO"),
            ComplexityInfo("Stack.pop", "O(1)", "O(1)", "O(1)", "O(1)", "LIFO"),
            ComplexityInfo("Stack.peek", "O(1)", "O(1)", "O(1)", "O(1)", ""),
            ComplexityInfo("Queue.enqueue", "O(1)", "O(1)", "O(1)", "O(1)", "FIFO"),
            ComplexityInfo("Queue.dequeue", "O(1)", "O(1)", "O(1)", "O(1)", "FIFO"),
            ComplexityInfo("CircularQueue.enqueue", "O(1)", "O(1)", "O(1)", "O(1)", "Sabit boyut"),
            ComplexityInfo("Deque.appendleft/right", "O(1)", "O(1)", "O(1)", "O(1)", "Çift uçlu"),
            ComplexityInfo("Deque.popleft/right", "O(1)", "O(1)", "O(1)", "O(1)", "Çift uçlu"),
        ]
    
    @staticmethod
    def get_linked_list_complexity() -> List[ComplexityInfo]:
        """Bağlı Liste Karmaşıklıkları"""
        return [
            ComplexityInfo("Append", "O(1)", "O(1)", "O(1)", "O(1)",
                          "Tail pointer ile"),
            ComplexityInfo("Prepend", "O(1)", "O(1)", "O(1)", "O(1)", ""),
            ComplexityInfo("Insert (index)", "O(1)", "O(n)", "O(n)", "O(1)", ""),
            ComplexityInfo("Delete (index)", "O(1)", "O(n)", "O(n)", "O(1)", ""),
            ComplexityInfo("Search", "O(1)", "O(n)", "O(n)", "O(1)", ""),
            ComplexityInfo("Get (index)", "O(1)", "O(n)", "O(n)", "O(1)", ""),
            ComplexityInfo("Reverse", "O(n)", "O(n)", "O(n)", "O(1)", "In-place"),
        ]
    
    # ==================== AMPİRİK TESTLER ====================
    
    @staticmethod
    def measure_time(func: Callable, *args, iterations: int = 1000) -> Dict[str, float]:
        """
        Fonksiyon çalışma süresini ölç
        
        Returns:
            total, average, min, max süreler (ms)
        """
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            func(*args)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # ms
        
        return {
            'total_ms': sum(times),
            'avg_ms': sum(times) / len(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'iterations': iterations
        }
    
    @staticmethod
    def benchmark_avl_tree(sizes: List[int] = None) -> Dict[str, List[Dict]]:
        """AVL Tree performans testi"""
        if sizes is None:
            sizes = [100, 500, 1000, 5000, 10000]
        
        results = {'insert': [], 'search': [], 'delete': []}
        
        for n in sizes:
            tree = AVLTree()
            data = list(range(n))
            random.shuffle(data)
            
            # Insert test
            start = time.perf_counter()
            for x in data:
                tree.insert(x)
            insert_time = (time.perf_counter() - start) * 1000
            results['insert'].append({'n': n, 'time_ms': insert_time, 'per_op_us': insert_time * 1000 / n})
            
            # Search test
            search_data = random.sample(data, min(1000, n))
            start = time.perf_counter()
            for x in search_data:
                tree.search(x)
            search_time = (time.perf_counter() - start) * 1000
            results['search'].append({'n': n, 'time_ms': search_time, 'per_op_us': search_time * 1000 / len(search_data)})
            
            # Delete test
            delete_data = random.sample(data, min(100, n))
            start = time.perf_counter()
            for x in delete_data:
                tree.delete(x)
            delete_time = (time.perf_counter() - start) * 1000
            results['delete'].append({'n': n, 'time_ms': delete_time, 'per_op_us': delete_time * 1000 / len(delete_data)})
        
        return results
    
    @staticmethod
    def benchmark_sorting(sizes: List[int] = None) -> Dict[str, List[Dict]]:
        """Sıralama algoritmaları karşılaştırması"""
        if sizes is None:
            sizes = [1000, 5000, 10000, 50000]
        
        results = {'quicksort': [], 'mergesort': [], 'heapsort': []}
        
        for n in sizes:
            data = [random.randint(0, n * 10) for _ in range(n)]
            
            # QuickSort
            arr = data.copy()
            start = time.perf_counter()
            quicksort(arr)
            qs_time = (time.perf_counter() - start) * 1000
            results['quicksort'].append({'n': n, 'time_ms': qs_time})
            
            # MergeSort
            arr = data.copy()
            start = time.perf_counter()
            mergesort(arr)
            ms_time = (time.perf_counter() - start) * 1000
            results['mergesort'].append({'n': n, 'time_ms': ms_time})
            
            # HeapSort
            arr = data.copy()
            start = time.perf_counter()
            heapsort(arr)
            hs_time = (time.perf_counter() - start) * 1000
            results['heapsort'].append({'n': n, 'time_ms': hs_time})
        
        return results
    
    @staticmethod
    def benchmark_heap(sizes: List[int] = None) -> Dict[str, List[Dict]]:
        """Heap performans testi"""
        if sizes is None:
            sizes = [1000, 5000, 10000, 50000]
        
        results = {'push': [], 'pop': [], 'heapify': []}
        
        for n in sizes:
            heap = MinHeap()
            data = [random.randint(0, n * 10) for _ in range(n)]
            
            # Push test
            start = time.perf_counter()
            for x in data:
                heap.push(x)
            push_time = (time.perf_counter() - start) * 1000
            results['push'].append({'n': n, 'time_ms': push_time, 'per_op_us': push_time * 1000 / n})
            
            # Pop test
            start = time.perf_counter()
            while not heap.is_empty():
                heap.pop()
            pop_time = (time.perf_counter() - start) * 1000
            results['pop'].append({'n': n, 'time_ms': pop_time, 'per_op_us': pop_time * 1000 / n})
            
            # Heapify test
            start = time.perf_counter()
            heap2 = MinHeap()
            heap2.heapify(data)
            heapify_time = (time.perf_counter() - start) * 1000
            results['heapify'].append({'n': n, 'time_ms': heapify_time})
        
        return results
    
    @staticmethod
    def benchmark_graph(sizes: List[int] = None) -> Dict[str, List[Dict]]:
        """Graf algoritmaları performans testi"""
        if sizes is None:
            sizes = [100, 500, 1000, 2000]
        
        results = {'bfs': [], 'dfs': [], 'dijkstra': []}
        
        for n in sizes:
            # Graf oluştur (sparse)
            graph = Graph()
            for i in range(n):
                graph.add_vertex(str(i))
            
            # Her düğüme 2-5 komşu ekle
            for i in range(n):
                num_neighbors = random.randint(2, min(5, n - 1))
                neighbors = random.sample([j for j in range(n) if j != i], num_neighbors)
                for j in neighbors:
                    weight = random.uniform(1, 10)
                    graph.add_edge(str(i), str(j), weight)
            
            # BFS test
            start = time.perf_counter()
            graph.bfs('0')
            bfs_time = (time.perf_counter() - start) * 1000
            results['bfs'].append({'n': n, 'time_ms': bfs_time})
            
            # DFS test
            start = time.perf_counter()
            graph.dfs('0')
            dfs_time = (time.perf_counter() - start) * 1000
            results['dfs'].append({'n': n, 'time_ms': dfs_time})
            
            # Dijkstra test
            target = str(n - 1)
            start = time.perf_counter()
            graph.dijkstra('0', target)
            dijkstra_time = (time.perf_counter() - start) * 1000
            results['dijkstra'].append({'n': n, 'time_ms': dijkstra_time})
        
        return results
    
    @staticmethod
    def benchmark_stack_queue(sizes: List[int] = None) -> Dict[str, List[Dict]]:
        """Stack ve Queue performans testi"""
        if sizes is None:
            sizes = [10000, 50000, 100000, 500000]
        
        results = {'stack_push': [], 'stack_pop': [], 'queue_enqueue': [], 'queue_dequeue': []}
        
        for n in sizes:
            # Stack test
            stack = Stack()
            
            start = time.perf_counter()
            for i in range(n):
                stack.push(i)
            push_time = (time.perf_counter() - start) * 1000
            results['stack_push'].append({'n': n, 'time_ms': push_time, 'per_op_ns': push_time * 1e6 / n})
            
            start = time.perf_counter()
            while not stack.is_empty():
                stack.pop()
            pop_time = (time.perf_counter() - start) * 1000
            results['stack_pop'].append({'n': n, 'time_ms': pop_time, 'per_op_ns': pop_time * 1e6 / n})
            
            # Queue test
            queue = Queue()
            
            start = time.perf_counter()
            for i in range(n):
                queue.enqueue(i)
            enqueue_time = (time.perf_counter() - start) * 1000
            results['queue_enqueue'].append({'n': n, 'time_ms': enqueue_time, 'per_op_ns': enqueue_time * 1e6 / n})
            
            start = time.perf_counter()
            while not queue.is_empty():
                queue.dequeue()
            dequeue_time = (time.perf_counter() - start) * 1000
            results['queue_dequeue'].append({'n': n, 'time_ms': dequeue_time, 'per_op_ns': dequeue_time * 1e6 / n})
        
        return results
    
    # ==================== RAPORLAMA ====================
    
    @staticmethod
    def print_complexity_table(title: str, complexities: List[ComplexityInfo]):
        """Karmaşıklık tablosu yazdır"""
        print(f"\n{'=' * 100}")
        print(f" {title}")
        print('=' * 100)
        
        header = f"{'İşlem':<25} {'Best':^12} {'Average':^12} {'Worst':^12} {'Space':^10} {'Notlar':<20}"
        print(header)
        print('-' * 100)
        
        for c in complexities:
            print(f"{c.operation:<25} {c.time_best:^12} {c.time_average:^12} "
                  f"{c.time_worst:^12} {c.space:^10} {c.notes:<20}")
    
    @staticmethod
    def print_benchmark_results(title: str, results: Dict[str, List[Dict]]):
        """Benchmark sonuçlarını yazdır"""
        print(f"\n{'=' * 80}")
        print(f" {title} - Ampirik Sonuçlar")
        print('=' * 80)
        
        for operation, data in results.items():
            print(f"\n  {operation.upper()}:")
            print(f"  {'n':>10} {'Süre (ms)':>15} {'Per-op':>15}")
            print(f"  {'-' * 45}")
            
            for d in data:
                n = d['n']
                time_ms = d['time_ms']
                
                if 'per_op_us' in d:
                    per_op = f"{d['per_op_us']:.2f} µs"
                elif 'per_op_ns' in d:
                    per_op = f"{d['per_op_ns']:.1f} ns"
                else:
                    per_op = "-"
                
                print(f"  {n:>10} {time_ms:>15.3f} {per_op:>15}")
    
    def generate_full_report(self):
        """Tam rapor oluştur"""
        print("\n" + "=" * 100)
        print(" " * 25 + "VERİ YAPILARI VE ALGORİTMALAR")
        print(" " * 25 + "KARMAŞIKLIK ANALİZİ RAPORU")
        print("=" * 100)
        
        # Teorik Karmaşıklıklar
        print("\n" + "=" * 100)
        print(" BÖLÜM 1: TEORİK ZAMAN VE ALAN KARMAŞIKLIKLARI")
        print("=" * 100)
        
        self.print_complexity_table("1.1 AVL Ağacı (Dengeli İkili Arama Ağacı)", 
                                    self.get_avl_tree_complexity())
        
        self.print_complexity_table("1.2 Interval Tree (Aralık Ağacı)", 
                                    self.get_interval_tree_complexity())
        
        self.print_complexity_table("1.3 Heap (Yığın) ve Priority Queue", 
                                    self.get_heap_complexity())
        
        self.print_complexity_table("1.4 Graf Algoritmaları", 
                                    self.get_graph_complexity())
        
        self.print_complexity_table("1.5 Sıralama Algoritmaları", 
                                    self.get_sorting_complexity())
        
        self.print_complexity_table("1.6 Stack, Queue ve Deque", 
                                    self.get_stack_queue_complexity())
        
        self.print_complexity_table("1.7 Bağlı Liste (Doubly Linked List)", 
                                    self.get_linked_list_complexity())
        
        # Ampirik Sonuçlar
        print("\n\n" + "=" * 100)
        print(" BÖLÜM 2: AMPİRİK PERFORMANS ÖLÇÜMLERİ")
        print("=" * 100)
        
        print("\nTest ediliyor... (Bu birkaç dakika sürebilir)")
        
        print("\n2.1 AVL Tree Benchmark")
        avl_results = self.benchmark_avl_tree([100, 500, 1000, 5000])
        self.print_benchmark_results("AVL Tree", avl_results)
        
        print("\n2.2 Sorting Algorithms Benchmark")
        sort_results = self.benchmark_sorting([1000, 5000, 10000])
        self.print_benchmark_results("Sorting Algorithms", sort_results)
        
        print("\n2.3 Heap Benchmark")
        heap_results = self.benchmark_heap([1000, 5000, 10000])
        self.print_benchmark_results("Min Heap", heap_results)
        
        print("\n2.4 Graph Algorithms Benchmark")
        graph_results = self.benchmark_graph([100, 500, 1000])
        self.print_benchmark_results("Graph Algorithms", graph_results)
        
        print("\n2.5 Stack & Queue Benchmark")
        sq_results = self.benchmark_stack_queue([10000, 50000, 100000])
        self.print_benchmark_results("Stack & Queue", sq_results)
        
        # Özet ve Analiz
        print("\n\n" + "=" * 100)
        print(" BÖLÜM 3: ANALİZ VE ÖNERİLER")
        print("=" * 100)
        
        print("""
        
    3.1 VERİ YAPISI SEÇİMİ
    ----------------------
    
    Rezervasyon Sistemi için kullanılan veri yapıları:
    
    ┌─────────────────────┬─────────────────────────────────────────────────────┐
    │ Veri Yapısı         │ Kullanım Amacı                                      │
    ├─────────────────────┼─────────────────────────────────────────────────────┤
    │ AVL Tree            │ Salon/Rezervasyon hızlı arama ve sıralı erişim      │
    │ Interval Tree       │ Çakışma kontrolü, boş zaman aralığı bulma          │
    │ MinHeap/PriorityQ   │ Öncelikli rezervasyonlar, zamanlama                 │
    │ Graph + Dijkstra    │ Salon arası en kısa yol bulma                       │
    │ Stack               │ Undo/Redo işlemleri                                 │
    │ Queue               │ Bekleme listesi, FIFO işlemler                      │
    │ LinkedList          │ Dinamik bekleme listesi                             │
    └─────────────────────┴─────────────────────────────────────────────────────┘
    
    3.2 ALGORİTMA KARŞILAŞTIRMASI
    -----------------------------
    
    Sıralama Algoritmaları:
    - QuickSort: Ortalamada en hızlı, ancak worst-case O(n²)
    - MergeSort: Kararlı, her durumda O(n log n), ancak O(n) extra bellek
    - HeapSort: In-place O(1) bellek, O(n log n) garantili
    
    Önerilen: 
    - Genel kullanım → QuickSort (hızlı ortalama performans)
    - Kararlılık gerekli → MergeSort
    - Bellek kısıtlı → HeapSort
    
    3.3 PERFORMANS İYİLEŞTİRME ÖNERİLERİ
    ------------------------------------
    
    1. Cache-Friendly Design:
       - Sık erişilen veriler için array tabanlı yapılar tercih edin
       - LinkedList yerine ArrayList kullanın (locality)
    
    2. Lazy Evaluation:
       - İstatistikleri ve raporları cache'leyin
       - Dirty flag ile sadece değiştiğinde yeniden hesaplayın
    
    3. Index Structures:
       - Çok sorgulanan alanlara index ekleyin
       - Hash table ile O(1) arama sağlayın
    
    4. Batch Operations:
       - Toplu insert/delete için bulk metodlar kullanın
       - Transaction benzeri gruplu işlemler yapın
        """)
        
        print("\n" + "=" * 100)
        print(" Rapor Sonu")
        print("=" * 100 + "\n")


def main():
    """Test ve rapor oluştur"""
    analyzer = PerformanceAnalyzer()
    
    # Tam rapor
    analyzer.generate_full_report()


if __name__ == "__main__":
    main()
