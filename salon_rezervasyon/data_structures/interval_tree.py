"""
Interval Tree Implementasyonu
=============================
Rezervasyon çakışma kontrolü için optimize edilmiş veri yapısı.
Zaman aralıklarını (başlangıç, bitiş) verimli şekilde saklar ve sorgular.

Zaman Karmaşıklığı:
- Ekleme (Insert): O(log n)
- Çakışma Sorgusu (Overlap Query): O(log n + k) - k: çakışan aralık sayısı
- Silme (Delete): O(log n)
- Belirli Noktadaki Aralıkları Bulma: O(log n + k)

Uzay Karmaşıklığı: O(n)
"""

from typing import Any, Optional, List, Tuple
from datetime import datetime, timedelta


class Interval:
    """Zaman aralığı sınıfı"""
    
    def __init__(self, start: Any, end: Any, data: Any = None):
        """
        Args:
            start: Başlangıç zamanı (datetime veya sayısal)
            end: Bitiş zamanı (datetime veya sayısal)
            data: İlişkili veri (rezervasyon bilgisi vb.)
        """
        if start > end:
            raise ValueError("Başlangıç zamanı bitiş zamanından büyük olamaz")
        
        self.start = start
        self.end = end
        self.data = data
    
    def overlaps(self, other: 'Interval') -> bool:
        """Başka bir aralık ile çakışıyor mu?"""
        return self.start < other.end and other.start < self.end
    
    def contains(self, point: Any) -> bool:
        """Verilen nokta bu aralıkta mı?"""
        return self.start <= point < self.end
    
    def duration(self) -> Any:
        """Aralık süresini döndür"""
        return self.end - self.start
    
    def __eq__(self, other):
        if not isinstance(other, Interval):
            return False
        return self.start == other.start and self.end == other.end
    
    def __hash__(self):
        return hash((self.start, self.end))
    
    def __repr__(self):
        return f"Interval({self.start}, {self.end})"
    
    def __lt__(self, other):
        if self.start != other.start:
            return self.start < other.start
        return self.end < other.end


class IntervalNode:
    """Interval Tree düğümü"""
    
    def __init__(self, interval: Interval):
        self.interval = interval
        self.max_end = interval.end  # Bu alt ağaçtaki maksimum bitiş zamanı
        self.left: Optional['IntervalNode'] = None
        self.right: Optional['IntervalNode'] = None
        self.height: int = 1
    
    def __repr__(self):
        return f"IntervalNode({self.interval}, max_end={self.max_end})"


class IntervalTree:
    """
    Interval Tree - Aralık sorguları için optimize edilmiş ağaç
    
    Kullanım Alanları:
    - Salon/oda rezervasyonları için çakışma kontrolü
    - Takvim uygulamalarında zaman aralığı sorguları
    - Kaynak planlama sistemleri
    """
    
    def __init__(self):
        self.root: Optional[IntervalNode] = None
        self.size: int = 0
    
    def _height(self, node: Optional[IntervalNode]) -> int:
        return node.height if node else 0
    
    def _balance_factor(self, node: Optional[IntervalNode]) -> int:
        if not node:
            return 0
        return self._height(node.left) - self._height(node.right)
    
    def _update_height_and_max(self, node: IntervalNode) -> None:
        """Yükseklik ve max_end değerlerini güncelle"""
        node.height = 1 + max(self._height(node.left), self._height(node.right))
        
        # max_end güncelle
        node.max_end = node.interval.end
        if node.left:
            node.max_end = max(node.max_end, node.left.max_end)
        if node.right:
            node.max_end = max(node.max_end, node.right.max_end)
    
    def _rotate_right(self, y: IntervalNode) -> IntervalNode:
        """Sağa rotasyon"""
        x = y.left
        T2 = x.right
        
        x.right = y
        y.left = T2
        
        self._update_height_and_max(y)
        self._update_height_and_max(x)
        
        return x
    
    def _rotate_left(self, x: IntervalNode) -> IntervalNode:
        """Sola rotasyon"""
        y = x.right
        T2 = y.left
        
        y.left = x
        x.right = T2
        
        self._update_height_and_max(x)
        self._update_height_and_max(y)
        
        return y
    
    def insert(self, interval: Interval) -> bool:
        """
        Yeni aralık ekle
        
        Args:
            interval: Eklenecek aralık
            
        Returns:
            bool: Ekleme başarılı ise True
            
        Zaman Karmaşıklığı: O(log n)
        """
        def _insert(node: Optional[IntervalNode], interval: Interval) -> IntervalNode:
            if not node:
                return IntervalNode(interval)
            
            # Başlangıç zamanına göre yerleştir
            if interval.start < node.interval.start:
                node.left = _insert(node.left, interval)
            else:
                node.right = _insert(node.right, interval)
            
            # Yükseklik ve max_end güncelle
            self._update_height_and_max(node)
            
            # Dengeyi kontrol et
            balance = self._balance_factor(node)
            
            # Sol-Sol durumu
            if balance > 1 and interval.start < node.left.interval.start:
                return self._rotate_right(node)
            
            # Sağ-Sağ durumu
            if balance < -1 and interval.start >= node.right.interval.start:
                return self._rotate_left(node)
            
            # Sol-Sağ durumu
            if balance > 1 and interval.start >= node.left.interval.start:
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)
            
            # Sağ-Sol durumu
            if balance < -1 and interval.start < node.right.interval.start:
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)
            
            return node
        
        self.root = _insert(self.root, interval)
        self.size += 1
        return True
    
    def find_overlapping(self, query: Interval) -> List[Interval]:
        """
        Verilen aralık ile çakışan tüm aralıkları bul
        
        Args:
            query: Sorgulanacak aralık
            
        Returns:
            Çakışan aralıkların listesi
            
        Zaman Karmaşıklığı: O(log n + k) - k: çakışan aralık sayısı
        """
        result = []
        
        def _search(node: Optional[IntervalNode]):
            if not node:
                return
            
            # Eğer bu düğümün max_end değeri query'nin başlangıcından küçükse,
            # bu alt ağaçta çakışan aralık olamaz
            if node.max_end <= query.start:
                return
            
            # Sol alt ağacı kontrol et
            if node.left:
                _search(node.left)
            
            # Mevcut düğümü kontrol et
            if node.interval.overlaps(query):
                result.append(node.interval)
            
            # Sağ alt ağacı kontrol et (sadece gerekiyorsa)
            if node.interval.start < query.end:
                _search(node.right)
        
        _search(self.root)
        return result
    
    def has_overlap(self, query: Interval) -> bool:
        """
        Verilen aralık ile çakışan herhangi bir aralık var mı?
        
        Args:
            query: Sorgulanacak aralık
            
        Returns:
            bool: Çakışma varsa True
            
        Zaman Karmaşıklığı: O(log n)
        """
        def _has_overlap(node: Optional[IntervalNode]) -> bool:
            if not node:
                return False
            
            # Bu alt ağaçta çakışma olamaz
            if node.max_end <= query.start:
                return False
            
            # Mevcut düğümü kontrol et
            if node.interval.overlaps(query):
                return True
            
            # Sol alt ağacı kontrol et
            if node.left and node.left.max_end > query.start:
                if _has_overlap(node.left):
                    return True
            
            # Sağ alt ağacı kontrol et
            if node.interval.start < query.end:
                return _has_overlap(node.right)
            
            return False
        
        return _has_overlap(self.root)
    
    def find_at_point(self, point: Any) -> List[Interval]:
        """
        Verilen noktayı içeren tüm aralıkları bul
        
        Args:
            point: Sorgulanacak nokta (zaman)
            
        Returns:
            Noktayı içeren aralıkların listesi
            
        Zaman Karmaşıklığı: O(log n + k)
        """
        # Noktayı [point, point+epsilon] aralığı olarak sor
        result = []
        
        def _search(node: Optional[IntervalNode]):
            if not node:
                return
            
            if node.max_end <= point:
                return
            
            if node.left:
                _search(node.left)
            
            if node.interval.contains(point):
                result.append(node.interval)
            
            if node.interval.start <= point:
                _search(node.right)
        
        _search(self.root)
        return result
    
    def delete(self, interval: Interval) -> bool:
        """
        Aralığı sil
        
        Args:
            interval: Silinecek aralık
            
        Returns:
            bool: Silme başarılı ise True
            
        Zaman Karmaşıklığı: O(log n)
        """
        def _find_min(node: IntervalNode) -> IntervalNode:
            current = node
            while current.left:
                current = current.left
            return current
        
        def _delete(node: Optional[IntervalNode], interval: Interval) -> Optional[IntervalNode]:
            if not node:
                return None
            
            if interval < node.interval:
                node.left = _delete(node.left, interval)
            elif interval.start > node.interval.start or \
                 (interval.start == node.interval.start and interval.end > node.interval.end):
                node.right = _delete(node.right, interval)
            elif interval == node.interval:
                # Silinecek düğüm bulundu
                if not node.left:
                    return node.right
                elif not node.right:
                    return node.left
                else:
                    successor = _find_min(node.right)
                    node.interval = successor.interval
                    node.right = _delete(node.right, successor.interval)
            else:
                node.right = _delete(node.right, interval)
            
            self._update_height_and_max(node)
            
            # Dengeleme
            balance = self._balance_factor(node)
            
            if balance > 1 and self._balance_factor(node.left) >= 0:
                return self._rotate_right(node)
            
            if balance > 1 and self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)
            
            if balance < -1 and self._balance_factor(node.right) <= 0:
                return self._rotate_left(node)
            
            if balance < -1 and self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)
            
            return node
        
        old_size = self.size
        self.root = _delete(self.root, interval)
        
        # Boyut kontrolü için basit yaklaşım
        new_size = self._count_nodes(self.root)
        if new_size < old_size:
            self.size = new_size
            return True
        return False
    
    def _count_nodes(self, node: Optional[IntervalNode]) -> int:
        """Düğüm sayısını hesapla"""
        if not node:
            return 0
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)
    
    def get_all_intervals(self) -> List[Interval]:
        """Tüm aralıkları sıralı olarak döndür"""
        result = []
        
        def _inorder(node: Optional[IntervalNode]):
            if node:
                _inorder(node.left)
                result.append(node.interval)
                _inorder(node.right)
        
        _inorder(self.root)
        return result
    
    def find_available_slots(self, start: Any, end: Any, duration: Any) -> List[Interval]:
        """
        Verilen zaman aralığında müsait slotları bul
        
        Args:
            start: Arama başlangıcı
            end: Arama bitişi
            duration: Minimum slot süresi
            
        Returns:
            Müsait zaman aralıklarının listesi
        """
        # Mevcut rezervasyonları al
        existing = self.find_overlapping(Interval(start, end))
        existing.sort(key=lambda x: x.start)
        
        available = []
        current_start = start
        
        for interval in existing:
            if interval.start > current_start:
                # Boşluk var
                gap = interval.start - current_start
                if isinstance(duration, timedelta):
                    if gap >= duration:
                        available.append(Interval(current_start, interval.start))
                else:
                    if gap >= duration:
                        available.append(Interval(current_start, interval.start))
            
            # current_start'ı güncelle
            if interval.end > current_start:
                current_start = interval.end
        
        # Son boşluğu kontrol et
        if current_start < end:
            gap = end - current_start
            if isinstance(duration, timedelta):
                if gap >= duration:
                    available.append(Interval(current_start, end))
            else:
                if gap >= duration:
                    available.append(Interval(current_start, end))
        
        return available
    
    def suggest_alternative(self, requested: Interval, search_range: Tuple[Any, Any] = None) -> List[Interval]:
        """
        Çakışma durumunda alternatif zaman öner
        
        Args:
            requested: İstenen aralık
            search_range: Arama aralığı (opsiyonel)
            
        Returns:
            Önerilen alternatif aralıkların listesi
        """
        duration = requested.duration()
        
        if search_range:
            start, end = search_range
        else:
            # Varsayılan: istenen günün başı ve sonu
            if isinstance(requested.start, datetime):
                start = requested.start.replace(hour=0, minute=0, second=0)
                end = requested.start.replace(hour=23, minute=59, second=59)
            else:
                start = 0
                end = 24 * 60  # Dakika cinsinden
        
        return self.find_available_slots(start, end, duration)
    
    def clear(self) -> None:
        """Ağacı temizle"""
        self.root = None
        self.size = 0
    
    def __len__(self) -> int:
        return self.size
    
    def __repr__(self):
        return f"IntervalTree(size={self.size})"
    
    def visualize(self) -> str:
        """Ağacı görselleştir"""
        if not self.root:
            return "Empty interval tree"
        
        lines = []
        self._visualize_node(self.root, "", True, lines)
        return "\n".join(lines)
    
    def _visualize_node(self, node: Optional[IntervalNode], prefix: str, 
                        is_last: bool, lines: List[str]):
        if not node:
            return
        
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}[{node.interval.start}, {node.interval.end}) max={node.max_end}")
        
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        children = []
        if node.left:
            children.append(node.left)
        if node.right:
            children.append(node.right)
        
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            self._visualize_node(child, new_prefix, is_last_child, lines)


# Kullanım örneği ve test
if __name__ == "__main__":
    print("=" * 60)
    print("Interval Tree Test - Rezervasyon Çakışma Kontrolü")
    print("=" * 60)
    
    tree = IntervalTree()
    
    # Örnek rezervasyonlar (dakika cinsinden: 9:00 = 540, 10:00 = 600, ...)
    reservations = [
        (540, 600, "Toplantı A"),   # 09:00-10:00
        (630, 720, "Toplantı B"),   # 10:30-12:00
        (780, 840, "Toplantı C"),   # 13:00-14:00
        (900, 960, "Toplantı D"),   # 15:00-16:00
        (600, 660, "Toplantı E"),   # 10:00-11:00
    ]
    
    print("\nRezervasyon ekleniyor:")
    for start, end, name in reservations:
        interval = Interval(start, end, name)
        tree.insert(interval)
        print(f"  {name}: {start//60:02d}:{start%60:02d} - {end//60:02d}:{end%60:02d}")
    
    print(f"\nToplam rezervasyon: {len(tree)}")
    
    # Ağaç yapısı
    print("\nInterval Tree yapısı:")
    print(tree.visualize())
    
    # Çakışma kontrolü
    print("\n" + "=" * 40)
    print("Çakışma Kontrolleri:")
    
    # Çakışan sorgu
    query1 = Interval(570, 650, "Yeni Toplantı 1")  # 09:30-10:50
    overlaps1 = tree.find_overlapping(query1)
    print(f"\n09:30-10:50 ile çakışan rezervasyonlar:")
    for interval in overlaps1:
        print(f"  - {interval.data}: {interval.start//60:02d}:{interval.start%60:02d} - {interval.end//60:02d}:{interval.end%60:02d}")
    
    # Çakışmayan sorgu
    query2 = Interval(720, 780, "Yeni Toplantı 2")  # 12:00-13:00
    overlaps2 = tree.find_overlapping(query2)
    print(f"\n12:00-13:00 ile çakışan rezervasyonlar: {len(overlaps2)}")
    
    # Müsait slotlar
    print("\n" + "=" * 40)
    print("Müsait Zaman Aralıkları (09:00-18:00, min 30 dk):")
    
    available = tree.find_available_slots(540, 1080, 30)
    for slot in available:
        print(f"  {slot.start//60:02d}:{slot.start%60:02d} - {slot.end//60:02d}:{slot.end%60:02d} ({(slot.end-slot.start)} dk)")
    
    # Alternatif öneri
    print("\n" + "=" * 40)
    print("Alternatif Zaman Önerileri:")
    
    requested = Interval(600, 660, "İstenen Toplantı")  # 10:00-11:00 (çakışıyor)
    if tree.has_overlap(requested):
        print(f"10:00-11:00 için çakışma var! Alternatifler:")
        alternatives = tree.suggest_alternative(requested, (540, 1080))
        for alt in alternatives[:3]:  # İlk 3 öneri
            print(f"  - {alt.start//60:02d}:{alt.start%60:02d} - {alt.end//60:02d}:{alt.end%60:02d}")
