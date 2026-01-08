"""
AVL Tree Implementasyonu
========================
Dengeli İkili Arama Ağacı - Rezervasyon ID'lerini ve kullanıcı bilgilerini
hızlı arama, ekleme ve silme işlemleri için kullanılır.

Zaman Karmaşıklığı:
- Arama (Search): O(log n)
- Ekleme (Insert): O(log n)
- Silme (Delete): O(log n)

Uzay Karmaşıklığı: O(n)
"""

from typing import Any, Optional, List, Callable


class AVLNode:
    """AVL Ağacı düğümü"""
    
    def __init__(self, key: Any, value: Any = None):
        self.key = key
        self.value = value if value is not None else key
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height: int = 1
    
    def __repr__(self):
        return f"AVLNode(key={self.key}, value={self.value})"


class AVLTree:
    """
    AVL Tree - Kendi kendini dengeleyen ikili arama ağacı
    
    Özellikler:
    - Her düğümde sol ve sağ alt ağaçların yükseklik farkı en fazla 1
    - Otomatik dengeleme (rotation) ile her zaman O(log n) performans
    """
    
    def __init__(self, compare_func: Callable = None):
        """
        Args:
            compare_func: Özel karşılaştırma fonksiyonu (varsayılan: < operatörü)
        """
        self.root: Optional[AVLNode] = None
        self.size: int = 0
        self._compare = compare_func if compare_func else lambda a, b: (a > b) - (a < b)
    
    def _height(self, node: Optional[AVLNode]) -> int:
        """Düğüm yüksekliğini döndür"""
        return node.height if node else 0
    
    def _balance_factor(self, node: Optional[AVLNode]) -> int:
        """Denge faktörünü hesapla (sol yükseklik - sağ yükseklik)"""
        if not node:
            return 0
        return self._height(node.left) - self._height(node.right)
    
    def _update_height(self, node: AVLNode) -> None:
        """Düğüm yüksekliğini güncelle"""
        node.height = 1 + max(self._height(node.left), self._height(node.right))
    
    def _rotate_right(self, y: AVLNode) -> AVLNode:
        """
        Sağa rotasyon
        
            y                x
           / \\              / \\
          x   C    =>      A   y
         / \\                  / \\
        A   B                B   C
        """
        x = y.left
        B = x.right
        
        # Rotasyonu gerçekleştir
        x.right = y
        y.left = B
        
        # Yükseklikleri güncelle
        self._update_height(y)
        self._update_height(x)
        
        return x
    
    def _rotate_left(self, x: AVLNode) -> AVLNode:
        """
        Sola rotasyon
        
          x                  y
         / \\                / \\
        A   y      =>      x   C
           / \\            / \\
          B   C          A   B
        """
        y = x.right
        B = y.left
        
        # Rotasyonu gerçekleştir
        y.left = x
        x.right = B
        
        # Yükseklikleri güncelle
        self._update_height(x)
        self._update_height(y)
        
        return y
    
    def _rebalance(self, node: AVLNode, key: Any) -> AVLNode:
        """Düğümü dengele"""
        balance = self._balance_factor(node)
        
        # Sol-Sol durumu (Left-Left Case)
        if balance > 1 and self._compare(key, node.left.key) < 0:
            return self._rotate_right(node)
        
        # Sağ-Sağ durumu (Right-Right Case)
        if balance < -1 and self._compare(key, node.right.key) > 0:
            return self._rotate_left(node)
        
        # Sol-Sağ durumu (Left-Right Case)
        if balance > 1 and self._compare(key, node.left.key) > 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        
        # Sağ-Sol durumu (Right-Left Case)
        if balance < -1 and self._compare(key, node.right.key) < 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        
        return node
    
    def insert(self, key: Any, value: Any = None) -> bool:
        """
        Ağaca yeni düğüm ekle
        
        Args:
            key: Anahtar değer
            value: Saklanacak değer (opsiyonel)
            
        Returns:
            bool: Ekleme başarılı ise True
            
        Zaman Karmaşıklığı: O(log n)
        """
        def _insert(node: Optional[AVLNode], key: Any, value: Any) -> AVLNode:
            # Boş düğüme ulaştık, yeni düğüm oluştur
            if not node:
                return AVLNode(key, value)
            
            # Karşılaştırma yap
            cmp = self._compare(key, node.key)
            
            if cmp < 0:
                node.left = _insert(node.left, key, value)
            elif cmp > 0:
                node.right = _insert(node.right, key, value)
            else:
                # Aynı anahtar varsa değeri güncelle
                node.value = value
                return node
            
            # Yüksekliği güncelle
            self._update_height(node)
            
            # Dengeyi kontrol et ve düzelt
            return self._rebalance(node, key)
        
        old_size = self.size
        self.root = _insert(self.root, key, value)
        self.size += 1
        return self.size > old_size
    
    def search(self, key: Any) -> Optional[Any]:
        """
        Anahtara göre değer ara
        
        Args:
            key: Aranacak anahtar
            
        Returns:
            Bulunan değer veya None
            
        Zaman Karmaşıklığı: O(log n)
        """
        node = self._search_node(key)
        return node.value if node else None
    
    def _search_node(self, key: Any) -> Optional[AVLNode]:
        """Anahtara göre düğüm ara"""
        current = self.root
        while current:
            cmp = self._compare(key, current.key)
            if cmp < 0:
                current = current.left
            elif cmp > 0:
                current = current.right
            else:
                return current
        return None
    
    def contains(self, key: Any) -> bool:
        """Anahtar ağaçta var mı kontrol et"""
        return self._search_node(key) is not None
    
    def _find_min(self, node: AVLNode) -> AVLNode:
        """Alt ağaçtaki en küçük düğümü bul"""
        current = node
        while current.left:
            current = current.left
        return current
    
    def _find_max(self, node: AVLNode) -> AVLNode:
        """Alt ağaçtaki en büyük düğümü bul"""
        current = node
        while current.right:
            current = current.right
        return current
    
    def delete(self, key: Any) -> bool:
        """
        Anahtara sahip düğümü sil
        
        Args:
            key: Silinecek anahtar
            
        Returns:
            bool: Silme başarılı ise True
            
        Zaman Karmaşıklığı: O(log n)
        """
        def _delete(node: Optional[AVLNode], key: Any) -> Optional[AVLNode]:
            if not node:
                return None
            
            cmp = self._compare(key, node.key)
            
            if cmp < 0:
                node.left = _delete(node.left, key)
            elif cmp > 0:
                node.right = _delete(node.right, key)
            else:
                # Silinecek düğüm bulundu
                if not node.left:
                    return node.right
                elif not node.right:
                    return node.left
                else:
                    # İki çocuklu düğüm: sağ alt ağacın en küçüğünü al
                    successor = self._find_min(node.right)
                    node.key = successor.key
                    node.value = successor.value
                    node.right = _delete(node.right, successor.key)
            
            # Yüksekliği güncelle
            self._update_height(node)
            
            # Dengeyi kontrol et
            balance = self._balance_factor(node)
            
            # Sol-Sol durumu
            if balance > 1 and self._balance_factor(node.left) >= 0:
                return self._rotate_right(node)
            
            # Sol-Sağ durumu
            if balance > 1 and self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)
            
            # Sağ-Sağ durumu
            if balance < -1 and self._balance_factor(node.right) <= 0:
                return self._rotate_left(node)
            
            # Sağ-Sol durumu
            if balance < -1 and self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)
            
            return node
        
        if not self.contains(key):
            return False
        
        self.root = _delete(self.root, key)
        self.size -= 1
        return True
    
    def get_min(self) -> Optional[Any]:
        """En küçük anahtarlı değeri döndür"""
        if not self.root:
            return None
        return self._find_min(self.root).value
    
    def get_max(self) -> Optional[Any]:
        """En büyük anahtarlı değeri döndür"""
        if not self.root:
            return None
        return self._find_max(self.root).value
    
    def inorder_traversal(self) -> List[Any]:
        """Inorder (sıralı) gezinti - O(n)"""
        result = []
        
        def _inorder(node: Optional[AVLNode]):
            if node:
                _inorder(node.left)
                result.append((node.key, node.value))
                _inorder(node.right)
        
        _inorder(self.root)
        return result
    
    def preorder_traversal(self) -> List[Any]:
        """Preorder gezinti - O(n)"""
        result = []
        
        def _preorder(node: Optional[AVLNode]):
            if node:
                result.append((node.key, node.value))
                _preorder(node.left)
                _preorder(node.right)
        
        _preorder(self.root)
        return result
    
    def postorder_traversal(self) -> List[Any]:
        """Postorder gezinti - O(n)"""
        result = []
        
        def _postorder(node: Optional[AVLNode]):
            if node:
                _postorder(node.left)
                _postorder(node.right)
                result.append((node.key, node.value))
        
        _postorder(self.root)
        return result
    
    def level_order_traversal(self) -> List[List[Any]]:
        """Level order (BFS) gezinti - O(n)"""
        if not self.root:
            return []
        
        result = []
        queue = [self.root]
        
        while queue:
            level = []
            level_size = len(queue)
            
            for _ in range(level_size):
                node = queue.pop(0)
                level.append((node.key, node.value))
                
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            
            result.append(level)
        
        return result
    
    def range_query(self, low: Any, high: Any) -> List[Any]:
        """
        Belirli aralıktaki tüm değerleri döndür
        
        Args:
            low: Alt sınır (dahil)
            high: Üst sınır (dahil)
            
        Returns:
            Aralıktaki değerlerin listesi
            
        Zaman Karmaşıklığı: O(log n + k) - k: sonuç sayısı
        """
        result = []
        
        def _range_query(node: Optional[AVLNode]):
            if not node:
                return
            
            # Sol alt ağaç low'dan büyük olabilir
            if self._compare(node.key, low) > 0:
                _range_query(node.left)
            
            # Mevcut düğüm aralıkta mı?
            if self._compare(node.key, low) >= 0 and self._compare(node.key, high) <= 0:
                result.append((node.key, node.value))
            
            # Sağ alt ağaç high'dan küçük olabilir
            if self._compare(node.key, high) < 0:
                _range_query(node.right)
        
        _range_query(self.root)
        return result
    
    def get_height(self) -> int:
        """Ağacın yüksekliğini döndür"""
        return self._height(self.root)
    
    def is_balanced(self) -> bool:
        """Ağacın dengeli olup olmadığını kontrol et"""
        def _check_balance(node: Optional[AVLNode]) -> bool:
            if not node:
                return True
            
            balance = self._balance_factor(node)
            if abs(balance) > 1:
                return False
            
            return _check_balance(node.left) and _check_balance(node.right)
        
        return _check_balance(self.root)
    
    def clear(self) -> None:
        """Ağacı temizle"""
        self.root = None
        self.size = 0
    
    def __len__(self) -> int:
        return self.size
    
    def __contains__(self, key: Any) -> bool:
        return self.contains(key)
    
    def __iter__(self):
        """Inorder sırasıyla iterasyon"""
        for key, value in self.inorder_traversal():
            yield key, value
    
    def __repr__(self):
        return f"AVLTree(size={self.size}, height={self.get_height()})"
    
    def visualize(self, max_depth: int = 5) -> str:
        """Ağacı görselleştir (konsol için)"""
        if not self.root:
            return "Empty tree"
        
        lines = []
        self._visualize_node(self.root, "", True, lines, 0, max_depth)
        return "\n".join(lines)
    
    def _visualize_node(self, node: Optional[AVLNode], prefix: str, is_last: bool, 
                        lines: List[str], depth: int, max_depth: int):
        if not node or depth > max_depth:
            return
        
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{node.key} (h={node.height})")
        
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        children = []
        if node.left:
            children.append(("L", node.left))
        if node.right:
            children.append(("R", node.right))
        
        for i, (side, child) in enumerate(children):
            is_last_child = (i == len(children) - 1)
            self._visualize_node(child, new_prefix, is_last_child, lines, depth + 1, max_depth)


# Kullanım örneği ve test
if __name__ == "__main__":
    print("=" * 60)
    print("AVL Tree Test")
    print("=" * 60)
    
    tree = AVLTree()
    
    # Ekleme testleri
    test_values = [50, 30, 70, 20, 40, 60, 80, 15, 25, 35, 45]
    print(f"\nEklenen değerler: {test_values}")
    
    for val in test_values:
        tree.insert(val, f"Rezervasyon_{val}")
    
    print(f"\nAğaç boyutu: {len(tree)}")
    print(f"Ağaç yüksekliği: {tree.get_height()}")
    print(f"Dengeli mi?: {tree.is_balanced()}")
    
    # Görselleştirme
    print("\nAğaç yapısı:")
    print(tree.visualize())
    
    # Arama testi
    print(f"\nArama(40): {tree.search(40)}")
    print(f"Arama(100): {tree.search(100)}")
    
    # Aralık sorgusu
    print(f"\nAralık sorgusu (25-50): {tree.range_query(25, 50)}")
    
    # Silme testi
    print(f"\n30 siliniyor...")
    tree.delete(30)
    print(f"Yeni boyut: {len(tree)}")
    print(f"Hala dengeli mi?: {tree.is_balanced()}")
    
    print("\nGüncel ağaç yapısı:")
    print(tree.visualize())
    
    # Gezinti
    print(f"\nInorder traversal: {tree.inorder_traversal()}")
