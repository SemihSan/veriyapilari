# Salon Rezervasyon Sistemi

Veri Yapıları Dersi Projem

## Proje hk

Bu proje, bir salon/toplantı odası rezervasyon sistemi uygulamasıdır. Sistemde çeşitli veri yapıları ve algoritmalar kullanılarak verimli bir şekilde rezervasyon yönetimi sağlanmaktadır.

## Kullanılan veri yapiları

### 1. Dengeli Arama Ağacı (AVL Tree)
- **Dosya:** `data_structures/avl_tree.py`
- **Amaç:** Salon ve rezervasyonların hızlı ekleme, silme ve arama işlemleri
- **Karmaşıklık:** O(log n) - insert, delete, search

### 2. Interval Tree (Aralık Ağacı)
- **Dosya:** `data_structures/interval_tree.py`
- **Amaç:** Zaman aralığı çakışma kontrolü, boş slot bulma
- **Karmaşıklık:** O(log n + k) - overlap query (k: sonuç sayısı)

### 3. Heap ve Priority Queue
- **Dosya:** `data_structures/heap.py`
- **Amaç:** Öncelikli rezervasyon kuyruğu, zamanlama
- **Karmaşıklık:** O(log n) - push/pop, O(1) - peek

### 4. Graf ve Yol Bulma Algoritmaları
- **Dosya:** `data_structures/graph.py`
- **Algoritmalar:**
  - BFS (Breadth-First Search) - O(V + E)
  - DFS (Depth-First Search) - O(V + E)
  - Dijkstra (En kısa yol) - O((V+E) log V)
  - A* (Heuristic arama) - O(E)

### 5. Sıralama Algoritmaları
- **Dosya:** `data_structures/sorting.py`
- **Algoritmalar:**
  - QuickSort - O(n log n) ortalama, O(n²) en kötü
  - MergeSort - O(n log n) her durumda
  - HeapSort - O(n log n) her durumda, in-place

### 6. Arama Algoritmaları
- **Dosya:** `data_structures/sorting.py`
- **Algoritmalar:**
  - Binary Search - O(log n)
  - Exponential Search - O(log n)

### 7. Stack ve Queue
- **Dosya:** `data_structures/stack_queue.py`
- **Yapılar:**
  - Stack (LIFO) - Undo/Redo desteği
  - Queue (FIFO) - Bekleme listesi
  - Circular Queue - Sabit boyutlu kuyruk
  - Deque - Çift uçlu kuyruk
- **Karmaşıklık:** O(1) - tüm temel işlemler

### 8. Linked List
- **Dosya:** `data_structures/linked_list.py`
- **Amaç:** Dinamik bekleme listesi yönetimi
- **Karmaşıklık:** O(1) - append/prepend, O(n) - search/delete

## Dosya Yapısı

```
salon_rezervasyon/
├── data_structures/
│   ├── __init__.py          # Paket tanımları ve export
│   ├── avl_tree.py          # AVL Tree implementasyonu
│   ├── interval_tree.py     # Interval Tree implementasyonu
│   ├── heap.py              # Heap ve Priority Queue
│   ├── graph.py             # Graf ve yol bulma algoritmaları
│   ├── sorting.py           # Sıralama ve arama algoritmaları
│   ├── stack_queue.py       # Stack, Queue, Deque
│   └── linked_list.py       # Bağlı liste
├── reservation_system.py     # Ana iş mantığı
├── data_manager.py          # JSON/CSV dosya işlemleri
├── cli.py                   # Komut satırı arayüzü
├── performance_analysis.py   # Karmaşıklık analizi
├── main.py                  # Giriş noktası
└── calisma.md                # Bu dosya
```

## 🚀 Kullanım

### Kurulum

```bash
# Proje dizinine gidin
cd salon_rezervasyon

# Python 3.8+ gereklidir
python --version
```

### Çalıştırma

```bash
# CLI (Komut Satırı Arayüzü) başlat
python main.py

# Demo verileriyle başlat
python main.py --demo

# Testleri çalıştır
python main.py --test

# Performans analizi
python main.py --benchmark
```

## Karmaşıklık Tablosu

### Zaman Karmaşıklıkları

| Veri Yapısı | Insert | Delete | Search | Space |
|-------------|--------|--------|--------|-------|
| AVL Tree | O(log n) | O(log n) | O(log n) | O(n) |
| Interval Tree | O(log n) | O(log n) | O(log n + k) | O(n) |
| Heap | O(log n) | O(log n) | O(n) | O(n) |
| Stack | O(1) | O(1) | O(n) | O(n) |
| Queue | O(1) | O(1) | O(n) | O(n) |
| LinkedList | O(1)* | O(n) | O(n) | O(n) |

*Başa/sona ekleme için

### Algoritma Karmaşıklıkları

| Algoritma | Best | Average | Worst | Space |
|-----------|------|---------|-------|-------|
| QuickSort | O(n log n) | O(n log n) | O(n²) | O(log n) |
| MergeSort | O(n log n) | O(n log n) | O(n log n) | O(n) |
| HeapSort | O(n log n) | O(n log n) | O(n log n) | O(1) |
| Binary Search | O(1) | O(log n) | O(log n) | O(1) |
| Dijkstra | O((V+E) log V) | O((V+E) log V) | O((V+E) log V) | O(V) |

## Özellikler

### Salon Yönetimi
- Salon ekleme, düzenleme, silme
- Kapasite ve donanım yönetimi
- Salon türleri (Toplantı, Konferans, Eğitim, Parti, Stüdyo)

### Rezervasyon Yönetimi
- Rezervasyon oluşturma ve iptal
- Çakışma kontrolü (Interval Tree ile)
- Öncelikli rezervasyonlar (Priority Queue ile)
- Otomatik alternatif önerisi

### Yol Bulma
- Salonlar arası en kısa yol (Dijkstra)
- Bina içi navigasyon

### Undo/Redo
- Tüm işlemler geri alınabilir
- Stack tabanlı undo/redo sistemi

### Bekleme Listesi
- FIFO ve öncelik tabanlı kuyruk
- Müsait olunca otomatik bildirim

### Veri Yönetimi
- JSON formatında kaydetme/yükleme
- CSV dışa aktarma
- Yedekleme ve geri yükleme

## Test

```bash
# Tüm testleri çalıştır
python main.py --test

# Beklenen çıktı:
# [TEST 1] AVL Tree
#   ✓ Insert, Search, Delete, Range Query - BAŞARILI
# [TEST 2] Interval Tree
#   ✓ Insert, Overlap Query, Point Query - BAŞARILI
# ...
# TÜM TESTLER BAŞARILI! ✓
```

##  Performans Analizi

```bash
# Detaylı performans raporu
python main.py --benchmark
```

Rapor içeriği:
- Teorik karmaşıklık tabloları
- Ampirik performans ölçümleri
- Farklı boyutlar için karşılaştırma

## nasil kullanilir

### 1. Yeni Salon Ekleme
```
Ana Menü > 1. Salon Yönetimi > 2. Yeni Salon Ekle
```

### 2. Rezervasyon Yapma
```
Ana Menü > 2. Rezervasyon Yönetimi > 1. Yeni Rezervasyon
```

### 3. Çakışma Kontrolü
```
Ana Menü > 2. Rezervasyon Yönetimi > 7. Çakışma Kontrolü
```

### 4. En Kısa Yol Bulma
```
Ana Menü > 1. Salon Yönetimi > 7. Salon Bağlantıları > 2. En Kısa Yol Bul
```

### 5. Geri Al (Undo)
```
Ana Menü > 7. Geri Al / Yinele > 1. Geri Al
```


##  Geliştirici Notları

Her modül bağımsız olarak test edilebilir:

```bash
# AVL Tree test
python data_structures/avl_tree.py

# Interval Tree test
python data_structures/interval_tree.py

# Sorting algoritmaları test
python data_structures/sorting.py
```

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.
