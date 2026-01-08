"""
Sıralama ve Arama Algoritmaları
===============================
QuickSort, MergeSort, HeapSort ve Binary Search implementasyonları.
Rezervasyonları tarih, öncelik, salon adı vb. kriterlere göre sıralamak için kullanılır.

Zaman Karmaşıklığı:
- QuickSort: O(n log n) ortalama, O(n²) en kötü
- MergeSort: O(n log n) her durumda
- HeapSort: O(n log n) her durumda
- Binary Search: O(log n)

Uzay Karmaşıklığı:
- QuickSort: O(log n) - recursive stack
- MergeSort: O(n) - yardımcı dizi
- HeapSort: O(1) - yerinde sıralama
- Binary Search: O(1) iteratif, O(log n) recursive
"""

from typing import Any, List, Callable, Optional, Tuple
import random
import time


# ==================== QUICKSORT ====================

def quicksort(arr: List[Any], key: Callable = None, reverse: bool = False) -> List[Any]:
    """
    QuickSort Algoritması - Divide and Conquer
    
    Args:
        arr: Sıralanacak liste
        key: Karşılaştırma için anahtar fonksiyonu
        reverse: True ise azalan sıra
        
    Returns:
        Sıralanmış yeni liste (orijinal değişmez)
        
    Zaman Karmaşıklığı: O(n log n) ortalama, O(n²) en kötü
    Uzay Karmaşıklığı: O(log n) stack için
    """
    if len(arr) <= 1:
        return arr.copy()
    
    result = arr.copy()
    _quicksort_inplace(result, 0, len(result) - 1, key, reverse)
    return result


def _quicksort_inplace(arr: List[Any], low: int, high: int, 
                       key: Callable = None, reverse: bool = False) -> None:
    """Yerinde QuickSort (in-place)"""
    if low < high:
        # Pivot seç ve partition yap
        pivot_idx = _partition(arr, low, high, key, reverse)
        
        # Sol ve sağ alt dizileri recursive sırala
        _quicksort_inplace(arr, low, pivot_idx - 1, key, reverse)
        _quicksort_inplace(arr, pivot_idx + 1, high, key, reverse)


def _partition(arr: List[Any], low: int, high: int, 
               key: Callable = None, reverse: bool = False) -> int:
    """
    Lomuto partition şeması
    Pivot olarak son elemanı seçer
    """
    if key is None:
        key = lambda x: x
    
    # Rastgele pivot seç (en kötü durumu önlemek için)
    random_idx = random.randint(low, high)
    arr[random_idx], arr[high] = arr[high], arr[random_idx]
    
    pivot = key(arr[high])
    i = low - 1
    
    for j in range(low, high):
        current = key(arr[j])
        
        if reverse:
            should_swap = current > pivot
        else:
            should_swap = current < pivot
        
        if should_swap:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quicksort_three_way(arr: List[Any], key: Callable = None) -> List[Any]:
    """
    3-Way QuickSort - Tekrarlayan elemanlar için optimize
    
    Dutch National Flag algoritması kullanır.
    Çok sayıda tekrarlayan eleman varsa daha verimli.
    """
    result = arr.copy()
    _quicksort_three_way(result, 0, len(result) - 1, key)
    return result


def _quicksort_three_way(arr: List[Any], low: int, high: int, key: Callable = None) -> None:
    if low >= high:
        return
    
    if key is None:
        key = lambda x: x
    
    # 3-way partition
    lt, gt = low, high
    pivot = key(arr[low])
    i = low + 1
    
    while i <= gt:
        current = key(arr[i])
        if current < pivot:
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        elif current > pivot:
            arr[gt], arr[i] = arr[i], arr[gt]
            gt -= 1
        else:
            i += 1
    
    _quicksort_three_way(arr, low, lt - 1, key)
    _quicksort_three_way(arr, gt + 1, high, key)


# ==================== MERGESORT ====================

def mergesort(arr: List[Any], key: Callable = None, reverse: bool = False) -> List[Any]:
    """
    MergeSort Algoritması - Kararlı sıralama
    
    Args:
        arr: Sıralanacak liste
        key: Karşılaştırma için anahtar fonksiyonu
        reverse: True ise azalan sıra
        
    Returns:
        Sıralanmış yeni liste
        
    Zaman Karmaşıklığı: O(n log n) her durumda
    Uzay Karmaşıklığı: O(n) yardımcı dizi için
    
    Not: Kararlı sıralama - eşit elemanların göreceli sırası korunur
    """
    if len(arr) <= 1:
        return arr.copy()
    
    if key is None:
        key = lambda x: x
    
    return _mergesort(arr, key, reverse)


def _mergesort(arr: List[Any], key: Callable, reverse: bool) -> List[Any]:
    """Recursive MergeSort"""
    if len(arr) <= 1:
        return arr
    
    # Diziyi ikiye böl
    mid = len(arr) // 2
    left = _mergesort(arr[:mid], key, reverse)
    right = _mergesort(arr[mid:], key, reverse)
    
    # Birleştir
    return _merge(left, right, key, reverse)


def _merge(left: List[Any], right: List[Any], key: Callable, reverse: bool) -> List[Any]:
    """İki sıralı diziyi birleştir"""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        left_key = key(left[i])
        right_key = key(right[j])
        
        if reverse:
            should_take_left = left_key >= right_key
        else:
            should_take_left = left_key <= right_key
        
        if should_take_left:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # Kalan elemanları ekle
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result


def mergesort_iterative(arr: List[Any], key: Callable = None, reverse: bool = False) -> List[Any]:
    """
    İteratif MergeSort (Bottom-up)
    
    Recursive stack kullanmaz, bellek açısından daha verimli.
    """
    if len(arr) <= 1:
        return arr.copy()
    
    if key is None:
        key = lambda x: x
    
    result = arr.copy()
    n = len(result)
    
    # Alt dizi boyutu 1'den başla, her seferinde 2 katına çık
    size = 1
    while size < n:
        left = 0
        while left < n:
            mid = min(left + size, n)
            right = min(left + 2 * size, n)
            
            # [left:mid] ve [mid:right] birleştir
            if mid < right:
                merged = _merge(result[left:mid], result[mid:right], key, reverse)
                result[left:left + len(merged)] = merged
            
            left += 2 * size
        
        size *= 2
    
    return result


# ==================== HEAPSORT ====================

def heapsort(arr: List[Any], key: Callable = None, reverse: bool = False) -> List[Any]:
    """
    HeapSort Algoritması - Yerinde sıralama
    
    Args:
        arr: Sıralanacak liste
        key: Karşılaştırma için anahtar fonksiyonu
        reverse: True ise azalan sıra
        
    Returns:
        Sıralanmış yeni liste
        
    Zaman Karmaşıklığı: O(n log n) her durumda
    Uzay Karmaşıklığı: O(1) yerinde
    """
    if len(arr) <= 1:
        return arr.copy()
    
    if key is None:
        key = lambda x: x
    
    result = arr.copy()
    n = len(result)
    
    # Max-heap oluştur (artan sıra için)
    # Min-heap oluştur (azalan sıra için)
    for i in range(n // 2 - 1, -1, -1):
        _heapify(result, n, i, key, not reverse)
    
    # Elemanları tek tek çıkar
    for i in range(n - 1, 0, -1):
        result[0], result[i] = result[i], result[0]
        _heapify(result, i, 0, key, not reverse)
    
    return result


def _heapify(arr: List[Any], n: int, i: int, key: Callable, is_max_heap: bool) -> None:
    """Heap özelliğini düzelt"""
    target = i
    left = 2 * i + 1
    right = 2 * i + 2
    
    if is_max_heap:
        # Max-heap: büyük eleman yukarı
        if left < n and key(arr[left]) > key(arr[target]):
            target = left
        if right < n and key(arr[right]) > key(arr[target]):
            target = right
    else:
        # Min-heap: küçük eleman yukarı
        if left < n and key(arr[left]) < key(arr[target]):
            target = left
        if right < n and key(arr[right]) < key(arr[target]):
            target = right
    
    if target != i:
        arr[i], arr[target] = arr[target], arr[i]
        _heapify(arr, n, target, key, is_max_heap)


# ==================== BINARY SEARCH ====================

def binary_search(arr: List[Any], target: Any, key: Callable = None) -> int:
    """
    Binary Search - Sıralı dizide arama
    
    Args:
        arr: Sıralı liste (küçükten büyüğe)
        target: Aranan değer
        key: Karşılaştırma için anahtar fonksiyonu
        
    Returns:
        Bulunan indeks, bulunamazsa -1
        
    Zaman Karmaşıklığı: O(log n)
    Uzay Karmaşıklığı: O(1)
    """
    if not arr:
        return -1
    
    if key is None:
        key = lambda x: x
    
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        mid_val = key(arr[mid])
        
        if mid_val == target:
            return mid
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1


def binary_search_recursive(arr: List[Any], target: Any, key: Callable = None) -> int:
    """Binary Search - Recursive versiyon"""
    if key is None:
        key = lambda x: x
    
    def _search(left: int, right: int) -> int:
        if left > right:
            return -1
        
        mid = (left + right) // 2
        mid_val = key(arr[mid])
        
        if mid_val == target:
            return mid
        elif mid_val < target:
            return _search(mid + 1, right)
        else:
            return _search(left, mid - 1)
    
    return _search(0, len(arr) - 1)


def binary_search_leftmost(arr: List[Any], target: Any, key: Callable = None) -> int:
    """
    En soldaki (ilk) eşleşen elemanı bul
    
    Tekrarlayan elemanlar varsa en küçük indeksi döndürür.
    """
    if not arr:
        return -1
    
    if key is None:
        key = lambda x: x
    
    left, right = 0, len(arr)
    
    while left < right:
        mid = (left + right) // 2
        if key(arr[mid]) < target:
            left = mid + 1
        else:
            right = mid
    
    if left < len(arr) and key(arr[left]) == target:
        return left
    return -1


def binary_search_rightmost(arr: List[Any], target: Any, key: Callable = None) -> int:
    """
    En sağdaki (son) eşleşen elemanı bul
    
    Tekrarlayan elemanlar varsa en büyük indeksi döndürür.
    """
    if not arr:
        return -1
    
    if key is None:
        key = lambda x: x
    
    left, right = 0, len(arr)
    
    while left < right:
        mid = (left + right) // 2
        if key(arr[mid]) <= target:
            left = mid + 1
        else:
            right = mid
    
    if left > 0 and key(arr[left - 1]) == target:
        return left - 1
    return -1


def binary_search_insert_position(arr: List[Any], target: Any, key: Callable = None) -> int:
    """
    Elemanın eklenmesi gereken pozisyonu bul
    
    Sıralı diziyi koruyacak şekilde ekleme pozisyonu döndürür.
    """
    if not arr:
        return 0
    
    if key is None:
        key = lambda x: x
    
    left, right = 0, len(arr)
    
    while left < right:
        mid = (left + right) // 2
        if key(arr[mid]) < target:
            left = mid + 1
        else:
            right = mid
    
    return left


def binary_search_range(arr: List[Any], low: Any, high: Any, key: Callable = None) -> List[Any]:
    """
    Belirli aralıktaki elemanları bul
    
    Args:
        arr: Sıralı liste
        low: Alt sınır (dahil)
        high: Üst sınır (dahil)
        key: Karşılaştırma fonksiyonu
        
    Returns:
        [low, high] aralığındaki elemanların listesi
    """
    if not arr:
        return []
    
    if key is None:
        key = lambda x: x
    
    # Sol sınırı bul
    left = binary_search_insert_position(arr, low, key)
    
    # Sağ sınırı bul
    right = binary_search_insert_position(arr, high, key)
    
    # high değerini içeren elemanları da dahil et
    while right < len(arr) and key(arr[right]) == high:
        right += 1
    
    return arr[left:right]


# ==================== KARŞILAŞTIRMALI TEST ====================

def benchmark_sorting_algorithms(arr: List[Any], key: Callable = None) -> dict:
    """
    Sıralama algoritmalarının performans karşılaştırması
    
    Returns:
        Her algoritma için çalışma süresi (saniye)
    """
    results = {}
    
    # QuickSort
    start = time.perf_counter()
    quicksort(arr, key)
    results['QuickSort'] = time.perf_counter() - start
    
    # MergeSort
    start = time.perf_counter()
    mergesort(arr, key)
    results['MergeSort'] = time.perf_counter() - start
    
    # HeapSort
    start = time.perf_counter()
    heapsort(arr, key)
    results['HeapSort'] = time.perf_counter() - start
    
    # Python built-in
    start = time.perf_counter()
    sorted(arr, key=key)
    results['Python sorted()'] = time.perf_counter() - start
    
    return results


# Kullanım örneği ve test
if __name__ == "__main__":
    print("=" * 60)
    print("Sıralama ve Arama Algoritmaları Test")
    print("=" * 60)
    
    # Test verisi - Rezervasyonlar
    reservations = [
        {"id": 1, "name": "Toplantı A", "start": 900, "priority": 2},
        {"id": 2, "name": "Toplantı B", "start": 600, "priority": 1},
        {"id": 3, "name": "Toplantı C", "start": 1400, "priority": 3},
        {"id": 4, "name": "Toplantı D", "start": 800, "priority": 1},
        {"id": 5, "name": "Toplantı E", "start": 1100, "priority": 2},
        {"id": 6, "name": "Toplantı F", "start": 700, "priority": 2},
    ]
    
    print("\nOrijinal rezervasyonlar:")
    for r in reservations:
        print(f"  {r['name']}: Saat {r['start']//60:02d}:{r['start']%60:02d}, Öncelik {r['priority']}")
    
    # QuickSort - Başlangıç saatine göre
    print("\n--- QuickSort (Başlangıç saatine göre) ---")
    sorted_by_start = quicksort(reservations, key=lambda r: r['start'])
    for r in sorted_by_start:
        print(f"  {r['name']}: {r['start']//60:02d}:{r['start']%60:02d}")
    
    # MergeSort - Önceliğe göre
    print("\n--- MergeSort (Önceliğe göre) ---")
    sorted_by_priority = mergesort(reservations, key=lambda r: r['priority'])
    for r in sorted_by_priority:
        print(f"  {r['name']}: Öncelik {r['priority']}")
    
    # HeapSort - Öncelik sonra başlangıç
    print("\n--- HeapSort (Öncelik, sonra başlangıç) ---")
    sorted_combined = heapsort(reservations, key=lambda r: (r['priority'], r['start']))
    for r in sorted_combined:
        print(f"  {r['name']}: Öncelik {r['priority']}, Saat {r['start']//60:02d}:{r['start']%60:02d}")
    
    # Binary Search testi
    print("\n" + "=" * 40)
    print("Binary Search Testleri")
    
    # Sıralı dizi oluştur
    sorted_starts = sorted([r['start'] for r in reservations])
    print(f"\nSıralı başlangıç saatleri: {sorted_starts}")
    
    # Arama
    target = 800
    idx = binary_search(sorted_starts, target)
    print(f"\n{target} araması: İndeks {idx}")
    
    target = 1000
    idx = binary_search(sorted_starts, target)
    print(f"{target} araması: İndeks {idx} (bulunamadı)")
    
    # Ekleme pozisyonu
    target = 1000
    pos = binary_search_insert_position(sorted_starts, target)
    print(f"\n{target} için ekleme pozisyonu: {pos}")
    
    # Aralık sorgusu
    low, high = 700, 1000
    range_result = binary_search_range(sorted_starts, low, high)
    print(f"\n[{low}, {high}] aralığındaki değerler: {range_result}")
    
    # Performans karşılaştırması
    print("\n" + "=" * 40)
    print("Performans Karşılaştırması (10000 eleman)")
    
    test_data = [random.randint(1, 100000) for _ in range(10000)]
    results = benchmark_sorting_algorithms(test_data)
    
    print(f"\n{'Algoritma':<20} {'Süre (saniye)':<15}")
    print("-" * 35)
    for algo, duration in sorted(results.items(), key=lambda x: x[1]):
        print(f"{algo:<20} {duration:.6f}")
    
    # Doğrulama
    print("\n" + "=" * 40)
    print("Algoritma Doğrulama")
    
    test = [64, 34, 25, 12, 22, 11, 90]
    expected = sorted(test)
    
    print(f"Orijinal: {test}")
    print(f"Beklenen: {expected}")
    print(f"QuickSort: {quicksort(test)} {'✓' if quicksort(test) == expected else '✗'}")
    print(f"MergeSort: {mergesort(test)} {'✓' if mergesort(test) == expected else '✗'}")
    print(f"HeapSort:  {heapsort(test)} {'✓' if heapsort(test) == expected else '✗'}")
